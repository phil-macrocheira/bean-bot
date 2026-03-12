import base64
import json

async def read_save(message, d):
    try:
        file_content = await message.attachments[0].read()
        file_content = base64.b64decode(file_content).decode('utf-8')
        file_content = json.loads(file_content)
        totalDarkCherry = []
        totalCherry = []
        totalGift = []
        totalGold = []
        darkCherryMsg = ""
        noDarkCherryMsg = ""
        cherryMsg = ""
        goldMsg = ""

        for x in range(1, 51):
            target = [y for y in d if x == int(y["game_id"])]
            target = target[0]
            if f"game0_gameWin{x}" in file_content:
                gameWin = file_content[f"game0_gameWin{x}"]
                if gameWin in (1.0, '1.0', 1, '1'):
                    totalGold.append(int(target["num"]))
                elif gameWin in (2.0, '2.0', 2, '2'):
                    totalCherry.append(int(target["num"]))

            if f"game0_gardenWin{x}" in file_content:
                gardenWin = file_content[f"game0_gardenWin{x}"]
                if gardenWin in (1.0, '1.0', 1, '1'):
                    totalGift.append(int(target["num"]))

            if f"game0_gameDarkWin{x}" in file_content:
                darkWin = file_content[f"game0_gameDarkWin{x}"]
                if darkWin in (10.0, '10.0', 10, '10'):
                    totalDarkCherry.append(int(target["num"]))

        totalGold.sort()
        totalCherry.sort()
        totalDarkCherry.sort()

        if len(totalDarkCherry) > 0:
            for x in totalDarkCherry:
                target = [y for y in d if x == int(y["num"])][0]
                darkCherryMsg += target["emoji"]

        if len(totalCherry) > 0:
            dark_set = set(totalDarkCherry)
            for x in totalCherry:
                if x in dark_set:
                    continue
                target = [y for y in d if x == int(y["num"])][0]
                cherryMsg += target["emoji"]

        if len(totalGold) > 0:
            for x in totalGold:
                target = [y for y in d if x == int(y["num"])][0]
                goldMsg += target["emoji"]

        if len(darkCherryMsg) > 0:
            darkCherryMsg = f"`Dark Cherries:` **{len(totalDarkCherry)}**\n{darkCherryMsg}\n"
            noDarkCherryMsg = f" ({len(totalCherry) - len(totalDarkCherry)} non-dark-cherried)"

        if len(cherryMsg) > 0:
            cherryMsg = '\n' + cherryMsg

        if len(goldMsg) > 0:
            goldMsg = '\n' + goldMsg

        await message.reply(
            f"{darkCherryMsg}`Cherries:` **{len(totalCherry)}**{noDarkCherryMsg}{cherryMsg}\n"
            f"`Golds:` **{len(totalGold) + len(totalCherry)}** ({len(totalGold)} non-cherried){goldMsg}\n"
            f"`Gifts:` **{len(totalGift)}**"
        )

    except ValueError:
        await message.reply(content="I was not able to parse the save file data.")