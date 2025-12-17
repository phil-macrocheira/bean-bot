import discord
from discord.ext import commands
import json
import random
import math
import re 
from thefuzz import fuzz
import base64
import os
import requests

# UFO 50 Discord server ID
GUILD_ID = discord.Object(id=525973026429206530)
TESTGUILD_ID = discord.Object(id=1292608815891480648)

# globally reused variables
game_list = []
d = []
counter = 0
file_content = ""
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

def get_answer():
    barbuta_response = random.randint(1,50)
    if barbuta_response == 50:
        return f'Ask me again in <:barbuta:1292612809682583564> **Barbuta**.'

    num = random.randint(1,13)
    if num == 1 or num == 2 or num == 3:
        response = 'YES'
    elif num == 4 or num == 5 or num == 6:
        response = 'NO'
    elif num == 7:
        response = 'MOST LIKELY'
    elif num == 8:
        response = 'IT IS POSSIBLE'
    elif num == 9:
        response = 'DON\'T COUNT ON IT'
    elif num == 10:
        response = 'PROBABLY NOT'
    elif num == 11:
        response = 'I DO NOT UNDERSTAND'
    elif num == 12:
        response = 'I DON\'T KNOW'
    elif num == 13:
        response = 'BETTER NOT TELL YOU NOW'

    return response

# create array of game names from json file as well as store json data
with open('data.json') as f:
    d = json.load(f)
    for x in d:
        game_list.append(x["name"])

# define client class
class Client(commands.Bot):
    async def on_ready(self):
        synced = await self.tree.sync(guild=GUILD_ID)

    # message replies
    async def on_message(self, message):
        # ignore all messages from self or from another bot
        if message.author == self.user or message.author.bot:
            return
        msg_ask = message.content.lower().replace(' ','')
        if ("bean," in msg_ask and msg_ask.endswith("?")) or msg_ask.endswith("bean?"):
            if (msg_ask != 'bean,?' and msg_ask != 'bean?'):
                await message.reply(get_answer())
                return
        msg = message.content.lower().replace(',','').replace('!','')
        if "thanks bean" in msg or "thank you bean" in msg:
            if random.randint(1,4) == 3:
                await message.reply("NICE SWORD, PAL.")
            else:
                await message.reply("NICE ROD, PAL.")
            return
        if not message.guild:
            return
        if not message.attachments:
            return
        
        # save reader
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

# format 2d array for codes
def codes_output(codes):
    if len(codes) == 0:
        return '*No terminal codes available for this game.*'
    return f"||{'||\n||'.join(': '.join(str(x) for x in row) for row in codes)}||"

