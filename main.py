import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import sys


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

bot = commands.Bot(command_prefix= '!', intents=intents)



@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(status=discord.Status.online,
         activity=discord.Activity(type=discord.ActivityType.listening, name="your commands!" )
    )
    print(f"{bot.user} is online!")


async def load_extensions():
    cog_files = ["Moderation", "Greetings", "Music"]  # Add your cog filenames here without the .py extension
    for extension in cog_files:
        module_path = f"cogs.{extension}"
        try:
            await bot.load_extension(f'cogs.{module_path}')
            print(f"Loaded extension: {module_path}")
        except Exception as e:
            print(f"Failed to load extension {module_path}. Error: {e}", file=sys.stderr)



async def main():
    await load_extensions()

    async with bot:
        await bot.start(TOKEN)


if __name__ == '__main__':
    asyncio.run(main())
