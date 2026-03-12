import discord
from discord import app_commands
from discord.ext import commands
from thefuzz import fuzz
from utils import filter_name, urandom, get_answer
from world_record import get_world_records
import save_reader

# ban_list = []

# format 2d array for codes
def codes_output(codes, game_name=None):
    if len(codes) == 0:
        return '*No terminal codes available for this game.*'
    if game_name == 'MT':
        return f"||{'||\n||'.join(': '.join(str(x) for x in row) for row in codes)}||"
    return "\n".join(f"**{row[0]}**: {row[1]}" for row in codes)

def game_value_output(type, target, emote, d, players=1):
    game_name = target['name']
    if type == 'codes':
        return f"The available {emote} **Terminal Codes** for {target['emoji']} **{game_name}** are...\n\n{codes_output(target['codes'], game_name)}"
    if type == 'mods':
        url_name = game_name.replace(' ', '+')
        return f"Check out mods for {target['emoji']} **{game_name}** here:\n\n<https://gamebanana.com/search?_sModelName=Mod&_sOrder=best_match&_sSearchString={url_name}&_idGameRow=23000&_csvFields=attribs>"
    if type == 'world record':
        return get_world_records(target, players)
    if type == 'history':
        return f"The {emote} **History** for {target['emoji']} **{game_name}** is...\n\n\"{target[type]}\""
    return f"The {emote} **{type.capitalize()}** requirement for {target['emoji']} **{game_name}** is...\n\n**{target[type]}**"

# shared function used for grabbing history, gift, gold, cherry, codes, wr, and mods values
async def get_game_value(interaction, game, number, type, emote, d, game_list, players=1):
    invalid_types = {'world record', 'mods', 'history', 'gift', 'gold', 'cherry'}

    if game is None and number is None:
        channel_name = interaction.channel.name
        if channel_name[:1] in '0123456789' and channel_name[1:2] in '0123456789':
            channel_num = int(channel_name[:2])
            if not (1 <= channel_num <= 50):
                return await interaction.followup.send(content=f"Please specify a game or number to check the {type} for.", ephemeral=True)
            target = d[channel_num - 1]
            await interaction.followup.send(game_value_output(type, target, emote, d, players))
        else:
            return await interaction.followup.send(content=f"Please specify a game or number to check the {type} for.", ephemeral=True)

    elif number is not None and game is None:
        if not (0 <= number <= 51):
            return await interaction.followup.send(content="Your input was not valid.", ephemeral=True)
        if number in (0, 51) and type in invalid_types:
            return await interaction.followup.send(content="Your input was not valid.", ephemeral=True)
        target = d[number - 1]
        await interaction.followup.send(game_value_output(type, target, emote, d, players))

    elif game is not None and number is None:
        target = [x for x in d if game.lower() in x["alias"]]
        if len(target) == 0:
            best_match = 0
            best_match_game = ""
            for x in game_list:
                match = fuzz.ratio(game.lower(), x.lower())
                if match > best_match:
                    best_match_game = x
                    best_match = match
            if best_match >= 90:
                target = [x for x in d if best_match_game.lower() == x["name"].lower()][0]
                if target['name'] in ('The Terminal', 'MT') and type in invalid_types:
                    return await interaction.followup.send(content="Your input was not valid.", ephemeral=True)
                await interaction.followup.send(game_value_output(type, target, emote, d, players))
            else:
                await interaction.followup.send(content="Your input was not recognized.", ephemeral=True)
        else:
            target = target[0]
            await interaction.followup.send(game_value_output(type, target, emote, d, players))

    else:
        await interaction.followup.send(content="Please only specify the name or the number, not both.", ephemeral=True)

class BasicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, guild_id: discord.Object, d: list, game_list: list):
        self.bot = bot
        self.guild_id = guild_id
        self.d = d
        self.game_list = game_list

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.bot:
            return

        msg_ask = message.content.lower()
        if msg_ask.endswith('?'):
            import re
            msg_ask_clean = re.sub(r'[^a-z0-9 ]', '', msg_ask)
            if ' bean ' in msg_ask_clean or msg_ask_clean.startswith('bean ') or msg_ask_clean.endswith(' bean'):
                if re.sub(r'[^a-z]', '', msg_ask_clean) != 'bean':
                    await message.reply(get_answer(self.d))
                    return

        msg = message.content.lower().replace(',', '').replace('!', '')
        if "thanks bean" in msg or "thank you bean" in msg:
            if urandom(4) == 3:
                await message.reply("NICE SWORD, PAL.")
            else:
                await message.reply("NICE ROD, PAL.")
            return

        if "nice rod bean" in msg or "nice sword bean" in msg:
            user_name = message.author.nick or message.author.display_name or message.author.name
            user_name = filter_name(user_name)
            #if message.author.id in ban_list:
            #    user_name = ''
            await message.reply(f"THANKS {user_name.upper()}")
            return

        if not message.guild or not message.attachments:
            return

        file_extension = message.attachments[0].filename.split(".")[-1].lower()
        if file_extension == 'ufo':
            await save_reader.read_save(message, self.d)

    @app_commands.command(name="ping", description="Check that I am online!")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message('NICE ROD, PAL.')

    @app_commands.command(name="guides", description="Get a link to steam guides for UFO 50!")
    async def guides(self, interaction: discord.Interaction):
        await interaction.response.send_message(content='Check out UFO 50 guides here:\n<https://steamcommunity.com/app/1147860/guides/>')

    @app_commands.command(name="tierlist", description="Get a link to the Tier List Maker for UFO 50")
    async def tier(self, interaction: discord.Interaction):
        await interaction.response.send_message(content='Make your own UFO 50 Tier List here:\n<https://tiermaker.com/create/ufo-50-games-16603442>', ephemeral=True)

    @app_commands.command(name="whatsthatdemogame", description="for when people ask about that one demo game")
    async def whatsthatdemogame(self, interaction: discord.Interaction):
        await interaction.response.send_message(content='That one demo game is from <:elfazarshat:1292610893200359516> **Elfazar\'s Hat**.')

    @app_commands.command(name="wiki", description="Get a link to the UFO 50 wiki")
    async def wiki(self, interaction: discord.Interaction):
        await interaction.response.send_message(content='Check out the UFO 50 wiki here:\n<https://ufo50.miraheze.org/wiki/Main_Page>')

    @app_commands.command(name="music", description="Get a link to UFO 50 music on Bandcamp")
    async def music(self, interaction: discord.Interaction):
        await interaction.response.send_message(content='Check out the music for UFO 50 here:\n<https://phlogiston.bandcamp.com/album/ufo-50>', ephemeral=True)

    @app_commands.command(name="moddinginfo", description="Get links for UFO 50 modding")
    async def moddinginfo(self, interaction: discord.Interaction):
        await interaction.response.send_message(content='UFO 50 GameBanana: <https://gamebanana.com/games/23000>\nUFO 50 Mod Loader: <https://gamebanana.com/tools/20160>\nModding Guide: <https://ufo50.miraheze.org/wiki/Guide_to_Modding_UFO_50#INSTALLING_MODS>')

    @app_commands.command(name="mods", description="Get a link to a UFO 50 game's mods")
    async def mods(self, interaction: discord.Interaction, game: str | None, number: int | None):
        await interaction.response.defer()
        await get_game_value(interaction, game, number, "mods", "", self.d, self.game_list)

    @app_commands.command(name="spreadsheet", description="Get a link to the data spreadsheet")
    async def spreadsheet(self, interaction: discord.Interaction):
        await interaction.response.send_message(content='Check out the UFO 50 Data Spreadsheet by Phil here:\n<https://docs.google.com/spreadsheets/d/1w4lU9UpBfMbH7z95RiBF1rsyQv5YFhRsDA2AD7ZGb4A/edit?gid=722957170#gid=722957170>')

    @app_commands.command(name="loredoc", description="Get a link to the lore documents")
    async def loredoc(self, interaction: discord.Interaction):
        await interaction.response.send_message(content='Check out UFO 50 lore documents here:\n\n**Write-Up Doc: **<https://docs.google.com/document/d/1yuVnnJDmKKGrlTIGVn1Zykp9Tpn4rthGFei1gztRAN4>\n\n**Game Lore Sheet: **<https://docs.google.com/spreadsheets/d/1JqOjkGkXjoRvE_uE-nc4bTfFOzcudvKP3WDanGdaio0/edit?gid=2032987708#gid=2032987708>\n\n**Recurring Themes / Jingles: **<https://tinyurl.com/ufomotif>\n\n**Mapping Music to Mias: **<https://tinyurl.com/musicmias>')

    @app_commands.command(name="resourcepack", description="Get a link to the resource pack")
    async def resourcepack(self, interaction: discord.Interaction):
        await interaction.response.send_message(content='Check out the UFO 50 Resource Pack here:\nhttps://discord.com/channels/525973026429206530/1297045222445944872/1341267216716529725')

    @app_commands.command(name="quibblechart", description="Get a link to the Quibble Race Speed Chart")
    async def quibblechart(self, interaction: discord.Interaction):
        await interaction.response.send_message(content='Check out the Quibble Race Speed Chart by The2ndBrick here:\nhttps://discord.com/channels/525973026429206530/1251507008427921559/1405303783088717914')

    @app_commands.command(name="history", description="Check history text for a game")
    async def history(self, interaction: discord.Interaction, game: str | None, number: int | None):
        await interaction.response.defer()
        await get_game_value(interaction, game, number, "history", "<:research:1349941940514455654>", self.d, self.game_list)

    @app_commands.command(name="gift", description="Check gift requirement for a game")
    async def gift(self, interaction: discord.Interaction, game: str | None, number: int | None):
        await interaction.response.defer()
        await get_game_value(interaction, game, number, "gift", "<:GiftGet:1292627978601365636>", self.d, self.game_list)

    @app_commands.command(name="gold", description="Check gold requirement for a game")
    async def gold(self, interaction: discord.Interaction, game: str | None, number: int | None):
        await interaction.response.defer()
        await get_game_value(interaction, game, number, "gold", "<:TrophyGet:1291281233254289460>", self.d, self.game_list)

    @app_commands.command(name="cherry", description="Check cherry requirement for a game")
    async def cherry(self, interaction: discord.Interaction, game: str | None, number: int | None):
        await interaction.response.defer()
        await get_game_value(interaction, game, number, "cherry", "<:CherryGet:1291281262870528073>", self.d, self.game_list)

    @app_commands.command(name="codes", description="Check the terminal codes for a game")
    async def codes(self, interaction: discord.Interaction, game: str | None, number: int | None):
        await interaction.response.defer()
        await get_game_value(interaction, game, number, "codes", "<:InfoBuddyOK:1291972595952123984>", self.d, self.game_list)

    @app_commands.command(name="50club", description="Check number of people with the cherry collector roles")
    async def fiftyclub(self, interaction: discord.Interaction):
        role50_pc_legacy = interaction.guild.get_role(1291962155469373451)
        role50_pc = interaction.guild.get_role(1293958225644884068)
        role50_switch_legacy = interaction.guild.get_role(1403267685932077117)
        role50_switch = interaction.guild.get_role(1403268500709048422)
        pc_members = len(role50_pc_legacy.members) + len(role50_pc.members)
        switch_members = len(role50_switch_legacy.members) + len(role50_switch.members)
        role_message = (
            "Here are the number of discord members who currently hold the 50 cherries role:\n\n"
            f"**{pc_members}** members on **PC**\n"
            f"**{switch_members}** members on **Switch**"
        )
        await interaction.response.send_message(role_message)