# get world record data from speedrun.com API
def get_world_records(target, players):
    game = target['name']
    emoji = target['emoji']
    category_id = target['sr_category']
    response = ""
    player_var = ""
    other_var_name = ""
    other_var_name2 = ""
    mode_2p = False
    init = False

    try:
        v = requests.get(f"https://www.speedrun.com/api/v1/categories/{category_id}/variables", timeout=5)
        v.raise_for_status()
    except requests.exceptions.Timeout:
        return f"Speedrun.com API timed out when grabbing category variables"
    if v.status_code != 200:
        return f"Error: Status code {v.status_code} from speedrun.com API"

    variable_data = v.json()["data"]

    for var in variable_data:
        var_name = var["name"]

        if var_name == 'Player Count' and game != 'Fist Hell':
            player_var_id = var["id"]
            if players == 2:
                player2_id, player2_data = list(var["values"]["values"].items())[1]
                player_var = f"&var-{player_var_id}={player2_id}"
                mode_2p = True
            else:
                player1_id, player1_data = list(var["values"]["values"].items())[0]
                player_var = f"&var-{player_var_id}={player1_id}"
        # Restrictions: Velgress, Bushido Ball, and Star Waspir
        # Upgrades: Campanella 2
        # Difficulty: Hyper Contender
        # Cave Extensions: Mini & Max
        elif var_name == 'Restrictions' or var_name == 'Upgrades' or var_name == 'Difficulty' or var_name == 'Cave Extensions':
            other_var_id = var["id"]
            other_id, other_data = list(var["values"]["values"].items())[0]
            other_var_name = f" **({other_data["label"]})**"
        # Item Restrictions: Mini & Max
        elif var_name == 'Item Restrictions':
            other_var_id2 = var["id"]
            other_id2, other_data2 = list(var["values"]["values"].items())[0]
            other_var_name2 = f" **({other_data2["label"]})**"

    for var in variable_data:
        if var["name"] == 'Subcategory':
            subcat_var_id = var["id"]
            for subcat_id, subcat_data in var["values"]["values"].items():
                subcat_name = subcat_data["label"]
                if subcat_name == 'Blindfolded' or subcat_name == 'GETM-EOUT':
                    continue

                try:
                    r = requests.get(f"https://www.speedrun.com/api/v1/leaderboards/v1pl7876/category/{category_id}?var-{subcat_var_id}={subcat_id}{player_var}&top=1", timeout=5)
                    r.raise_for_status()
                except requests.exceptions.Timeout:
                    return f"Speedrun.com API timed out when grabbing leaderboard for {subcat_name}"
                if r.status_code != 200:
                    return f"Error: Status code {v.status_code} from speedrun.com API"

                data = r.json()["data"]

                player_num_text = ""
                if mode_2p:
                    player_num_text = f" **(2 Player)**"
                    
                if not init:
                    game_link_id = data["weblink"].split('#')[1]
                    game_link = f"https://www.speedrun.com/UFO_50?h={game_link_id}-gold&x={category_id}-{subcat_var_id}.{subcat_id}"
                    response += f"The current world records for {emoji} **[{game}]({game_link})**{other_var_name}{other_var_name2}{player_num_text} are:\n"
                    init = True

                if len(data["runs"]) == 0:
                    continue
                wr_entry = data["runs"][0]["run"]

                date = wr_entry["date"]

                time_sec = wr_entry["times"]["primary_t"]
                m, s = divmod(time_sec, 60)
                m = int(m)
                s = int(s)
                ms = round((time_sec - (m*60) - s)*1000)
                time = f"{m}m {s}s {ms:03d}ms"

                video_link = wr_entry["videos"]["links"][0]["uri"]
                if video_link:
                    time_and_video = f"[{time}](<{video_link}>)"
                else:
                    time_and_video = time

                user_data = wr_entry["players"]
                user1_data = user_data[0]
                if user1_data["rel"] == 'user':
                    try:
                        user1_response = requests.get(user1_data["uri"], timeout=5)
                        user1_response.raise_for_status()
                        user1 = user1_response.json()["data"]
                    except requests.exceptions.Timeout:
                        return f"Speedrun.com API timed out when grabbing user data at {user1_data["uri"]}"
                    username1 = user1["names"]["international"]
                    user1_link = user1["weblink"]
                    player1 = f"**[{username1}]({user1_link})**"
                elif user1_data["rel"] == 'guest':
                    player1 = f"**{user1_data["name"]}**"

                if len(user_data) > 1:
                    user2_data = wr_entry["players"][1]
                    if user2_data["rel"] == 'user':
                        try:
                            user2_response = requests.get(user2_data["uri"], timeout=5)
                            user2_response.raise_for_status()
                            user2 = user2_response.json()["data"]
                        except requests.exceptions.Timeout:
                            return f"Speedrun.com API timed out when grabbing user2 data at {user2_data["uri"]}"
                        username2 = user2["names"]["international"]
                        user2_link = user2["weblink"]
                        player2 = f" and **[{username2}]({user2_link})**"
                    elif user2_data["rel"] == 'guest':
                        player2 = f" and **{user2_data["name"]}**"
                else:
                    player2 = ""

                response += f"\n**{subcat_name}: {time_and_video}** by {player1}{player2} ({date})"

    return response

def game_value_output(type, target, emote, players):
    game_name = target['name']
    if type == 'codes':
        return f"The available {emote} **Terminal Codes** for {target['emoji']} **{game_name}** are...\n{codes_output(target['codes'])}"
    if type == 'mods':
        url_name = game_name.replace(' ','+')
        return f"Check out mods for {target['emoji']} **{game_name}** here:\n<https://gamebanana.com/search?_sModelName=Mod&_sOrder=best_match&_sSearchString={url_name}&_idGameRow=23000&_csvFields=attribs>"
    if type == 'world record':
        return get_world_records(target, players)
    return f"The {emote} **{type.capitalize()}** requirement for {target['emoji']} **{game_name}** is...\n||{target[type]}||"

