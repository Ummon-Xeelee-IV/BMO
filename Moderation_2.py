import discord
from discord.ext import commands
from discord import app_commands
from database import Database
import datetime

db = Database()

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # This works as BOTH !warn and /warn
    @commands.hybrid_command(
        name="warn", 
        description="Warn a member and track escalations"
    )
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(member="The user to warn", reason="Why are they being warned?")
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        # 1. Security Check: Prevent mods from warning admins or themselves
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You cannot warn someone with a higher or equal role.", ephemeral=True)

        # 2. Database: Record the warning and get the new total
        count = db.add_warning(member.id, ctx.guild.id)
        
        # 3. User Feedback: Send a professional Embed to the channel
        embed = discord.Embed(title="User Warning Issued", color=discord.Color.gold())
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Warning Count", value=f"**{count}**", inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_timestamp()
        
        await ctx.send(embed=embed)

        # 4. Logging: Send a report to the Logging Cog
        logging_cog = self.bot.get_cog('Logging')
        if logging_cog:
            # We reuse the same embed or create a more detailed one for logs
            await logging_cog.emit_log(ctx.guild, embed)

        # 5. Auto-Escalation: 3 Warnings = 30 Minute Timeout
# 5. Auto-Escalation Logic: 3 Warnings = 30 Minute Timeout
        if count >= 3:
            try:
                import datetime
                duration = datetime.timedelta(minutes=30)
                
                # Apply the timeout
                await member.timeout(duration, reason="Automatic escalation: Threshold of 3 warnings reached.")
                
                # Create a high-visibility escalation embed
                escalation_embed = discord.Embed(
                    title="Auto-Escalation Triggered",
                    description=f"{member.mention} has reached the **maximum warning threshold**.",
                    color=discord.Color.dark_red()
                )
                escalation_embed.add_field(name="Action Taken", value="**30-Minute Timeout**", inline=True)
                escalation_embed.add_field(name="Total Infractions", value=f"{count}", inline=True)
                escalation_embed.set_footer(text="System Policy: 3 warnings = Automatic Mute")
                
                await ctx.send(embed=escalation_embed)

                # Send a specific log to the Logging Cog for the escalation
                if logging_cog:
                    await logging_cog.emit_log(ctx.guild, escalation_embed)

            except discord.Forbidden:
                await ctx.send("**System Error:** I do not have high enough permissions to timeout this user (Hierarchy error).")



    @commands.hybrid_command(
        name="modstats", 
        description="View moderation statistics for a specific member"
    )
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member whose stats you want to view")
    async def modstats(self, ctx, member: discord.Member = None):
        # If no member is specified, check the author's own stats
        member = member or ctx.author
        
        # 1. Fetch data from DB
        warn_count = db.get_warnings(member.id, ctx.guild.id)
        
        # 2. Design the Embed
        embed = discord.Embed(
            title=f"Moderation Stats: {member.display_name}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # We can calculate the "Risk Level" based on warning count
        if warn_count == 0:
            status = "Clean Record"
            color = discord.Color.green()
        elif warn_count < 3:
            status = "At Risk"
            color = discord.Color.gold()
        else:
            status = "High Risk / Restricted"
            color = discord.Color.red()
            
        embed.color = color
        
        embed.add_field(name="Total Warnings", value=f"**{warn_count}**", inline=True)
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%b %d, %Y"), inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)



    @commands.hybrid_command(
        name="clear_warnings", 
        description="Resets a user's warning count to zero"
    )
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(member="The member to forgive")
    async def clear_warnings(self, ctx, member: discord.Member):
        # 1. Database: Delete the records
        db.reset_warnings(member.id, ctx.guild.id)
        
        # 2. Visual Feedback: Create a "Forgiveness" Embed
        embed = discord.Embed(
            title="Warnings Cleared",
            description=f"All warnings for {member.mention} have been removed.",
            color=discord.Color.green()
        )
        embed.add_field(name="Moderator", value=ctx.author.mention)
        embed.set_footer(text="User record has been reset to 0.")
        
        await ctx.send(embed=embed)

        # 3. Logging: Notify the staff channel
        logging_cog = self.bot.get_cog('Logging')
        if logging_cog:
            await logging_cog.emit_log(ctx.guild, embed)



async def setup(bot):
    await bot.add_cog(Moderation(bot))