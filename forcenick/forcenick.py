from redbot.core import commands, checks, modlog, Config
import discord
from typing import Optional
from datetime import datetime


class ForceNick(commands.Cog):
    """ForceNick"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=190420201535, force_registration=True)
        standard = {"modlog": True, "nick": "CHANGEME", "dm": False}
        self.config.register_guild(**standard)

    async def initialize(self):
        await self.register_casetypes()
        await self.bot.send_to_owners(
            "Forcenick is outdated and will be removed in December 2020. Use NickNamer instead."
        )

    @staticmethod
    async def register_casetypes():
        forcechange_case = {
            "name": "forcechange",
            "default_setting": True,
            "image": ":pencil2:",
            "case_str": "Nickname force-changed",
        }
        try:
            await modlog.register_casetype(**forcechange_case)
        except RuntimeError:
            pass

    @checks.mod()
    @commands.command()
    async def forcenick(self, ctx, user: discord.Member, *, reason: Optional[str]):
        """Forcibly change a user's nickname"""
        if not reason:
            reason = f"Nickname force-changed"
        try:
            await user.edit(nick=await self.config.guild(ctx.guild).nick())
            await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
            if await self.config.guild(ctx.guild).modlog() == True:
                await modlog.create_case(
                    self.bot,
                    ctx.guild,
                    datetime.now(),
                    "forcechange",
                    user,
                    moderator=ctx.author,
                    reason=reason,
                    channel=ctx.channel,
                )
            if await self.config.guild(ctx.guild).dm():
                await user.send(
                    f"Your nickname on ``{ctx.guild.name}`` has been force-changed by a moderator."
                )
        except discord.errors.Forbidden:
            await ctx.send("Missing permissions.")

    @checks.admin()
    @commands.group()
    async def forcenickset(self, ctx):
        """Forcenick settings"""
        pass

    @forcenickset.command()
    async def name(self, ctx, *, name: str):
        """Set the default name that will be applied when using ``[p]forcenick``"""
        if len(name) < 33 and len(name) > 1:
            await self.config.guild(ctx.guild).nick.set(name)
            await ctx.send(f"Standard Nickname set to ``{name}``.")

    @forcenickset.command()
    async def modlog(self, ctx, true_or_false: bool):
        """Set if you would like to create a modlog entry everytime ``[p]forcenick`` is used."""
        await self.config.guild(ctx.guild).modlog.set(true_or_false)
        await ctx.send(f"Modlog entries set to {true_or_false}.")

    @forcenickset.command()
    async def dm(self, ctx, true_or_false: bool):
        """Set if you would like the bot to DM the user who's nickname was force-changed."""
        await self.config.guild(ctx.guild).dm.set(true_or_false)
        await ctx.send(f"Sending a DM set to {true_or_false}.")
