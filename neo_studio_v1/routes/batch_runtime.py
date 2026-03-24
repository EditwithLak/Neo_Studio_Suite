from __future__ import annotations

import asyncio
import json
import os
import platform
import threading
import time
from pathlib import Path
from uuid import uuid4

from ..utils.config import APP_DIR
from ..utils.kobold import caption_image_with_settings
from ..utils.library_captions import dataset_txt_output_path, image_files_in_folder, save_caption_from_path
from ..utils.library_settings_store import list_categories
from ..utils.library_stats import stats
from ..utils.logging_utils import get_logger
from .common import parse_bool, parse_exts, settings_dict

logger = get_logger(__name__)

BATCH_JOBS: dict[str, dict] = {}
BATCH_LOCK = threading.Lock()
BATCH_STATE_DIR = APP_DIR / 'user_data' / 'batch_jobs'
BATCH_STATE_DIR.mkdir(parents=True, exist_ok=True)
BATCH_POST_ACTION_COUNTDOWN = 60


_ALLOWED_COMPONENT_TYPES = {'', 'face', 'person', 'outfit', 'pose', 'location', 'custom'}
_ALLOWED_BATCH_CAPTION_MODES = {'full_image', 'face_only', 'person_only', 'outfit_only', 'pose_only', 'location_only'}
_ALLOWED_DETAIL_LEVELS = {'basic', 'detailed', 'attribute_rich'}


def _normalize_component_type(value: str) -> str:
    value = (value or '').strip().lower().replace(' ', '_')
    return value if value in _ALLOWED_COMPONENT_TYPES else ''


def _normalize_caption_mode(value: str) -> str:
    value = (value or 'full_image').strip().lower().replace(' ', '_')
    return value if value in _ALLOWED_BATCH_CAPTION_MODES else 'full_image'


def _normalize_detail_level(value: str) -> str:
    value = (value or 'detailed').strip().lower().replace('-', '_').replace(' ', '_')
    return value if value in _ALLOWED_DETAIL_LEVELS else 'detailed'


def _state_path(job_id: str) -> Path:
    return BATCH_STATE_DIR / f'{job_id}.json'


def _now() -> float:
    return time.time()


def _json_safe(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, list):
        return [_json_safe(x) for x in value]
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    return value


def persist_batch_state(job_id: str) -> None:
    with BATCH_LOCK:
        state = BATCH_JOBS.get(job_id)
        if not state:
            return
        payload = _json_safe(dict(state))
    try:
        _state_path(job_id).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    except Exception:
        logger.exception('Failed to persist batch state for %s', job_id)


def load_batch_state(job_id: str) -> dict | None:
    path = _state_path(job_id)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            return data
    except Exception:
        logger.exception('Failed to load batch state for %s', job_id)
    return None


def list_saved_batch_jobs() -> list[dict]:
    items: list[dict] = []
    for path in sorted(BATCH_STATE_DIR.glob('*.json')):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        items.append({
            'job_id': data.get('job_id') or path.stem,
            'status': data.get('status') or 'unknown',
            'message': data.get('message') or '',
            'folder_path': data.get('params', {}).get('folder_path', ''),
            'mode': data.get('mode') or data.get('params', {}).get('mode', 'dataset'),
            'total_items': int(data.get('total_items') or 0),
            'processed': int(data.get('processed') or 0),
            'saved': int(data.get('saved') or 0),
            'skipped': int(data.get('skipped') or 0),
            'errors': int(data.get('errors') or 0),
            'started_at': float(data.get('started_at') or 0.0),
            'finished_at': float(data.get('finished_at') or 0.0),
        })
    items.sort(key=lambda x: x.get('started_at') or 0.0, reverse=True)
    return items[:20]


def batch_summary(state: dict) -> str:
    processed = int(state.get('processed') or 0)
    saved = int(state.get('saved') or 0)
    skipped = int(state.get('skipped') or 0)
    errors = int(state.get('errors') or 0)
    duplicates = int(state.get('duplicates') or 0)
    parts = [f'Processed: {processed}', f'saved: {saved}', f'skipped: {skipped}', f'errors: {errors}']
    if duplicates:
        parts.append(f'duplicates: {duplicates}')
    return ', '.join(parts) + '.'


