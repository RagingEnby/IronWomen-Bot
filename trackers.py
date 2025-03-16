from disnake.ext import commands, tasks
import asyncio
import aiofiles
import json
from typing import Optional

from modules import hypixel

RUNNING: bool = False
TASK: Optional[asyncio.Task] = None


class TrackerCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        
    @tasks.loop(seconds=15)
    async def profile_tracker_task():
        profile = await hypixel.get_profile()
        async with aiofiles.open('storage/profile.json', 'w') as file:
            await file.write(json.dumps(profile, indent=2))

    @commands.Cog.listener()
    async def on_ready(self):
        self.profile_tracker_task.start()
        