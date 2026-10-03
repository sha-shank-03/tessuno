"""Structural consistency checks for an inert proposal, not a CI security verifier."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
CHECKOUT = 'actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683'
PYTHON = 'actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065'


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
    if job['if'] != '${{ false }}' or job['permissions'] != {'contents': 'read'} or job['timeout-minutes'] != 10:
        raise ValueError('disabled/read-only/time bound changed')
    steps = job['steps']
    if len(steps) != 6 or [s.get('uses') for s in steps[:3]] != [CHECKOUT, CHECKOUT, PYTHON]:
        raise ValueError('immutable acquisition references changed')
    for step in steps[:2]:
        if step['with']['persist-credentials'] is not False or step['with']['submodules'] is not False or step['with']['lfs'] is not False:
            raise ValueError('checkout credential/extra acquisition changed')
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
    if list((ROOT / '.github/workflows').glob('*')):
        raise ValueError('live workflow files unexpectedly present')
    print('PASS: inert proposal YAML/constraints; isolation and activation NOT verified')
