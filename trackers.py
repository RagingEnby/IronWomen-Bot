from datetime import datetime
from disnake.ext import commands, tasks
import asyncio
import disnake
from typing import Optional, Any
from datetime import datetime

from modules import hypixel, datamanager, utils, mojang
import config

RUNNING: bool = False
TASK: Optional[asyncio.Task] = None


class SkillTracker:
    skill_manager = datamanager.JsonWrapper('storage/skills.json')

    @staticmethod
    async def on_skill_update(skill: str, uuid: str, before: int, after: int):
        player = await mojang.get(uuid)
        embed = disnake.Embed(
            color=disnake.Color.green(),
            description=f"`{before}` :arrow_right: `{after}`",
            timestamp=datetime.now()
        )
        player.set_author(embed=embed, text=f"Leveled Up {skill.title()}!")
        await utils.send_to_channel(config.SKILL_CHANNEL_ID, embed=embed)

    @staticmethod
    async def on_profile_update(profile: dict[str, Any]):
        try:
            for uuid, member in profile.get('members', {}).items():
                print(f"[DEBUG] SkillTracker: Processing member {uuid}")
                experience_data = member.get('player_data', {}).get('experience', {})
                print(f"[DEBUG] SkillTracker: Found {len(experience_data)} skill entries")
                
                for skill, exp in experience_data.items():
                    skill_name = skill.replace('SKILL_', '')
                    print(f"[DEBUG] SkillTracker: Processing skill {skill_name} with exp {exp}")
                    lvl = hypixel.calculate_skill(skill_name, exp)
                    print(f"[DEBUG] SkillTracker: Calculated level {lvl} for {skill_name}")
                    
                    before = SkillTracker.skill_manager.get(uuid, {}).get(skill, 0)
                    if lvl != before:
                        print(f"[DEBUG] SkillTracker: Level change detected for {skill_name}: {before} -> {lvl}")
                        if uuid not in SkillTracker.skill_manager:
                            SkillTracker.skill_manager[uuid] = {}
                        SkillTracker.skill_manager[uuid][skill] = lvl
            
            print("[DEBUG] SkillTracker: Saving skill manager data")
            await SkillTracker.skill_manager.save()
            print("[DEBUG] SkillTracker: Data saved successfully")
        except Exception as e:
            print(f"[ERROR] SkillTracker: Fatal error in on_profile_update: {str(e)}")
            import traceback
            traceback.print_exc()


class CollectionTracker:
    collection_manager = datamanager.JsonWrapper('storage/collection.json')

    @staticmethod
    async def on_collection_update(collection: str, before: int, after: int):
        embed = disnake.Embed(
            color=disnake.Color.green(),
            description=f"`{before}` :arrow_right: `{after}`",
            timestamp=datetime.now()
        )
        embed.set_author(
            icon_url="https://sky.shiiyu.moe/item/" + collection.upper(),
            name=f"{collection.title()} Collection Leveled Up!"
        )
        await utils.send_to_channel(config.COLLECTION_CHANNEL_ID, embed=embed)


    @staticmethod
    async def on_profile_update(profile: dict[str, Any]):
        print(f"[DEBUG] CollectionTracker: Processing profile update")
        collection_count = len(hypixel.COLLECTION_BRACKETS)
        print(f"[DEBUG] CollectionTracker: Processing {collection_count} collections")
        
        for collection in hypixel.COLLECTION_BRACKETS:
            print(f"[DEBUG] CollectionTracker: Processing collection {collection}")
            collected = 0
            
            for member_id, member in profile.get('members', {}).items():
                member_collection = member.get('collection', {}).get(collection, 0)
                print(f"[DEBUG] CollectionTracker: Member {member_id} has {member_collection} of {collection}")
                collected += member_collection
                print(f"[ERROR] CollectionTracker: Error processing member {member_id} for collection {collection}: {str(e)}")
            
            print(f"[DEBUG] CollectionTracker: Total collected for {collection}: {collected}")
            lvl = hypixel.calculate_collection(collection, collected)
            print(f"[DEBUG] CollectionTracker: Calculated level {lvl} for {collection}")
            
            before = CollectionTracker.collection_manager.get(collection, 0)
            if lvl != before:
                print(f"[DEBUG] CollectionTracker: Level change detected for {collection}: {before} -> {lvl}")
                await CollectionTracker.on_collection_update(
                    collection=collection,
                    before=before,
                    after=lvl
                )
                CollectionTracker.collection_manager[collection] = lvl
        
        print("[DEBUG] CollectionTracker: Saving collection manager data")
        await CollectionTracker.collection_manager.save()
        print("[DEBUG] CollectionTracker: Data saved successfully")


class BankTracker:
    action_verbs = {
        "DEPOSIT": "Desposited",
        "WITHDRAW": "Withdrew"
    }
    transaction_manager = datamanager.JsonWrapper('storage/transactions.json')

    @staticmethod
    async def on_transaction(balance: int | float, amount: float, timestamp: int, action: str, name: str):
        player = await mojang.get(name) if name != "Bank Interest" else None
        before_balance = balance - amount if action == "DEPOSIT" else balance + amount
        verb = BankTracker.action_verbs[action]
        color = disnake.Color.green() if action == "DEPOSIT" else disnake.Color.red()
        if not player:
            color = disnake.Color.gold()
        embed = disnake.Embed(
            color=color,
            description=f"**Bank Balance:**\n`{utils.commaize(before_balance)}` :arrow_right: `{utils.commaize(balance)}`",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        embed.set_author(
            icon_url=player.avatar if player else config.STEVE_AVATAR,
            name=f"{player.name if player else name} {verb} {utils.commaize(amount)} coins"
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
        try:
            print("[DEBUG] TrackerCog: Fetching profile data")
            profile = await hypixel.get_profile()
            print("[DEBUG] TrackerCog: Profile data received")
            
            print("[DEBUG] TrackerCog: Starting all trackers")
            tasks = [
                utils.write_json('storage/profile.json', profile, 2),
                SkillTracker.on_profile_update(profile),
                CollectionTracker.on_profile_update(profile),
                LevelTracker.on_profile_update(profile),
                BankTracker.on_profile_update(profile),
            ]
            
            # Run all tasks but handle errors individually
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check for exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"[ERROR] TrackerCog: Task {i} failed with error: {str(result)}")
                    import traceback
                    traceback.print_exc()
            
            print("[DEBUG] TrackerCog: Profile update complete")
        except Exception as e:
            print(f"[ERROR] TrackerCog: Fatal error in profile_tracker_task: {str(e)}")
            import traceback
            traceback.print_exc()

    @commands.Cog.listener()
    async def on_ready(self):
        print('TrackerCog.on_ready()')
        self.profile_tracker_task.start()
