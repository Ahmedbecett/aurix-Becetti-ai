# Capture real, user-arranged AURIX windows. No test data or authentication bypass.
# Run locally on Windows: powershell -ExecutionPolicy Bypass -File .\scripts\capture-windows-store-screenshots.ps1
param([string]$OutputDirectory = "$env:USERPROFILE\Desktop\AURIX-Store-Screenshots")
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class AurixCapture {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd, int command);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
}
'@
[AurixCapture]::SetProcessDPIAware() | Out-Null
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
Write-Host 'Start the final AURIX MSIX on Windows. Use a disposable account and only non-confidential content.'
Write-Host 'Use a display of at least 1920x1080. Close private notifications and overlapping windows.'
$scenes = @(
  @('01-dashboard','Open Dashboard. Real zero counts are fine.'),
  @('02-image-result','Generate a real image successfully. Do NOT substitute an imported or fake result.'),
  @('03-writing-or-code','Generate a real writing/code response and review it.'),
  @('04-projects','Open Projects or History with your own non-confidential saved work.')
)
$provenance = @()
foreach ($scene in $scenes) {
  Write-Host "`n$($scene[1])"
  $answer = Read-Host 'Arrange the AURIX screen; Enter to capture, or S to skip'
  if ($answer -eq 'S') { continue }
  $process = Get-Process -Name AURIX -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
  if (-not $process) { throw 'AURIX window not found. Start the actual packaged application.' }
  $handle = $process.MainWindowHandle
  [AurixCapture]::ShowWindow($handle, 3) | Out-Null
  [AurixCapture]::SetForegroundWindow($handle) | Out-Null
  Start-Sleep -Seconds 3
  $rect = New-Object AurixCapture+RECT
  if (-not [AurixCapture]::GetWindowRect($handle, [ref]$rect)) { throw 'Could not read window bounds.' }
  # Clamp invisible maximized-window borders to the actual display bounds.
  $screen = [System.Windows.Forms.Screen]::FromHandle($handle).Bounds
  $left = [Math]::Max($rect.Left, $screen.Left); $top = [Math]::Max($rect.Top, $screen.Top)
  $right = [Math]::Min($rect.Right, $screen.Right); $bottom = [Math]::Min($rect.Bottom, $screen.Bottom)
  $width = $right-$left; $height = $bottom-$top
  if ($width -lt 1366 -or $height -lt 768) { throw 'Capture too small. Use a larger desktop display; no artificial upscaling.' }
  $bitmap = New-Object System.Drawing.Bitmap($width, $height)
  $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
  $file = Join-Path $OutputDirectory ($scene[0]+'.png')
  try {
    $graphics.CopyFromScreen($left, $top, 0, 0, $bitmap.Size)
    $bitmap.Save($file, [System.Drawing.Imaging.ImageFormat]::Png)
  } finally { $graphics.Dispose(); $bitmap.Dispose() }
  $provenance += [pscustomobject]@{ file = $scene[0]+'.png'; width = $width; height = $height; capturedAt = (Get-Date).ToUniversalTime().ToString('o'); process = 'AURIX'; runtime = 'Local Windows process; owner must confirm final MSIX/version'; ownerReviewRequired = $true }
  Write-Host "Saved $file. Inspect for obstructions and private data before upload."
}
$provenance | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $OutputDirectory 'provenance.json')
Write-Host "Done: $OutputDirectory. Inspect every PNG; this script does not prove MSIX identity or Store approval."