def _status_with_eta(payload: dict) -> dict:
    now = _now()
    started = float(payload.get('started_at') or now)
    current_started = float(payload.get('current_item_started_at') or 0.0)
    payload['elapsed_total_seconds'] = max(0.0, now - started)
    payload['elapsed_current_seconds'] = max(0.0, now - current_started) if current_started and payload.get('status') == 'running' else float(payload.get('last_item_elapsed_seconds') or 0.0)
    total = max(0, int(payload.get('total_items') or 0))
    current = max(0, int(payload.get('current_index') or 0))
    payload['progress_percent'] = (current / total * 100.0) if total else 0.0
    avg_seconds = 0.0
    processed = max(0, int(payload.get('processed') or 0))
    if processed > 0 and payload['elapsed_total_seconds'] > 0:
        avg_seconds = payload['elapsed_total_seconds'] / processed
    elif current > 0 and payload['elapsed_total_seconds'] > 0:
        avg_seconds = payload['elapsed_total_seconds'] / current
    remaining = max(0, total - current)
    payload['avg_item_seconds'] = avg_seconds
    payload['eta_seconds'] = max(0.0, avg_seconds * remaining) if avg_seconds and payload.get('status') in {'running', 'queued', 'cancelling'} else 0.0
    return payload


def batch_status_payload(job_id: str) -> dict | None:
    with BATCH_LOCK:
        state = BATCH_JOBS.get(job_id)
        if not state:
            state = load_batch_state(job_id)
            if state:
                BATCH_JOBS[job_id] = state
        if not state:
            return None
        payload = dict(state)
    payload = _status_with_eta(payload)
    payload['summary'] = batch_summary(payload)
    payload['detail_lines'] = list(payload.get('detail_lines') or [])[-300:]
    payload['error_lines'] = list(payload.get('error_lines') or [])[-100:]
    payload['duplicate_lines'] = list(payload.get('duplicate_lines') or [])[-100:]
    payload['failed_items'] = list(payload.get('failed_items') or [])[-200:]
    payload['remaining_items_count'] = len(payload.get('remaining_items') or [])
    payload['ok'] = True
    payload['job_id'] = job_id
    payload['recent_jobs'] = list_saved_batch_jobs()
    if payload.get('post_action_execute_at'):
        payload['post_action_seconds_left'] = max(0, int(float(payload['post_action_execute_at']) - _now()))
    else:
        payload['post_action_seconds_left'] = 0
    return payload


def update_batch_state(job_id: str, persist: bool = True, **updates) -> None:
    with BATCH_LOCK:
        state = BATCH_JOBS.get(job_id)
        if not state:
            return
        state.update(updates)
    if persist:
        persist_batch_state(job_id)


def _mark_cancel(job_id: str) -> dict | None:
    payload = batch_status_payload(job_id)
    if not payload:
        return None
    status = payload.get('status')
    if status in {'completed', 'failed', 'cancelled'}:
        return payload
    update_batch_state(job_id, cancel_requested=True, status='cancelling', message='Cancel requested. The batch will stop after the current file finishes.')
    return batch_status_payload(job_id)


def request_batch_cancel(job_id: str) -> dict | None:
    return _mark_cancel(job_id)


def _write_export_log(state: dict) -> Path:
    log_path = BATCH_STATE_DIR / f"{state.get('job_id','batch')}_log.txt"
    lines: list[str] = []
    lines.append('Neo Studio Batch Run Log')
    lines.append('=' * 30)
    lines.append(f"Job ID: {state.get('job_id','')}")
    lines.append(f"Status: {state.get('status','')}")
    lines.append(f"Mode: {state.get('mode','')}")
    lines.append(f"Folder: {state.get('params', {}).get('folder_path','')}")
    lines.append(f"Summary: {batch_summary(state)}")
    lines.append('')
    if state.get('duplicate_lines'):
        lines.append('Duplicate Summary')
        lines.append('-' * 18)
        lines.extend(state.get('duplicate_lines') or [])
        lines.append('')
    if state.get('error_lines'):
        lines.append('Errors')
        lines.append('-' * 18)
        lines.extend(state.get('error_lines') or [])
        lines.append('')
    if state.get('detail_lines'):
        lines.append('Details')
        lines.append('-' * 18)
        lines.extend(state.get('detail_lines') or [])
        lines.append('')
    log_path.write_text('\n'.join(lines), encoding='utf-8')
    return log_path


def export_batch_log_payload(job_id: str) -> dict | None:
    payload = batch_status_payload(job_id)
    if not payload:
        return None
    log_path = _write_export_log(payload)
    return {
        'ok': True,
        'job_id': job_id,
        'filename': log_path.name,
        'path': str(log_path),
        'content': log_path.read_text(encoding='utf-8'),
        'message': 'Batch log exported.',
    }


