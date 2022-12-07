import collections
from utils.session import Session


class Queue:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

        # user currently in queue
        self.user_cache = {}

        # game queues per region
        self._queues = {}

        for region in self.config['supported_regions']:
            regional_container = self._queues[region] = {}

            for game in self.config['supported_games']:
                regional_container[game] = collections.deque()

    async def gather_sessions(self):
        for region in self.config['supported_regions']:
            for game in self.config['supported_games']:
                iterable = self._queues[region][game]
                if len(iterable) >= 2:
                    first_user_id = iterable.popleft()
                    second_user_id = iterable.popleft()

                    first_user_data = self.user_cache.get(first_user_id)
                    second_user_data = self.user_cache.get(second_user_id)

                    if None in (first_user_data, second_user_data):
                        continue

                    first_user = first_user_data[-1]
                    second_user = second_user_data[-1]

                    session = Session(self.bot, first_user, second_user, region, game)
                    yield session
                    break

    def in_queue(self, user_id):
        return self.user_cache.get(user_id) is not None

    def add(self, region, game, user):
        iterable = self._queues[region][game]

        if self.in_queue(user.id):
            in_same_game_queue = user.id in iterable
            self._remove(region, game, user)

            # if user is already in that queue we only delete
            if in_same_game_queue:
                return False

        iterable.append(user.id)
        self.user_cache[user.id] = (region, game, user)
        return True

    def _remove(self, region, game, user):
        try:
            self._queues[region][game].remove(user.id)
            self.user_cache.pop(user.id)
            return True
        except ValueError:
            return False

    def remove_user(self, user):
        queue_data = self.user_cache.get(user.id)

        if queue_data is None:
            return False

        region, game = queue_data
        return self._remove(region, game, user)

    def vip(self, region, game, user):
        iterable = self._queues[region][game]

        iterable.append(user.id)
        self.user_cache[user.id] = (region, game, user)
        return True
