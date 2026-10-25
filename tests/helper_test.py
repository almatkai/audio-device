import importlib.util, pathlib, unittest
path=pathlib.Path(__file__).resolve().parents[1]/'scripts/prepare-helpers.py'
spec=importlib.util.spec_from_file_location('helpers',path);helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
class HelperIntegrity(unittest.TestCase):
    def test_rejects_tampering_without_fetch_or_execution(self):
        import hashlib
        descriptor={'filename':'fixture','expected_sha256':hashlib.sha256(b'fixture').hexdigest()}
        helpers.verify(b'fixture',descriptor)
        with self.assertRaises(ValueError):helpers.verify(b'tampered',descriptor)
    def test_refuses_plaintext_redirect(self):
        with self.assertRaises(ValueError):helpers.HTTPSRedirect().redirect_request(None,None,302,'',{},'http://example.com/helper')
