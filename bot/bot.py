from discord.ext.commands import Bot


class TeamBot(Bot):
    @staticmethod
    async def on_ready() -> None:
        """Runs when the bot is connected."""
        print('Awaiting...')
        print("Bot Is Ready For Commands")
