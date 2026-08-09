# role assignement and deassignement using emoji reactions
import discord
from discord.ext import commands

channel_id = 123456789012345678     # channel the message lives in
msg_id = 123456789012345678     # the message users react to

role_map: dict[str, int] = {
    "emojiId": roleId, # for emojiId u can set it as a default unicode emoji if its not a server custom one
}


class ReactionRoles(commands.Cog):8

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def _emoji_key(emoji: discord.PartialEmoji) -> str:
        return str(emoji.id) if emoji.id else str(emoji)

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            print(f"[cogs.member.role] Could not find channel {channel_id}")
            return

        guild = channel.guild

        try:
            message = await channel.fetch_message(msg_id)
        except (discord.NotFound, discord.Forbidden) as e:
            print(f"[cogs.member.role] Could not fetch message {msg_id}: {e}")
            return

        existing = {self._emoji_key(r.emoji) for r in message.reactions}
        for key in role_map:
            if key in existing:
                continue
            try:
                emoji_to_add = key
                if key.isdigit():
                    custom = self.bot.get_emoji(int(key))
                    if custom is None:
                        print(f"[cogs.member.role] Unknown custom emoji ID {key}, skipping")
                        continue
                    emoji_to_add = custom
                await message.add_reaction(emoji_to_add)
            except discord.HTTPException as e:
                print(f"[cogs.member.role] Failed to add reaction {key}: {e}")

        print("[cogs.member.role] Synced reactions on target message.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self._handle_reaction(payload, adding=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self._handle_reaction(payload, adding=False)

    async def _handle_reaction(
        self, payload: discord.RawReactionActionEvent, adding: bool
    ) -> None:
        if payload.message_id != msg_id:
            return
        if self.bot.user and payload.user_id == self.bot.user.id:
            return

        key = self._emoji_key(payload.emoji)
        role_id = role_map.get(key)
        if role_id is None:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        role = guild.get_role(role_id)
        if role is None:
            print(f"[cogs.member.role] Role {role_id} not found in guild")
            return

        member = payload.member or guild.get_member(payload.user_id)
        if member is None:
            try:
                member = await guild.fetch_member(payload.user_id)
            except discord.NotFound:
                return

        if member.bot:
            return

        try:
            if adding:
                if role not in member.roles:
                    await member.add_roles(role, reason="Reaction role")
            else:
                if role in member.roles:
                    await member.remove_roles(role, reason="Reaction role removed")
        except discord.Forbidden:
            print(f"[cogs.member.role] Missing permission to assign role {role_id}")


async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionRoles(bot))