#!/usr/bin/env python3
"""Audit shareable candidates, including decompressed Word parts; never print secrets."""
import argparse
import json
import io
from xml.etree import ElementTree as ET
from pathlib import Path
import re
from zipfile import ZipFile

FIXED = {'.gitignore', 'README.md', 'README.en.md', 'SKILL.md', 'LICENSE', 'artifact-template.json',
         'agents/openai.yaml', 'assets/reference.docx', 'assets/statement-reference.docx',
         'examples/profile.example.json', 'examples/payment.example.json'}
LOCAL_PATH = re.compile('/' + '(?:Users|Volumes)' + r'/[A-Za-z0-9_\u4e00-\u9fff]')
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})')


def inspect_text(data, label, deny_values):
    value = data.decode('utf-8')
    if LOCAL_PATH.search(value):
        raise ValueError('Personal absolute path in ' + label)
    if any(match[1] not in ['example.invalid', 'example.com', 'example.org'] for match in EMAIL.finditer(value)):
        raise ValueError('Non-example email in ' + label)
    if any(secret.casefold() in value.casefold() for secret in deny_values):
        raise ValueError('Local private value in ' + label)
    if re.search('-----' + r'BEGIN .*PRIVATE KEY' + r'-----|gh[pousr]_[A-Za-z0-9]{20,}', value):
        raise ValueError('Possible credential in ' + label)


def check(root, deny_values=()):
    root = Path(root).resolve()
    files = []
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if any(part in ['.git', '__pycache__', '.venv'] for part in rel.parts) or not path.is_file():
            continue
        name = rel.as_posix()
        if path.is_symlink():
            raise ValueError('Symlink is not a publishable candidate: ' + name)
        allowed = name in FIXED or (rel.parts[0] in ['scripts', 'tests'] and path.suffix == '.py') or (rel.parts[0] == 'references' and path.suffix == '.md')
        if not allowed:
            raise ValueError('Unexpected publication candidate: ' + name)
        if path.suffix == '.docx':
            with ZipFile(path) as archive:
                if archive.testzip() is not None:
                    raise ValueError('Corrupt Word package: ' + name)
                for part in archive.namelist():
                    if part.endswith('/'):
                        continue
                    if part.startswith(('customXml/', 'docProps/', 'word/media/', 'word/embeddings/')):
                        raise ValueError('Private/opaque Word part: ' + name + ':' + part)
                    if not part.endswith(('.xml', '.rels')):
                        raise ValueError('Unexpected Word part: ' + name + ':' + part)
                    data = archive.read(part)
                    inspect_text(data, name + ':' + part, deny_values)
                    tree = ET.fromstring(data)
                    prefixes = {prefix for _, (prefix, _) in ET.iterparse(io.BytesIO(data), events=['start-ns'])}
                    for node in tree.iter():
                        ignored = node.get('{http://schemas.openxmlformats.org/markup-compatibility/2006}Ignorable', '').split()
                        if not set(ignored) <= prefixes:
                            raise ValueError('Unbound Word compatibility prefix: ' + name + ':' + part)
                    if part.endswith('.rels') and b'TargetMode="External"' in data:
                        raise ValueError('External Word relationship: ' + name)
        else:
            inspect_text(path.read_bytes(), name, deny_values)
        files.append(name)
    if not FIXED <= set(files):
        raise ValueError('Missing expected public files: ' + ', '.join(sorted(FIXED - set(files))))
    return {'privacy_check': 'passed', 'files': files, 'note': 'Candidate and known-value checks do not replace human review or a Git history audit.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument('--deny-values', type=Path, help='Local-only JSON array of exact private strings; never commit it')
    args = parser.parse_args()
    try:
        deny = json.loads(args.deny_values.read_text()) if args.deny_values else []
        if not isinstance(deny, list) or any(not isinstance(v, str) or not v for v in deny):
            raise ValueError('Deny-values must be a nonempty-string array')
        print(json.dumps(check(args.root, deny), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
