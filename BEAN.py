import discord
from discord.ext import commands
import json
import random
import math
import re 
from thefuzz import fuzz
import base64
import os

# UFO 50 Discord server ID
GUILD_ID = discord.Object(id=525973026429206530)
TESTGUILD_ID = discord.Object(id=1292608815891480648)

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

character_types = [
    ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".",
    "<a:dancer:1302691372003758130> `DANCER`",
    "<a:hippy:1302691395357900841> `HIPPY`", 
    "<a:cute_dog:1302692176882569336> `CUTE DOG`",
    "<a:security:1302691420276002826> `SECURITY`",
    "<a:wrestler:1302692526829998182> `WRESTLER`",
    "<a:watch_dog:1302691431240040519> `WATCH DOG`", 
    "<a:spy:1302692186583859330> `SPY`", 
    "<a:driver:1302691377712468040> `DRIVER`",
    "<a:private_i:1302691416534679655> `PRIVATE I.`",
    "<a:grillmastr:1302692179558404290> `GRILLMASTR`",
    "<a:athlete:1302691354077429841> `ATHLETE`", 
    "<a:mr_popular:1302692524820795412> `MR POPULAR`",
    "<a:celebrity:1302691360452775976> `CELEBRITY`", 
    "<a:comedian:1302691364613521468> `COMEDIAN`",
    "<a:photographr:1302691413984804916> `PHOTOGRAPHR`", 
    "<a:caterer:1302691358942953553> `CATERER`", 
    "<a:ticket_tkr:1302691427653783602> `TICKET TKR`",
    "<a:auctioneer:1302691356249948200> `AUCTIONEER`",
    "<a:monkey:1302691410167988224> `MONKEY`",
    "<a:rock_star:1302692184709136484> `ROCK STAR`", 
    "<a:gangster:1302691386675564554> `GANGSTER`",
    "<a:gambler:1302691385412943922> `GAMBLER`", 
    "<a:werewolf:1302691433211232266> `WEREWOLF`",
    "<a:mascot:1302691406447378582> `MASCOT`",
    "<a:introvert:1302691398721474560> `INTROVERT`", 
    "<a:counselor:1302692175854698597> `COUNSELOR`", 
    "<a:stylist:1302691423874711715> `STYLIST`", 
    "<a:bartender:1302691358175399998> `BARTENDER`", 
    "<a:writer:1302691437145493644> `WRITER`",
    "<a:climber:1302691362914832395> `CLIMBER`", 
    "<a:cupid:1302691368237404190> `CUPID`", 
    "<a:magician:1302691403674947615> `MAGICIAN`",
    "<a:greeter:1302691391716986942> `GREETER`", 
    "<a:cheerleadr:1302691361576976404> `CHEERLEADR`",
    ".", ".", ".", ".", ".",
    "<a:alien:1302691352672473148> `ALIEN`", 
    "<a:dinosaur:1302692177897590794> `DINOSAUR`",
    "<a:leprechaun:1302692180359647282> `LEPRECHAUN`",
    "<a:genie:1302691388067942461> `GENIE`", 
    "<a:mermaid:1302692181814935572> `MERMAID`", 
    "<a:dragon:1302704429736263813> `DRAGON`",
    "<a:ghost:1302692178442715172> `GHOST`", 
    "<a:unicorn:1302692190757195857> `UNICORN`", 
    "<a:superhero:1302692525731086377> `SUPERHERO`"
]
pop_costs = {
    "DIVIDER": -1,
    "OLD FRIEND": 2,
    "OLD FRIEND": 2,
    "OLD FRIEND": 2,
    "OLD FRIEND": 2,
    "RICH PAL": 3,
    "RICH PAL": 3,
    "RICH PAL": 3,
    "RICH PAL": 3,
    "WILD BUDDY": 1,
    "WILD BUDDY": 1,
    "DANCER": 7,
    "HIPPY": 4,
    "CUTE DOG": 7,
    "SECURITY": 4,
    "WRESTLER": 9,
    "WATCH DOG": 4,
    "SPY": 8,
    "DRIVER": 3,
    "PRIVATE I.": 4,
    "GRILLMASTR": 5,
    "ATHLETE": 6,
    "MR POPULAR": 5,
    "CELEBRITY": 11,
    "COMEDIAN": 5,
    "PHOTOGRAPHR": 5,
    "CATERER": 5,
    "TICKET TKR": 4,
    "AUCTIONEER": 9,
    "MONKEY": 3,
    "ROCK STAR": 5,
    "GANGSTER": 6,
    "GAMBLER": 7,
    "WEREWOLF": 5,
    "MASCOT": 5,
    "INTROVERT": 4,
    "COUNSELOR": 7,
    "STYLIST": 7,
    "BARTENDER": 11,
    "WRITER": 8,
    "CLIMBER": 12,
    "CUPID": 8,
    "MAGICIAN": 5,
    "GREETER": 5,
    "CHEERLEADR": 5,
    "45": -1,
    "46": -1,
    "47": -1,
    "48": -1,
    "49": -1,
    "ALIEN": 40,
    "DINOSAUR": 25,
    "LEPRECHAUN": 50,
    "GENIE": 55,
    "MERMAID": 30,
    "DRAGON": 30,
    "GHOST": 45,
    "UNICORN": 45,
    "SUPERHERO": 50
}

CHAR_START = 11
CHAR_END = 44
CHAR_PRESTIGE_START = 50
CHAR_PRESTIGE_END = 58

