from __future__ import annotations

import json
import mimetypes
import tempfile
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image

from ..utils.kobold import caption_image_with_settings, clamp_float, clamp_int
from ..utils.library_captions import (
    caption_entries,
    delete_caption_record,
    get_caption_record,
    save_caption,
    update_caption_record,
)
from ..utils.library_presets import set_last_used_caption_preset
from ..utils.library_prompts import prompt_categories
from ..utils.library_settings_store import get_library_root, list_categories
from ..utils.library_stats import stats
from ..utils.library_storage import delete_temp_upload, save_temp_upload
from ..utils.logging_utils import get_logger
from ..utils.output_metadata import (
    compare_output_metadata,
    get_output_metadata_record,
    parse_output_metadata_bytes,
    save_metadata_as_character,
    save_metadata_as_prompt,
)
from .common import json_error

logger = get_logger(__name__)
router = APIRouter()

_ALLOWED_COMPONENTS = {'', 'face', 'person', 'outfit', 'pose', 'location', 'custom'}
_ALLOWED_MODES = {'full_image', 'face_only', 'person_only', 'outfit_only', 'pose_only', 'location_only', 'custom_crop'}


def _normalize_component_type(value: str) -> str:
    value = (value or '').strip().lower().replace(' ', '_')
    return value if value in _ALLOWED_COMPONENTS else ''


def _normalize_caption_mode(value: str) -> str:
    value = (value or 'full_image').strip().lower().replace(' ', '_')
    return value if value in _ALLOWED_MODES else 'full_image'


def _normalize_detail_level(value: str) -> str:
    value = (value or 'detailed').strip().lower().replace('-', '_').replace(' ', '_')
    return value if value in {'basic', 'detailed', 'attribute_rich'} else 'detailed'


def _default_component_for_mode(mode: str) -> str:
    return {
        'face_only': 'face',
        'person_only': 'person',
        'outfit_only': 'outfit',
        'pose_only': 'pose',
        'location_only': 'location',
        'custom_crop': 'custom',
    }.get(_normalize_caption_mode(mode), '')


def _parse_crop_json(raw: str) -> Dict[str, float] | None:
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    try:
        x = max(0.0, min(1.0, float(payload.get('x', 0.0))))
        y = max(0.0, min(1.0, float(payload.get('y', 0.0))))
        w = max(0.0, min(1.0 - x, float(payload.get('w', 0.0))))
        h = max(0.0, min(1.0 - y, float(payload.get('h', 0.0))))
    except Exception:
        return None
    if w <= 0.01 or h <= 0.01:
        return None
    return {'x': round(x, 6), 'y': round(y, 6), 'w': round(w, 6), 'h': round(h, 6)}


def _default_crop_meta(mode: str) -> Dict[str, float] | None:
    mode = _normalize_caption_mode(mode)
    if mode == 'face_only':
        return {'x': 0.18, 'y': 0.02, 'w': 0.64, 'h': 0.42}
    if mode == 'person_only':
        return {'x': 0.10, 'y': 0.03, 'w': 0.80, 'h': 0.92}
    if mode == 'outfit_only':
        return {'x': 0.18, 'y': 0.18, 'w': 0.64, 'h': 0.62}
    if mode == 'pose_only':
        return {'x': 0.08, 'y': 0.03, 'w': 0.84, 'h': 0.92}
    return None


def _crop_temp_image(src_path: str, crop_meta: Dict[str, float]) -> str:
    src = Path(src_path)
    with Image.open(src) as im:
        width, height = im.size
        left = max(0, min(width - 1, int(round(crop_meta['x'] * width))))
        top = max(0, min(height - 1, int(round(crop_meta['y'] * height))))
        right = max(left + 1, min(width, int(round((crop_meta['x'] + crop_meta['w']) * width))))
        bottom = max(top + 1, min(height, int(round((crop_meta['y'] + crop_meta['h']) * height))))
        cropped = im.crop((left, top, right, bottom))
        suffix = src.suffix.lower() or '.png'
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=str(src.parent))
        try:
            save_format = (im.format or '').upper() or 'PNG'
            if save_format == 'JPEG' and cropped.mode in {'RGBA', 'LA'}:
                cropped = cropped.convert('RGB')
            cropped.save(tmp.name, format=save_format)
        finally:
            tmp.close()
        return tmp.name


def _caption_payload(rec: dict) -> dict:
    clean = {k: v for k, v in rec.items() if not str(k).startswith('_')}
    caption_id = str(clean.get('id') or '')
    clean['thumb_url'] = f'/api/caption-thumb?caption_id={caption_id}' if caption_id else ''
    clean['image_url'] = f'/api/caption-image-file?caption_id={caption_id}' if caption_id else ''
    return clean


