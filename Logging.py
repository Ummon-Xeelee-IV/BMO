import discord
from discord.ext import commands
import datetime

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def emit_log(self, guild, embed):
        """Helper method to find the log channel and send the embed."""
        # For this version, we search for a channel by name.
        log_channel = discord.utils.get(guild.text_channels, name = "mod=logs")

        if log_channel:
            try:
                await log_channel.send(embed = embed)
            except discord.Forbidden:
                print(f"Missing permision to post in #mod-logs in {guild.name}")


    # Example of an automatic listener: Logs deleted messages
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        embed = discord.Embed(
            title="Message Deleted",
            description=f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Content", value=message.content or "[No text content]", inline=False)
        embed.set_footer(text=f"User ID: {message.author.id}")
        
        await self.emit_log(message.guild, embed)

async def setup(bot):

    await bot.add_cog(Logging(bot))