def rng_random():
    global rng_state_1, rng_state_2
    rng_state_1 = (65192 * (rng_state_1 & 65535)) + ((rng_state_1 & 4294901760) >> 16)
    rng_state_2 = (64473 * (rng_state_2 & 65535)) + ((rng_state_2 & 4294901760) >> 16)
    ret = (((rng_state_1 & 65535) << 16) + rng_state_2) & 4294967295
    return ret

def rng_random_int(arg0, arg1):
    r = rng_random()
    ret = arg0 + math.floor(((arg1 - arg0 + 1) * r) / 4294967296)
    return ret

def generate_scenario(seed):
    global rng_state_1, rng_state_2
    mask = 1431655765
    rng_state_1 = 1253089769 ^ (seed & mask)
    rng_state_2 = 2342871706 ^ (seed & ~mask)
    for i in range(20):
        rng_random()
    deck = []
    num_reg_chars = 11
    num_prestige_chars = 13 - num_reg_chars
    for i in range(num_reg_chars):
        while True:
            rand_char = rng_random_int(CHAR_START, CHAR_END)
            if rand_char not in deck and rand_char <= 44:
                deck.append(rand_char)
                break
        rng_random()
    for i in range(num_prestige_chars):
        while True:
            rand_char = rng_random_int(CHAR_PRESTIGE_START, CHAR_PRESTIGE_END)
            if rand_char not in deck and rand_char <= 58:
                deck.append(rand_char)
                break
        rng_random()
    return deck

def sort_deck(deck):
    character_names = [character_types[index] for index in deck]
    sort_keys = [pop_costs[re.search(r'\`(.*?)\`', name).group(1)] for name in character_names]
    combined = list(zip(deck, sort_keys))
    combined.sort(key=lambda x: x[1])
    sorted_deck,sorted_keys = zip(*combined)
    return sorted_deck

async def get_scenario_result(interaction, seed):
    global rng_state_1, rng_state_2
    rng_state_1 = -1
    rng_state_2 = -1
    if seed is None:
        seed = random.randint(0, 999999)
    elif not isinstance(seed, (int, float)):
        return await interaction.response.send_message(content=f"Please specify a valid number value between **000000** and **999999**.", ephemeral=True)
    elif seed < 0 or seed > 999999:
        return await interaction.response.send_message(content=f"That seed value is not between **000000** and **999999**.", ephemeral=True)
    seed = int(seed)
    deck = sort_deck(generate_scenario(seed)) # Input can be from 0 to 999999
    deck_names = [character_types[index] for index in deck]
    return await interaction.response.send_message(f"**SEED {str(seed).zfill(6)}**\n\n{" ".join(deck_names)}")

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
        test_channel = self.get_channel(1295089365097386014)
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
            if number > 51 or number < 0:
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
@client.tree.command(name="speedrun",description="Get a link to speedrun.com page for UFO 50!", guild=GUILD_ID)
async def spdrun(interaction: discord.Interaction):
    await interaction.response.send_message(content='Check out or submit UFO 50 speedruns here:\n<https://www.speedrun.com/UFO_50>')

# link to steam page
@client.tree.command(name="steam",description="Get a link to steam page for UFO 50!", guild=GUILD_ID)
async def steam(interaction: discord.Interaction):
    await interaction.response.send_message(content='Buy UFO 50 here:\n<https://store.steampowered.com/app/1147860/UFO_50/>')

# link to tier list maker
@client.tree.command(name="tierlist",description="Get a link to the Tier List Maker for UFO 50!", guild=GUILD_ID)
async def tier(interaction: discord.Interaction):
    await interaction.response.send_message(content='Make your own UFO 50 Tier List here:\n<https://tiermaker.com/create/ufo-50-games-16603442>', ephemeral=True)

# since people ask so much
@client.tree.command(name="whatsthatdemogame",description="for when people ask about that one demo preview game", guild=GUILD_ID)
async def whatsthatdemogame(interaction: discord.Interaction):
    await interaction.response.send_message(content='That one demo game is from <:elfazarshat:1292610893200359516> **Elfazar\'s Hat**.')

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
        while response["name"] == "The Terminal" or response["name"] == "MT":
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
    await get_game_value(interaction, game, number, "codes", "<:InfoBuddyOK:1291972595952123984>")

# gift command
@client.tree.command(name="partyhouseseed",description="check a seed for Party House, or get a random one.", guild=GUILD_ID)
async def getphseed(interaction: discord.Interaction, seed: int|None):
    await get_scenario_result(interaction, seed)


# 50club command
@client.tree.command(name="50club",description="Check number of people with the cherry collector role.", guild=GUILD_ID)
async def fiftyclub(interaction: discord.Interaction):
    role50_pc_legacy = interaction.guild.get_role(1291962155469373451)
    role50_pc = interaction.guild.get_role(1293958225644884068)
    role50_switch_legacy = interaction.guild.get_role(1403267685932077117)
    role50_switch = interaction.guild.get_role(1403268500709048422)

    role_message = "Here are the number of discord members who currently hold the 50 cherries role:\n\n"
    role_message += f"**{len(role50_pc_legacy.members)}** members on PC in 2024\n"
    role_message += f"**{len(role50_pc.members)}** members on PC after 2024\n"
    role_message += f"**{len(role50_switch_legacy.members)}** members on Switch in 2025\n"
    role_message += f"**{len(role50_switch.members)}** members on Switch after 2025\n"

    await interaction.response.send_message(role_message)

# Get token from fly.io
TOKEN = os.getenv('BEAN_TOKEN')

# initialize bot online
client.run(TOKEN)
