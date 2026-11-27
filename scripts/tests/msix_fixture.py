"""Build a synthetic, structurally valid MSIX fixture.

This is NOT a runnable Windows package and never becomes a release artifact: it exists only so
`scripts/tests/test_diagnose_msix.py` can exercise `scripts/diagnose-msix.py` on Linux.
"""
import base64
import hashlib
import struct
import xml.etree.ElementTree as ET
import zipfile
import zlib

BLOCK = 65536
BM = '{http://schemas.microsoft.com/appx/2010/blockmap}'
LOGOS = {
    'StoreLogo.png': (50, 50), 'Square44x44Logo.png': (44, 44), 'Square150x150Logo.png': (150, 150),
    'Square310x310Logo.png': (310, 310), 'Wide310x150Logo.png': (310, 150),
}
MANIFEST = '''<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
         xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities">
  <Identity Name="Ahmedbecetti.AURIXAI" Publisher="CN=A5D5DC31-4A15-4059-8030-D96C51054596" Version="{version}" ProcessorArchitecture="{arch}" />
  <Properties><DisplayName>AURIX AI</DisplayName><PublisherDisplayName>Ahmedbecetti</PublisherDisplayName><Description>Fixture</Description><Logo>Assets\\StoreLogo.png</Logo></Properties>
  <Resources><Resource Language="en-us" /></Resources>
  <Dependencies><TargetDeviceFamily Name="Windows.Desktop" MinVersion="{min_version}" MaxVersionTested="10.0.19045.0" /></Dependencies>
  <Applications><Application Id="AURIX" Executable="{executable}" EntryPoint="{entry_point}">
    <uap:VisualElements DisplayName="AURIX AI" Description="Fixture" BackgroundColor="#0b1020"
        Square150x150Logo="Assets\\Square150x150Logo.png" Square44x44Logo="Assets\\Square44x44Logo.png">
      <uap:DefaultTile Wide310x150Logo="Assets\\Wide310x150Logo.png" Square310x310Logo="Assets\\Square310x310Logo.png" />
    </uap:VisualElements>
  </Application></Applications>
  <Capabilities><rescap:Capability Name="runFullTrust" /></Capabilities>
</Package>'''


def png(width, height):
    def chunk(kind, data):
        body = kind + data
        return struct.pack('>I', len(data)) + body + struct.pack('>I', zlib.crc32(body) & 0xffffffff)
    header = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    raw = b''.join(b'\x00' + b'\x0b\x10\x20\xff' * width for _ in range(height))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header)
            + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


def pe(machine=0x8664):
    data = bytearray(1024)
    data[0:2] = b'MZ'
    struct.pack_into('<I', data, 60, 128)
    data[128:132] = b'PE\0\0'
    struct.pack_into('<H', data, 132, machine)
    return bytes(data)


def build(path, version='1.0.3.0', arch='x64', min_version='10.0.17763.0',
          executable='app\\AURIX.exe', entry_point='Windows.FullTrustApplication',
          logo_size=(150, 150), ship_executable=True):
    files = {}
    if ship_executable:
        files[executable.replace('\\', '/')] = pe(0x8664 if arch == 'x64' else 0x014c)
    for name, size in LOGOS.items():
        files['Assets/' + name] = png(*(logo_size if name == 'Square150x150Logo.png' else size))
    files['AppxManifest.xml'] = MANIFEST.format(
        version=version, arch=arch, min_version=min_version,
        executable=executable, entry_point=entry_point).encode()
    blockmap = ET.Element(BM + 'BlockMap', {'HashMethod': 'http://www.w3.org/2001/04/xmlenc#sha256'})
    for name, data in files.items():
        item = ET.SubElement(blockmap, BM + 'File',
                             {'Name': name.replace('/', '\\'), 'Size': str(len(data)), 'LfhSize': '0'})
        for index in range(0, len(data), BLOCK):
            ET.SubElement(item, BM + 'Block', {
                'Hash': base64.b64encode(hashlib.sha256(data[index:index + BLOCK]).digest()).decode()})
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)
        archive.writestr('AppxBlockMap.xml', ET.tostring(blockmap))
        archive.writestr('[Content_Types].xml', '<Types/>')
    return path
