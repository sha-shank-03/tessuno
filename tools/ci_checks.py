"""Local command parity only; executes repository code and provides no isolation."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = (
    ('tools/check_source_format.py',),
    ('tools/validate.py',),
    ('-m', 'unittest', 'discover', '-s', 'tests', '-v'),
    ('tools/build.py',),
)


def main():
    for args in COMMANDS:
        result = subprocess.run([sys.executable, *args], cwd=ROOT, timeout=120, check=False)
        if result.returncode:
            return result.returncode
    # Publication must remain rejected, separately from structural success.
    result = subprocess.run([sys.executable, 'tools/validate.py', '--publication'],
                            cwd=ROOT, timeout=30, check=False)
    if result.returncode != 1:
        print('FAIL: publication gate no longer rejects as expected', file=sys.stderr)
        return 1
    print('PASS: local command parity; publication remains blocked; no CI/runtime evidence')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
