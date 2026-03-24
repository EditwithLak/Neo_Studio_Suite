
import base64
import mimetypes
import os
import re
import time
from typing import Any, Dict, List

import httpx

from .config import (
    BACKEND_TIMEOUT_SECONDS,
    CHAT_TIMEOUT_SECONDS,
    DEFAULT_BASE_URL,
    DEFAULT_CHAT_PATH,
    DEFAULT_MODELS_PATH,
)
from .logging_utils import get_logger

logger = get_logger(__name__)


def _normalized_base_url() -> str:
    return os.getenv('KOBOLDCPP_BASE_URL', DEFAULT_BASE_URL).strip().rstrip('/') or DEFAULT_BASE_URL


def _build_backend_url(path_value: str, default_path: str) -> str:
    base_url = _normalized_base_url()
    path_value = (path_value or '').strip() or default_path
    if path_value.startswith('http://') or path_value.startswith('https://'):
        return path_value.rstrip('/')
    if not path_value.startswith('/'):
        path_value = '/' + path_value
    return base_url + path_value


def get_kobold_chat_url() -> str:
    return _build_backend_url(os.getenv('KOBOLDCPP_CHAT_PATH', DEFAULT_CHAT_PATH), DEFAULT_CHAT_PATH)


def get_kobold_models_url() -> str:
    return _build_backend_url(os.getenv('KOBOLDCPP_MODELS_PATH', DEFAULT_MODELS_PATH), DEFAULT_MODELS_PATH)


async def get_models() -> List[str]:
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(get_kobold_models_url(), timeout=BACKEND_TIMEOUT_SECONDS)
            if response.status_code == 200:
                return [m['id'] for m in response.json().get('data', []) if m.get('id')]
    except Exception:
        logger.exception('Failed to fetch backend model list from %s', get_kobold_models_url())
    return ['default']


