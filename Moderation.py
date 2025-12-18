import discord 
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import bot_has_permissions, BotMissingPermissions

class Moderation(commands.Cog):
    """Commands for server administration and moderation"""
    def __init__(self, bot):
        self.bot = bot

        

    @commands.hybrid_command(name="kick", help="Kicks a member from the server.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason stated"):
        try:
            await member.kick(reason=reason)
            await ctx.send(f"user {member.display_name} has been kicked from the server. Reason: {reason or ""}")
        except discord.Forbidden:
            await ctx.send("No permision for execution")

    
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("You do not have permission to kick members.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please mention a member to kick (`!kick @User` ).")


    # Ban Command
    @commands.command(help="Bans a member from the server.")
    @bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"User {member.display_name} has been banned from the server. Reason: {reason or "None"}")

    @ban.error
    async def unban_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to ban members.")
        
    
    # Unban Command
    @commands.command(help="Unbans a member from the server.")
    @bot_has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_indentifier):
        baned_users = await ctx.guild.bans()
        try:
            member_name, member_discriminator = member_indentifier.split('#')
        except ValueError:
            return await ctx.send(" Invalid format. Please use the format (`Username#1234`)")
        
        for ban_entry in baned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"User {user} has been unbanned.")
                return
            
        await ctx.send(f"Coild not find baned user: {member_indentifier}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))


    