@router.post('/api/caption-image')
async def api_caption_image(
    model: str = Form('default'),
    image: UploadFile = File(...),
    prompt_style: str = Form('Stable Diffusion Prompt'),
    caption_length: str = Form('any'),
    custom_prompt: str = Form(''),
    max_new_tokens: int = Form(160),
    temperature: float = Form(0.2),
    top_p: float = Form(0.9),
    top_k: int = Form(40),
    prefix: str = Form(''),
    suffix: str = Form(''),
    output_style: str = Form('Auto (match input)'),
    preset_name: str = Form(''),
    caption_mode: str = Form('full_image'),
    component_type: str = Form(''),
    detail_level: str = Form('detailed'),
    crop_json: str = Form(''),
):
    saved = None
    cropped_path = ''
    try:
        caption_mode = _normalize_caption_mode(caption_mode)
        component_type = _normalize_component_type(component_type) or _default_component_for_mode(caption_mode)
        detail_level = _normalize_detail_level(detail_level)
        crop_meta = _parse_crop_json(crop_json)
        content = await image.read()
        saved = save_temp_upload(content, Path(image.filename or 'upload.png').suffix)
        if preset_name:
            set_last_used_caption_preset(preset_name)
        max_new_tokens = clamp_int(max_new_tokens, 24, 1000, 160)
        temperature = clamp_float(temperature, 0.0, 1.5, 0.2)
        top_p = clamp_float(top_p, 0.0, 1.0, 0.9)
        top_k = clamp_int(top_k, 0, 200, 40)

        effective_crop = crop_meta
        if not effective_crop:
            if caption_mode == 'custom_crop':
                raise ValueError('Custom crop mode needs a selected crop box.')
            effective_crop = _default_crop_meta(caption_mode)

        image_path = saved['temp_image_path']
        if effective_crop:
            cropped_path = _crop_temp_image(image_path, effective_crop)
            image_path = cropped_path

        result = await caption_image_with_settings(
            image_path=image_path,
            model=model,
            prompt_style=prompt_style,
            caption_length=caption_length,
            custom_prompt=custom_prompt,
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            prefix=prefix,
            suffix=suffix,
            output_style=output_style,
            caption_mode=caption_mode,
            detail_level=detail_level,
        )
    except Exception as e:
        if saved and saved.get('temp_image_id'):
            delete_temp_upload(saved['temp_image_id'])
        if cropped_path:
            Path(cropped_path).unlink(missing_ok=True)
        logger.exception('Caption image failed')
        return json_error(str(e), 500)
    finally:
        if cropped_path:
            Path(cropped_path).unlink(missing_ok=True)
    finish_reason = result.get('finish_reason', '')
    reasoning_stripped = bool(result.get('reasoning_stripped'))
    if reasoning_stripped and not result.get('text', ''):
        warning = 'Visible reasoning was stripped, but the model never reached a final caption. Raise max new tokens or use a non-reasoning / no-think model setting.'
    elif finish_reason == 'length':
        warning = 'Caption may be truncated. Increase max new tokens.'
    elif reasoning_stripped:
        warning = 'Visible reasoning was stripped automatically. Showing final caption only.'
    else:
        warning = ''
    return JSONResponse({
        'ok': True,
        'caption': result.get('text', ''),
        'temp_image_id': saved['temp_image_id'],
        'preview_name': image.filename or saved['temp_image_id'],
        'finish_reason': finish_reason,
        'warning': warning,
        'reasoning_stripped': reasoning_stripped,
        'caption_mode': caption_mode,
        'component_type': component_type,
        'detail_level': detail_level,
        'effective_crop': effective_crop,
    })


