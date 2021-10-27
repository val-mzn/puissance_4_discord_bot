from discord.errors import PrivilegedIntentsRequired
from discord.ext.commands.core import before_invoke
from discord.utils import parse_time
from random import randrange
import requests
import json

class Power4:
    def __init__(self):
        self.turn = False
        self.p1 = ""
        self.p2 = ""
        self.p1_name = "?????"
        self.p2_name = "?????"
        self.win = 0

        # selection aléatoire de couleurs pour les joueurs
        color = ['🔴', '🟠', '🟡', '🟢', '🔵', '🟣']
        self.p1_color = color[randrange(len(color))]
        self.p2_color = color[randrange(len(color))]
        while(self.p1_color == self.p2_color):
            self.p2_color = color[randrange(len(color))]

        # creation de la grille
        self.grid = []
        for i in range(0, 7):
            self.grid.append([0,0,0,0,0,0,0])

    # permet d'ajouter un jeton du joueur 1 dans une colone
    def addTokenPlayerOne(self, player, col):
        if(player == self.p1):
            if(self.grid[0][col] == 0):
                count = 0
                while(self.grid[count][col] == 0 and count < 6):
                    count += 1
                if(self.grid[count][col] == 0):
                    self.grid[count][col] = 1
                else:
                    self.grid[count-1][col] = 1

                # on passe au tour suivant
                if self.turn == False: 
                    self.turn = True
                elif self.turn == True: 
                    self.turn = False

    # permet d'ajouter un jeton du joueur 2 dans une colone
    def addTokenPlayerTwo(self, player, col):
        if(player == self.p2):
            if(self.grid[0][col] == 0):
                count = 0
                while(self.grid[count][col] == 0 and count < 6):
                    count += 1
                if(self.grid[count][col] == 0):
                    self.grid[count][col] = 2
                else:
                    self.grid[count-1][col] = 2
                
                # on passe au tour suivant
                if self.turn == False: 
                    self.turn = True
                elif self.turn == True: 
                    self.turn = False

    # vérifie les collonnes horizontalement, verticalement et les diagonales
    # on ajoute chaque case a une chaine de charactères et on vérifie si elle contient '1111' ou '2222'
    # si c'est le cas c'est qu'il y a 4 jeton aligner et on renvoit le joueur qui a gagner
    def verifWin(self):

        # Vertical
        for i in range(0, 7):
            row = ""
            for j in range(0, 7):
                row += str(self.grid[i][j])
            if "1111" in row:
                return 1
            elif "2222" in row:
                return 2
                
        # Horizontal
        for i in range(0, 7):
            row = ""
            for j in range(0, 7):
                row += str(self.grid[j][i])
            if "1111" in row:
                return 1
            elif "2222" in row:
                return 2
        
        # Diagonal 1
        for i in range(0, 4):
            row = ""
            for j in range(0, 4 + i):
                row += str(self.grid[3 + i-j][j])
            if "1111" in row:
                return 1
            elif "2222" in row:
                return 2

        # Diagonal 1
        for i in range(0, 3):
            row = ""
            for j in range(0, 6 - i):
                row += str(self.grid[6-j][i+j+1])
            if "1111" in row:
                return 1
            elif "2222" in row:
                return 2
        
        # Diagonal 2
        for i in range(0, 4):
            row = ""
            for j in range(0, 4 + i):
                row += str(self.grid[3 + i-j][6-j])
            if "1111" in row:
                return 1
            elif "2222" in row:
                return 2

        # Diagonal 2
        for i in range(0, 3):
            row = ""
            for j in range(0, 6 - i):
                row += str(self.grid[6-j][6-(i+j+1)])
            if "1111" in row:
                return 1
            elif "2222" in row:
                return 2

        # recupère la ligne du haut si elle est complete renvoit le code pour égalité
        row = ""
        for i in range(0, 7):
            row += str(self.grid[0][i])
        if '0' not in row:
            return 3

        # si pas de gagants on renvoit le code 0
        return 0
       

    # revoit la grille avec le jeu
    def getGrid(self):

        if(self.verifWin() == 1):
            self.win = 1
        elif(self.verifWin() == 2):
            self.win = 2
        elif(self.verifWin() == 3):
            self.win = 3

        s = ""

        # remplisage de la grille avec les jetons
        for i in range(0, 7):
            for j in range(0, 7):
                if(self.grid[i][j] == 1):
                    s += self.p1_color + " "
                elif(self.grid[i][j] == 2):
                    s += self.p2_color + " "
                else:
                    s += '⬛️ '

            # ajout du texte sur le coté droit
            if (i== 1):
                s += " "*8 +self.p1_color + " : " + str(self.p1_name)
                if(self.win == 1):
                    s += " 🏆"
                elif(self.win == 2):
                    s += " 💩"
                elif(self.win == 3):
                    s += " 😑"
            elif(i== 2):
                s += " "*8 +self.p2_color + " : " + str(self.p2_name)
                if(self.win == 2):
                    s += " 🏆"
                elif(self.win == 1):
                    s += " 💩"
                elif(self.win == 3):
                    s += " 😑"
            elif(i== 4):
                if(self.win == 1):
                    s += " "*8 + "Les " + self.p1_color + " on gagnéeee"
                elif(self.win == 2):
                    s += " "*8 + "Les " + self.p2_color + " on gagnéeee"
                elif(self.win == 3):
                    s += " "*8 + "Egalité"
                else:
                    if (self.turn):
                        s += " "*8 + "Au tour " + self.p1_color + " de jouer"
                    else:
                        s += " "*8 + "Au tour " + self.p2_color + " de jouer"

            s += "\n"
        
        # ajout de l'index permettant au repère
        if(self.win == 0):
            s += "1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ "
        return s
    
    # Appelle d'API pour que le bot joue 
    def getMove(self):

        #on crée les paramètres
        data = ""
        for i in range(0, 7):
            for j in range(0, 7):
                data += str(self.grid[i][j])
        player = 2
        if self.turn: player = 1

        # envoie de la requete
        url = "http://kevinalbs.com/connect4/back-end/index.php/getMoves?board_data=" + data + "&player=" + str(player)

        # transformation de <byte> a json
        res = requests.post(url).content.decode("utf-8") 
        data = json.loads(res)

        # on récupère la collones avec la valeur la plus élever (c'est le coup a jouer)
        max = data['0']
        index_max = 0
        for i in data:
            if(data[i] > max): 
                max = data[i]
                index_max = i

        # et on renvoit le coup
        return int(index_max);