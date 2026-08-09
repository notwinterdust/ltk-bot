import asyncio
import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("token")
prefix = os.getenv("prefix", "!")
cogs_directory = Path(__file__).parent / "cogs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
log = logging.getLogger("bot")


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(command_prefix=prefix, intents=intents)

    async def setup_hook(self):
        await self.load_cogs()
        synced = await self.tree.sync()
        log.info("Synced %d application command(s).", len(synced))

    async def load_cogs(self):
        """Recursively discover and load every cog in cogs/."""
        if not cogs_directory.exists():
            log.warning("Cogs directory '%s' does not exist, skipping.", cogs_directory)
            return

        for path in sorted(cogs_directory.rglob("*.py")):
            if path.name.startswith("_"):
                continue

            relative = path.relative_to(cogs_directory.parent).with_suffix("")
            extension = ".".join(relative.parts)

            try:
                await self.load_extension(extension)
                log.info("Loaded cog: %s", extension)
            except commands.ExtensionError:
                log.exception("Failed to load cog: %s", extension)

    async def on_ready(self):
        log.info("Logged in as %s (ID: %s)", self.user, self.user.id)
        log.info("Connected to %d guild(s).", len(self.guilds))


async def main():
    if not token:
        raise RuntimeError(
            "token is not set. Copy .env.example to .env and fill the token value"
        )

    bot = Bot()
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