def _windows_post_action_command(action: str) -> str | None:
    action = (action or '').strip().lower()
    if action == 'shutdown':
        return 'shutdown /s /t 0'
    if action == 'hibernate':
        return 'shutdown /h'
    if action == 'sleep':
        return 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0'
    return None


def _execute_post_action(job_id: str, action: str) -> None:
    command = _windows_post_action_command(action)
    if not command:
        return
    if platform.system().lower() != 'windows':
        update_batch_state(job_id, post_action_status='unsupported', message=f'Post-task action {action} is only enabled on Windows.')
        return
    try:
        update_batch_state(job_id, post_action_status='executing', message=f'Executing post-task action: {action}.')
        os.system(command)
    except Exception:
        logger.exception('Failed to execute post-task action %s for %s', action, job_id)
        update_batch_state(job_id, post_action_status='failed', message=f'Failed to execute post-task action: {action}.')


def _schedule_post_action(job_id: str, action: str) -> None:
    action = (action or 'none').strip().lower()
    if action in {'', 'none', 'do_nothing'}:
        return
    execute_at = _now() + BATCH_POST_ACTION_COUNTDOWN
    update_batch_state(job_id, post_action=action, post_action_status='countdown', post_action_execute_at=execute_at, message=f'Batch finished. {action.title()} will run in {BATCH_POST_ACTION_COUNTDOWN} seconds unless cancelled.')

    def worker():
        while True:
            state = batch_status_payload(job_id)
            if not state:
                return
            if state.get('post_action_status') == 'cancelled':
                return
            left = int(state.get('post_action_seconds_left') or 0)
            if left <= 0:
                break
            time.sleep(1)
        latest = batch_status_payload(job_id)
        if latest and latest.get('post_action_status') != 'cancelled':
            _execute_post_action(job_id, action)

    threading.Thread(target=worker, daemon=True).start()


def cancel_post_action(job_id: str) -> dict | None:
    payload = batch_status_payload(job_id)
    if not payload:
        return None
    if not payload.get('post_action_execute_at'):
        return payload
    update_batch_state(job_id, post_action_status='cancelled', post_action_execute_at=0.0, message='Post-task action cancelled.')
    return batch_status_payload(job_id)


def _build_retry_or_resume_params(job_id: str, *, retry_failed_only: bool = False) -> tuple[dict, int] | tuple[None, int]:
    state = batch_status_payload(job_id)
    if not state:
        return None, 0
    params = dict(state.get('params') or {})
    if not params:
        return None, 0
    if retry_failed_only:
        target_items = [x for x in (state.get('failed_items') or []) if x]
    else:
        target_items = [x for x in (state.get('remaining_items') or []) if x]
        if state.get('current_item_path') and state.get('status') == 'cancelling':
            target_items.insert(0, state.get('current_item_path'))
    target_items = list(dict.fromkeys(target_items))
    if not target_items:
        return None, 0
    params['target_images'] = target_items
    return params, len(target_items)


def create_retry_batch_job(job_id: str) -> dict | None:
    params, count = _build_retry_or_resume_params(job_id, retry_failed_only=True)
    if not params:
        return None
    return create_batch_job(params, count, source_job_id=job_id, purpose='retry_failed')


def create_resume_batch_job(job_id: str) -> dict | None:
    params, count = _build_retry_or_resume_params(job_id, retry_failed_only=False)
    if not params:
        return None
    return create_batch_job(params, count, source_job_id=job_id, purpose='resume')


