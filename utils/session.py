import discord


class Session:
    def __init__(self, bot, first_user, second_user, region, game):
        self.bot = bot
        self.id = 0
        self.first_user = first_user
        self.second_user = second_user
        self.region = region
        self.game = game

    def get_partner(self, user_id):
        return self.second_user if user_id == self.first_user.id else self.first_user

    def entry_embed(self):
        welcome = "Welcome to your gaming session. Simply write in this chat and any message besides" \
                  "commands will be relayed to your session partner. Be kind!"
        embed = discord.Embed(title=f"User: {self.first_user.name} - {self.second_user.name}", description=welcome)
        footer = "End your session with /end"
        embed.set_footer(text=footer)
        return embed

    async def initialize(self):
        embed = self.entry_embed()

        for user in (self.first_user, self.second_user):
            try:
                await user.send(embed=embed)
            except Exception as error:
                self.bot.logger.error(f"session init {user.id}: {error}")

                if user == self.first_user:
                    return self.second_user
                else:
                    return self.first_user

        query = "INSERT INTO session (first_user_id, second_user_id, region, game) " \
                "VALUES ($1, $2, $3, $4)"

        # cursor = await self.bot.db.execute(query, [self.first_user.id, self.second_user.id, self.region, self.game])
        cursor = await self.bot.db.execute(query, [20, 20, self.region, self.game])
        self.id = cursor.lastrowid
        return True

    async def end(self, user):
        try:
            partner = self.get_partner(user.id)
            end = f"{user.name} closed the session or was unreachable."
            embed = discord.Embed(title=f"User: {self.first_user.name} - {self.second_user.name}", description=end)
            await partner.send(embed=embed)
        except Exception as error:
            self.bot.logger.error(error)
