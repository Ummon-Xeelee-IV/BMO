import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import sys
from database import Database

db = Database()

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
    print(f"--- BMO ONLINE ---")
    print(f"Logged in as: {bot.user}")
    print(f"ID: {bot.user.id}")
    print(f"------------------")


async def load_extensions():
    cog_files = ["Moderation_2", "Utility", "Logging", "Automation"]  # Add your cog filenames here without the .py extension
    for extension in cog_files:
        module_path = f"cogs.{extension}"
        try:
            await bot.load_extension(module_path)
            print(f"Loaded extension: {module_path}")
        except Exception as e:
            print(f"Failed to load extension {module_path}. Error: {e}", file=sys.stderr)



async def main():
    await load_extensions()

    async with bot:
        await bot.start(TOKEN)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down BMO...")
    except Exception as e:
        print(f"Bot terminated with an error: {e}")