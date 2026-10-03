"""Inert Lane B consistency and exact Lane A file identity; not a CI security verifier."""
from pathlib import Path
import hashlib
import yaml

ROOT = Path(__file__).resolve().parents[1]
CHECKOUT = 'actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683'
PYTHON = 'actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065'
# Already reviewed and activated by PR 18. This check grants no dispatch authority.
CONTROLLER = 'reviewed-source-validation.yml'
CONTROLLER_SHA256 = 'aa96215d825cc9e801e6dc155160a6b1044b66fe02d35bd64549d1dc534819d9'


def check_live_workflows(root=ROOT):
    root = Path(root).resolve()
    directory = root
    for part in ('.github', 'workflows'):
        directory = directory / part
        if directory.is_symlink():
            raise ValueError('workflow directory symlink rejected')
        if not directory.exists():
            return 0
        if not directory.is_dir():
            raise ValueError('workflow directory is not a directory')
    entries = list(directory.iterdir())
    if not entries:
        return 0
    if len(entries) != 1 or entries[0].name != CONTROLLER:
        raise ValueError('unreviewed workflow path present')
    path = entries[0]
    if path.is_symlink() or not path.is_file():
        raise ValueError('workflow must be a regular file without symlinks')
    if hashlib.sha256(path.read_bytes()).hexdigest() != CONTROLLER_SHA256:
        raise ValueError('reviewed Lane A workflow bytes changed')
    return 1


class UniqueLoader(yaml.SafeLoader):
    pass


def mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError('duplicate YAML key')
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def check(text):
    data = yaml.load(text, Loader=UniqueLoader)
    if data['on'] != {'pull_request': {'branches': ['main']}} or data['permissions'] != {}:
        raise ValueError('event/default permissions changed')
    if set(data['jobs']) != {'inspect'}:
        raise ValueError('unexpected jobs')
    job = data['jobs']['inspect']
    if (job['if'] != '${{ false }}' or job['permissions'] != {'contents': 'read'}
            or job['timeout-minutes'] != 10 or job['runs-on'] != 'ubuntu-24.04'):
        raise ValueError('disabled/read-only/time/runner bound changed')
    steps = job['steps']
    if len(steps) != 6 or [s.get('uses') for s in steps[:3]] != [CHECKOUT, CHECKOUT, PYTHON]:
        raise ValueError('immutable acquisition references changed')
    for step, ref, path in zip(steps[:2],
                               ('f19a87ab6d1a390f0c1848b2338b21301163494e',
                                'refs/pull/${{ github.event.pull_request.number }}/merge'),
                               ('protected', 'candidate')):
        if step['with'] != {'ref': ref, 'path': path, 'persist-credentials': False,
                            'submodules': False, 'lfs': False}:
            raise ValueError('checkout identity/path/credentials changed')
    if 'continue-on-error' in job or any('continue-on-error' in step or 'if' in step for step in steps):
        raise ValueError('step failure/condition overrides are forbidden')
    if steps[3]['run'] != "echo 'BLOCKED: no reviewed offline sandbox/image/wheelhouse/protected harness.'\nexit 1\n":
        raise ValueError('hard activation blocker changed')
    if steps[4]['run'].strip() != 'python -m pip --isolated install --no-index --only-binary=:all: --require-hashes --find-links /opt/tessuno-reviewed/wheels -r protected/requirements-dev.lock':
        raise ValueError('offline hash-locked dependency plan changed')
    if steps[5]['run'] != 'python tools/ci_checks.py' or steps[5]['working-directory'] != 'candidate':
        raise ValueError('command parity changed')
    for forbidden in ('secrets.', 'pull_request_target', 'workflow_run', 'upload-artifact', 'environment:', 'id-token:', 'self-hosted'):
        if forbidden in text:
            raise ValueError('forbidden construct')
    return data


if __name__ == '__main__':
    check((ROOT / 'docs/ci/validation.yml.disabled').read_text())
    count = check_live_workflows()
    print(f'PASS: inert Lane B constraints; {count} exact reviewed Lane A controller; no isolation/dispatch/qualification verdict')
