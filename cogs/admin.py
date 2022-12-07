from discord.ext import commands
from typing import Optional, Literal
import discord


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx, guild: discord.Object, spec: Optional[Literal["~", "*", "^"]] = None):
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=guild)
            synced = await ctx.bot.tree.sync(guild=guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=guild)
            await ctx.bot.tree.sync(guild=guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the guild.'}")
        return


async def setup(bot):
    await bot.add_cog(Admin(bot))
