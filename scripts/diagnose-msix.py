#!/usr/bin/env python3
"""Pre-upload audit for a Microsoft Store MSIX.

Explains, from the file itself, every condition Partner Center validates before it accepts a
package for certification — including the ones behind a bare "certification failed with error
code 5001" (which Microsoft documents only as a failed preprocessing / unusable package).

Usage:
    python scripts/diagnose-msix.py path/to/Ahmedbecetti.AURIXAI_1.0.3.0_x64.msix

Everything is read-only: the file is never modified, repacked or renamed. Exit code 0 means the
audit found no blocking problem; 1 means at least one FAIL. WARNINGs never fail the run.
"""
import base64
import hashlib
import json
import re
import struct
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOCK = 65536
NSA = {
    'f': '{http://schemas.microsoft.com/appx/manifest/foundation/windows10}',
    'uap': '{http://schemas.microsoft.com/appx/manifest/uap/windows10}',
    'rescap': '{http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities}',
}
BM = '{http://schemas.microsoft.com/appx/2010/blockmap}'
# Microsoft stopped accepting packages that target Windows 10 1803 (10.0.17134) or older.
MIN_TARGET = (10, 0, 17763, 0)
ASSET_SIZES = {
    'StoreLogo.png': (50, 50), 'Square44x44Logo.png': (44, 44),
    'Square150x150Logo.png': (150, 150), 'Square310x310Logo.png': (310, 310),
    'Wide310x150Logo.png': (310, 150),
}
BAD_CHARS = re.compile(r'[\\:*?"<>|\x00-\x1f]')
RESERVED = re.compile(r'^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?$', re.I)

results = []


def check(level, area, message):
    results.append((level, area, message))


def ok(area, message):
    check('PASS', area, message)


def warn(area, message):
    check('WARN', area, message)


def fail(area, message):
    check('FAIL', area, message)


def version_tuple(value):
    try:
        return tuple(int(part) for part in str(value).split('.'))
    except ValueError:
        return None


