import disnake
from disnake.ext import commands
import asyncio

import config
import trackers


bot = commands.InteractionBot(
    intents=disnake.Intents.all(),
    owner_id=config.RAGINGENBY_USER_ID
)


@bot.event
async def on_ready():
    asyncio.create_task(trackers.start())
    print('bot ready')


bot.run(config.BOT_TOKEN)
