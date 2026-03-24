from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = APP_DIR.parent
STATIC_DIR = APP_DIR / 'static'
TEMPLATES_DIR = APP_DIR / 'templates'
LOGS_DIR = APP_DIR / 'logs'

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8000
DEFAULT_BASE_URL = 'http://localhost:5001'
DEFAULT_CHAT_PATH = '/v1/chat/completions'
DEFAULT_MODELS_PATH = '/v1/models'
BACKEND_TIMEOUT_SECONDS = 5.0
CHAT_TIMEOUT_SECONDS = 180.0

CHARACTER_STORE_PATH = ROOT_DIR / 'neo_library_v1' / 'user_data' / 'saved_characters.json'