async def run_batch_caption_job(job_id: str, params: dict) -> None:
    try:
        images = [Path(x) for x in (params.get('target_images') or []) if x]
        if not images:
            images = image_files_in_folder(params['folder_path'], recursive=params['recursive'], include_exts=params['include_exts'])
    except Exception as e:
        update_batch_state(job_id, status='failed', message=str(e), finished_at=_now())
        return
    if not images:
        update_batch_state(job_id, status='failed', message='No supported image files found in that folder.', finished_at=_now())
        return

    processed = saved_count = skipped = errors = duplicates = 0
    error_lines = []
    duplicate_lines = []
    detail_lines = []
    failed_items: list[str] = []
    counter = max(1, int(params['numbering_start'] or 1))
    total = len(images)
    update_batch_state(job_id, total_items=total, remaining_items=[str(p) for p in images], message=f'Queued {total} files.')

    for idx, img in enumerate(images, start=1):
        img_path = str(img)
        item_started = _now()
        remaining_items = [str(p) for p in images[idx:]]
        update_batch_state(
            job_id,
            status='running',
            current_index=idx,
            current_item_name=img.name,
            current_item_path=img_path,
            current_item_started_at=item_started,
            remaining_items=remaining_items,
            message=f'Processing {idx}/{total}: {img.name}',
            processed=processed,
            saved=saved_count,
            skipped=skipped,
            errors=errors,
            duplicates=duplicates,
            detail_lines=detail_lines[-300:],
            error_lines=error_lines[-100:],
            duplicate_lines=duplicate_lines[-100:],
            failed_items=failed_items[-200:],
        )
        try:
            result = await caption_image_with_settings(
                image_path=img_path,
                model=params['model'],
                prompt_style=params['prompt_style'],
                caption_length=params['caption_length'],
                custom_prompt=params['custom_prompt'],
                max_tokens=params['max_new_tokens'],
                temperature=params['temperature'],
                top_p=params['top_p'],
                top_k=params['top_k'],
                prefix=params['prefix'],
                suffix=params['suffix'],
                output_style=params['output_style'],
                caption_mode=params['caption_mode'],
                detail_level=params['detail_level'],
            )
            caption_text = (result.get('text', '') or '').strip()
            finish_reason = str(result.get('finish_reason', '') or '').strip().lower()
            if not caption_text:
                raise RuntimeError('No caption text was generated.')
            if finish_reason == 'error' or caption_text.lower().startswith('vision error:') or caption_text == 'Invalid image file.':
                raise RuntimeError(caption_text)
            if params['mode'] == 'dataset':
                txt_path = dataset_txt_output_path(img, params['folder_path'], params['output_folder'])
                if txt_path.exists() and params['skip_existing_txt'] and not params['overwrite_existing']:
                    skipped += 1
                    detail_lines.append(f'Skipped existing txt: {img.name}')
                elif txt_path.exists() and not params['overwrite_existing'] and not params['skip_existing_txt']:
                    skipped += 1
                    detail_lines.append(f'Skipped existing txt: {img.name}')
                else:
                    txt_path.write_text(caption_text + '\n', encoding='utf-8')
                    processed += 1
                    saved_count += 1
                    detail_lines.append(f'Wrote txt: {img.name}')
            else:
                name = f"{params['base_name']}_{counter:03d}"
                rec = save_caption_from_path(
                    name=name,
                    category=params['category'],
                    caption=caption_text,
                    image_path=img_path,
                    model=params['model'],
                    raw_caption=caption_text,
                    skip_duplicates=params['skip_duplicates'],
                    prompt_style=params['prompt_style'],
                    finish_reason=result.get('finish_reason', ''),
                    settings=params['settings'],
                    component_type=params['component_type'],
                    caption_mode=params['caption_mode'],
                    detail_level=params['detail_level'],
                )
                processed += 1
                if rec is None:
                    skipped += 1
                    duplicates += 1
                    duplicate_lines.append(f'Duplicate skipped: {img.name}')
                    detail_lines.append(f'Skipped duplicate: {img.name}')
                else:
                    saved_count += 1
                    counter += 1
                    detail_lines.append(f'Saved library entry: {img.name}')
        except Exception as e:
            errors += 1
            failed_items.append(img_path)
            error_lines.append(f'{img.name}: {e}')
            detail_lines.append(f'Error: {img.name} -> {e}')
        finally:
            state = batch_status_payload(job_id) or {}
            update_batch_state(
                job_id,
                processed=processed,
                saved=saved_count,
                skipped=skipped,
                errors=errors,
                duplicates=duplicates,
                detail_lines=detail_lines[-300:],
                error_lines=error_lines[-100:],
                duplicate_lines=duplicate_lines[-100:],
                failed_items=failed_items[-200:],
                last_item_elapsed_seconds=max(0.0, _now() - item_started),
            )
            if state.get('cancel_requested'):
                final_message = f"Batch cancelled. {batch_summary({'processed': processed, 'saved': saved_count, 'skipped': skipped, 'errors': errors, 'duplicates': duplicates})}"
                update_batch_state(
                    job_id,
                    status='cancelled',
                    message=final_message,
                    processed=processed,
                    saved=saved_count,
                    skipped=skipped,
                    errors=errors,
                    duplicates=duplicates,
                    current_index=idx,
                    finished_at=_now(),
                    stats=stats(),
                    categories=list_categories(),
                )
                _write_export_log(batch_status_payload(job_id) or {})
                return

    final_message = f"Batch finished. {batch_summary({'processed': processed, 'saved': saved_count, 'skipped': skipped, 'errors': errors, 'duplicates': duplicates})}"
    update_batch_state(
        job_id,
        status='completed',
        message=final_message,
        processed=processed,
        saved=saved_count,
        skipped=skipped,
        errors=errors,
        duplicates=duplicates,
        current_index=total,
        current_item_name='',
        current_item_path='',
        current_item_started_at=0.0,
        remaining_items=[],
        finished_at=_now(),
        stats=stats(),
        categories=list_categories(),
    )
    state = batch_status_payload(job_id) or {}
    _write_export_log(state)
    _schedule_post_action(job_id, params.get('post_task_action', 'none'))


