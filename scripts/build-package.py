#!/usr/bin/env python3
"""Build deterministic public plugin and reviewer ZIPs from a fixed inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

PLUGIN_FILES = (
    '.claude-plugin/plugin.json',
    '.mcp.json',
    'CHANGELOG.md',
    'LICENSE',
    'README.md',
    'docs/assets/tvijo-icon-256.png',
    'skills/inspect-project/SKILL.md',
)
REVIEW_FILES = (
    '.claude-plugin/plugin.json',
    '.mcp.json',
    'CHANGELOG.md',
    'LICENSE',
    'README.md',
    'docs/assets/tvijo-icon-256.png',
    'docs/listing.en.json',
    'docs/listing.ru.json',
    'docs/review-cases.json',
    'docs/reviewer-guide.md',
    'review-fixture/README.md',
    'review-fixture/app.py',
    'review-fixture/notes/release.txt',
    'scripts/build-package.py',
    'skills/inspect-project/SKILL.md',
)
FORBIDDEN_PUBLIC_MARKERS = (
    '/' + 'root' + '/', '/' + 'tmp' + '/' + 'codex-',
    '/' + 'mnt' + '/' + 'HC_Volume_', 'OPENAI_' + 'API_KEY=',
    'ANTHROPIC_' + 'API_KEY=',
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inventory(root: Path, names: tuple[str, ...]) -> dict[str, bytes]:
    if root.is_symlink():
        raise ValueError('Package root must not be a symlink')
    output: dict[str, bytes] = {}
    for name in names:
        rel = PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or '\\' in name:
            raise ValueError(f'Unsafe archive path: {name}')
        path = root.joinpath(*rel.parts)
        cursor = path
        while cursor != root:
            if cursor.is_symlink():
                raise ValueError(f'Symlink is not allowed in package: {name}')
            cursor = cursor.parent
        if not path.is_file():
            raise ValueError(f'Missing package file: {name}')
        raw = path.read_bytes()
        if len(raw) > 5 * 1024 * 1024:
            raise ValueError(f'Unexpectedly large package file: {name}')
        if re.search(rb'(?m)^-----BEGIN [A-Z ]*PRIVATE KEY-----', raw):
            raise ValueError(f'Private key material found in {name}')
        lowered = raw.lower()
        for marker in FORBIDDEN_PUBLIC_MARKERS:
            if marker.lower().encode() in lowered:
                raise ValueError(f'Private path or credential marker in {name}')
        output[name] = raw
    return output


def validate_content(plugin: dict[str, bytes], review: dict[str, bytes]) -> dict:
    manifest = json.loads(plugin['.claude-plugin/plugin.json'])
    mcp = json.loads(plugin['.mcp.json'])
    if manifest.get('version') != '0.1.0' or manifest.get('license') != 'MIT':
        raise ValueError('Unexpected public version or license')
    if manifest.get('name') != 'tvijo-remdesk':
        raise ValueError('Unexpected plugin name')
    if mcp != {'mcpServers': {'remdesk': {
            'type': 'http', 'url': 'https://mcp.tvijo.com/mcp'}}}:
        raise ValueError('Remote MCP URL or transport changed; review before packaging')
    for lang in ('en', 'ru'):
        listing = json.loads(review[f'docs/listing.{lang}.json'])
        if listing.get('version') != manifest['version'] or listing.get('license') != 'MIT':
            raise ValueError(f'{lang} listing does not match package version/license')
        if listing.get('server_url') != mcp['mcpServers']['remdesk']['url']:
            raise ValueError(f'{lang} listing and plugin endpoints differ')
        if listing.get('listing_status') != 'SOURCE_PUBLICATION_ONLY_NOT_SUBMITTED':
            raise ValueError(f'{lang} listing must not imply portal submission')
    cases = json.loads(review['docs/review-cases.json'])
    if cases.get('status') != 'PREPARED_NOT_RUN':
        raise ValueError('Review cases must preserve their not-run status')
    if any(case.get('status') != 'NOT_RUN' for case in cases.get('cases', [])):
        raise ValueError('A prepared test case is marked as run')
    return manifest


def write_archive(path: Path, content: dict[str, bytes]) -> dict:
    with path.open('xb') as handle:
        with zipfile.ZipFile(handle, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(content.items()):
                info = zipfile.ZipInfo(name, date_time=(2026, 11, 6, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError(f'CRC failure: {path.name}')
        if set(archive.namelist()) != set(content):
            raise ValueError(f'Archive inventory mismatch: {path.name}')
        for name, data in content.items():
            if archive.read(name) != data:
                raise ValueError(f'Archive content mismatch: {name}')
            if any(part in ('..', '') for part in PurePosixPath(name).parts):
                raise ValueError(f'Unsafe archive member: {name}')
    return {
        'file': path.name,
        'bytes': path.stat().st_size,
        'sha256': sha256(path.read_bytes()),
        'entries': {name: {'bytes': len(data), 'sha256': sha256(data)}
                    for name, data in sorted(content.items())},
    }


def build(root: Path, output: Path) -> dict:
    plugin = inventory(root, PLUGIN_FILES)
    review = inventory(root, REVIEW_FILES)
    manifest = validate_content(plugin, review)
    if output.exists():
        raise FileExistsError(f'Refusing to reuse output directory: {output}')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    archives = [
        write_archive(output / f'tvijo-remdesk-claude-plugin-{manifest["version"]}.zip', plugin),
        write_archive(output / f'tvijo-remdesk-review-materials-{manifest["version"]}.zip', review),
    ]
    receipt = {
        'prepared_on': '2026-11-06',
        'plugin': manifest['name'],
        'version': manifest['version'],
        'license': manifest['license'],
        'publication_status': 'SOURCE_PACKAGE_PREPARED_NOT_SUBMITTED',
        'archives': archives,
    }
    with (output / 'SHA256SUMS.json').open('x') as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = build(Path(__file__).resolve().parents[1], args.output)
    for item in result['archives']:
        print(f"{item['sha256']}  {item['file']}  {item['bytes']} bytes")
