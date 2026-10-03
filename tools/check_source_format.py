"""Small dependency-free code/schema hygiene check, not a style formatter."""
import ast
from pathlib import Path
from library import ROOT, read_json


def check(root=ROOT):
    count = 0
    for folder in ('tools', 'tests', 'schemas', 'site/assets'):
        for path in sorted((Path(root) / folder).rglob('*')):
            if path.suffix not in ('.py', '.json', '.js', '.css'):
                continue
            if path.is_symlink():
                raise ValueError('source symlink rejected')
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
