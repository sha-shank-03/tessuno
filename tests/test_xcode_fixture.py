import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from run_xcode_fixture import ROOT, FIXTURE, classify, command, inventory, seed


class XcodeFixture(unittest.TestCase):
    def test_reviewed_inventory_and_static_only_project(self):
        self.assertEqual(inventory(FIXTURE), json.loads((ROOT / 'evals/xcode-fixture-inventory.json').read_text()))
        project = (FIXTURE / 'ReferenceFixture.xcodeproj/project.pbxproj').read_text()
        self.assertIn('com.apple.product-type.library.static', project)
        for forbidden in ('PBXShellScriptBuildPhase', 'XCRemoteSwiftPackageReference', 'DEVELOPMENT_TEAM', 'PRODUCT_BUNDLE_IDENTIFIER'):
            self.assertNotIn(forbidden, project)

    def test_permission_denial_overrides_success(self):
        self.assertEqual(classify('baseline', 0, '** BUILD SUCCEEDED **\nOperation not permitted', True), 'blocked-permission')
        self.assertEqual(classify('baseline', 0, 'Using NSCachesDirectory instead.\n** BUILD SUCCEEDED **', True), 'pass')
        self.assertEqual(classify('baseline', 0, '** BUILD SUCCEEDED **', False), 'unexpected-result')

    def test_failure_requires_diagnostic_and_nonzero(self):
        log = "Counter.swift:3: error: cannot find 'missingIncrement' in scope"
        self.assertEqual(classify('seeded', 65, log, False), 'pass')
        self.assertEqual(classify('seeded', 0, log, False), 'unexpected-result')
        self.assertEqual(classify('seeded', 65, '** BUILD FAILED **', False), 'unexpected-result')

    def test_seed_and_command_do_not_execute(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'Counter.swift'
            path.write_bytes((FIXTURE / 'Sources/Counter.swift').read_bytes())
            seed(path)
            self.assertIn('return missingIncrement + value', path.read_text())
            with self.assertRaises(ValueError):
                seed(path)
        argv = command(Path('/fixture'), Path('/evidence'), 'iphonesimulator27.0')
        self.assertEqual(argv[-1], 'build')
        self.assertIn('CODE_SIGNING_ALLOWED=NO', argv)
        self.assertIn('generic/platform=iOS Simulator', argv)
        for forbidden in ('test', 'archive', '-allowProvisioningUpdates', '-skipPackagePluginValidation'):
            self.assertNotIn(forbidden, argv)