# shared function code used for grabbing cherry, gold, and gift values
async def get_game_value(interaction, game, number, type, emote, players=1):
    # no game or number specified
    if game is None and number is None:
        # check channel for number values to determine target game
        if interaction.channel.name[:1] in '0123456789' and interaction.channel.name[1:2] in '0123456789':
            if (int(interaction.channel.name[:2]) > 50 or int(interaction.channel.name[:2]) < 1):
                return await interaction.followup.send(content=f"Please specify a game or number to check the {type} for.", ephemeral=True)
            else:
                target = d[int(interaction.channel.name[:2])-1]
                await interaction.followup.send(game_value_output(type,target,emote,players))
        # no target game, give error
        else:
            return await interaction.followup.send(content=f"Please specify a game or number to check the {type} for.", ephemeral=True)
    # game and or number is specified
    else:
        # number specified
        if game is None and not number is None:
            if number > 51 or number < 0:
                return await interaction.followup.send(content=f"Your input was not valid.", ephemeral=True)
            else:
                if (number == 51 or number == 0) and (type == 'world record' or type == 'mods'):
                    return await interaction.followup.send(content=f"Your input was not valid.", ephemeral=True)
                target = d[number-1]
                await interaction.followup.send(game_value_output(type,target,emote,players))
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
                    if (target['name'] == 'The Terminal' or target['name'] == 'MT') and (type == 'world record' or type == 'mods'):
                        return await interaction.followup.send(content=f"Your input was not valid.", ephemeral=True)
                    await interaction.followup.send(game_value_output(type,target,emote,players))
                else:
                    await interaction.followup.send(content=f"Your input was not recognized.", ephemeral=True)
            # direct alias search succeeds
            else:
                target = target[0]
                await interaction.followup.send(game_value_output(type,target,emote,players))
        # error if both number and game are specified
        else:
            await interaction.followup.send(content="Please only specify the name or the number, not both.", ephemeral=True)

# ping test command
@client.tree.command(name="ping",description="Check that I am online!", guild=GUILD_ID)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('NICE ROD, PAL.')

# link to steam guides
@client.tree.command(name="guides",description="Get a link to steam guides for UFO 50!", guild=GUILD_ID)
async def guides(interaction: discord.Interaction):
    await interaction.response.send_message(content='Check out UFO 50 guides here:\n<https://steamcommunity.com/app/1147860/guides/>')

# link to tier list maker
@client.tree.command(name="tierlist",description="Get a link to the Tier List Maker for UFO 50", guild=GUILD_ID)
async def tier(interaction: discord.Interaction):
    await interaction.response.send_message(content='Make your own UFO 50 Tier List here:\n<https://tiermaker.com/create/ufo-50-games-16603442>', ephemeral=True)

# since people ask so much
@client.tree.command(name="whatsthatdemogame",description="for when people ask about that one demo game", guild=GUILD_ID)
async def whatsthatdemogame(interaction: discord.Interaction):
    await interaction.response.send_message(content='That one demo game is from <:elfazarshat:1292610893200359516> **Elfazar\'s Hat**.')

# link to wiki
@client.tree.command(name="wiki",description="Get a link to the UFO 50 wiki", guild=GUILD_ID)
async def wiki(interaction: discord.Interaction):
    await interaction.response.send_message(content='Check out the UFO 50 wiki here:\n<https://ufo50.miraheze.org/wiki/Main_Page>')

# link to bandcamp music
@client.tree.command(name="music",description="Get a link to UFO 50 music on Bandcamp", guild=GUILD_ID)
async def music(interaction: discord.Interaction):
    await interaction.response.send_message(content='Check out the music for UFO 50 here:\n<https://phlogiston.bandcamp.com/album/ufo-50>', ephemeral=True)

