import collections
import asyncio


class Queue:
    def __init__(self, config):
        self.config = config

        # user currently in queue
        self.user_cache = {}

        # game queues per region
        self._queues = {}

        for region in self.config['supported_regions']:
            regional_container = self._queues[region] = {}

            for game in self.config['supported_games']:
                regional_container[game] = collections.deque()

    async def run(self):
        for region in self.config['supported_regions']:
            for game in self.config['supported_games']:
                iterable = self._queues[region][game]
                if len(iterable) >= 2:
                    pass

        await asyncio.sleep(5)

    def in_queue(self, user_id):
        return bool(self.user_cache.get(user_id))

    def add(self, region, game, user):
        iterable = self._queues[region][game]

        if self.in_queue(user.id):
            if user in iterable:
                return self.remove
            else:
                return False
        else:
            iterable.append(user)
            self.user_cache[user.id] = True
            return True

    def remove(self, region, game, user):
        if not self.in_queue(user.id):
            return False
        else:
            try:
                self._queues[region][game].remove(user)
                return True
            except ValueError:
                return False
