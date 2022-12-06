import json
import aiosqlite
import discord
from discord.ext import commands
from discord import app_commands
from glob import glob
from utils import Queue


class LinkUp(commands.Bot):
    def __init__(self):
        custom_intents = discord.Intents.default()
        super().__init__(intents=custom_intents, command_prefix="#")
        self.config = json.load(open("config.json"))
        self.queue = Queue(self.config)
        print(self.queue)
        self.db = None

    async def setup_hook(self):
        self.db = await aiosqlite.connect('config.db')
        await self.execute('CREATE TABLE IF NOT EXISTS user_config (id BIGINT PRIMARY KEY, region TEXT)')
        await self.setup_cogs()

        guild_id = discord.Object(id=918204250893475900)
        self.tree.copy_global_to(guild=guild_id)
        await self.tree.sync(guild=guild_id)

        self.loop.create_task(self.queue.run())
        print("LinkUp connected")

    async def execute(self, query, *args):
        await self.db.execute(query, args)
        await self.db.commit()

    async def fetch(self, query, *args):
        cursor = await self.db.execute(query, args)
        return await cursor.fetchall()

    async def fetchone(self, query, *args):
        cursor = await self.db.execute(query, args)
        return await cursor.fetchone()

    async def setup_cogs(self):
        for file in glob("cogs/*.py"):
            try:
                filename = file.replace("\\", ".")[:-3]
                a = await self.load_extension(filename)
            except commands.ExtensionNotFound:
                print(f"module {file} not found")

    def initialize(self):
        self.run(self.config['TOKEN'])


bot = LinkUp()
bot.initialize()
