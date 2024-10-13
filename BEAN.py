import discord
from discord.ext import commands
import json
import random
from thefuzz import fuzz
import base64
import os

# UFO 50 Discord server ID
GUILD_ID = discord.Object(id=525973026429206530)
# TESTGUILD_ID = discord.Object(id=1292608815891480648)

# globally reused variables
game_list = []
d = []
counter = 0
file_content = ""
suggest = [
    "You should **give yourself a break**.",
    "You should play **UFO 50**.",
    "You should **try for a new record** in **your favorite game**.",
    "You should **hunt for some secrets**.",
    "You should pick the random tab and select **the first result**.",
    "You should pick the random tab and select **the last result**.",
    "You should play your **most played game again**.",
    "You should play more of your **least played game so far**."
]

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
        test_channel = client.get_channel('1295089365097386014')
        await test_channel.send("Restarted just now.")
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
        msg = message.content.replace(',','').replace('!','').lower()
        if "thanks bean" in msg or "thank you bean" in msg or "thankyou bean" in msg:
            if random.randint(1,4) == 3:
                await message.reply("NICE SWORD, PAL.")
            else:
                await message.reply("NICE ROD, PAL.")
        if not message.guild:
            return
        if not message.attachments:
            return
        
        # # Uncomment for testing message related stuff exclusively in test server
        # if not message.guild.id == 1292608815891480648:
        #     return
        
        file_extension = message.attachments[0].filename.split(".")[-1].lower()
        if file_extension == 'ufo':
            print(f"UFO File attachment detected from {message.author.name} ({message.author.id})")
            try:
                file_content = await message.attachments[0].read()
                file_content = base64.b64decode(file_content).decode('utf-8')
                file_content = json.loads(file_content)
                totalCherry = []
                totalGift = []
                totalGold = []
                cherryMsg = ""
                goldMsg = ""
                for x in range(1,51):
                    target = [y for y in d if x == int(y["game_id"])]
                    target = target[0]
                    if f"game0_gameWin{x}" in file_content:
                        if file_content[f"game0_gameWin{x}"] == 1.0:
                            totalGold.append(int(target["num"]))
                        elif file_content[f"game0_gameWin{x}"] == 2.0:
                            totalCherry.append(int(target["num"]))
                    if f"game0_gardenWin{x}" in file_content:
                        if file_content[f"game0_gardenWin{x}"] == 1.0:
                            totalGift.append(int(target["num"]))
                totalGold.sort()
                totalCherry.sort()
                if len(totalCherry) > 0:
                    for x in totalCherry:
                        target = [y for y in d if x == int(y["num"])]
                        target = target[0]
                        cherryMsg += target["emoji"]
                else:
                    cherryMsg += "*Nothing to show here*"
                if len(totalGold) > 0:
                    for x in totalGold:
                        target = [y for y in d if x == int(y["num"])]
                        target = target[0]
                        goldMsg += target["emoji"]
                else:
                    if len(totalCherry) > 0:
                        goldMsg += ""
                    else:
                        goldMsg += "*Nothing to show here*"
                if len(cherryMsg) > 0:
                    cherryMsg = "\n" + cherryMsg
                if len(goldMsg) > 0:
                    goldMsg = "\n" + goldMsg
                await message.reply(f"`Cherries:` **{len(totalCherry)}**{cherryMsg}\n`Golds:` **{len(totalGold)+len(totalCherry)}** ({len(totalGold)} non-cherried){goldMsg}\n`Gifts:` **{len(totalGift)}**")
            except ValueError as e:
                await message.reply(content=f"I was not able to parse the save file data.", ephemeral=True)

# define client and intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = Client(command_prefix="/",activity=discord.Game(name="UFO 50"),intents=intents)

# # once every 20 entered commands, change the bot's "Now playing" to the most recently specified game if there was one
async def change_presence(target):
    global client
    global counter
    if counter < 20:
        counter += 1
    else:
        counter = 0
        activity = discord.Game(name=target["name"])
        print(f"Changing status to {target["name"]}")
        await client.change_presence(status=discord.Status.Online,activity=activity)

# format 2d array for codes
def codes_output(codes):
    if len(codes) == 0:
        return '*No terminal codes available for this game.*'
    return f"||{'||\n||'.join(': '.join(str(x) for x in row) for row in codes)}||"

def game_value_output(type, target, emote):
    if type == 'codes':
        return f"The available {emote} **Terminal Codes** for {target["emoji"]} **{target["name"]}** are...\n{codes_output(target['codes'])}"
    return f"The {emote} **{type.capitalize()}** requirement for {target["emoji"]} **{target["name"]}** is...\n||{target[type]}||"