@router.post('/api/save-caption')
async def api_save_caption(
    name: str = Form(...),
    category: str = Form('uncategorized'),
    caption: str = Form(...),
    temp_image_id: str = Form(...),
    model: str = Form('default'),
    notes: str = Form(''),
    raw_caption: str = Form(''),
    preset_name: str = Form(''),
    prompt_style: str = Form(''),
    finish_reason: str = Form(''),
    settings_json: str = Form(''),
    component_type: str = Form(''),
    caption_mode: str = Form('full_image'),
    detail_level: str = Form('detailed'),
    crop_json: str = Form(''),
):
    try:
        settings = json.loads(settings_json) if settings_json else {}
        crop_meta = _parse_crop_json(crop_json)
        component_type = _normalize_component_type(component_type) or _default_component_for_mode(caption_mode)
        caption_mode = _normalize_caption_mode(caption_mode)
        detail_level = _normalize_detail_level(detail_level)
        if isinstance(settings, dict):
            settings = dict(settings)
            settings['caption_mode'] = caption_mode
            settings['component_type'] = component_type
            settings['detail_level'] = detail_level
            if crop_meta:
                settings['crop_meta'] = crop_meta
        rec = save_caption(
            name=name,
            category=category,
            caption=caption,
            temp_image_id=temp_image_id,
            model=model,
            notes=notes,
            raw_caption=raw_caption or caption,
            preset_name=preset_name,
            prompt_style=prompt_style,
            finish_reason=finish_reason,
            settings=settings if isinstance(settings, dict) else {},
            component_type=component_type,
            caption_mode=caption_mode,
            crop_meta=crop_meta,
            detail_level=detail_level,
        )
    except Exception as e:
        logger.exception('Validation error in API request')
        return json_error(str(e), 400)
    return JSONResponse({'ok': True, 'message': f"Saved caption as {rec['name']} in {rec['category']}.", 'categories': list_categories(), 'stats': stats(), 'record': _caption_payload(rec)})


