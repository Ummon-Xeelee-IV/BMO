import discord
from discord.ext import commands
import asyncio
import sys



class Music(commands.Cog):
    """Voice channel control and music playback commands"""

    def __init__(self, bot):
        self.bot = bot
        self.queues = {}


    def get_check_queue_callback(self, ctx, guild_id):
        def check_queue(error):
            if error:
                print(f"Player error in guild {guild_id}: {error}", file=sys.stderr)
                return
            
            async def play_next():
                if guild_id in self.queues and self.queues[guild_id]:
                    voice = ctx.voice_client
                    next_source = self.queues[guild_id].pop(0)

                    voice.play(next_source, after=self.get_check_queue_callback(ctx, guild_id))
                    await ctx.send(f"Now Playing: {next_source.title} (Queued track)")

                elif guild_id in self.queues:
                    del self.queues[guild_id]
                    await ctx.send("Queue finished. Disconnecting in 60 seconds...", delere_after=60)
                    await asyncio.sleep(60)
                    if ctx.voice_client and not ctx.voice_client.is_playing():
                        await ctx.voice_client.disconnect()

            self.bot.loop.call_soon_threadsafe(self.bot.loop.create_task, play_next())
        return check_queue



# !join command
@commands.command(help="Makes the bot join the voice channel you are in in.")
@commands.has_permissions(connect=True)
async def join(self, ctx):
    if ctx.author.voice is None:
        return await ctx.send("You must be in a voice channel to use this command")
    
    if ctx.voice_client is not None:
        if ctx.voice_client.channel == ctx.author.voice.cheannel:
            return await ctx.send("I am already in youe voice channel.")
        else:
            await ctx.voice_client.move_to(ctx.author.voice.channel)
            return await ctx.send(f"Move to {ctx.author.voice.channel.name}")

    channel = ctx.author.voice.channel
    await channel.connect()
    await ctx.send(f"Joined {channel.name}! :)")



# !leave command
@commands.command(help="makes the bot leave the current voice channel.")
async def leave(self, ctx):
    if ctx.voice_client:
        guild_id = ctx.guild_id
        if guild_id in self.queues:
            del self.queues[guild_id]

        await ctx.guild.voice_client.disconnect()
        await ctx.send("I left the voice channel.")
    else:
        await ctx.send("I am not connected to a voice channel.") 



# play and queue commands
@commands.command(help="Plays a file in the queue.")
async def play(self, ctx, *, arg):
    if ctx.author.voice is None:
        return await ctx.send("You are not connected to a voice channel. You must be in a voice channel to run this command.")

    if ctx.voice_client is None:
        await ctx.invoice(self.join)

    
    voice = ctx.voice_client
    guild_id = ctx.guild.id

    try:
        # youtube_dl or lavalink here
        source = discord.FFmpegPCMAudio(arg)
        source.title = arg  #'title' attribute for better queue messaging
    except Exception as e:
        print(f"FFmpeg Error: {e}")
        return await ctx.send(" Error loading audio file/path. Is FFmpeg insatlled and the path correct?")
    

    if voice. is_playing() or voice.is_paused():
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        self.queues[guild_id].append(source)
        await ctx.send(f"Added to queue: {arg}")
    else:
        voice.play(source, after=self.get_check_queue_callback(ctx, guild_id))
        await ctx.send(f"Now playing: {arg}")



# playback commands
@commands.command(help="Pauses the currently playing audio.")
async def pause(self, ctx):
    voice = ctx.voice_client

    if voice and voice.is_playing():
        voice.pause()
        await ctx.send("Paused the playback.")
    elif not voice:
        await ctx.send("Not connected to a voice channel.")
    else:
        await ctx.send("No audio is playing anything at the moment.")



@commands.command(help="Resumes paused audio")
async def resume(self, ctx):
    voice = ctx.voice_client
    if voice and voice.is_paused():
        voice.resume()
        await ctx.send("Resumed playback")
    else:
        await ctx.send("The audio is not paused.")


@commands.command(help="Stops the playback snd clears the queue.")
async def stop(self ,ctx):
    voice = ctx.voice_client
    if voice and (voice.is_playing() or voice.is_paused()):
        voice.stop()

        guild_id = ctx.guild.id
        if guild_id in self.queues:
            del self.queues[guild_id]
        await ctx.send("Playback stopped and queue cleared.")
    else:
        await ctx.send("Nothing is currently playing or paused.")


# ----- Function Cog Loading-----
async def setup(bot):
    await bot.add_cog(Music(bot))
