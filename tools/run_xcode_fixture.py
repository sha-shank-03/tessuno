"""Opt-in compile-only experiment for the exact reviewed original fixture.

Never called by catalog tools, unit tests, or CI. Keeps all run artifacts locally.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'evals/xcode-build-fixture'
DENIALS = ('operation not permitted', 'permission denied', 'sandbox: deny')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('fixture symlinks are forbidden')
        if path.is_file():
            result[path.relative_to(root).as_posix()] = digest(path)
    return result


def seed(source):
    text = source.read_text()
    if text.count('return value + 1') != 1:
        raise ValueError('seed expression must occur exactly once')
    source.write_text(text.replace('return value + 1', 'return missingIncrement + value'))


def classify(name, code, log, product_exists):
    if any(marker in log.lower() for marker in DENIALS):
        return 'blocked-permission'
    if name == 'seeded':
        return ('pass' if code != 0 and "cannot find 'missingIncrement' in scope" in log
                and 'Counter.swift:' in log else 'unexpected-result')
    return 'pass' if code == 0 and '** BUILD SUCCEEDED **' in log and product_exists else 'unexpected-result'


def command(snapshot, output, sdk):
    return ['/usr/bin/xcodebuild', '-project', str(snapshot / 'ReferenceFixture.xcodeproj'),
            '-scheme', 'ReferenceFixture', '-configuration', 'Debug', '-sdk', sdk,
            '-destination', 'generic/platform=iOS Simulator', '-derivedDataPath', str(output / 'derived'),
            '-packageCachePath', str(output / 'packages'), '-disableAutomaticPackageResolution',
            '-skipPackageUpdates', 'CODE_SIGNING_ALLOWED=NO', 'CODE_SIGNING_REQUIRED=NO',
            'CODE_SIGN_IDENTITY=', f'CLANG_MODULE_CACHE_PATH={output / "clang-cache"}',
            f'SWIFT_MODULE_CACHE_PATH={output / "swift-cache"}', f'CACHE_ROOT={output / "cache"}', 'build']


def run(output, sdk):
    if output == ROOT or ROOT in output.parents:
        raise ValueError('evidence must stay outside the source repository')
    expected = json.loads((ROOT / 'evals/xcode-fixture-inventory.json').read_text())
    if inventory(FIXTURE) != expected:
        raise ValueError('fixture differs from reviewed inventory')
    # A new destination is mandatory; never delete or overwrite previous evidence.
    output.mkdir(parents=True, exist_ok=False)
    receipt = {'sdkRequested': sdk, 'modelInvoked': False, 'simulatorLaunched': False,
               'fixtureSha256': expected, 'attempts': [], 'status': 'incomplete'}
    receipt_path = output / 'receipt.json'
    def save():
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    save()
    for label, argv in [('version', ['/usr/bin/xcodebuild', '-version']),
                        ('sdks', ['/usr/bin/xcodebuild', '-showsdks', '-json'])]:
        with (output / f'{label}.log').open('wb') as log:
            try:
                probe = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT,
                                       timeout=30, check=False)
            except (subprocess.TimeoutExpired, OSError) as error:
                receipt['status'] = 'preflight-blocked'
                receipt['preflightError'] = type(error).__name__
                save()
                return 1
        text = (output / f'{label}.log').read_text(errors='replace')
        receipt[label] = {'command': argv, 'exitCode': probe.returncode,
                          'logSha256': digest(output / f'{label}.log')}
        if probe.returncode or any(marker in text.lower() for marker in DENIALS):
            receipt['status'] = 'preflight-blocked'
            save()
            return 1
        save()
    for name in ('baseline', 'seeded', 'restored'):
        attempt = output / name
        attempt.mkdir()
        snapshot = attempt / 'source'
        shutil.copytree(FIXTURE, snapshot)
        if name == 'seeded':
            seed(snapshot / 'Sources/Counter.swift')
        argv = command(snapshot, attempt, sdk)
        record = {'name': name, 'command': argv, 'inputSha256': inventory(snapshot)}
        receipt['attempts'].append(record)
        save()
        env = dict(os.environ)
        (attempt / 'tmp').mkdir()
        env['TMPDIR'] = str(attempt / 'tmp')
        try:
            with (attempt / 'build.log').open('wb') as log:
                completed = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT,
                                           env=env, timeout=120, check=False)
            record['exitCode'] = completed.returncode
            product = attempt / 'derived/Build/Products/Debug-iphonesimulator/libReferenceFixture.a'
            record['status'] = classify(name, completed.returncode,
                (attempt / 'build.log').read_text(errors='replace'), product.is_file())
            if product.is_file():
                record['productSha256'] = digest(product)
        except (subprocess.TimeoutExpired, OSError) as error:
            record['status'] = 'timeout' if isinstance(error, subprocess.TimeoutExpired) else 'process-blocked'
        record['logSha256'] = digest(attempt / 'build.log')
        save()
        if record['status'] != 'pass':
            receipt['status'] = record['status']
            save()
            return 1
    receipt['status'] = 'pass'
    save()
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='new private local evidence directory')
    parser.add_argument('--sdk', required=True, help='reviewed installed Simulator SDK, e.g. iphonesimulator27.0')
    args = parser.parse_args()
    if not args.sdk.startswith('iphonesimulator') or not args.sdk.replace('.', '').isalnum():
        parser.error('only an explicit iPhone Simulator SDK is supported')
    raise SystemExit(run(args.output.resolve(), args.sdk))
