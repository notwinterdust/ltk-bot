import discord
from discord import app_commands
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @commands.hybrid_command(name="ping", description="test")
    async def ping(self, ctx: commands.Context):
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f"`{latency_ms}ms`")

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))