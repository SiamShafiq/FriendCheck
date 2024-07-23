"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.2.0
"""

from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime
import discord


# Here we name the cog and create a new class for the cog.
class Track(commands.Cog, name="track"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.join_times = {}
        self.total_durations = {}

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    def updateDuration(self, member, duration):
        if member.id in self.total_durations:
            self.total_durations[member.id] += duration
        else:
            self.total_durations[member.id] = duration

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        now = datetime.now()
        
        # Check if the user joined a voice channel
        if before.channel is None and after.channel is not None:
            self.join_times[member.id] = now  # Record the join time
            print(f'{member} joined {after.channel} at {now.strftime("%Y-%m-%d %H:%M:%S")}')
        
        # Check if the user left a voice channel
        elif before.channel is not None and after.channel is None:
            if member.id in self.join_times:
                join_time = self.join_times.pop(member.id)  # Get and remove the join time
                duration = now - join_time  # Calculate the duration
                duration_seconds = duration.total_seconds()

                self.updateDuration(member, duration)

                hours, remainder = divmod(duration_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f'{member} left {before.channel} at {now.strftime("%Y-%m-%d %H:%M:%S")}. Duration: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds')
        
        # Check if the user switched voice channels
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            print(f'{member} moved from {before.channel} to {after.channel} at {now.strftime("%Y-%m-%d %H:%M:%S")}')
    
    #Find how long user has been in voice channels total.
    @commands.command()
    async def duration(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author  # Default to the user who invoked the command

        if member.id in self.total_durations:
            total_duration_seconds = self.total_durations[member.id].total_seconds()
            total_hours, total_remainder = divmod(total_duration_seconds, 3600)
            total_minutes, total_seconds = divmod(total_remainder, 60)
            await ctx.send(f'Total time spent in voice channels by {member}: {int(total_hours)} hours, {int(total_minutes)} minutes, {int(total_seconds)} seconds')
        else:
            await ctx.send(f'No data available for {member}')


    
# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Track(bot))
