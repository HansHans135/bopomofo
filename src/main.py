"""
The main module of the bot.
"""

import tracemalloc

import discord


class Bot(discord.AutoShardedBot):
    """
    The main class of the bot.
    """

    def __init__(self) -> None:
        self._client_ready = False
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        for k, v in self.load_extension("src.cogs", recursive=True, store=True).items():
            if v is True:
                print(f"Loaded extension {k}")
            else:
                print(f"Failed to load extension {k} with exception: {v}")

    async def on_shard_connect(self, shard_id: int) -> None:
        """
        The event that is triggered when a shard connected.

        :param shard_id: The shard ID.
        :type shard_id: int
        """
        print(f"Shard {shard_id} connected.")

    async def on_shard_ready(self, shard_id: int) -> None:
        """
        The event that is triggered when a shard is ready.

        :param shard_id: The shard ID.
        :type shard_id: int
        """
        print(f"Shard {shard_id} ready.")

    async def on_shard_resumed(self, shard_id: int) -> None:
        """
        The event that is triggered when a shard resumed.

        :param shard_id: The shard ID.
        :type shard_id: int
        """
        print(f"Shard {shard_id} resumed.")

    async def on_shard_disconnect(self, shard_id: int) -> None:
        """
        The event that is triggered when a shard disconnected.

        :param shard_id: The shard ID.
        :type shard_id: int
        """
        print(f"Shard {shard_id} disconnected.")

    async def on_start(self) -> None:
        """
        The event that is triggered when the bot started.
        This method is called with the first on_ready event only.
        """
        print(
            f"""
-------------------------
Logged in as: {self.user.name}#{self.user.discriminator} ({self.user.id})
Shards Count: {self.shard_count}
Memory Usage: {tracemalloc.get_traced_memory()[0] / 1024 ** 2:.2f} MB
 API Latency: {self.latency * 1000:.2f} ms
Guilds Count: {len(self.guilds)}
-------------------------
"""
        )

    async def on_ready(self) -> None:
        """
        The event that is triggered when the bot is ready.
        """
        if self._client_ready:
            return
        await self.on_start()
        self._client_ready = True

    async def close(self) -> None:
        """
        Closes the bot.
        """
        print("Closing the bot...")
        await super().close()

    def run(self, token: str) -> None:
        """
        Starts the bot.
        """
        print("Starting the bot...")
        super().run(token)
