import discord
from discord import app_commands
from discord.ext import commands
import requests


# Standalone function imported by basic_commands.game_value_output
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
        return "Speedrun.com API timed out when grabbing category variables"
    if v.status_code != 200:
        return f"Error: Status code {v.status_code} from speedrun.com API"

    variable_data = v.json()["data"]

    for var in variable_data:
        var_name = var["name"]
        if var_name == 'Player Count' and game != 'Fist Hell':
            player_var_id = var["id"]
            if players == 2:
                player2_id, _ = list(var["values"]["values"].items())[1]
                player_var = f"&var-{player_var_id}={player2_id}"
                mode_2p = True
            else:
                player1_id, _ = list(var["values"]["values"].items())[0]
                player_var = f"&var-{player_var_id}={player1_id}"
        elif var_name in ('Restrictions', 'Upgrades', 'Difficulty', 'Cave Extensions'):
            other_id, other_data = list(var["values"]["values"].items())[0]
            if game == 'Pilot Quest':
                other_id, other_data = list(var["values"]["values"].items())[1]
            other_var_name = f" **({other_data['label']})**"
        elif var_name == 'Item Restrictions':
            _, other_data2 = list(var["values"]["values"].items())[0]
            other_var_name2 = f" **({other_data2['label']})**"

    for var in variable_data:
        if var["name"] == 'Subcategory':
            subcat_var_id = var["id"]
            for subcat_id, subcat_data in var["values"]["values"].items():
                subcat_name = subcat_data["label"]
                if subcat_name in ('Blindfolded', 'GETM-EOUT'):
                    continue

                try:
                    r = requests.get(
                        f"https://www.speedrun.com/api/v1/leaderboards/v1pl7876/category/{category_id}"
                        f"?var-{subcat_var_id}={subcat_id}{player_var}&top=1",
                        timeout=5
                    )
                    r.raise_for_status()
                except requests.exceptions.Timeout:
                    return f"Speedrun.com API timed out when grabbing leaderboard for {subcat_name}"
                if r.status_code != 200:
                    return f"Error: Status code {r.status_code} from speedrun.com API"

                data = r.json()["data"]
                player_num_text = " **(2 Player)**" if mode_2p else ""

                if not init:
                    game_link_id = data["weblink"].split('#')[1]
                    game_link = (
                        f"https://www.speedrun.com/UFO_50?h={game_link_id}-gold"
                        f"&x={category_id}-{subcat_var_id}.{subcat_id}"
                    )
                    response += (
                        f"The current world records for {emoji} **[{game}]({game_link})**"
                        f"{other_var_name}{other_var_name2}{player_num_text} are:\n"
                    )
                    init = True

                if len(data["runs"]) == 0:
                    continue

                wr_entry = data["runs"][0]["run"]
                date = wr_entry["date"]

                time_sec = wr_entry["times"]["primary_t"]
                m, s = divmod(time_sec, 60)
                m, s = int(m), int(s)
                ms = round((time_sec - (m * 60) - s) * 1000)
                time_str = f"{m}m {s}s {ms:03d}ms"

                video_link = wr_entry["videos"]["links"][0]["uri"]
                time_and_video = f"[{time_str}](<{video_link}>)" if video_link else time_str

                user_data = wr_entry["players"]
                user1_data = user_data[0]
                if user1_data["rel"] == 'user':
                    try:
                        user1_response = requests.get(user1_data["uri"], timeout=5)
                        user1_response.raise_for_status()
                        user1 = user1_response.json()["data"]
                    except requests.exceptions.Timeout:
                        return f"Speedrun.com API timed out when grabbing user data at {user1_data['uri']}"
                    player1 = f"**[{user1['names']['international']}]({user1['weblink']})**"
                elif user1_data["rel"] == 'guest':
                    player1 = f"**{user1_data['name']}**"

                player2 = ""
                if len(user_data) > 1:
                    user2_data = user_data[1]
                    if user2_data["rel"] == 'user':
                        try:
                            user2_response = requests.get(user2_data["uri"], timeout=5)
                            user2_response.raise_for_status()
                            user2 = user2_response.json()["data"]
                        except requests.exceptions.Timeout:
                            return f"Speedrun.com API timed out when grabbing user2 data at {user2_data['uri']}"
                        player2 = f" and **[{user2['names']['international']}]({user2['weblink']})**"
                    elif user2_data["rel"] == 'guest':
                        player2 = f" and **{user2_data['name']}**"

                response += f"\n**{subcat_name}: {time_and_video}** by {player1}{player2} ({date})"

    return response


class WorldRecord(commands.Cog):
    def __init__(self, bot: commands.Bot, guild_id: discord.Object, d: list, game_list: list):
        self.bot = bot
        self.guild_id = guild_id
        self.d = d
        self.game_list = game_list

    @app_commands.command(name="wr", description="Check the speedrun world records for a game")
    async def worldrecord(
        self, interaction: discord.Interaction, game: str | None, number: int | None, players: int = 1
    ):
        await interaction.response.defer()
        try:
            # Imported inside the method to avoid circular imports at module load time
            # (basic_commands imports get_world_records from this file at the top level)
            from basic_commands import get_game_value
            await get_game_value(interaction, game, number, "world record", "", self.d, self.game_list, players)
        except Exception as e:
            await interaction.followup.send("An error occurred while fetching world record data.", ephemeral=True)
            raise