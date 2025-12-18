import discord
from discord.ext import commands

class Utility(commands.Cog):
    """General utility commands and passive event listeners."""
    def __init__(self, bot):
        self.bot = bot
        self.forbidden_words = ["38 W B", "fragile_word_1", "another_bad_word"] # Load this from a JSON file in a real app

    # --- Slash Command: /greet ---
    # Slash commands must also be defined inside a Cog
    @commands.hybrid_command(description="Sends a friendly greeting.")
    async def greet(self, ctx):
        await ctx.send(f"Hello there, {ctx.author.mention}", ephemeral=True)


    # --- Event Listener: on_message (Profanity Filter) ---
    @commands.Cog.listener() # Use the decorator to register an event listener inside a Cog
    async def on_message(self, message):
        # Prevent bot from replying to itself
        if message.author.bot:
            return
            
        content = message.content.lower().strip()

        # Check for forbidden words
        if any(word in content for word in self.forbidden_words):
            try:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention}, your message was removed for containing forbidden content.", 
                    delete_after=5
                )
                return 
            except discord.Forbidden:
                print(f"Bot missing permissions to delete message in {message.channel}.")
                await self.bot.process_commands(message)


def setup(bot):
    bot.add_cog(Greetings(bot))






