from pathlib import Path
from discord import Color

from .utils import setting

COMMAND_PREFIX = setting("COMMAND_PREFIX", default=".")

TOKEN = setting("BOT_TOKEN", required=True)

SAVE_DATA_FILE = setting("SAVE_DATA_FILE", default=Path.cwd() / "save_data.json", _type=Path)

EMBED_COLOR = Color.orange()

# TODO change this back
MAX_TEAM_SIZE = setting("MAX_TEAM_SIZE", default=3, _type=int)
