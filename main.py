import disnake
from disnake.ext import commands
import asyncio

import config
from trackers import TrackerCog

bot = commands.InteractionBot(
    intents=disnake.Intents.all(),
    owner_id=config.RAGINGENBY_USER_ID
)
bot.add_cog(TrackerCog(bot))


@bot.event
async def on_ready():
    print('bot ready')


bot.run(config.BOT_TOKEN)
