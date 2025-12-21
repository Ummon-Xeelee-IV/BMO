from discord.ext import commands
from rapidfuzz import fuzz

class Automation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.forbidden_words = ["badword1", "badword2"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower()
        
        # Smart Fuzzy Check
        for word in self.forbidden_words:
            if fuzz.partial_ratio(word, content) > 85:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, your message was flagged by the smart filter.", delete_after = 5)
                return

        await self.bot.process_commands(message)

async def setup(bot):

    await bot.add_cog(Automation(bot))
