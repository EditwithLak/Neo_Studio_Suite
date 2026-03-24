from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable
from uuid import uuid4

from .library_constants import IMAGE_EXTS, NEO_LIBRARY_SETTINGS_PATH, SETTINGS_PATH


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json_dict(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def sync_library_root_to_shared_settings(value: str) -> None:
    target = (value or '').strip()
    for settings_path in (SETTINGS_PATH, NEO_LIBRARY_SETTINGS_PATH):
        try:
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            data = read_json_dict(settings_path)
            data['library_root'] = target
            settings_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception:
            continue


def safe_name(name: str) -> str:
    name = (name or '').strip() or 'untitled'
    return ''.join(c if c.isalnum() or c in ('-', '_', ' ') else '_' for c in name).strip()[:80] or 'untitled'


def new_id(prefix: str) -> str:
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'{prefix}_{stamp}_{uuid4().hex[:8]}'


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def record_sort_key(rec: Dict[str, Any]) -> str:
    return str(rec.get('updated_at') or rec.get('created_at') or '')


def normalize_ext_list(include_exts: Iterable[str] | None) -> set[str]:
    if not include_exts:
        return set(IMAGE_EXTS)
    out = set()
    for ext in include_exts:
        ext = str(ext or '').strip().lower()
        if not ext:
            continue
        if not ext.startswith('.'):
            ext = f'.{ext}'
        if ext in IMAGE_EXTS:
            out.add(ext)
    return out or set(IMAGE_EXTS)
