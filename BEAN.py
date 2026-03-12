import discord
from discord.ext import commands
import os
import json
import asyncio
from basic_commands import BasicCommands
from rng_commands import RngCommands
from world_record import WorldRecord
from party_house import PartyHouse

GUILD_ID = discord.Object(id=525973026429206530)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", activity=discord.Game(name="UFO 50"), intents=intents)

with open('data.json') as f:
    d = json.load(f)
    game_list = [x["name"] for x in d]

async def main():
    async with bot:
        await bot.add_cog(BasicCommands(bot, GUILD_ID, d, game_list))
        await bot.add_cog(RngCommands(bot, GUILD_ID, d))
        await bot.add_cog(WorldRecord(bot, GUILD_ID, d, game_list))
        await bot.add_cog(PartyHouse(bot, GUILD_ID))
        await bot.tree.sync(guild=GUILD_ID)
        await bot.start(os.getenv("BEAN_TOKEN"))

asyncio.run(main())