from pathlib import Path

from .utils import setting

COMMAND_PREFIX = setting("COMMAND_PREFIX", default=".")

TOKEN = setting("BOT_TOKEN", required=True)

SAVE_DATA_FILE = setting("SAVE_DATA_FILE", default=Path.cwd() / "src" / "save_data.json", _type=Path)
