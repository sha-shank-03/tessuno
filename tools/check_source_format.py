"""Code/schema hygiene using existing dependencies; not a formatter or sandbox."""
import ast
from pathlib import Path
from library import ROOT, read_json


def check(root=ROOT):
    root = Path(root).resolve()
    count = 0
    for folder in ('tools', 'tests', 'schemas', 'site/assets'):
        scanned = root
        for part in Path(folder).parts:
            scanned = scanned / part
            if scanned.is_symlink():
                raise ValueError('source directory symlink rejected')
        for path in sorted(scanned.rglob('*')):
            if path.is_symlink():
                raise ValueError('source symlink rejected')
            if path.suffix not in ('.py', '.json', '.js', '.css'):
                continue
            data = path.read_bytes()
            text = data.decode('utf-8')
            if b'\r' in data or not text.endswith('\n'):
                raise ValueError(f'{path}: require LF and final newline')
            if any(line.rstrip() != line for line in text.splitlines()):
                raise ValueError(f'{path}: trailing whitespace')
            if path.suffix == '.py':
                ast.parse(text, filename=str(path))
            if path.suffix == '.json':
                read_json(path)  # Existing duplicate-key rejection.
            count += 1
    return count


if __name__ == '__main__':
    print(f'PASS: {check()} code/schema files; syntax/JSON and whitespace hygiene only')