def start_batch_thread(job_id: str, params: dict) -> None:
    asyncio.run(run_batch_caption_job(job_id, params))


def create_batch_job(params: dict, image_count: int, *, source_job_id: str = '', purpose: str = 'run') -> dict:
    job_id = str(uuid4())
    state = {
        'job_id': job_id,
        'source_job_id': source_job_id,
        'purpose': purpose,
        'status': 'queued',
        'message': f'Queued {image_count} files.',
        'mode': params['mode'],
        'total_items': image_count,
        'current_index': 0,
        'current_item_name': '',
        'current_item_path': '',
        'current_item_started_at': 0.0,
        'last_item_elapsed_seconds': 0.0,
        'processed': 0,
        'saved': 0,
        'skipped': 0,
        'errors': 0,
        'duplicates': 0,
        'detail_lines': [],
        'error_lines': [],
        'duplicate_lines': [],
        'failed_items': [],
        'remaining_items': list(params.get('target_images') or []),
        'started_at': _now(),
        'finished_at': 0.0,
        'stats': {},
        'categories': [],
        'cancel_requested': False,
        'post_action': params.get('post_task_action', 'none'),
        'post_action_status': 'idle',
        'post_action_execute_at': 0.0,
        'params': dict(params),
    }
    with BATCH_LOCK:
        BATCH_JOBS[job_id] = state
    persist_batch_state(job_id)
    thread = threading.Thread(target=start_batch_thread, args=(job_id, params), daemon=True)
    thread.start()
    payload = batch_status_payload(job_id) or {'ok': True, 'job_id': job_id}
    payload['message'] = f'Started batch for {image_count} files.'
    return payload


def normalized_batch_params(*, model: str, mode: str, folder_path: str, category: str, base_name: str, numbering_start: int,
    overwrite_existing: str, skip_existing_txt: str, skip_duplicates: str, recursive: str, include_exts: str,
    prompt_style: str, caption_length: str, custom_prompt: str, max_new_tokens: int, temperature: float,
    top_p: float, top_k: int, prefix: str, suffix: str, output_style: str, output_folder: str,
    component_type: str, caption_mode: str, detail_level: str, post_task_action: str,
    clamp_int, clamp_float) -> dict:
    max_new_tokens = clamp_int(max_new_tokens, 24, 1000, 160)
    temperature = clamp_float(temperature, 0.0, 1.5, 0.2)
    top_p = clamp_float(top_p, 0.0, 1.0, 0.9)
    top_k = clamp_int(top_k, 0, 200, 40)
    caption_mode = _normalize_caption_mode(caption_mode)
    component_type = _normalize_component_type(component_type)
    detail_level = _normalize_detail_level(detail_level)
    settings = settings_dict(max_new_tokens, temperature, top_p, top_k)
    settings['caption_mode'] = caption_mode
    settings['component_type'] = component_type
    settings['detail_level'] = detail_level
    return {
        'model': model,
        'mode': (mode or 'dataset').strip().lower(),
        'folder_path': folder_path,
        'category': (category or '').strip() or 'uncategorized',
        'base_name': (base_name or '').strip() or 'Batch_Caption',
        'numbering_start': max(1, int(numbering_start or 1)),
        'overwrite_existing': parse_bool(overwrite_existing),
        'skip_existing_txt': parse_bool(skip_existing_txt),
        'skip_duplicates': parse_bool(skip_duplicates),
        'recursive': parse_bool(recursive),
        'include_exts': parse_exts(include_exts),
        'prompt_style': prompt_style,
        'caption_length': caption_length,
        'custom_prompt': custom_prompt,
        'max_new_tokens': max_new_tokens,
        'temperature': temperature,
        'top_p': top_p,
        'top_k': top_k,
        'prefix': prefix,
        'suffix': suffix,
        'output_style': output_style,
        'output_folder': output_folder,
        'component_type': component_type,
        'caption_mode': caption_mode,
        'detail_level': detail_level,
        'post_task_action': (post_task_action or 'none').strip().lower() or 'none',
        'settings': settings,
    }
