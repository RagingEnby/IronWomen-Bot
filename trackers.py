from datetime import datetime
from disnake.ext import commands, tasks
import asyncio
import disnake
from typing import Optional, Any

from modules import hypixel, datamanager, utils, mojang
import config

RUNNING: bool = False
TASK: Optional[asyncio.Task] = None


class BankTracker:
    action_verbs = {
        "DEPOSIT": "Desposited",
        "WITHDRAW": "Withdrew"
    }
    transaction_manager = datamanager.JsonWrapper('storage/transactions.json')

    @staticmethod
    async def on_transaction(balance: int, amount: float, timestamp: int, action: str, name: str):
        player = await mojang.get(name) if name != "Bank Interest" else None
        before_balance = balance - amount if action == "DEPOSIT" else balance + amount
        verb = BankTracker.action_verbs[action]
        color = disnake.Color.green() if action == "DEPOSIT" else disnake.Color.red()
        if not player:
            color = disnake.Color.gold()
        embed = disnake.Embed(
            color=color,
            description=f"**Bank Balance:**\n`{utils.commaize(before_balance)}` :arrow_right: `{utils.commaize(balance)}`"
        )
        embed.set_author(
            icon_url=player.avatar if player else config.STEVE_AVATAR,
            name=f"{player.name if player else name} {verb} {amount} coins"
        )
        await utils.send_to_channel(config.BANK_CHANNEL_ID, embed=embed)
    
    @staticmethod
    async def on_profile_update(profile: dict[str, Any]):
        for transaction in profile.get('banking', {}).get('transactions', []):
            existing_data = BankTracker.transaction_manager.get(str(transaction['timestamp']))
            if existing_data:
                continue
            BankTracker.transaction_manager[str(transaction['timestamp'])] = transaction
            await BankTracker.on_transaction(
                balance=profile.get('banking', {}).get('balance', 0.0),
                amount=transaction['amount'],
                timestamp=transaction['timestamp'],
                action=transaction['action'],
                name=transaction['initiator_name']
            )
        await BankTracker.transaction_manager.save()


class LevelTracker:
    levels_manager = datamanager.JsonWrapper('storage/levels.json')
    
    @staticmethod
    async def on_level_update(uuid: str, before: int, after: int):
        print(uuid, 'LEVEL UPDATE:', before, '->', after)
        player = await mojang.get(uuid)
        embed = player.set_author(disnake.Embed(
            color=disnake.Color.green(),
            description=f"`{before}` :arrow_right: `{after}`",
            timestamp=datetime.now()
        ), text="Leveled Up!")
        await utils.send_to_channel(config.SB_LEVEL_CHANNEL_ID, embed=embed)
    
    @staticmethod
    async def on_profile_update(profile: dict[str, Any]):
        for uuid, member in profile.get('members', {}).items():
            level = member.get('leveling', {}).get('experience', 0) // 100
            if level == LevelTracker.levels_manager.get(uuid, 0):
                continue
            await LevelTracker.on_level_update(uuid, LevelTracker.levels_manager.get(uuid, 0), level)
            LevelTracker.levels_manager[uuid] = level
        await LevelTracker.levels_manager.save()


class TrackerCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.last_profile = {}

    """
    async def save_profile(self, profile: dict):
        diff_data = utils.dict_diff(self.last_profile, profile)
        self.last_profile = profile
        await asyncio.gather(
            utils.write_json('storage/profile.json', profile, 2),
            utils.write_json(f"storage/history/{int(time.time())}.json", diff_data, None),
            utils.write_json("storage/diff.json", diff_data, 2)
        )
    """

    @tasks.loop(seconds=15)
    async def profile_tracker_task(self):
        profile = await hypixel.get_profile()
        
        await asyncio.gather(
            #self.save_profile(profile),
            utils.write_json('storage/profile.json', profile, 2),
            LevelTracker.on_profile_update(profile),
            BankTracker.on_profile_update(profile)
        )

    @commands.Cog.listener()
    async def on_ready(self):
        print('TrackerCog.on_ready()')
        self.profile_tracker_task.start()
        