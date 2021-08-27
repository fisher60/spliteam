import json
from dataclasses import dataclass
from typing import Any

from discord import VoiceChannel
from discord.ext.commands import Bot, Context, Cog, group, command

from ..settings import SAVE_DATA_FILE


@dataclass
class SplitConfig:
    """
    Config is read from SAVE_DATA_FILE when this class in instantiated.

    When a value is updated, this will be written to the file.
    """
    lobby_channel: int

    def __init__(self):
        self.__ensure_file_exits()
        self.__sync_with_file()

    @staticmethod
    def __ensure_file_exits() -> None:
        """If the file is not created, create it."""
        if not SAVE_DATA_FILE.exists():
            SAVE_DATA_FILE.write_text("{}")

    def __sync_with_file(self):
        """Sync this dataclass with the file content"""
        with open(SAVE_DATA_FILE) as f:
            data = json.loads(f.read())

        for key in data:
            setattr(self, key, data[key])

    def __write_file(self) -> None:
        """Write the current dataclass to SAVE_DATA_FILE"""
        with open(SAVE_DATA_FILE, "w") as f:
            json.dump(vars(self), f)

    def __setattr__(self, key: str, value: Any) -> None:
        """Over write the set attr to also write out changes to a file."""
        self.__dict__[key] = value
        self.__write_file()


class Split(Cog):
    """Utilities for splitting up teams."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.data = SplitConfig()

    @group()
    async def config(self, ctx: Context):
        pass

    @config.command()
    async def channel(self, ctx: Context, lobby: VoiceChannel) -> None:
        if not SAVE_DATA_FILE.exists():
            async with aopen(SAVE_DATA_FILE, "w") as f:
                await f.write("{}")

        async with aopen(SAVE_DATA_FILE, "r") as f:
            config_data_raw = await f.read()
        config_data = json.loads(config_data_raw)

        config_data["lobby_channel"] = lobby.id

        async with aopen(SAVE_DATA_FILE, "w") as f:
            await f.write(json.dumps(config_data))

        await ctx.send(f"Channel config {lobby}")


def setup(bot: Bot) -> None:
    bot.add_cog(Split(bot))
