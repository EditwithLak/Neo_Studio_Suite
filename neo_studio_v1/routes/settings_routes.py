from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

from ..utils.library_settings_store import list_categories, set_library_root
from ..utils.library_stats import stats
from ..utils.logging_utils import get_logger
from .common import json_error

logger = get_logger(__name__)
router = APIRouter()


@router.post('/api/pick-folder')
async def api_pick_folder(initial_path: str = Form('')):
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        start_dir = str(initial_path or '').strip()
        if start_dir and Path(start_dir).exists():
            path = filedialog.askdirectory(initialdir=start_dir) or ''
        else:
            path = filedialog.askdirectory() or ''
        try:
            root.destroy()
        except Exception:
            pass
    except Exception as e:
        logger.exception('Folder picker failed')
        return json_error(f'Folder picker failed: {e}', 500)
    return JSONResponse({'ok': True, 'path': path})


@router.post('/api/save-settings')
async def api_save_settings(library_root: str = Form(...)):
    try:
        set_library_root(library_root)
    except Exception as e:
        logger.exception('Validation error in API request')
        return json_error(str(e), 400)
    return JSONResponse({'ok': True, 'stats': stats(), 'categories': list_categories()})
