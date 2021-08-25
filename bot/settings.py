import os
import pathlib

COMMAND_PREFIX = "."

TOKEN = os.environ.get("BOT_TOKEN")

SAVE_DATA_FILE = pathlib.Path.cwd() / "bot" / "save_data.json"
