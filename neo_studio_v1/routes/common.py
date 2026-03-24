from __future__ import annotations

from fastapi.responses import JSONResponse

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


def json_error(message: str, status_code: int = 400):
    if status_code >= 500:
        logger.error('API error %s: %s', status_code, message)
    return JSONResponse({'ok': False, 'message': message}, status_code=status_code)


def parse_bool(value) -> bool:
    return str(value or '').strip().lower() in {'1', 'true', 'yes', 'on'}


def re_split_csv(text: str) -> list[str]:
    return [x for x in [p.strip() for p in text.replace(';', ',').split(',')] if x]


def parse_exts(raw: str) -> list[str]:
    text = (raw or '').strip()
    if not text:
        return []
    out = []
    for part in re_split_csv(text):
        part = part.strip().lower()
        if not part:
            continue
        if not part.startswith('.'):
            part = f'.{part}'
        out.append(part)
    return out


def settings_dict(max_tokens, temperature, top_p, top_k):
    return {
        'max_tokens': max_tokens,
        'temperature': temperature,
        'top_p': top_p,
        'top_k': top_k,
    }
