import os
import json
import discord
from discord import app_commands
from discord.ext import commands
import random
import datetime
from utils import urandom, get_random_game, filter_name

class RngCommands(commands.Cog):
    STRENGTH = 1.42
    USER_HISTORY_FILE = "/data/user_history.json"

    def __init__(self, bot: commands.Bot, guild_id: discord.Object, d: list):
        self.bot = bot
        self.guild_id = guild_id
        self.d = d

    suggest = [
        "You should play <:bingo:1406508535579279451> **UFO 50 Bingo**.",
        "You should play a **UFO 50 Mod**.",
        "You should play <:railheist:1292610861835354183> **Rail Heist** Blindfolded.",
        "You should **try for a new record** in **your favorite game**.",
        "You should pick the random tab and select **the first result**.",
        "You should pick the random tab and select **the last result**.",
        "You should play your **most played game again**.",
        "You should play more of your **least played game so far**."
    ]

    @app_commands.command(name="random", description="Get a random UFO 50 game suggestion")
    async def rnd(self, interaction: discord.Interaction):
        if urandom(50) == 50:
            response = random.choice(self.suggest)
        else:
            game = get_random_game(self.d)
            response = f'You should play {game["emoji"]} **{game["name"]}**.'
        await interaction.response.send_message(response)

    @app_commands.command(name="randomdaily",description="Get a personalized random UFO 50 game suggestion for the day based on your username and today's date")
    async def randomdaily(self, interaction: discord.Interaction):
        user_name = interaction.user.nick or interaction.user.display_name or interaction.user.name
        user_name = filter_name(user_name)
        PST = datetime.timezone(datetime.timedelta(hours=-7))
        today = datetime.datetime.now(PST).date()
        seed = f"{interaction.user.name}-{today.toordinal()}"
        random.seed(seed)
        num = random.randint(1, 50)
        game = d[num-1]
        response = f'{user_name} should play {game["emoji"]} **{game["name"]}** today.'
        await interaction.response.send_message(response)

    def load_history():
        if not os.path.exists(USER_HISTORY_FILE):
            return {}
        with open(USER_HISTORY_FILE, "r") as f:
            return json.load(f)

    def save_history(history):
        with open(USER_HISTORY_FILE, "w") as f:
            json.dump(history, f)

    def get_weighted_game(d, counts):
        weights = [1 / ((counts[i] + 1) ** strength) for i in range(50)]
        return random.choices(range(50), weights=weights, k=1)[0]

    @app_commands.command(name="randomforme", description="Get a personalized random UFO 50 game suggestion for the day with odds adjusted based on your past rolls")
    async def randomforme(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        user_name = interaction.user.nick or interaction.user.display_name or interaction.user.name
        user_name = filter_name(user_name)
        PST = datetime.timezone(datetime.timedelta(hours=-7))
        today = datetime.datetime.now(PST).date().isoformat()

        history = load_history()
        user_data = history.get(user_id, {"date": None, "game": None, "counts": [0] * 50})

        # If already rolled today
        if user_data["date"] == today:
            game_num = user_data["game"]
            game = self.d[game_num]
        # If have not rolled today yet
        else:
            counts = user_data["counts"]
            game_num = get_weighted_game(self.d, counts)
            counts[game_index] += 1
            history[user_id] = {"date": today, "game": game_index, "counts": counts}
            save_history(history)
            game = self.d[game_num]

        await interaction.response.send_message(f'{user_name} should play {game["emoji"]} **{game["name"]}** today.')