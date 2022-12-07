from discord.ext import commands
from discord import app_commands
import discord
from utils import Region


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    set_group = app_commands.Group(name="set", description="config")

    @set_group.command(name="region", description="Sets your global region")
    async def set_region(self, interaction: discord.Interaction, region: Region):
        if region is None:
            await interaction.response.send_message("Invalid Region")
            return

        response = await self.bot.fetchone('SELECT region FROM user_config WHERE id = $1', interaction.user.id)

        if response is None or response[0] != region:
            # we have to use this monstrosity since sqlite3 on ubuntu
            # doesn't support on conflict update, don't ask me why
            query = 'INSERT OR REPLACE INTO user_config (id, region) ' \
                    'VALUES ($1, COALESCE($2, (SELECT region FROM user_config WHERE id = $1)))'
            await self.bot.execute(query, interaction.user.id, region)
            await interaction.response.send_message(f"{region} is now your region")
        else:
            await interaction.response.send_message(f"{region} is already your region")


async def setup(bot):
    await bot.add_cog(Config(bot))
