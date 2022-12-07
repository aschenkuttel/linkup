import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ext import tasks
import asyncio


class Searching(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = bot.queue
        self.user_sessions = {}
        self.sessions = {}

        for game_key, title in self.bot.config['supported_games'].items():
            description = f"Joins the queue for {title}"
            command = app_commands.Command(name=game_key, description=description, callback=self.game) # noqa
            self.bot.tree.add_command(command)

        self.engine.start()

    @tasks.loop(seconds=5)
    async def engine(self):
        async for session in self.bot.queue.gather_sessions():
            response = await session.initialize()

            if response is not True:
                self.queue.vip(session.region, session.game, response)
            else:
                self.sessions[session.id] = session
                ids = [session.first_user.id, session.second_user.id]

                for user_id in ids:
                    self.user_sessions[user_id] = session
                    self.user_sessions[user_id] = session

                message = "session {} between {} - {} initialized"
                self.bot.logger.debug(message.format(session.id, *ids))

    @engine.before_loop
    async def before_engine(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        # ignores server and bot messages
        if message.guild is not None or message.author.bot:
            return

        # ignores ctx commands from admin
        if message.content.startswith("#") or message.content.startswith("/"):
            return

        session = self.user_sessions.get(message.author.id)

        if session is None:
            await message.author.send("you're currently not in an active session")
            return

        partner = session.get_partner(message.author.id)
        content = f"**{message.author.name}:** {message.content}"

        try:
            await partner.send(content)
        except Exception as error:
            self.bot.logger.error(error)
            # bot couldn't reach the partner anymore
            await self.end_session(session, partner)

    async def end_session(self, session, user):
        self.sessions.pop(session.id)
        self.user_sessions.pop(session.first_user.id)
        self.user_sessions.pop(session.second_user.id)
        await session.end(user)

    async def get_region(self, user_id):
        response = await self.bot.fetchone('SELECT region FROM user_config WHERE id = $1', user_id)
        return response if response is None else response[0]

    async def game(self, interaction: Interaction):
        region = await self.get_region(interaction.user.id)

        if region is None:
            await interaction.response.send_message("missing region")
            return

        session = self.user_sessions.get(interaction.user.id)
        if session is not None:
            await self.end_session(session, interaction.user.id)

        game_key = interaction.command.name
        game_name = self.bot.config['supported_games'][game_key]
        response = self.queue.add(region, game_key, interaction.user)

        if response is True:
            await interaction.response.send_message(f"you're in queue for: {game_name}")
            return
        else:
            await interaction.response.send_message(f"you're no longer in queue for {game_name}")
            return

    @app_commands.command(name="leave", description="Leaves queue")
    async def leave(self, interaction: Interaction):
        response = self.bot.queue.remove_user(interaction.user)
        if response is True:
            await interaction.response.send_message(f"you're no longer in queue")
        else:
            await interaction.response.send_message(f"you never were in queue")

    @app_commands.command(name="end", description="Ends current session")
    async def end(self, interaction: Interaction):
        session = self.user_sessions.get(interaction.user.id)

        if session is not None:
            await self.end_session(session, interaction.user.id)
            await interaction.response.send_message("session successfully ended")
        else:
            await interaction.response.send_message("you're currently not in an active session")


async def setup(bot):
    await bot.add_cog(Searching(bot))
