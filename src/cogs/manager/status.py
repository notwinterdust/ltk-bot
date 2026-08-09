import json
from pathlib import Path
import discord
from discord.ext import commands

channel_id = 123456789012345678
on_name = "STATUS:🟢"
off_name = "STATUS:🔴"
status_file = Path("status.json")


def load_status():
    if status_file.exists():
        try:
            return json.loads(status_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_status(data):
    status_file.write_text(json.dumps(data), encoding="utf-8")


class StatusToggle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_status()

    def is_admin():
        async def predicate(ctx):
            return ctx.guild is not None and ctx.author.guild_permissions.administrator
        return commands.check(predicate)

    @commands.command(name="on")
    @is_admin()
    async def on(self, ctx):
        channel = self.bot.get_channel(channel_id)
        await channel.edit(name=on_name)
        self.data["is_on"] = True
        save_status(self.data)
        await ctx.message.delete()
        msg = await ctx.send(f"channel set to `{on_name}`")
        await msg.delete(delay=5)

    @commands.command(name="off")
    @is_admin()
    async def off(self, ctx):
        channel = self.bot.get_channel(channel_id)
        await channel.edit(name=off_name)
        self.data["is_on"] = False
        save_status(self.data)
        await ctx.message.delete()
        msg = await ctx.send(f"channel set to `{off_name}`")
        await msg.delete(delay=5)

    @on.error
    @off.error
    async def on_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            try:
                await ctx.message.delete()
            except discord.HTTPException:
                pass
            msg = await ctx.send("you need administrator permission to use this command")
            await msg.delete(delay=5)
        else:
            raise error


async def setup(bot):
    await bot.add_cog(StatusToggle(bot))