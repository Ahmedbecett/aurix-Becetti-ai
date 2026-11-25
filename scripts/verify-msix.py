#!/usr/bin/env python3
"""Independently check the actual MSIX ZIP, CRCs and SHA-256 block map.
Never repacks, renames or modifies the package. SDK validation is also required.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

BLOCK = 65536
BM = '{http://schemas.microsoft.com/appx/2010/blockmap}'
FOUNDATION = '{http://schemas.microsoft.com/appx/manifest/foundation/windows10}'
FOOTPRINTS = {'AppxBlockMap.xml', '[Content_Types].xml', 'AppxSignature.p7x'}


def name(value):
    value = value.replace('\\', '/')
    if value.startswith('/') or any(part in ('', '.', '..') for part in value.split('/')) or ':' in value:
        raise ValueError('Unsafe archive path: ' + value)
    return value


def file_sha256(filename):
    digest = hashlib.sha256()
    with Path(filename).open('rb') as data:
        for chunk in iter(lambda: data.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify(package, expected_manifest=None, staged=None):
    package = Path(package)
    with zipfile.ZipFile(package) as archive:
        entries = {}
        seen = set()
        for entry in archive.infolist():
            normalized = name(entry.filename.rstrip('/') if entry.is_dir() else entry.filename)
            if normalized.casefold() in seen:
                raise ValueError('Duplicate/case-colliding package path: ' + normalized)
            seen.add(normalized.casefold())
            if entry.flag_bits & 1:
                raise ValueError('Encrypted ZIP entry is not allowed')
            if not entry.is_dir():
                entries[normalized] = entry
        for required in ('AppxManifest.xml', 'AppxBlockMap.xml', '[Content_Types].xml'):
            if required not in entries:
                raise ValueError('Not a root-level MSIX package; missing ' + required + '. Do not upload the outer artifact ZIP.')
        # read() checks the CRC of each footprint as well as its XML structure.
        manifest_bytes = archive.read(entries['AppxManifest.xml'])
        manifest = ET.fromstring(manifest_bytes)
        identity = manifest.find(FOUNDATION + 'Identity')
        if identity is None:
            raise ValueError('Missing manifest Identity')
        if expected_manifest:
            expected_bytes = Path(expected_manifest).read_bytes()
            expected = ET.fromstring(expected_bytes).find(FOUNDATION + 'Identity')
            if expected is None or identity.attrib != expected.attrib:
                raise ValueError('Packaged identity/version differs from staged manifest')
        ET.fromstring(archive.read(entries['[Content_Types].xml']))
        blockmap = ET.fromstring(archive.read(entries['AppxBlockMap.xml']))
        if blockmap.tag != BM + 'BlockMap' or blockmap.attrib.get('HashMethod') != 'http://www.w3.org/2001/04/xmlenc#sha256':
            raise ValueError('Unsupported MSIX block-map format/hash method')
        mapped = set()
        files = {}
        for item in blockmap.findall(BM + 'File'):
            filename = name(item.attrib['Name'])
            if filename in mapped or filename not in entries:
                raise ValueError('Missing/duplicate block-map payload: ' + filename)
            mapped.add(filename)
            entry = entries[filename]
            if entry.file_size != int(item.attrib['Size']):
                raise ValueError('Block-map file size mismatch: ' + filename)
            digest = hashlib.sha256()
            size = 0
            with archive.open(entry) as data:
                for index, block in enumerate(item.findall(BM + 'Block')):
                    chunk = data.read(BLOCK)
                    if not chunk and entry.file_size:
                        raise ValueError('Too many block hashes: ' + filename)
                    if base64.b64encode(hashlib.sha256(chunk).digest()).decode() != block.attrib['Hash']:
                        raise ValueError('Block hash mismatch: ' + filename + ' block ' + str(index))
                    digest.update(chunk)
                    size += len(chunk)
                if data.read(1) or size != entry.file_size:
                    raise ValueError('Incomplete block map: ' + filename)
            files[filename] = {'bytes': size, 'sha256': digest.hexdigest()}
        if set(entries) - FOOTPRINTS != mapped:
            raise ValueError('Block map does not cover exactly the payload files')
        for footprint in FOOTPRINTS & set(entries):
            archive.read(entries[footprint])  # Signature CRC too, if present.
        if staged:
            staged = Path(staged)
            source_files = {p.relative_to(staged).as_posix(): p for p in staged.rglob('*') if p.is_file()}
            if set(source_files) != mapped:
                raise ValueError('Archive payload differs from staged file list')
            for filename, source in source_files.items():
                if file_sha256(source) != files[filename]['sha256']:
                    raise ValueError('Packaged bytes differ from staging: ' + filename)
    digest = file_sha256(package)
    return {'file': package.name, 'bytes': package.stat().st_size, 'sha256': digest,
            'identity': identity.attrib, 'payloadFiles': len(files),
            'zipCrcVerified': True, 'sha256BlockMapVerified': True,
            'stagingCompared': bool(staged), 'signaturePresent': 'AppxSignature.p7x' in entries,
            'storeAcceptance': 'NOT_VERIFIED_BY_PARTNER_CENTER'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package')
    parser.add_argument('--manifest')
    parser.add_argument('--staged')
    parser.add_argument('--report')
    args = parser.parse_args()
    result = verify(args.package, args.manifest, args.staged)
    output = json.dumps(result, indent=2) + '\n'
    if args.report:
        Path(args.report).write_text(output, encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()
