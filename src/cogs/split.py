import json
import random
from dataclasses import dataclass, asdict
from typing import Any, Optional

from discord import VoiceChannel, Embed, Forbidden, Role, AllowedMentions, HTTPException
from discord.ext.commands import Bot, Context, Cog, group, BadArgument, CommandError, command, MissingPermissions

from ..settings import SAVE_DATA_FILE, EMBED_COLOR


@dataclass
class SplitConfig:
    """
    Config is read from SAVE_DATA_FILE when this class in instantiated.

    When a value is updated, this will be written to the file.
    """
    lobby_channel_id: Optional[int] = None
    captain_role_id: Optional[int] = None
    team_one_channel_id: Optional[int] = None
    team_two_channel_id: Optional[int] = None
    minimum_team_size: int = 3

    def __init__(self) -> None:
        self.__ensure_file_exits()
        self.__sync_with_file()

    def __ensure_file_exits(self) -> None:
        """If the file is not created, create it."""
        if not SAVE_DATA_FILE.exists():
            with open(SAVE_DATA_FILE, "+w") as f:
                json.dump(asdict(self), f)

    def __sync_with_file(self) -> None:
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

    def cog_check(self, ctx: Context) -> bool:
        if ctx.author.guild_permissions.administrator:
            return True

        if self.data.captain_role_id:
            captain_role = ctx.guild.get_role(self.data.captain_role_id)
            if captain_role in ctx.author.roles:
                return True

        raise MissingPermissions("User doesn't have Admin permissions or the Captain role.")

    @property
    def lobby_channel(self) -> Optional[VoiceChannel]:
        """Get the channel id from the settings and construct the VoiceChannel object if one is set."""
        if self.data.lobby_channel_id:
            return self.bot.get_channel(self.data.lobby_channel_id)

    @property
    def team_one_channel(self) -> Optional[VoiceChannel]:
        """Get the channel id from the settings and construct the VoiceChannel object if one is set."""
        if self.data.team_one_channel_id:
            return self.bot.get_channel(self.data.team_one_channel_id)

    @property
    def team_two_channel(self) -> Optional[VoiceChannel]:
        """Get the channel id from the settings and construct the VoiceChannel object if one is set."""
        if self.data.team_two_channel_id:
            return self.bot.get_channel(self.data.team_two_channel_id)

    @group(aliases=["settings", "conf"])
    async def config(self, ctx: Context) -> None:
        """Display the current config."""

        if not ctx.subcommand_passed:
            embed = Embed(title="SplitTeam Config", colour=EMBED_COLOR)

            lobby = self.lobby_channel
            embed.add_field(name="Lobby", value=lobby.mention if lobby else "Not Configured")

            team_one = self.team_one_channel
            embed.add_field(name="Team One", value=team_one.mention if team_one else "Not Configured")

            team_two = self.team_two_channel
            embed.add_field(name="Team Two", value=team_two.mention if team_two else "Not Configured")

            embed.add_field(name="Minimum Team Size", value=str(self.data.minimum_team_size))

            role = ctx.guild.get_role(self.data.captain_role_id)
            embed.add_field(name="Captain Role", value=role.mention if role else "Not Configured")

            await ctx.send(embed=embed)

    @config.command()
    async def lobby(self, ctx: Context, lobby: VoiceChannel) -> None:
        """Set the lobby channel to be used for splitting."""
        self.data.lobby_channel_id = lobby.id
        await ctx.send(f"> Lobby set to {lobby.mention}", delete_after=5)

    @config.command(aliases=["one", "team1", "t1"])
    async def team_one(self, ctx: Context, channel: VoiceChannel) -> None:
        """Set the voice channel for team one."""
        self.data.team_one_channel_id = channel.id
        await ctx.send(f"> Team One set to {channel.mention}", delete_after=5)

    @config.command(aliases=["two", "team2", "t2"])
    async def team_two(self, ctx: Context, channel: VoiceChannel) -> None:
        """Set the voice channel for team two."""
        self.data.team_two_channel_id = channel.id
        await ctx.send(f"> Team Two set to {channel.mention}", delete_after=5)

    @lobby.error
    @team_two.error
    @team_one.error
    async def channel_error(self, ctx: Context, error: CommandError) -> None:
        if isinstance(error, BadArgument):
            await ctx.send("> Please make sure you are tagging a **Voice Channel**.")
        else:
            raise error

    @config.command(aliases=["min_size", "min"])
    async def minimum_team_size(self, ctx: Context, min_team_size: int) -> None:
        """Set the minimum players per team."""
        if min_team_size <= 0:
            await ctx.send("> Idk chief, this seems kinda weird. (*Please chose a number greater than 0*()", delete_after=5)
            return

        self.data.minimum_team_size = min_team_size
        await ctx.send(f"> Minimum team size set to {min_team_size}", delete_after=5)

    @config.command(aliases=["cap", "leader", "role"])
    async def captain_role(self, ctx: Context, role: Role) -> None:
        """Set the captain role."""
        self.data.captain_role_id = role.id
        await ctx.send(f"> Set captain role to {role.mention}", delete_after=5, allowed_mentions=AllowedMentions(roles=False))

    @command()
    async def split(self, ctx: Context) -> None:

        # Get a list of invalid settings and display them to the user if there is
        # at least one invalid setting before trying to split.
        invalid_settings = []
        if self.lobby_channel is None:
            invalid_settings.append("Lobby")
        if self.team_one_channel is None:
            invalid_settings.append("Team One")
        if self.team_two_channel is None:
            invalid_settings.append("Team Two")

        if len(invalid_settings) > 0:
            await ctx.send(f"> You must configure the following settings before a split: {', '.join(invalid_settings)}", delete_after=5)
            return

        # FIXME: This list may be incomplete. See issue #5
        assert self.lobby_channel is not None
        lobby_members = self.lobby_channel.members

        if len(lobby_members) // 2 < self.data.minimum_team_size:
            await ctx.send("> There is not enough members to meet the minimum team size", delete_after=5)
            return

        # Our randomization strategy is using random.shuffle then splitting the list in the middle
        random.shuffle(lobby_members)

        team_one, team_two = lobby_members[len(lobby_members) // 2:], lobby_members[:len(lobby_members) // 2]

        embed = Embed(title="Teams", colour=EMBED_COLOR)
        embed.add_field(name="__**Team 1**__", value='\n'.join([user.mention for user in team_one]))
        embed.add_field(name="__**Team 2**__", value='\n'.join([user.mention for user in team_two]))
        await ctx.send(embed=embed)

        teams = (team_one, team_two)
        channels = (self.team_one_channel, self.team_two_channel)

        for team, channel in zip(teams, channels):
            for member in team:
                try:
                    await member.move_to(channel, reason="Team split")
                except Forbidden:
                    await ctx.send("> It feels like I don't have the power to move people. Missing Permissions.")
                    return
                except HTTPException as e:
                    if e.code == 40032: # target user not connected to voice
                        pass
                    else:
                        raise e


def setup(bot: Bot) -> None:
    bot.add_cog(Split(bot))
