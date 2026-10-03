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

    def test_standard_sandbox_denial_stops_orchestration(self):
        from unittest.mock import patch
        import subprocess
        from run_xcode_fixture import run
        denial = 'Sandbox: xcodebuild(123) deny(1) file-write-create /outside/CoreSimulator.log'
        self.assertEqual(classify('baseline', 0, '** BUILD SUCCEEDED **\n' + denial, True), 'blocked-permission')
        for denied_call in (1, 2, 3):
            with self.subTest(denied_call=denied_call), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / 'evidence'
                calls = []
                def fake(argv, **kwargs):
                    calls.append(argv)
                    text = '** BUILD SUCCEEDED **' if argv[-1] == 'build' else 'mock preflight'
                    if argv[-1] == 'build':
                        product = output / 'baseline/derived/Build/Products/Debug-iphonesimulator/libReferenceFixture.a'
                        product.parent.mkdir(parents=True)
                        product.write_bytes(b'mock archive')
                    if len(calls) == denied_call:
                        text += '\n' + denial
                    kwargs['stdout'].write(text.encode())
                    return subprocess.CompletedProcess(argv, 0)
                with patch('run_xcode_fixture.subprocess.run', side_effect=fake):
                    self.assertEqual(run(output, 'iphonesimulator27.0'), 1)
                self.assertEqual(len(calls), denied_call)
                receipt = json.loads((output / 'receipt.json').read_text())
                self.assertEqual(receipt['status'], 'blocked-permission' if denied_call == 3 else 'preflight-blocked')
                self.assertEqual(len(receipt['attempts']), 1 if denied_call == 3 else 0)
                self.assertFalse((output / 'seeded').exists())
                self.assertFalse((output / 'restored').exists())

    def test_relative_and_symlink_output_rejected_before_write_or_process(self):
        from unittest.mock import patch
        import os
        from run_xcode_fixture import run
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'repo'
            root.mkdir()
            (base / 'alias').symlink_to(root, target_is_directory=True)
            previous = Path.cwd()
            try:
                os.chdir(root)
                with patch('run_xcode_fixture.ROOT', root), patch('run_xcode_fixture.subprocess.run') as process:
                    for output in (Path('evidence'), Path('../alias/evidence'), Path('.')):
                        with self.subTest(output=output), self.assertRaises(ValueError):
                            run(output, 'iphonesimulator27.0')
                    process.assert_not_called()
                self.assertEqual(list(root.iterdir()), [])
            finally:
                os.chdir(previous)
