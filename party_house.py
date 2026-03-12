import discord
from discord import app_commands
from discord.ext import commands
import random
import re
import math

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
    "DANCER": 7, "HIPPY": 4, "CUTE DOG": 7, "SECURITY": 4, "WRESTLER": 9,
    "WATCH DOG": 4, "SPY": 8, "DRIVER": 3, "PRIVATE I.": 4, "GRILLMASTR": 5,
    "ATHLETE": 6, "MR POPULAR": 5, "CELEBRITY": 11, "COMEDIAN": 5,
    "PHOTOGRAPHR": 5, "CATERER": 5, "TICKET TKR": 4, "AUCTIONEER": 9,
    "MONKEY": 3, "ROCK STAR": 5, "GANGSTER": 6, "GAMBLER": 7, "WEREWOLF": 5,
    "MASCOT": 5, "INTROVERT": 4, "COUNSELOR": 7, "STYLIST": 7,
    "BARTENDER": 11, "WRITER": 8, "CLIMBER": 12, "CUPID": 8, "MAGICIAN": 5,
    "GREETER": 5, "CHEERLEADR": 5,
    "ALIEN": 40, "DINOSAUR": 25, "LEPRECHAUN": 50, "GENIE": 55,
    "MERMAID": 30, "DRAGON": 30, "GHOST": 45, "UNICORN": 45, "SUPERHERO": 50
}

CHAR_START = 11
CHAR_END = 44
CHAR_PRESTIGE_START = 50
CHAR_PRESTIGE_END = 58


class PartyHouse(commands.Cog):
    def __init__(self, bot: commands.Bot, guild_id: discord.Object):
        self.bot = bot
        self.guild_id = guild_id
        self.rng_state_1 = -1
        self.rng_state_2 = -1

    def rng_random(self):
        self.rng_state_1 = (65192 * (self.rng_state_1 & 65535)) + ((self.rng_state_1 & 4294901760) >> 16)
        self.rng_state_2 = (64473 * (self.rng_state_2 & 65535)) + ((self.rng_state_2 & 4294901760) >> 16)
        return (((self.rng_state_1 & 65535) << 16) + self.rng_state_2) & 4294967295

    def rng_random_int(self, arg0, arg1):
        r = self.rng_random()
        return arg0 + math.floor(((arg1 - arg0 + 1) * r) / 4294967296)

    def generate_scenario(self, seed):
        mask = 1431655765
        self.rng_state_1 = 1253089769 ^ (seed & mask)
        self.rng_state_2 = 2342871706 ^ (seed & ~mask)
        for _ in range(20):
            self.rng_random()
        deck = []
        num_reg_chars = 11
        num_prestige_chars = 13 - num_reg_chars
        for _ in range(num_reg_chars):
            while True:
                rand_char = self.rng_random_int(CHAR_START, CHAR_END)
                if rand_char not in deck and rand_char <= 44:
                    deck.append(rand_char)
                    break
            self.rng_random()
        for _ in range(num_prestige_chars):
            while True:
                rand_char = self.rng_random_int(CHAR_PRESTIGE_START, CHAR_PRESTIGE_END)
                if rand_char not in deck and rand_char <= 58:
                    deck.append(rand_char)
                    break
            self.rng_random()
        return deck

    def sort_deck(self, deck):
        character_names = [character_types[index] for index in deck]
        sort_keys = [pop_costs[re.search(r'`(.*?)`', name).group(1)] for name in character_names]
        combined = sorted(zip(deck, sort_keys), key=lambda x: x[1])
        sorted_deck, _ = zip(*combined)
        return sorted_deck

    @app_commands.command(name="partyhouseseed", description="Check a seed for Party House or get a random one")
    async def getphseed(self, interaction: discord.Interaction, seed: int | None):
        if seed is None:
            seed = random.randint(0, 999999)
        elif not isinstance(seed, (int, float)):
            return await interaction.response.send_message(
                content="Please specify a valid number value between **000000** and **999999**.", ephemeral=True
            )
        elif seed < 0 or seed > 999999:
            return await interaction.response.send_message(
                content="That seed value is not between **000000** and **999999**.", ephemeral=True
            )
        seed = int(seed)
        deck = self.sort_deck(self.generate_scenario(seed))
        deck_names = [character_types[index] for index in deck]
        await interaction.response.send_message(f"**SEED {str(seed).zfill(6)}**\n\n{' '.join(deck_names)}")