# shared function code used for grabbing cherry, gold, and gift values
async def get_game_value(interaction, game, number, type, emote):
    # no game or number specified
    if game is None and number is None:
        # check channel for number values to determine target game
        if interaction.channel.name[:1] in '0123456789' and interaction.channel.name[1:2] in '0123456789':
            if (int(interaction.channel.name[:2]) > 50 or int(interaction.channel.name[:2]) < 1):
                return await interaction.response.send_message(content=f"Please specify a game or number to check the {type} for.", ephemeral=True)
            else:
                target = d[int(interaction.channel.name[:2])-1]
                await interaction.response.send_message(game_value_output(type,target,emote))
                await change_presence(target)
        # no target game, give error
        else:
            return await interaction.response.send_message(content=f"Please specify a game or number to check the {type} for.", ephemeral=True)
    # game and or number is specified
    else:
        # number specified
        if game is None and not number is None:
            if number > 50 or number < 1:
                return await interaction.response.send_message(content=f"Your input was not valid.", ephemeral=True)
            else:
                target = d[number-1]
                await interaction.response.send_message(game_value_output(type,target,emote))
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
                    await interaction.response.send_message(game_value_output(type,target,emote))
                    await change_presence(target)
                else:
                    await interaction.response.send_message(content=f"Your input was not recognized.", ephemeral=True)
            # direct alias search succeeds
            else:
                target = target[0]
                await interaction.response.send_message(game_value_output(type,target,emote))
                await change_presence(target)
        # error if both number and game are specified
        else:
            await interaction.response.send_message(content="Please only specify the name or the number, not both.", ephemeral=True)

# ping test command
@client.tree.command(name="ping",description="Check that I am online!", guild=GUILD_ID)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('NICE ROD, PAL.')

# link to steam guides
@client.tree.command(name="guides",description="Get a link to steam guides for UFO 50!", guild=GUILD_ID)
async def guides(interaction: discord.Interaction):
    await interaction.response.send_message(content='Check out UFO 50 guides here:\n<https://steamcommunity.com/app/1147860/guides/>')

# link to steam guides
@client.tree.command(name="speedruns",description="Get a link to speedrun.com page for UFO 50!", guild=GUILD_ID)
async def speedruns(interaction: discord.Interaction):
    await interaction.response.send_message(content='Check out or submit UFO 50 speedruns here:\n<https://www.speedrun.com/UFO_50>')

# link to steam page
@client.tree.command(name="steam",description="Get a link to steam page for UFO 50!", guild=GUILD_ID)
async def steam(interaction: discord.Interaction):
    await interaction.response.send_message(content='Buy UFO 50 here:\n<https://store.steampowered.com/app/1147860/UFO_50/>')

# link to tier list maker
@client.tree.command(name="tierlist",description="Get a link to the Tier List Maker for UFO 50!", guild=GUILD_ID)
async def tier(interaction: discord.Interaction):
    await interaction.response.send_message(content='Make your own UFO 50 Tier List here:\n<https://tiermaker.com/create/ufo-50-games-16603442>', ephemeral=True)

# link to wiki
@client.tree.command(name="wiki",description="Get a link to the UFO 50 wiki!", guild=GUILD_ID)
async def wiki(interaction: discord.Interaction):
    await interaction.response.send_message(content='Check out the UFO 50 wiki here:\n<https://ufo50.miraheze.org/wiki/Main_Page>')

# link to bandcamp music
@client.tree.command(name="music",description="Get a link to UFO 50 music on Bandcamp!", guild=GUILD_ID)
async def music(interaction: discord.Interaction):
    await interaction.response.send_message(content='Check out the music for UFO 50 here:\n<https://phlogiston.bandcamp.com/album/ufo-50>', ephemeral=True)

# random game command
@client.tree.command(name="random",description="Pick out a UFO 50 game at random.", guild=GUILD_ID)
async def rnd(interaction: discord.Interaction):
    if random.randint(1,150) == 50:
        response = random.choice(suggest)
    else:
        response = random.choice(d)
        change_presence(response)
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

# terminal codes command
@client.tree.command(name="codes",description="Check terminal codes for a game.", guild=GUILD_ID)
async def codes(interaction: discord.Interaction, game: str|None, number: int|None):
    await get_game_value(interaction, game, number, "codes", ":InfoBuddyOK:1291972595952123984>")


# 50club command
@client.tree.command(name="50club",description="Check number of people with the cherry collector role.", guild=GUILD_ID)
async def fiftyclub(interaction: discord.Interaction):
    role2024 = interaction.guild.get_role(1291962155469373451)
    roleother = interaction.guild.get_role(1293958225644884068)
    await interaction.response.send_message(f"There are currently **{len(role2024.members)}** discord members who earned the 50 cherries role in 2024 and **{len(roleother.members)}** who earned it after 2024.")

# Get token from fly.io
TOKEN = os.getenv('BEAN_TOKEN')

# initialize bot online
client.run(TOKEN)