from __future__ import annotations

import threading
import webbrowser

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routes import batch_router, bundle_router, caption_router, character_router, library_transfer_router, preset_router, prompt_router, settings_router, system_router
from .utils.characters import character_entries
from .utils.config import STATIC_DIR, TEMPLATES_DIR
from .utils.kobold import get_models
from .utils.library_presets import (
    get_caption_presets,
    get_last_used_caption_preset,
    get_last_used_prompt_preset,
    get_prompt_presets,
)
from .utils.library_prompts import prompt_categories, prompt_entries
from .utils.library_settings_store import get_last_used_category, list_categories
from .utils.library_stats import stats
from .utils.library_storage import cleanup_temp_uploads
from .utils.prompt_bundles import bundle_entries

STATIC_DIR.mkdir(parents=True, exist_ok=True)
cleanup_temp_uploads()

app = FastAPI(title='Neo Studio')
app.mount('/static', StaticFiles(directory=str(STATIC_DIR)), name='static')
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

for router in (
    system_router,
    prompt_router,
    bundle_router,
    character_router,
    caption_router,
    batch_router,
    library_transfer_router,
    settings_router,
    preset_router,
):
    app.include_router(router)


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    models = await get_models()
    categories = list_categories()
    prompt_category_list = prompt_categories()
    last_prompt_category = get_last_used_category('prompt')
    last_caption_category = get_last_used_category('caption')
    prompt_presets = get_prompt_presets()
    caption_presets = get_caption_presets()
    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
            'models': models,
            'categories': categories,
            'stats': stats(),
            'last_prompt_category': last_prompt_category,
            'last_caption_category': last_caption_category,
            'caption_presets': caption_presets,
            'last_caption_preset': get_last_used_caption_preset(),
            'prompt_presets': prompt_presets,
            'last_prompt_preset': get_last_used_prompt_preset(),
            'prompt_categories': prompt_category_list,
            'saved_prompt_entries': prompt_entries(last_prompt_category),
            'saved_character_entries': character_entries(),
            'boot_data': {
                'initialCategories': categories,
                'initialPromptPresets': prompt_presets,
                'initialCaptionPresets': caption_presets,
                'initialPromptEntries': prompt_entries(last_prompt_category),
                'initialCharacterEntries': character_entries(),
                'lastPromptCategory': last_prompt_category,
                'lastCaptionCategory': last_caption_category,
                'promptCategories': prompt_category_list,
                'lastPromptPreset': get_last_used_prompt_preset(),
                'lastCaptionPreset': get_last_used_caption_preset(),
                'initialBundleEntries': bundle_entries(),
            },
        },
    )


def open_browser():
    webbrowser.open_new('http://localhost:8000')


if __name__ == '__main__':
    threading.Timer(1.2, open_browser).start()
    import uvicorn
    uvicorn.run('neo_studio_v1.app:app', host='0.0.0.0', port=8000, reload=True)
