import importlib.util
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('diagnose_msix', Path(__file__).parents[1] / 'diagnose-msix.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

sys.path.insert(0, str(Path(__file__).parent))
import importlib.util as _u
_fs = _u.spec_from_file_location('fixture', Path(__file__).parents[1] / 'tests' / 'msix_fixture.py')
fixture = _u.module_from_spec(_fs)
_fs.loader.exec_module(fixture)


def run(**kwargs):
    with tempfile.TemporaryDirectory() as tmp:
        package = Path(tmp) / 'test.msix'
        fixture.build(package, **kwargs)
        module.results.clear()
        module.audit(package)
        return list(module.results)


def failures(rows):
    return [r[2] for r in rows if r[0] == 'FAIL']


class AuditTests(unittest.TestCase):
    def test_clean_package_has_no_failure(self):
        self.assertEqual(failures(run()), [])

    def test_blocks_a_published_full_name_and_an_equal_version(self):
        problems = failures(run(version='1.0.2.0'))
        self.assertTrue(any('already published' in p for p in problems))
        self.assertTrue(any('not higher than the published' in p for p in problems))

    def test_blocks_legacy_target_and_wrong_architecture(self):
        self.assertTrue(any('below the Store minimum' in p for p in failures(run(min_version='10.0.17134.0'))))
        self.assertTrue(any('x64-only' in p for p in failures(run(arch='x86'))))

    def test_blocks_missing_executable_wrong_logo_and_bad_entrypoint(self):
        missing = failures(run(executable='app\\Other.exe', ship_executable=False))
        self.assertTrue(any('not inside the package' in p for p in missing))
        self.assertTrue(any('logo' in p.lower() for p in failures(run(logo_size=(120, 120)))))

    def test_detects_corrupt_zip_and_foreign_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / 'g.msix'
            fixture.build(good)
            broken = Path(tmp) / 'b.msix'
            broken.write_bytes(good.read_bytes()[:-30])
            module.results.clear()
            module.audit(broken)
            self.assertTrue(any('ZIP structure is damaged' in r[2] for r in module.results if r[0] == 'FAIL'))

            other = Path(tmp) / 'o.msix'
            other.write_bytes(b'MZ' + b'\0' * 2000)
            module.results.clear()
            module.audit(other)
            self.assertTrue(any('Not a ZIP container' in r[2] for r in module.results if r[0] == 'FAIL'))


if __name__ == '__main__':
    unittest.main()
