import os
import re

# filter usernames
def filter_name(name):
    if name is None or name == '':
        return None
    name = re.split(r'[\U0001F300-\U0001FAFF]', name, 1)[0]    # remove anything after an emoji
    name = name.split('(', 1)[0]                               # remove anything after a left paren
    name = name.split('{', 1)[0]                               # remove anything after a left curly brace
    name = re.sub(r'[^A-Za-z0-9 ]', '', name)                  # alphanumeric only
    return name.rstrip()

def urandom(n: int) -> int:
    k = (n - 1).bit_length()
    byte_len = (k + 7) // 8
    max_val = 1 << (byte_len * 8)
    limit = max_val - (max_val % n)
    while True:
        r = int.from_bytes(os.urandom(byte_len), "big")
        if r < limit:
            return (r % n) + 1

def get_random_game(d):
    num = urandom(50)
    return d[num - 1]

def get_answer(d):
    num = urandom(1000)
    if num <= 375:
        response = 'YES'
    elif num <= 750:
        response = 'NO'
    elif num <= 800:
        response = 'MOST LIKELY'
    elif num <= 850:
        response = 'PROBABLY NOT'
    elif num <= 900:
        response = 'IT IS POSSIBLE'
    elif num <= 925:
        response = 'YOU ALREADY KNOW THE ANSWER'
    elif num <= 950:
        response = 'IT\'S A SECRET'
    elif num <= 960:
        response = 'I DON\'T KNOW'
    elif num <= 970:
        response = 'I DO NOT UNDERSTAND'
    elif num <= 980:
        response = 'REMEMBER WHAT THEY SAY ABOUT MAKING OMELETTES'
    elif num <= 990:
        response = 'HA HA. THAT\'S A GOOD ONE.'
    elif num <= 999:
        game = get_random_game(d)
        response = f'THE SOLUTION TO YOUR TROUBLES LIES IN {game["emoji"]} **{game["name"]}**.'
    elif num == 1000:
        response = 'ASK ME AGAIN IN <:barbuta:1292612809682583564> **BARBUTA**'
    return response