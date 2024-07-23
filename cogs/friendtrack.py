"""
Copyright © Siam Shafiq 2024-Present - https://github.com/siamshafiq
"""

from discord.ext import commands
from discord.ext.commands import Context
import datetime
import discord

# Here we name the cog and create a new class for the cog.
class Track(commands.Cog, name="track"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.join_times = {}
        self.total_durations = {}

    def updateDuration(self, member, duration):
        if member.id in self.total_durations:
            self.total_durations[member.id] += duration
        else:
            self.total_durations[member.id] = duration

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        now = datetime.datetime.now()
        
        # Check if the user joined a voice channel
        if before.channel is None and after.channel is not None:
            #self.join_times[member.id] = now  # Record the join time

            await self.bot.database.connection.execute(
                'INSERT INTO user_data (user_id, join_time, total_duration) VALUES (?, ?, ?)',
                (str(member.id), now, 0)
            )

            print(f'{member} joined {after.channel} at {now.strftime("%Y-%m-%d %H:%M:%S")}')
        
        # Check if the user left a voice channel
        elif before.channel is not None and after.channel is None:
            async with self.bot.database.connection.execute(
                'SELECT id, join_time FROM user_data WHERE user_id = ? ORDER BY id DESC LIMIT 1',
                (str(member.id),)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    join_time_str = row[1].split('.')[0]  # Split and take the part before the fractional seconds
                    join_time = datetime.datetime.strptime(join_time_str, '%Y-%m-%d %H:%M:%S')
                    duration = (datetime.datetime.now() - join_time).total_seconds()

                    await self.bot.database.connection.execute(
                        'UPDATE user_data SET total_duration = total_duration + ? WHERE id = ?',
                        (duration, row[0])
                    )
                    await self.bot.database.connection.commit()
                    print(f'{member} left {before.channel} at {now}. Duration: {duration} seconds')
        
        # Check if the user switched voice channels
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            print(f'{member} moved from {before.channel} to {after.channel} at {now.strftime("%Y-%m-%d %H:%M:%S")}')
    
    #Find how long user has been in voice channels total.
    @commands.command()
    async def duration(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author  # Default to the user who invoked the command

        async with self.bot.database.connection.execute(
            'SELECT SUM(total_duration) FROM user_data WHERE user_id = ?',
            (str(member.id),)
        ) as cursor:
            row = await cursor.fetchone()
            if row and row[0] is not None:
                total_duration_seconds = row[0]
                total_hours, total_remainder = divmod(total_duration_seconds, 3600)
                total_minutes, total_seconds = divmod(total_remainder, 60)
                await ctx.send(f'Total time spent in voice channels by {member}: {int(total_hours)} hours, {int(total_minutes)} minutes, {int(total_seconds)} seconds')
            else:
                await ctx.send(f'No data available for {member}')


    
# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Track(bot))
