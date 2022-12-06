from discord.ext import commands
from discord import app_commands, Interaction


class Searching(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = bot.queue

        for game in self.bot.config['supported_games']:
            command = app_commands.Command(name=game, description="Game", callback=self.game)
            self.bot.tree.add_command(command)

    async def get_region(self, user_id):
        response = await self.bot.fetchone('SELECT region FROM user_config WHERE id = $1', user_id)
        return response if response is None else response[0]

    async def game(self, interaction: Interaction):
        region = await self.get_region(interaction.user.id)
        if region is None:
            await interaction.response.send_message("missing region")
            return

        response = self.queue.add(region, "league", interaction.user)

        if response is True:
            await interaction.response.send_message("added")
        else:
            await interaction.response.send_message("you are already in queue")


async def setup(bot):
    await bot.add_cog(Searching(bot))
