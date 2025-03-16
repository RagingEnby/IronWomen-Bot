from disnake.ext import commands, tasks
import asyncio
import aiofiles
import json

from modules import hypixel

RUNNING: bool = False
TASK: asyncio.Task = None

class Trackers(commands.Cog):
    def __init__(self, bot: commands.Interactionbot):
        self.bot = bot
        
    @tasks.loop(seconds=15):
    async def profile_tracker_task():
        profile = await hypixel.get_profile()
        async with aiofiles.open('storage/profile.json', 'w') as file:
            await file.write(json.dumps(profile, indent=2))
    
    
    async def start():
        global RUNNING, TASK
        if RUNNING:
            raise RuntimeError("Already running")
        RUNNING = True
        TASK = asyncio.create_task(main())
    
    
    async def stop():
        global RUNNING, TASK
        if not RUNNING:
            raise RuntimeError("Not running")
        RUNNING = False
        await TASK.cancel()
        