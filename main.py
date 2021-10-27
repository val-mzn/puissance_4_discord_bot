import os
from discord.activity import Game
from dotenv import load_dotenv
from discord.ext import commands
from power4 import Power4
from threading import Timer
import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix="!")

# Contient tout les différentes parti avec comme identitfiant l'id du premier message envoyer
# Permet de gérer plusieurs parti en meme temps avec différentes personnes

games = {}
emoji = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣']
help_message = """
`!p4` *(Lance une parti de puissance 4)*
`!p4 bot/b` *(Lance une parti de puissance 4 avec un ordinateur)*
`!p4 surrender/s` *(permet d'adandonner la partie en cours)*
`!p4 jeton/j <emoji>` *(permet de customizer son jeton)*
"""

def isEmoji(char):
    try:
        unicode = ord(char)
    except:
        unicode = ord(char[0])
    if unicode > int("0x1F600", 16) and unicode < int("0x1F64F", 16): return True
    if unicode > int("0x1F300", 16) and unicode < int("0x1F5FF", 16): return True
    if unicode > int("0x1F680", 16) and unicode < int("0x1F6FF", 16): return True
    if unicode > int("0x2600", 16) and unicode < int("0x26FF", 16): return True
    if unicode > int("0x2700", 16) and unicode < int("0x27BF", 16): return True
    if unicode > int("0xFE00", 16) and unicode < int("0xFE0F", 16): return True
    if unicode > int("0x1F900", 16) and unicode < int("0x1F9FF", 16): return True
    if unicode > int("0x1F1E6", 16) and unicode < int("0x1F1FF", 16): return True
    return False

def customPiece(name, piece):
    data = open("p_data.txt", "r", encoding='utf-8')
    rows = data.readlines()

    find = False
    i = 0
    for r in rows:
        if name in r:
            rows[i] = name + ":" + piece + "\n"
            find = True
        i += 1

    if not find:
        rows.append(name + ":" + piece + "\n") 

    a_file = open("p_data.txt", "w", encoding='utf-8')
    a_file.writelines(rows)
    a_file.close()

def getGame(id):
    for key, value in games.items():
        if(key == id):
            return value

async def checkHasAGame(name):
    all_ready_game = False
    for key, value in games.items():
        if(name == value.p1_name):
            all_ready_game = True
        if(name == value.p2_name):
            all_ready_game = True
    return all_ready_game

async def addGame(ctx, use_bot):
    if not await checkHasAGame(ctx.message.author.name):
        # on initialize le jeu et on ajoute le nom des joueurs 
        game = Power4()
        game.p1 = ctx.message.author.id
        game.p1_name = ctx.message.author.name

        if(use_bot):
            game.p2 = 0
            game.p2_name = "API Bot"
            game.turn = True

        # jeton custom
        data = open("p_data.txt", "r", encoding='utf-8')
        rows = data.readlines()
        for r in rows:
            if ctx.message.author.name in r:
                game.p1_color = re.search(':(.*)\n', r).group(1)
            
        # on envoie la grille 
        msg = await ctx.send(game.getGrid())
        games[msg.id] = game

        # on ajoute les controlles avec les réaction
        for i in range(0, 7):
            await msg.add_reaction(emoji[i])
    else:
        await ctx.send("Tu as deja une parti en cours")

@client.command()
async def p4(ctx: commands.Context, *args):
    if(args):
        if(args[0] == "help" or args[0] == "h"):
            await ctx.send(help_message)
        elif(args[0] == "surrender" or args[0] == "s"):
            current_game = None
            winner_id = 0
            for key, value in games.items():
                if(ctx.message.author.name == value.p1_name):
                    current_game = key
                    winner_id = 2
                if(ctx.message.author.name == value.p2_name):
                    current_game = key
                    winner_id = 1
            game = getGame(current_game)
            game.win = winner_id
            msg = await ctx.fetch_message(current_game)
            await msg.edit(content=game.getGrid())
        elif(args[0] == "jeton" or args[0] == "j"):
            if(len(args) != 1 and isEmoji(args[1])):
                customPiece(ctx.message.author.name, args[1])         
                await ctx.send("Ton jeton a bien été customisé ("+ args[1] + ")")
            else:
                await ctx.send("Utilise: !p4 <jeton/j> <emoji> ")

        elif(args[0] == "bot" or args[0] == "b"):
            await addGame(ctx, True)
        else:
            await ctx.send("parametres inconnu '!p4 h' for help")
    else:
        await addGame(ctx, False)


@client.event
async def on_reaction_add(reaction, user):

    # le bot ne réagi pas a ces propres reactions logique
    if not user.bot:

        # on recupere l'instance de la parti avec l'id du message original
        game = getGame(reaction.message.id)

        # si le joueurs 2 n'est pas défini on ajoute celui qui a réagi au message
        if(user.id != game.p1 and game.p2 == ""):
            game.p2 = user.id
            game.p2_name = user.name
            
            # jeton custom
            data = open("p_data.txt", "r", encoding='utf-8')
            rows = data.readlines()
            for r in rows:
                if user.name in r:
                    game.p2_color = r[-2]

        # test des différents controlle
        for i in range(0, 7):
            if reaction.emoji == emoji[i]:
                if(game.turn):

                    # on ajoute un jeton pour p1
                    game.addTokenPlayerOne(user.id, i)

                    # si joue contre bot on ajoute jeton
                    if(game.p2 == 0):
                        game.addTokenPlayerTwo(0, game.getMove())
                        
                else:
                    # on ajoute un jeton pour p2
                    game.addTokenPlayerTwo(user.id, i)

                # on modifie la grille et on retire la reaction
                await reaction.message.edit(content=game.getGrid())
                await reaction.message.remove_reaction(emoji[i], user)
        
        # si gagner on enleve les controlles
        if(game.win != 0):
            del games[reaction.message.id]
            for i in range(0,7):
                await reaction.message.remove_reaction(emoji[i], reaction.message.author)

client.run(TOKEN)
