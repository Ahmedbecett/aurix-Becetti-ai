[CmdletBinding()]
param([string]$IdentityFile = '')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Invoke-Checked {
    param([string]$File, [string[]]$Arguments)
    & $File @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$File failed with exit code $LASTEXITCODE" }
}
function Find-MakeAppx {
    $command = Get-Command makeappx.exe -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    $kits = Join-Path ${env:ProgramFiles(x86)} 'Windows Kits\10\bin'
    if (Test-Path $kits) {
        $candidates = Get-ChildItem $kits -Directory | Where-Object { $_.Name -match '^10\.0\.\d+\.0$' } | Sort-Object { [version]$_.Name } -Descending
        foreach ($directory in $candidates) {
            $tool = Join-Path $directory.FullName 'x64\makeappx.exe'
            if (Test-Path $tool) { return $tool }
        }
    }
    throw 'MakeAppx.exe not found. Install the Windows 10/11 SDK packaging tools first.'
}
if ($env:OS -ne 'Windows_NT') { throw 'The final MSIX must be built on Windows with the Windows SDK.' }
$IdentityArguments = @()
if ($IdentityFile) { $IdentityArguments = @('--identity', $IdentityFile) }
Invoke-Checked 'node' (@('scripts/store.cjs', '--check') + $IdentityArguments)
$MakeAppx = Find-MakeAppx
$env:CSC_IDENTITY_AUTO_DISCOVERY = 'false'
$env:PYTHONUTF8 = '1'
Invoke-Checked 'npm.cmd' @('test')
Invoke-Checked 'npx.cmd' @('--no-install', 'electron-builder', '--win', '--x64', '--dir', '--publish', 'never', '--config.directories.output=dist/store-runtime')
Invoke-Checked 'node' (@('scripts/store.cjs', '--app-dir', 'dist/store-runtime/win-unpacked') + $IdentityArguments)
$report = Get-Content 'dist/store/store-build.json' -Raw | ConvertFrom-Json
$package = Join-Path $Root ('dist\store\' + $report.packageFile)
# Keep MakeAppx schema/semantic validation enabled. Never use /nv here.
& $MakeAppx pack /d (Join-Path $Root 'dist\store\staging') /p $package /o 2>&1 | Tee-Object -FilePath 'dist/store/makeappx.log'
if ($LASTEXITCODE -ne 0) { throw "MakeAppx validation/pack failed with exit code $LASTEXITCODE" }
if (!(Test-Path $package)) { throw 'MakeAppx returned without producing the expected MSIX.' }
# Validate the emitted package itself, not only the input manifest/staging tree.
Invoke-Checked 'python' @('-X', 'utf8', 'scripts/verify-msix.py', $package, '--manifest', 'dist/store/staging/AppxManifest.xml', '--staged', 'dist/store/staging', '--report', 'dist/store/msix-integrity.json')
$Unpacked = Join-Path $Root 'dist\store\sdk-unpacked'
& $MakeAppx unpack /p $package /d $Unpacked /o 2>&1 | Tee-Object -FilePath 'dist/store/makeappx-unpack.log'
if ($LASTEXITCODE -ne 0) { throw "MakeAppx round-trip unpack validation failed with exit code $LASTEXITCODE" }
$integrity = Get-Content 'dist/store/msix-integrity.json' -Raw | ConvertFrom-Json
$integrity | Add-Member -NotePropertyName sdkUnpackVerified -NotePropertyValue $true
$integrity | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 'dist/store/msix-integrity.json'
Write-Host "Verified package size: $($integrity.bytes) bytes; SHA256: $($integrity.sha256)"
$hash = Get-FileHash $package -Algorithm SHA256
"$($hash.Hash.ToLower())  $($report.packageFile)" | Set-Content -Encoding utf8 'dist/store/SHA256SUMS.txt'
Copy-Item 'dist/store/staging/AppxManifest.xml' 'dist/store/AppxManifest.xml' -Force
Write-Host "Built unsigned Store candidate: $package"
Write-Host 'Not ready for public sideloading. Complete Windows testing, WACK, screenshots and Partner Center declarations before submission.'

# ---------------------------------------------------------------------------------------------
# Pre-publish gate. This build is only useful if its package full name does not already exist on
# the product: Partner Center rejects a second payload under an existing name, and re-uploading a
# version that already failed certification (1.0.3.0 / error 5001) fails again.
# When STORE_ACCESS_TOKEN is set, the answer comes from Partner Center itself.
# ---------------------------------------------------------------------------------------------
# A clash that Partner Center knows about is fatal. Without a token only the local lists apply, so the
# artifact stays a dev download and the upload step must run the preflight with a token first.
node scripts/store-preflight.cjs --enforce
$preflight = if ($LASTEXITCODE -eq 0 -and $env:STORE_ACCESS_TOKEN) { 'partner-center-confirmed' } elseif ($LASTEXITCODE -eq 0) { 'local-lists-only' } else { 'unknown' }
$report = Get-Content 'dist/store/store-build.json' -Raw | ConvertFrom-Json
$report | Add-Member -NotePropertyName preflight -NotePropertyValue $preflight -Force
$report | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 'dist/store/store-build.json'
if ($preflight -eq 'unknown') { throw 'The store preflight could not confirm that this package full name is free.' }
Write-Host "Preflight: $preflight" 
$gate = Get-Content 'dist/store/store-build.json' -Raw | ConvertFrom-Json
Write-Host "Publish this file only: $($gate.packageFile)  ($($gate.manifestSHA256.Substring(0,12))...)"