async def probe_backend_status() -> Dict[str, Any]:
    started = time.perf_counter()
    payload: Dict[str, Any] = {
        'base_url': _normalized_base_url(),
        'chat_url': get_kobold_chat_url(),
        'models_url': get_kobold_models_url(),
        'reachable': False,
        'status_code': None,
        'latency_ms': None,
        'models': [],
        'error': '',
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(payload['models_url'], timeout=BACKEND_TIMEOUT_SECONDS)
            payload['status_code'] = response.status_code
            payload['latency_ms'] = round((time.perf_counter() - started) * 1000, 1)
            if response.status_code == 200:
                data = response.json()
                payload['models'] = [m['id'] for m in data.get('data', []) if m.get('id')]
                payload['reachable'] = True
            else:
                payload['error'] = f'Unexpected status code: {response.status_code}'
    except Exception as exc:
        payload['latency_ms'] = round((time.perf_counter() - started) * 1000, 1)
        payload['error'] = str(exc)
        logger.warning('Backend probe failed: %s', exc)
    return payload


def clamp_int(value: Any, minimum: int, maximum: int, default: int) -> int:
    try:
        ivalue = int(float(value))
    except Exception:
        ivalue = default
    return max(minimum, min(maximum, ivalue))



def clamp_float(value: Any, minimum: float, maximum: float, default: float) -> float:
    try:
        fvalue = float(value)
    except Exception:
        fvalue = default
    return max(minimum, min(maximum, fvalue))


_REASONING_TAGS = ('think', 'analysis', 'reasoning', 'thought', 'scratchpad')


def _strip_visible_reasoning(text: str) -> Dict[str, Any]:
    raw = text or ''
    cleaned = raw
    had_reasoning = False

    for tag in _REASONING_TAGS:
        pattern = rf'<\s*{tag}\b[^>]*>.*?<\s*/\s*{tag}\s*>'
        updated, count = re.subn(pattern, '', cleaned, flags=re.I | re.S)
        if count:
            had_reasoning = True
            cleaned = updated

    if re.search(r'<\s*(?:' + '|'.join(_REASONING_TAGS) + r')\b', cleaned, flags=re.I):
        had_reasoning = True
        cleaned = re.split(r'<\s*(?:' + '|'.join(_REASONING_TAGS) + r')\b', cleaned, maxsplit=1, flags=re.I)[0]

    if had_reasoning and not cleaned.strip():
        marker = re.search(
            r'(?:^|\n)\s*(?:final\s+answer|answer|final\s+prompt|prompt)\s*:\s*(.+)$',
            raw,
            flags=re.I | re.S,
        )
        if marker:
            cleaned = marker.group(1).strip()

    cleaned = re.sub(r'^\s*(?:final\s+answer|answer|final\s+prompt|prompt)\s*:\s*', '', cleaned.strip(), flags=re.I)
    return {
        'content': cleaned.strip(),
        'had_reasoning': had_reasoning,
        'raw_content': raw,
    }


async def _post_chat(payload: dict, timeout: float = CHAT_TIMEOUT_SECONDS) -> Dict[str, str]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(get_kobold_chat_url(), json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        choice = (data.get('choices', [{}]) or [{}])[0] or {}
        message = (choice.get('message', {}) or {}).get('content', '').strip()
        finish_reason = str(choice.get('finish_reason') or '').strip()
        reasoning = _strip_visible_reasoning(message)
        return {
            'content': reasoning['content'],
            'finish_reason': finish_reason,
            'raw': data,
            'raw_content': reasoning['raw_content'],
            'reasoning_stripped': reasoning['had_reasoning'],
        }



def _looks_like_sd_tags(text: str) -> bool:
    text = (text or '').strip()
    if not text:
        return False
    if ',' in text and text.count(',') >= 3:
        sentence_punct = len(re.findall(r'[.!?]', text))
        return sentence_punct <= 1
    return False



def _build_prompt_request(idea: str, style: str, custom_instructions: str) -> Dict[str, str]:
    system_prompt = (
        'You write only the final positive image-generation prompt. '
        'Do not output JSON. Do not output a negative prompt. '
        'Do not explain your choices. Never reveal chain-of-thought, scratch work, or <think> tags. '
        'If you reason internally, keep it hidden and output only the final prompt. '
        'Keep it usable immediately.'
    )
    style = (style or 'Stable Diffusion Prompt').strip()
    if style == 'Descriptive':
        style_rule = 'Write a concise, vivid natural-language prompt suitable for an image model.'
    elif style == 'Custom':
        style_rule = 'Follow the user instructions exactly and output only the final positive prompt.'
    elif style == 'Style Convert':
        if _looks_like_sd_tags(idea):
            style_rule = 'Convert the input Stable Diffusion tags into one clean, vivid natural-language prompt. Preserve content and do not invent new elements.'
        else:
            style_rule = 'Convert the input prose into one concise comma-separated Stable Diffusion style prompt. Preserve content and do not invent new elements.'
    else:
        style_rule = 'Write a single-line Stable Diffusion style prompt using concise comma-separated tags.'
    user_prompt = (
        f'Idea: {(idea or "").strip()}\n\n'
        f'{style_rule}\n'
        'Focus on visible subject, clothing, pose, mood, lighting, camera/composition, environment, and style. '
        'Keep it grounded and production-ready.'
    )
    if (custom_instructions or '').strip():
        user_prompt += f"\n\nExtra instructions: {custom_instructions.strip()}"
    return {'system_prompt': system_prompt, 'user_prompt': user_prompt}


_CHARACTER_CARD_LABELS = [
    'Name/Label',
    'Core Traits',
    'Visual Traits',
    'Style Notes',
    'Prompt-Ready Description',
]


def _cleanup_character_card_value(value: str) -> str:
    value = (value or '').replace('\r\n', '\n').replace('\r', '\n').strip().strip('"“”').strip()
    value = re.sub(r'^[\-*•]+\s*', '', value, flags=re.M)
    value = re.sub(r'\n{3,}', '\n\n', value)
    value = re.sub(r'[ \t]+', ' ', value)
    value = re.sub(r' *\n *', '\n', value)
    return value.strip()


def _extract_character_card_section(text: str, labels: List[str], aliases: List[str]) -> str:
    escaped_aliases = '|'.join(re.escape(a) for a in aliases)
    escaped_labels = '|'.join(re.escape(l) for l in labels)
    pattern = (
        rf'(?:^|\n)\s*(?:{escaped_aliases})\s*:\s*(.*?)'
        rf'(?=\n\s*(?:{escaped_labels})\s*:|$)'
    )
    match = re.search(pattern, text, flags=re.I | re.S)
    return _cleanup_character_card_value(match.group(1)) if match else ''


def _normalize_character_card_text(text: str) -> str:
    raw = (text or '').strip()
    if not raw:
        return (
            'Name/Label:\nRefined Character\n\n'
            'Core Traits:\n\n'
            'Visual Traits:\n\n'
            'Style Notes:\n\n'
            'Prompt-Ready Description:\n'
        )

    cleaned = raw.replace('\r\n', '\n').replace('\r', '\n')
    cleaned = re.sub(r'^```[a-zA-Z0-9_-]*\n?', '', cleaned)
    cleaned = re.sub(r'\n?```$', '', cleaned)
    cleaned = re.sub(r'^\s*[*#>`-]+\s*', '', cleaned, flags=re.M)
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
    cleaned = re.sub(r'__([^_]+)__', r'\1', cleaned)
    cleaned = re.sub(r"(?im)^here(?: is|'s) my revised prompt\s*:\s*", 'Prompt-Ready Description:\n', cleaned)
    cleaned = re.sub(r'(?im)^revised prompt\s*:\s*', 'Prompt-Ready Description:\n', cleaned)
    cleaned = re.sub(r'(?im)^final prompt\s*:\s*', 'Prompt-Ready Description:\n', cleaned)
    cleaned = re.sub(r'(?im)^prompt\s*:\s*', 'Prompt-Ready Description:\n', cleaned)

    alias_map = {
        'Name/Label': ['Name/Label', 'Name', 'Label', 'Character Name'],
        'Core Traits': ['Core Traits', 'Traits', 'Personality', 'Personality Traits'],
        'Visual Traits': ['Visual Traits', 'Appearance', 'Visual Details', 'Appearance Details'],
        'Style Notes': ['Style Notes', 'Style', 'Mood', 'Style Cues'],
        'Prompt-Ready Description': ['Prompt-Ready Description', 'Prompt Ready Description', 'Revised Prompt', 'Final Prompt', 'Prompt'],
    }

    values: Dict[str, str] = {}
    for label in _CHARACTER_CARD_LABELS:
        values[label] = _extract_character_card_section(cleaned, _CHARACTER_CARD_LABELS, alias_map[label])

    if not values['Prompt-Ready Description']:
        quoted = re.search(r'["“](.+?)["”]', cleaned, flags=re.S)
        if quoted:
            values['Prompt-Ready Description'] = _cleanup_character_card_value(quoted.group(1))

    if not values['Prompt-Ready Description']:
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', cleaned) if p.strip()]
        filtered = [
            p for p in paragraphs
            if not re.match(r'(?i)^(the image shows|overall impression|this description captures|let me know if)', p)
        ]
        if filtered:
            values['Prompt-Ready Description'] = _cleanup_character_card_value(filtered[-1])

    if not values['Name/Label']:
        values['Name/Label'] = 'Refined Character'

    return '\n\n'.join(f'{label}:\n{values.get(label, "")}' for label in _CHARACTER_CARD_LABELS).strip()


async def improve_character_card(
    content: str,
    model: str,
    mode: str = '',
    max_tokens: int = 420,
    temperature: float = 0.22,
    top_p: float = 0.9,
    top_k: int = 40,
) -> Dict[str, str]:
    mode_text = (mode or 'Refine this character card while preserving the same identity.').strip()
    system_prompt = (
        'You rewrite character descriptions into a clean reusable character card for image-prompt workflows. '
        'Return only plain text using exactly these section headers in this order: '
        'Name/Label, Core Traits, Visual Traits, Style Notes, Prompt-Ready Description. '
        'Do not output markdown bullets unless they are part of the value text. '
        'Do not explain the image. Do not say "the image shows". '
        'Do not add commentary, introductions, closing lines, or quotes around the final description.'
    )
    user_prompt = (
        'Rewrite the source character content into this exact format:\n\n'
        'Name/Label:\n'
        '<short reusable label>\n\n'
        'Core Traits:\n'
        '<comma-separated personality / vibe traits>\n\n'
        'Visual Traits:\n'
        '<concise visible appearance details>\n\n'
        'Style Notes:\n'
        '<concise style / mood / rendering notes>\n\n'
        'Prompt-Ready Description:\n'
        '<one clean reusable natural-language character description>\n\n'
        f'Extra instruction: {mode_text}\n\n'
        'Rules:\n'
        '- keep the same character identity\n'
        '- keep it reusable for future prompts\n'
        '- no assistant chatter\n'
        '- no "here is" or "let me know" text\n'
        '- no analysis paragraphs\n\n'
        f'Source character content:\n{(content or "").strip()}'
    )
    result = await _post_chat(
        {
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            'max_tokens': clamp_int(max_tokens, 64, 1200, 420),
            'temperature': clamp_float(temperature, 0.0, 1.2, 0.22),
            'top_p': clamp_float(top_p, 0.0, 1.0, 0.9),
            'top_k': clamp_int(top_k, 0, 200, 40),
            'repetition_penalty': 1.1,
        },
        timeout=180.0,
    )
    result['text'] = _normalize_character_card_text(result.get('content', ''))
    return result


async def generate_prompt_text(
    idea: str,
    model: str,
    style: str = 'Stable Diffusion Prompt',
    custom_instructions: str = '',
    max_tokens: int = 220,
    temperature: float = 0.35,
    top_p: float = 0.9,
    top_k: int = 40,
) -> Dict[str, str]:
    req = _build_prompt_request(idea=idea, style=style, custom_instructions=custom_instructions)
    result = await _post_chat(
        {
            'model': model,
            'messages': [
                {'role': 'system', 'content': req['system_prompt']},
                {'role': 'user', 'content': req['user_prompt']},
            ],
            'max_tokens': clamp_int(max_tokens, 32, 1200, 220),
            'temperature': clamp_float(temperature, 0.0, 1.5, 0.35),
            'top_p': clamp_float(top_p, 0.0, 1.0, 0.9),
            'top_k': clamp_int(top_k, 0, 200, 40),
            'repetition_penalty': 1.12,
        },
        timeout=180.0,
    )
    result['text'] = _cleanup_prompt_text(result.get('content', ''), style)
    return result


async def continue_prompt_text(
    idea: str,
    current_output: str,
    model: str,
    style: str = 'Stable Diffusion Prompt',
    custom_instructions: str = '',
    max_tokens: int = 220,
    temperature: float = 0.35,
    top_p: float = 0.9,
    top_k: int = 40,
) -> Dict[str, str]:
    req = _build_prompt_request(idea=idea, style=style, custom_instructions=custom_instructions)
    user_prompt = (
        f"{req['user_prompt']}\n\n"
        'The previous output was cut off. Continue from exactly where it stopped. '
        'Do not restart from the beginning. Do not repeat the existing text. '
        'Return only the continuation text.\n\n'
        f'Existing partial output:\n{(current_output or "").strip()}'
    )
    result = await _post_chat(
        {
            'model': model,
            'messages': [
                {'role': 'system', 'content': req['system_prompt']},
                {'role': 'user', 'content': user_prompt},
            ],
            'max_tokens': clamp_int(max_tokens, 32, 1200, 220),
            'temperature': clamp_float(temperature, 0.0, 1.5, 0.35),
            'top_p': clamp_float(top_p, 0.0, 1.0, 0.9),
            'top_k': clamp_int(top_k, 0, 200, 40),
            'repetition_penalty': 1.1,
        },
        timeout=180.0,
    )
    continuation = _cleanup_prompt_text(result.get('content', ''), style)
    combined = _merge_continuation(current_output, continuation, style)
    result['text'] = combined
    result['continuation'] = continuation
    return result



def _merge_continuation(existing: str, continuation: str, style: str) -> str:
    existing = (existing or '').rstrip()
    continuation = (continuation or '').lstrip(' ,\n')
    if not existing:
        return continuation
    if not continuation:
        return existing
    if style == 'Stable Diffusion Prompt':
        joiner = ', ' if not existing.endswith(',') else ' '
    else:
        joiner = '' if existing.endswith((' ', '\n', ',', ';', ':', '-')) else ' '
    return _cleanup_prompt_text(existing + joiner + continuation, style)



def _cleanup_prompt_text(text: str, style: str) -> str:
    text = (text or '').strip()
    text = re.sub(r'^assistant\s*:\s*', '', text, flags=re.I)
    if style in {'Stable Diffusion Prompt', 'Style Convert'} and _looks_like_sd_tags(text):
        text = text.replace('\n', ', ')
        text = re.sub(r'(?:^|,\s*)(?:\d+\.|\d+\)|[-*•])\s*', ', ', text)
        parts = [re.sub(r'\s+', ' ', p.strip()) for p in text.split(',') if p.strip()]
        seen = set()
        clean = []
        for part in parts:
            key = part.lower()
            if key in seen:
                continue
            seen.add(key)
            clean.append(part)
        text = ', '.join(clean)
    else:
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'\s+([,.;:])', r'\1', text)
    return text or 'No prompt generated.'


PROMPT_STYLE_MAP = {
    'Stable Diffusion Prompt': 'sd',
    'Descriptive': 'descriptive',
    'Style Convert': 'style_convert',
    'Custom': 'custom',
}



def _guess_mime_type(image_path: str) -> str:
    mime, _ = mimetypes.guess_type(image_path)
    if mime and mime.startswith('image/'):
        return mime
    return 'image/jpeg'



def _caption_length_hint(length: str) -> str:
    length = (length or 'any').strip().lower()
    if length == 'short':
        return 'Keep it short.'
    if length == 'medium':
        return 'Keep it medium length.'
    if length == 'long':
        return 'Be detailed, but stay literal.'
    return 'Length is flexible, but stay concise.'



def _caption_detail_level_hint(detail_level: str) -> str:
    level = (detail_level or 'detailed').strip().lower().replace('-', '_').replace(' ', '_')
    if level == 'basic':
        return 'Keep it concise and useful. Mention only the strongest visible traits.'
    if level == 'attribute_rich':
        return (
            'Be richly specific and cover as many visible attributes as possible. '
            'For face-focused captions, include visible facial structure, eyebrow shape, eye shape and color when visible, eyelids, nose, lips, jawline, chin, skin tone or texture, hair color, hairstyle, hair length, bangs, facial hair, accessories, and expression. '
            'For person-focused captions, include visible body build, posture, pose, outfit pieces, colors, fabrics, fit, accessories, footwear, hairstyle, and overall archetype or vibe. '
            'Only mention details that are actually visible. Do not invent hidden or uncertain traits.'
        )
    return 'Be clearly detailed and cover important visible attributes without padding.'



def _caption_mode_hint(caption_mode: str, detail_level: str = 'detailed') -> str:
    mode = (caption_mode or 'full_image').strip().lower()
    detail_hint = _caption_detail_level_hint(detail_level)
    if mode == 'face_only':
        base = 'Focus only on the visible face, head, hair, expression, age cues, and facial accessories. Ignore clothing, pose, and background unless unavoidable.'
        extra = 'Describe all visible facial attributes such as face shape, forehead, eyebrow shape or thickness, eye shape, eye color when visible, eyelashes, nose shape, lips, jawline, chin, cheek structure, skin tone or texture, hairstyle, hair color, hair length, bangs, and visible accessories.'
        return f'{base} {extra} {detail_hint}'
    if mode == 'person_only':
        base = 'Focus on the main visible person or character only. Ignore most background details unless they are required to understand the visible subject.'
        extra = 'Describe the visible person in detail, including body build, posture, pose, framing, outfit pieces, layering, materials, colors, hairstyle, face if visible, accessories, footwear, and the overall character vibe or archetype.'
        return f'{base} {extra} {detail_hint}'
    if mode == 'outfit_only':
        base = 'Focus only on clothing, outfit layers, fabrics, footwear, and accessories worn by the main visible subject. Ignore face, body proportions, pose, and location unless unavoidable.'
        extra = 'Break down visible garment types, layering, fit, colors, patterns, textures, fabrics, closures, jewelry, and shoes.'
        return f'{base} {extra} {detail_hint}'
    if mode == 'pose_only':
        base = 'Focus only on the body pose, stance, gesture, limb placement, balance, and framing of the subject. Ignore clothing details, facial features, and environment unless unavoidable.'
        extra = 'Describe body orientation, head angle, arm placement, hand gesture, leg position, weight distribution, and silhouette clearly.'
        return f'{base} {extra} {detail_hint}'
    if mode == 'location_only':
        base = 'Focus only on the environment, background, setting, architecture, props, lighting, and atmosphere. Ignore people and outfits except for minimal generic foreground mentions when impossible to avoid.'
        extra = 'Describe the location with concrete visual details, materials, scale cues, weather, time-of-day cues, and mood lighting when visible.'
        return f'{base} {extra} {detail_hint}'
    if mode == 'custom_crop':
        return f'Describe only what is visible inside the selected crop region. Ignore everything outside the crop. {detail_hint}'
    return f'Describe the full visible image. Cover the main subject first, then visible appearance, outfit, pose, and setting as needed. {detail_hint}'


def build_caption_user_prompt(
    prompt_style: str,
    caption_length: str,
    custom_prompt: str,
    prefix: str,
    suffix: str,
    output_style: str,
    caption_mode: str = 'full_image',
    detail_level: str = 'detailed',
) -> str:
    prompt_style = (prompt_style or 'Stable Diffusion Prompt').strip()
    length_hint = _caption_length_hint(caption_length)
    custom_prompt = (custom_prompt or '').strip()
    prefix = (prefix or '').strip()
    suffix = (suffix or '').strip()
    output_style = (output_style or 'Auto (match input)').strip()

    mode_hint = _caption_mode_hint(caption_mode, detail_level)

    if prompt_style == 'Custom' and custom_prompt:
        user = f"{custom_prompt.strip()} {mode_hint}".strip()
    elif prompt_style == 'Descriptive':
        user = (
            'Describe only what is clearly visible in the image. '
            'Write plain factual text only. '
            'Do not invent extra people, relationships, props, or off-camera details. '
            'Count visible people exactly. '
            'If gender is unclear, use neutral words like person or adult. '
            f'{length_hint} '
            f'{mode_hint}'
        )
    elif prompt_style == 'Style Convert':
        user = (
            'Describe the image in the opposite output style. '
            'If the visible content looks photorealistic, describe it as anime / illustration friendly text. '
            'If it already looks illustrated, describe it as realistic / photographic text. '
            'Use only visible details and do not invent extra people or props. '
            'Output plain text only. '
            f'{mode_hint}'
        )
    else:
        user = (
            'Return exactly one single line of comma-separated Stable Diffusion tags. '
            'Use only visible details. '
            'Do not add people or objects that are not present. '
            'Count visible people exactly. '
            'Do not number anything. Do not use bullet points. Do not write explanations. '
            f'{length_hint} '
            f'{mode_hint}'
        )

    if output_style == 'Realistic':
        user += ' Bias the wording toward realistic photography.'
    elif output_style == 'Anime':
        user += ' Bias the wording toward anime / illustrated style.'
    if prefix:
        user += f' Prefix the final output with: {prefix}.'
    if suffix:
        user += f' Suffix the final output with: {suffix}.'
    return user


async def caption_image_with_settings(
    image_path: str,
    model: str,
    prompt_style: str = 'Stable Diffusion Prompt',
    caption_length: str = 'any',
    custom_prompt: str = '',
    max_tokens: int = 160,
    temperature: float = 0.2,
    top_p: float = 0.9,
    top_k: int = 40,
    prefix: str = '',
    suffix: str = '',
    output_style: str = 'Auto (match input)',
    caption_mode: str = 'full_image',
    detail_level: str = 'detailed',
) -> Dict[str, str]:
    if not os.path.isfile(image_path):
        return {'text': 'Invalid image file.', 'content': 'Invalid image file.', 'finish_reason': 'error'}
    mime_type = _guess_mime_type(image_path)
    system_prompt = (
        'You are a literal vision captioning assistant. '
        'Describe only directly visible details. '
        'Never invent extra people, genders, relationships, objects, or background elements. '
        'Never reveal chain-of-thought, scratch work, or <think> tags. '
        'If you reason internally, keep it hidden and output only the final caption. '
        'Count visible people exactly. If a detail is unclear, say less rather than guessing.'
    )
    user_prompt = build_caption_user_prompt(prompt_style, caption_length, custom_prompt, prefix, suffix, output_style, caption_mode, detail_level)

    try:
        with open(image_path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': user_prompt},
                        {'type': 'image_url', 'image_url': {'url': f'data:{mime_type};base64,{b64}'}},
                    ],
                },
            ],
            'max_tokens': clamp_int(max_tokens, 24, 1000, 160),
            'temperature': clamp_float(temperature, 0.0, 1.5, 0.2),
            'top_p': clamp_float(top_p, 0.0, 1.0, 0.9),
            'top_k': clamp_int(top_k, 0, 200, 40),
            'repetition_penalty': 1.12,
        }
        result = await _post_chat(payload, timeout=240.0)
        result['text'] = _cleanup_caption_text(result.get('content', ''), prompt_style)
        return result
    except Exception as e:
        return {'text': f'Vision error: {e}', 'content': f'Vision error: {e}', 'finish_reason': 'error'}



def _cleanup_caption_text(text: str, prompt_style: str) -> str:
    text = (text or '').strip()
    text = text.replace('<br>', ' ')
    text = re.sub(r'^assistant\s*:\s*', '', text, flags=re.I)
    if prompt_style == 'Stable Diffusion Prompt':
        text = text.replace('\n', ', ')
        text = re.sub(r'(?:^|,\s*)(?:\d+\.|\d+\)|[-*•])\s*', ', ', text)
        raw_tags = [re.sub(r'\s+', ' ', tag.strip()) for tag in text.split(',')]
        seen = set()
        cleaned = []
        for tag in raw_tags:
            if not tag:
                continue
            low = tag.lower()
            if low not in seen:
                seen.add(low)
                cleaned.append(tag)
        text = ', '.join(cleaned[:40])
    elif prompt_style == 'Custom':
        text = re.sub(r'\n{3,}', '\n\n', text)
    else:
        text = re.sub(r'\n{3,}', '\n\n', text)
    return text or 'No description generated.'
