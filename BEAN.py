import discord
from discord.ext import commands
import json
import random
from thefuzz import fuzz

# UFO 50 Discord server ID
GUILD_ID = discord.Object(id=525973026429206530)
# TESTGUILD_ID = discord.Object(id=1292608815891480648)

# globally reused variables
game_list = []
d = []
counter = 0

# create array of game names from json file as well as store json data
with open('data.json') as f:
    d = json.load(f)
    for x in d:
        game_list.append(x["name"])

# define client class
class Client(commands.Bot):
    async def on_ready(self):
        # display console log when starting bot
        print(f'Logged in as {self.user}!')
        # attempt to sync slash commands
        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f'Synced {len(synced)} commands to guild {GUILD_ID.id}')
            # synced = await self.tree.sync(guild=TESTGUILD_ID)
            # print(f'Synced {len(synced)} commands to guild {TESTGUILD_ID.id}')
        except Exception as e:
            print(f'Error syncing commands: {e}')
    # easter egg message replies
    async def on_message(self, message):
        # ignore all messages from self or from another bot
        if message.author == self.user or message.author.bot:
            return
        if "thanks bean" in message.content.lower().replace(',','').replace('!',''):
            await message.reply("NICE ROD, PAL.")

# define client and intents
intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="/",activity=discord.Game(name="UFO 50"),intents=intents)

# once every 50 entered commands, change the bot's "Now playing" to the most recently specified game
async def change_presence(target):
    global counter
    if counter < 50:
        counter += 1
    else:
        counter = 0
        activity = discord.Game(name=target["name"])
        await client.change_presence(status=discord.Status.Online,activity=activity)

# shared function code used for grabbing cherry, gold, and gift values
async def get_game_value(interaction, game, number, type, emote):
    # no game or number specified
    if game is None and number is None:
        # check channel for number values to determine target game
        if interaction.channel.name[:1] in '0123456789' and interaction.channel.name[1:2] in '0123456789':
            if (int(interaction.channel.name[:2]) > 50 or int(interaction.channel.name[:2]) < 1):
                return await interaction.response.send_message(f"Please specify a game or number to check {type} of.")
            else:
                target = d[int(interaction.channel.name[:2])-1]
                await interaction.response.send_message(f"The {emote} **{type.capitalize()}** requirement for {target["emoji"]} **{target["name"]}** is...\n||{target[type]}||")
                await change_presence(target)
        # no target game, give error
        else:
            return await interaction.response.send_message(f"Please specify a game or number to check {type} requirement of.")
    # game and or number is specified
    else:
        # number specified
        if game is None and not number is None:
            if number > 50 or number < 1:
                return await interaction.response.send_message(f"input '{number}' is not valid.")
            else:
                target = d[number-1]
                await interaction.response.send_message(f"The {emote} **{type.capitalize()}** requirement for {target["emoji"]} **{target["name"]}** is...\n||{target[type]}||")
                await change_presence(target)
        # game specified
        elif number is None and not game is None:
            target = [x for x in d if game.lower() in x["alias"]]
            # fuzzy search if alias search fails
            if len(target) == 0:
                best_match = 0
                best_match_game = ""
                for x in game_list:
                    match = fuzz.ratio(game.lower(), x.lower())
                    if match > best_match:
                        best_match_game = x
                        best_match = match
                if (best_match >= 90):
                    target = [x for x in d if best_match_game.lower() == x["name"].lower()]
                    target = target[0]
                    await interaction.response.send_message(f"The {emote} **{type.capitalize()}** requirement for {target["emoji"]} **{target["name"]}** is...\n||{target[type]}||")
                    await change_presence(target)
                else:
                    await interaction.response.send_message(f"input '{game}' not recognized")
            # direct alias search succeeds
            else:
                target = target[0]
                await interaction.response.send_message(f"The {emote} **{type.capitalize()}** requirement for {target["emoji"]} **{target["name"]}** is...\n||{target[type]}||")
                await change_presence(target)
        # error if both number and game are specified
        else:
            await interaction.response.send_message("Please only specify the name or the number, not both.")

# ping test command
@client.tree.command(name="ping",description="Check that I am online!", guild=GUILD_ID)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('NICE ROD, PAL.')

# link to steam guides
@client.tree.command(name="guides",description="Get a link to steam guides for UFO 50!", guild=GUILD_ID)
async def guides(interaction: discord.Interaction):
    await interaction.response.send_message('Check out UFO 50 guides here:\n<https://steamcommunity.com/app/1147860/guides/>')

# link to tier list maker
@client.tree.command(name="tierlist",description="Get a link to the Tier List Maker for UFO 50!", guild=GUILD_ID)
async def tier(interaction: discord.Interaction):
    await interaction.response.send_message('Make your own UFO 50 Tier List here:\n<https://tiermaker.com/create/ufo-50-games-16603442>')

# link to wiki
@client.tree.command(name="wiki",description="Get a link to the UFO 50 wiki!", guild=GUILD_ID)
async def wiki(interaction: discord.Interaction):
    await interaction.response.send_message('Check out the UFO 50 wiki here:\n<https://ufo50.miraheze.org/wiki/Main_Page>')

# link to bandcamp music
@client.tree.command(name="music",description="Get a link to UFO 50 music on Bandcamp!", guild=GUILD_ID)
async def music(interaction: discord.Interaction):
    await interaction.response.send_message('Check out the music for UFO 50 here:\n<https://phlogiston.bandcamp.com/album/ufo-50>')

# random game command
@client.tree.command(name="random",description="Pick out a UFO 50 game at random.", guild=GUILD_ID)
async def rnd(interaction: discord.Interaction):
    response = random.choice(d)
    await interaction.response.send_message(f"You should play {response["emoji"]} **{response["name"]}**.")

# gift command
@client.tree.command(name="gift",description="Check gift requirement for a game.", guild=GUILD_ID)
async def gift(interaction: discord.Interaction, game: str|None, number: int|None):
    await get_game_value(interaction, game, number, "gift", "<:GiftGet:1292627978601365636>")

# gold command
@client.tree.command(name="gold",description="Check gold requirement for a game.", guild=GUILD_ID)
async def gold(interaction: discord.Interaction, game: str|None, number: int|None):
    await get_game_value(interaction, game, number, "gold", "<:TrophyGet:1291281233254289460>")

# cherry command
@client.tree.command(name="cherry",description="Check cherry requirement for a game.", guild=GUILD_ID)
async def cherry(interaction: discord.Interaction, game: str|None, number: int|None):
    await get_game_value(interaction, game, number, "cherry", "<:CherryGet:1291281262870528073>")

# token in separate file
with open("token.txt") as file:
    TOKEN = file.read()

# initialize bot online
client.run(TOKEN)