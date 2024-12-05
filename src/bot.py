from discord.ext.commands import Bot, CommandError, Context, MissingPermissions


class TeamBot(Bot):
    @staticmethod
    async def on_ready() -> None:
        """Runs when the bot is connected."""
        print('Awaiting...')
        print("Bot Is Ready For Commands")

    async def on_command_error(self, ctx: Context, exception: CommandError) -> None:
        if isinstance(exception, MissingPermissions):
            await ctx.send("> You canne do that, Captain or Admin only baws.", delete_after=5)
