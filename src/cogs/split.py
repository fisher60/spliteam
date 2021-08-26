import json

from aiofiles import open as aopen
from discord import VoiceChannel
from discord.ext.commands import Bot, Context, Cog, group


from ..settings import SAVE_DATA_FILE


class Split(Cog):
    """Utilities for splitting up teams."""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

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