@router.get('/api/caption-records')
async def api_caption_records(
    query: str = '',
    category: str = '',
    model: str = '',
    prompt_style: str = '',
    date_from: str = '',
    date_to: str = '',
    limit: int = 200,
    component_type: str = '',
    detail_level: str = '',
    component_only: bool = False,
    sort: str = 'newest',
    page: int = 1,
    page_size: int = 0,
):
    effective_page_size = max(1, int(page_size or limit or 200))
    page_items, total = caption_entries(
        query=query,
        category=category,
        model=model,
        prompt_style=prompt_style,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        component_type=component_type,
        detail_level=detail_level,
        component_only=component_only,
        sort=sort,
        page=page,
        page_size=effective_page_size,
        return_total=True,
    )
    entries = [
        {
            **entry,
            'thumb_url': f"/api/caption-thumb?caption_id={entry.get('id')}",
            'image_url': f"/api/caption-image-file?caption_id={entry.get('id')}",
        }
        for entry in page_items
    ]
    total_pages = max(1, (total + effective_page_size - 1) // effective_page_size)
    current_page = min(max(1, int(page or 1)), total_pages)
    return JSONResponse({
        'ok': True,
        'entries': entries,
        'categories': list_categories(),
        'total': total,
        'page': current_page,
        'page_size': effective_page_size,
        'total_pages': total_pages,
        'sort': (sort or 'newest').strip().lower() or 'newest',
    })


@router.get('/api/caption-record')
async def api_caption_record(caption_id: str = '', name: str = '', category: str = ''):
    rec = get_caption_record(caption_id=caption_id, name=name, category=category)
    if not rec:
        return json_error('Caption not found.', 404)
    return JSONResponse({'ok': True, 'record': _caption_payload(rec)})


@router.post('/api/update-caption')
async def api_update_caption(
    caption_id: str = Form(''),
    name: str = Form(''),
    category: str = Form(''),
    caption: str = Form(...),
    notes: str = Form(''),
    model: str = Form(''),
    prompt_style: str = Form(''),
    component_type: str = Form(''),
    detail_level: str = Form(''),
):
    try:
        rec = update_caption_record(
            caption_id=caption_id,
            name=name,
            category=category,
            caption=caption,
            notes=notes,
            model=model,
            prompt_style=prompt_style,
            component_type=component_type,
            detail_level=detail_level,
        )
    except FileNotFoundError as e:
        return json_error(str(e), 404)
    except Exception as e:
        logger.exception('Update caption failed')
        return json_error(str(e), 400)
    return JSONResponse({'ok': True, 'message': f"Updated caption: {rec['name']}", 'record': _caption_payload(rec), 'stats': stats()})


@router.post('/api/delete-caption')
async def api_delete_caption(caption_id: str = Form(''), name: str = Form(''), category: str = Form('')):
    ok = delete_caption_record(caption_id=caption_id, name=name, category=category)
    if not ok:
        return json_error('Caption not found.', 404)
    return JSONResponse({'ok': True, 'message': 'Deleted caption.', 'stats': stats(), 'categories': list_categories()})


@router.post('/api/caption-to-prompt')
async def api_caption_to_prompt(caption_id: str = Form(...), category: str = Form(''), prompt_name: str = Form('')):
    from ..utils.library_prompts import save_prompt

    rec = get_caption_record(caption_id=caption_id)
    if not rec:
        return json_error('Caption not found.', 404)
    final_category = (category or rec.get('category') or 'uncategorized').strip() or 'uncategorized'
    final_name = (prompt_name or f"{rec.get('name') or 'Caption'} Prompt").strip()
    prompt_record = save_prompt(
        name=final_name,
        category=final_category,
        prompt=str(rec.get('caption') or '').strip(),
        model=str(rec.get('model') or '').strip(),
        notes=str(rec.get('notes') or '').strip(),
        raw_prompt=str(rec.get('raw_caption') or rec.get('caption') or '').strip(),
        preset_name='Caption Browser',
        style='Caption Import',
        finish_reason='caption_import',
        settings={
            'source_caption_id': rec.get('id') or '',
            'source_prompt_style': rec.get('prompt_style') or '',
            'source_component_type': rec.get('component_type') or '',
            'source_caption_mode': rec.get('caption_mode') or '',
        },
        generation_mode='caption_import',
    )
    return JSONResponse({'ok': True, 'message': f"Created prompt from caption: {prompt_record['name']}", 'record': prompt_record, 'prompt_categories': prompt_categories(), 'stats': stats()})


@router.get('/api/caption-thumb')
async def api_caption_thumb(caption_id: str = ''):
    rec = get_caption_record(caption_id=caption_id)
    if not rec:
        return json_error('Caption not found.', 404)
    root = get_library_root()
    file_path = root / str(rec.get('thumb_path') or '')
    if not file_path.exists():
        return json_error('Thumbnail not found.', 404)
    media_type = mimetypes.guess_type(str(file_path))[0] or 'image/webp'
    return FileResponse(file_path, media_type=media_type)


@router.get('/api/caption-image-file')
async def api_caption_image_file(caption_id: str = ''):
    rec = get_caption_record(caption_id=caption_id)
    if not rec:
        return json_error('Caption not found.', 404)
    root = get_library_root()
    file_path = root / str(rec.get('image_path') or '')
    if not file_path.exists():
        return json_error('Image not found.', 404)
    media_type = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
    return FileResponse(file_path, media_type=media_type)


@router.post('/api/inspect-output-metadata')
async def api_inspect_output_metadata(image: UploadFile = File(...)):
    try:
        content = await image.read()
        parsed = parse_output_metadata_bytes(content, image.filename or 'output.png')
    except Exception as e:
        logger.exception('Metadata inspection failed')
        return json_error(f'Could not read metadata: {e}', 400)
    return JSONResponse({'ok': True, 'parsed': parsed})


@router.post('/api/compare-output-metadata')
async def api_compare_output_metadata(primary_image: UploadFile = File(...), secondary_image: UploadFile = File(...)):
    try:
        primary = parse_output_metadata_bytes(await primary_image.read(), primary_image.filename or 'primary.png')
        secondary = parse_output_metadata_bytes(await secondary_image.read(), secondary_image.filename or 'secondary.png')
        diff = compare_output_metadata(primary, secondary)
    except Exception as e:
        logger.exception('Metadata compare failed')
        return json_error(f'Could not compare metadata: {e}', 400)
    return JSONResponse({'ok': True, 'primary': primary, 'secondary': secondary, 'diff': diff})


@router.post('/api/save-output-metadata-prompt')
async def api_save_output_metadata_prompt(
    metadata_json: str = Form(...),
    name: str = Form(...),
    category: str = Form('uncategorized'),
    notes: str = Form(''),
    model: str = Form(''),
):
    try:
        parsed = json.loads(metadata_json)
        if not isinstance(parsed, dict):
            raise ValueError('Invalid metadata payload.')
        rec = save_metadata_as_prompt(name=name, category=category, parsed=parsed, model=model, notes=notes)
    except Exception as e:
        logger.exception('Save metadata as prompt failed')
        return json_error(str(e), 400)
    return JSONResponse({'ok': True, 'message': f"Saved metadata as prompt: {rec['name']}", 'record': rec, 'stats': stats(), 'categories': list_categories(), 'prompt_categories': prompt_categories()})


@router.post('/api/save-output-metadata-character')
async def api_save_output_metadata_character(
    metadata_json: str = Form(...),
    name: str = Form(...),
    notes: str = Form(''),
):
    try:
        parsed = json.loads(metadata_json)
        if not isinstance(parsed, dict):
            raise ValueError('Invalid metadata payload.')
        rec = save_metadata_as_character(name=name, parsed=parsed, notes=notes)
    except Exception as e:
        logger.exception('Save metadata as character failed')
        return json_error(str(e), 400)
    return JSONResponse({'ok': True, 'message': f"Saved metadata as character: {rec['name']}", 'record': rec})


@router.get('/api/output-metadata-record')
async def api_output_metadata_record(record_id: str = ''):
    rec = get_output_metadata_record(record_id)
    if not rec:
        return json_error('Metadata record not found.', 404)
    return JSONResponse({'ok': True, 'record': rec})
