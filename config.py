from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SFX_DIR = DATA_DIR / "sfx"
MINIBAR_DIR = BASE_DIR / "minibar"
COMMON_DIR = BASE_DIR / "common"
THEMES_DIR = DATA_DIR / "themes"
LOCALE_DIR = DATA_DIR / "localization"
LOCALIZATION_FILE = LOCALE_DIR / "translate.json"
LOCALE = "ru"