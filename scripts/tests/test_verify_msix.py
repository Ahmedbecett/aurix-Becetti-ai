import base64
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

spec = importlib.util.spec_from_file_location('verify_msix', Path(__file__).parents[1] / 'verify-msix.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class VerifyTests(unittest.TestCase):
    def fixture(self, root, *, bad_hash=False, omitted_block=False, extra=False):
        # Tiny parser fixtures, NOT runnable Windows packages or release artifacts.
        manifest = b'<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"><Identity Name="Test.Aurix" Publisher="CN=Test" Version="1.0.1.0" ProcessorArchitecture="x64" /></Package>'
        payload = {'AppxManifest.xml': manifest, 'app/AURIX.exe': b'x' * (65536 + 11)}
        bm = ET.Element(module.BM + 'BlockMap', {'HashMethod': 'http://www.w3.org/2001/04/xmlenc#sha256'})
        for name, data in payload.items():
            item = ET.SubElement(bm, module.BM + 'File', {'Name': name.replace('/', '\\'), 'Size': str(len(data)), 'LfhSize': '0'})
            chunks = [data[n:n + 65536] for n in range(0, len(data), 65536)]
            for chunk in chunks[:-1] if omitted_block else chunks:
                digest = hashlib.sha256(b'wrong' if bad_hash else chunk).digest()
                ET.SubElement(item, module.BM + 'Block', {'Hash': base64.b64encode(digest).decode()})
        archive = root / 'test.msix'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, data in payload.items():
                z.writestr(name, data)
            z.writestr('AppxBlockMap.xml', ET.tostring(bm))
            z.writestr('[Content_Types].xml', '<Types />')
            if extra:
                z.writestr('not-in-blockmap.txt', 'unexpected')
        staging = root / 'staging'
        staging.mkdir()
        for name, data in payload.items():
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        return archive, staging

    def test_checks_full_zip_blockmap_staging_and_file_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            package, staging = self.fixture(Path(tmp))
            result = module.verify(package, staging / 'AppxManifest.xml', staging)
            self.assertEqual(result['bytes'], package.stat().st_size)
            self.assertEqual(result['sha256'], hashlib.sha256(package.read_bytes()).hexdigest())
            self.assertTrue(result['zipCrcVerified'])
            self.assertTrue(result['sha256BlockMapVerified'])
            self.assertTrue(result['stagingCompared'])
            self.assertEqual(result['identity']['Version'], '1.0.1.0')

    def test_rejects_truncated_download_missing_zip_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            package, _ = self.fixture(Path(tmp))
            package.write_bytes(package.read_bytes()[:-22])
            with self.assertRaises(zipfile.BadZipFile):
                module.verify(package)

    def test_rejects_outer_artifact_zip_renamed_as_msix(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / 'outer.msix'
            with zipfile.ZipFile(package, 'w') as z:
                z.writestr('actual.msix', b'not the outer archive')
            with self.assertRaisesRegex(ValueError, 'outer artifact ZIP'):
                module.verify(package)

    def test_rejects_bad_hash_missing_block_and_unmapped_payload(self):
        for arguments, error in [({'bad_hash': True}, 'Block hash mismatch'), ({'omitted_block': True}, 'Incomplete block map'), ({'extra': True}, 'exactly the payload')]:
            with self.subTest(arguments=arguments), tempfile.TemporaryDirectory() as tmp:
                package, _ = self.fixture(Path(tmp), **arguments)
                with self.assertRaisesRegex(ValueError, error):
                    module.verify(package)

    def test_rejects_changed_identity_and_changed_staged_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            package, staging = self.fixture(Path(tmp))
            manifest = staging / 'AppxManifest.xml'
            manifest.write_bytes(manifest.read_bytes().replace(b'1.0.1.0', b'1.0.2.0'))
            with self.assertRaisesRegex(ValueError, 'identity/version'):
                module.verify(package, manifest)
            with self.assertRaisesRegex(ValueError, 'differ from staging'):
                module.verify(package, staged=staging)

    def test_rejects_unsafe_paths(self):
        for value in ['../x', '/x', 'C:/x', 'app/../../secret', 'app\\..\\secret']:
            with self.assertRaises(ValueError):
                module.name(value)


if __name__ == '__main__':
    unittest.main()