def png_size(data):
    if len(data) < 24 or data[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    return struct.unpack('>II', data[16:24])


def pe_arch(data):
    """Return 'x64'/'x86'/'arm64'/None for a PE image, or None when it is not a PE file."""
    if len(data) < 64 or data[:2] != b'MZ':
        return None
    offset = struct.unpack('<I', data[60:64])[0]
    if offset + 6 > len(data) or data[offset:offset + 4] != b'PE\0\0':
        return None
    machine = struct.unpack('<H', data[offset + 4:offset + 6])[0]
    return {0x8664: 'x64', 0x014c: 'x86', 0xaa64: 'arm64'}.get(machine, hex(machine))


def load_product():
    try:
        return json.loads((ROOT / 'store/product.json').read_text(encoding='utf-8'))
    except Exception:
        return {}


def load_identity():
    for name in ('store/identity.json', 'store/identity.store.json'):
        path = ROOT / name
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
    return {}


def audit(package):
    package = Path(package)
    product, identity = load_product(), load_identity()

    # ---------------------------------------------------------------- 1. the file itself
    area = 'file'
    if not package.exists():
        fail(area, 'File not found: %s' % package)
        return
    raw = package.read_bytes()
    ok(area, 'File: %s (%d bytes, sha256 %s)' % (package.name, len(raw), hashlib.sha256(raw).hexdigest()))
    if not raw.startswith(b'PK'):
        fail(area, 'Not a ZIP container. An MSIX starts with "PK"; a renamed EXE/ZIP with a wrapper will fail preprocessing.')
        return
    if package.suffix.lower() not in ('.msix', '.appx'):
        warn(area, 'Extension is %s. Upload the .msix/.appx itself, not the outer artifact ZIP.' % package.suffix)
    try:
        archive = zipfile.ZipFile(package)
    except zipfile.BadZipFile as error:
        fail(area, 'ZIP structure is damaged (%s). This is the classic 5001 cause: re-download or rebuild.' % error)
        return
    bad = archive.testzip()
    if bad:
        fail(area, 'CRC mismatch in %s — the upload/transfer corrupted the file.' % bad)
    else:
        ok(area, 'ZIP central directory and every CRC are intact')

    entries, seen = {}, {}
    for entry in archive.infolist():
        name = entry.filename.replace('\\', '/')
        if entry.is_dir():
            continue
        entries[name] = entry
        folded = name.casefold()
        if folded in seen:
            fail(area, 'Duplicate/case-colliding path: %s vs %s' % (seen[folded], name))
        seen[folded] = name
        if name.startswith('/') or '..' in name.split('/'):
            fail(area, 'Absolute or traversing path not allowed: %s' % name)
        for part in name.split('/'):
            if BAD_CHARS.search(part):
                fail(area, 'Illegal character in package path: %s' % name)
            if RESERVED.match(part):
                fail(area, 'Windows-reserved file name inside the package: %s' % name)
            if part != part.rstrip(' .'):
                fail(area, 'Trailing dot/space in package path: %s' % name)
        if entry.file_size == 0:
            warn(area, 'Zero-byte file in package: %s' % name)
        if entry.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            fail(area, 'Unsupported compression method %s on %s' % (entry.compress_type, name))
    for required in ('AppxManifest.xml', 'AppxBlockMap.xml', '[Content_Types].xml'):
        if required not in entries:
            fail(area, 'Missing root file %s — not a valid MSIX (this alone blocks submission).' % required)
    if 'AppxSignature.p7x' in entries:
        ok(area, 'Package carries AppxSignature.p7x (the Store re-signs it anyway)')
    else:
        ok(area, 'Package is unsigned — accepted for Store upload; the Store signs it after certification')
    ok(area, '%d payload files, largest %.1f MB' % (
        len(entries), max((e.file_size for e in entries.values()), default=0) / 1048576))

    if not {'AppxManifest.xml', 'AppxBlockMap.xml'} <= set(entries):
        return

    # ---------------------------------------------------------------- 2. manifest identity
    area = 'identity'
    try:
        manifest = ET.fromstring(archive.read('AppxManifest.xml'))
    except ET.ParseError as error:
        fail(area, 'AppxManifest.xml is not well-formed XML: %s' % error)
        return
    node = manifest.find(NSA['f'] + 'Identity')
    if node is None:
        fail(area, 'Manifest has no <Identity> element')
        return
    name, publisher = node.get('Name', ''), node.get('Publisher', '')
    version, arch = node.get('Version', ''), node.get('ProcessorArchitecture', '')
    full_name = '%s_%s_%s' % (name, version, arch.lower())
    ok(area, 'Identity Name: %s' % name)
    ok(area, 'Publisher: %s' % publisher)
    ok(area, 'Version: %s   Architecture: %s' % (version, arch))
    ok(area, 'Full name: %s' % full_name)

    if identity.get('identityName') and name != identity['identityName']:
        fail(area, 'Name does not match the reserved product identity (%s)' % identity['identityName'])
    if identity.get('publisher') and publisher != identity['publisher']:
        fail(area, 'Publisher does not match Partner Center (%s)' % identity['publisher'])
    if arch.lower() != 'x64':
        fail(area, 'Architecture is %s; this product is x64-only' % arch)
    if not re.fullmatch(r'\d+\.\d+\.\d+\.0', version):
        fail(area, 'Version must be four parts with a zero revision (got %s)' % version)
    published = [str(v).lower() for v in product.get('publishedFullNames', [])]
    if full_name.lower() in published:
        fail(area, 'Full name %s is already published with different contents — Partner Center rejects it. Bump package.json.' % full_name)
    live = version_tuple(product.get('liveVersion', ''))
    if live and version_tuple(version) and version_tuple(version) <= live:
        fail(area, 'Version %s is not higher than the published %s' % (version, product.get('liveVersion')))
    elif live:
        ok(area, 'Version is higher than the published %s' % product.get('liveVersion'))

    display = manifest.find(NSA['f'] + 'Properties/' + NSA['f'] + 'DisplayName')
    if display is not None and product.get('reservedDisplayName') and display.text.strip() != product['reservedDisplayName']:
        fail(area, 'Properties/DisplayName "%s" is not the reserved name "%s"' % (display.text, product['reservedDisplayName']))
    description = manifest.find(NSA['f'] + 'Properties/' + NSA['f'] + 'Description')
    if description is not None and len(description.text or '') > 2048:
        fail(area, 'Properties/Description is longer than 2048 characters')

    # ---------------------------------------------------------------- 3. dependencies / targeting
    area = 'dependencies'
    families = manifest.findall(NSA['f'] + 'Dependencies/' + NSA['f'] + 'TargetDeviceFamily')
    if not families:
        fail(area, 'No TargetDeviceFamily dependency — cannot install on any device family')
    desktop = [f for f in families if f.get('Name') == 'Windows.Desktop']
    if not desktop:
        fail(area, 'Windows.Desktop target missing; this is a full-trust desktop package')
    else:
        target = desktop[0]
        minimum, tested = version_tuple(target.get('MinVersion', '')), version_tuple(target.get('MaxVersionTested', ''))
        ok(area, 'Target: Windows.Desktop MinVersion=%s MaxVersionTested=%s' % (target.get('MinVersion'), target.get('MaxVersionTested')))
        if minimum and minimum < MIN_TARGET:
            fail(area, 'MinVersion %s is below the Store minimum 10.0.17763.0 — Partner Center rejects it at upload.' % target.get('MinVersion'))
        if tested and minimum and tested < minimum:
            fail(area, 'MaxVersionTested (%s) is lower than MinVersion (%s)' % (target.get('MaxVersionTested'), target.get('MinVersion')))
    frameworks = manifest.findall(NSA['f'] + 'Dependencies/' + NSA['f'] + 'PackageDependency')
    if frameworks:
        for dep in frameworks:
            warn(area, 'Extra framework dependency %s %s — the Store will require that framework to be trusted.' % (dep.get('Name'), dep.get('MinVersion')))
    else:
        ok(area, 'No extra package dependencies (self-contained Electron runtime)')
    resources = [r.get('Language') for r in manifest.findall(NSA['f'] + 'Resources/' + NSA['f'] + 'Resource')]
    ok(area, 'Declared resource languages: %s' % (', '.join(resources) if resources else 'none'))

    # ---------------------------------------------------------------- 4. application entry point
    area = 'application'
    apps = manifest.findall(NSA['f'] + 'Applications/' + NSA['f'] + 'Application')
    if not apps:
        fail(area, 'Manifest declares no <Application>')
    for app in apps:
        declared_exe = app.get('Executable', '')
        exe, entry = declared_exe.replace('\\', '/'), app.get('EntryPoint', '')
        ok(area, 'Executable: %s   EntryPoint: %s' % (declared_exe, entry))
        if entry != 'Windows.FullTrustApplication':
            fail(area, 'EntryPoint must be Windows.FullTrustApplication for a packaged desktop app')
        caps = manifest.findall(NSA['f'] + 'Capabilities/' + NSA['rescap'] + 'Capability')
        if 'runFullTrust' not in [c.get('Name') for c in caps]:
            fail(area, 'runFullTrust capability is missing — required by Windows.FullTrustApplication')
        else:
            ok(area, 'runFullTrust declared (needs the restricted-capability justification in Partner Center)')
        if exe not in entries:
            fail(area, 'Executable %s is not inside the package (case-sensitive match required)' % exe)
        else:
            machine = pe_arch(archive.read(exe))
            if machine != 'x64':
                fail(area, '%s is %s, not x64' % (exe, machine or 'not a PE binary'))
            else:
                ok(area, '%s is a valid x64 PE image (%.1f MB)' % (exe, entries[exe].file_size / 1048576))
        visuals = app.findall(NSA['uap'] + 'VisualElements')
        for visual in visuals:
            for attr in ('Square150x150Logo', 'Square44x44Logo'):
                if not visual.get(attr):
                    fail(area, 'VisualElements/{%s} is missing' % attr)
            tiles = visual.findall(NSA['uap'] + 'DefaultTile')
            sources = [visual.get('Square150x150Logo'), visual.get('Square44x44Logo')]
            for tile in tiles:
                sources += [tile.get('Wide310x150Logo'), tile.get('Square310x310Logo')]
            for logo in [s.replace('\\', '/') for s in sources if s]:
                if logo not in entries:
                    fail(area, 'Declared logo is not in the package: %s' % logo)
                    continue
                size = png_size(archive.read(logo))
                expected = ASSET_SIZES.get(logo.split('/')[-1])
                if size is None:
                    fail(area, '%s is not a PNG' % logo)
                elif expected and size != expected:
                    fail(area, '%s is %dx%d but %dx%d is required' % (logo, *size, *expected))
                else:
                    ok(area, '%s %dx%d OK' % (logo, *size))

    # ---------------------------------------------------------------- 5. block map / payload integrity
    area = 'blockmap'
    try:
        blockmap = ET.fromstring(archive.read('AppxBlockMap.xml'))
    except ET.ParseError as error:
        fail(area, 'AppxBlockMap.xml is malformed: %s' % error)
        return
    mapped, mismatched = set(), 0
    for item in blockmap.findall(BM + 'File'):
        name = (item.get('Name') or '').replace('\\', '/')
        if name not in entries:
            fail(area, 'Block map lists a file that is not in the ZIP: %s' % name)
            continue
        mapped.add(name)
        entry = entries[name]
        if entry.file_size != int(item.get('Size', '-1')):
            fail(area, 'Size mismatch between block map and ZIP for %s' % name)
        declared = [b.get('Hash') for b in item.findall(BM + 'Block')]
        data = archive.read(name)
        for index in range(0, len(data), BLOCK):
            expected = declared[index // BLOCK] if index // BLOCK < len(declared) else None
            if expected is None:
                fail(area, 'Missing block hash %d for %s' % (index // BLOCK, name))
                continue
            if base64.b64encode(hashlib.sha256(data[index:index + BLOCK]).digest()).decode() != expected:
                mismatched += 1
    if mismatched:
        fail(area, '%d block hashes do not match the payload — the archive was rewritten after signing/packing.' % mismatched)
    elif mapped:
        ok(area, 'All %d files and every SHA-256 block in AppxBlockMap.xml match the payload' % len(mapped))
    payload = {n for n in entries if n not in ('AppxBlockMap.xml', '[Content_Types].xml', 'AppxSignature.p7x')}
    if mapped != payload:
        missing = sorted(payload - mapped)[:5]
        fail(area, 'Block map does not cover exactly the payload; unhashed: %s' % missing)
    elif mapped:
        ok(area, 'Block map covers exactly the payload file set')


def report(package):
    audit(package)
    widths = {'PASS': 'PASS', 'WARN': 'WARN', 'FAIL': 'FAIL'}
    print('\nMSIX pre-upload audit — %s' % Path(package).name)
    print('=' * 78)
    last = None
    for level, area, message in results:
        if area != last:
            print('\n[%s]' % area)
            last = area
        print('  %s  %s' % (widths[level], message))
    fails = [r for r in results if r[0] == 'FAIL']
    warns = [r for r in results if r[0] == 'WARN']
    print('\n' + '=' * 78)
    print('%d PASS · %d WARN · %d FAIL' % (
        sum(1 for r in results if r[0] == 'PASS'), len(warns), len(fails)))
    if fails:
        print('\nDo not upload this file. Fix every FAIL above, rebuild with a higher version if')
        print('identity/structure changed, then run this audit again.')
    else:
        print('\nNo blocking problem found in the package itself. If Partner Center still fails')
        print('with 5001, the remaining causes are outside the package: an incomplete submission')
        print('section (age rating, restricted capability, privacy URL, screenshots) or a Store-side')
        print('processing error — open a support ticket with this audit report attached.')
    return 1 if fails else 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(report(sys.argv[1]))