# link to gamebanana
@client.tree.command(name="moddinginfo",description="Get links for UFO 50 modding", guild=GUILD_ID)
async def moddinginfo(interaction: discord.Interaction):
    await interaction.response.send_message(content='UFO 50 GameBanana: <https://gamebanana.com/games/23000>\nUFO 50 Mod Loader: <https://gamebanana.com/tools/20160>\nModding Guide: <https://ufo50.miraheze.org/wiki/Guide_to_Modding_UFO_50#INSTALLING_MODS>')

# link to a game's mods
@client.tree.command(name="mods",description="Get a link to a UFO 50 game's mods", guild=GUILD_ID)
async def mods(interaction: discord.Interaction, game: str|None, number: int|None):
    await interaction.response.defer()
    await get_game_value(interaction, game, number, "mods", "")

# random game command
@client.tree.command(name="random",description="Get a random UFO 50 game suggestion", guild=GUILD_ID)
async def rnd(interaction: discord.Interaction):
    if random.randint(1,50) == 50:
        response = random.choice(suggest)
    else:
        game = random.choice(d)
        while game["name"] == "The Terminal" or game["name"] == "MT":
            game = random.choice(d)
        response = f'You should play {game["emoji"]} **{game["name"]}**.'
    await interaction.response.send_message(response)

# gift command
@client.tree.command(name="gift",description="Check gift requirement for a game", guild=GUILD_ID)
async def gift(interaction: discord.Interaction, game: str|None, number: int|None):
    await interaction.response.defer()
    await get_game_value(interaction, game, number, "gift", "<:GiftGet:1292627978601365636>")

# gold command
@client.tree.command(name="gold",description="Check gold requirement for a game", guild=GUILD_ID)
async def gold(interaction: discord.Interaction, game: str|None, number: int|None):
    await interaction.response.defer()
    await get_game_value(interaction, game, number, "gold", "<:TrophyGet:1291281233254289460>")

# cherry command
@client.tree.command(name="cherry",description="Check cherry requirement for a game", guild=GUILD_ID)
async def cherry(interaction: discord.Interaction, game: str|None, number: int|None):
    await interaction.response.defer()
    await get_game_value(interaction, game, number, "cherry", "<:CherryGet:1291281262870528073>")

# terminal codes command
@client.tree.command(name="codes",description="Check the terminal codes for a game", guild=GUILD_ID)
async def codes(interaction: discord.Interaction, game: str|None, number: int|None):
    await interaction.response.defer()
    await get_game_value(interaction, game, number, "codes", "<:InfoBuddyOK:1291972595952123984>")

# gift command
@client.tree.command(name="partyhouseseed",description="Check a seed for Party House or get a random one", guild=GUILD_ID)
async def getphseed(interaction: discord.Interaction, seed: int|None):
    await get_scenario_result(interaction, seed)

# world record command
@client.tree.command(name="wr",description="Check the speedrun world records for a game", guild=GUILD_ID)
async def worldrecord(interaction: discord.Interaction, game: str|None, number: int|None, players: int = 1):
    await interaction.response.defer()
    try:
        await get_game_value(interaction, game, number, "world record", "", players)
    except Exception as e:
        await interaction.followup.send("An error occurred while fetching world record data.", ephemeral=True)
        raise

# 50club command
@client.tree.command(name="50club",description="Check number of people with the cherry collector roles", guild=GUILD_ID)
async def fiftyclub(interaction: discord.Interaction):
    role50_pc_legacy = interaction.guild.get_role(1291962155469373451)
    role50_pc = interaction.guild.get_role(1293958225644884068)
    role50_switch_legacy = interaction.guild.get_role(1403267685932077117)
    role50_switch = interaction.guild.get_role(1403268500709048422)
    pc_legacy_members = len(role50_pc_legacy.members)
    pc_2025_members = len(role50_pc.members)
    pc_members = pc_legacy_members + pc_2025_members
    switch_legacy_members = len(role50_switch_legacy.members)
    switch_2025_members = len(role50_switch.members)
    switch_members = switch_legacy_members + switch_2025_members

    role_message = "Here are the number of discord members who currently hold the 50 cherries role:\n\n"
    role_message += f"**{pc_members}** members on **PC**\n"
    role_message += f"**{switch_members}** members on **Switch**"

    await interaction.response.send_message(role_message)

# Get token from fly.io
TOKEN = os.getenv('BEAN_TOKEN')

# initialize bot online
client.run(TOKEN)