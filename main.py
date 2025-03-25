import disnake
from disnake.ext import commands
import asyncio
import signal

from modules import asyncreqs

import config
import constants as g
from trackers import TrackerCog


bot = commands.InteractionBot(
    intents=disnake.Intents.all(),
    owner_id=config.RAGINGENBY_USER_ID
)
bot.add_cog(TrackerCog(bot))
g.BOT = bot


async def on_close():
    if asyncreqs.SESSION and not asyncreqs.SESSION.closed:
        await asyncreqs.SESSION.close()
    await bot.close()
    
@bot.event
async def on_ready():
    def signal_handler(*_) -> None:
        print("Received CTRL+C, shutting down...")
        asyncio.create_task(on_close())
        # Add a hook to stop the event loop after cleanup
        loop = asyncio.get_event_loop()
        loop.stop()
    signal.signal(signal.SIGINT, signal_handler)
    print('bot ready')


bot.run(config.BOT_TOKEN)
