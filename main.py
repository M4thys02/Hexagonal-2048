import pygame as pg
import math
import numpy as np
import random as r
import sys
import pyjokes
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pg.init()

colors = {0: (255, 255, 255), # Barvy pro self.base = 2
            2: (9, 246, 112),
            4: (18, 222, 147),
            8: (18, 222, 181),
            16: (18, 222, 222),
            32: (18, 181, 222),
            64: (18, 137, 222),
            128: (24, 83, 201),
            256: (35, 24, 201),
            512: (142, 24, 201),
            1024: (212, 72, 234),
            2048: (254, 47, 226),
            4096: (254, 47, 147),
            8192: (254, 47, 85),
            16384: (254, 1, 1),
            32768: (255, 35, 0),
            65536: (250, 62, 0),

            3: (112, 9, 246), # Barvy pro self.base = 3
            9: (147, 18, 222),
            27: (181, 18, 222),
            81: (222, 18, 222),
            243: (222, 18, 181),
            729: (222, 18, 137),
            2187: (201, 24, 83),
            6561: (201, 35, 24),
            19683: (201, 142, 24),
            59049: (234, 212, 72),
            177147: (226, 254, 47),
            531441: (147, 254, 47),
            1594323: (85, 254, 47),
            4782969: (1, 254, 1,),
            14348907: (0, 255, 35),
            43046721: (0, 250, 62),
            
            5: (9, 112, 246), # Barvy pro self.base = 5
            25: (18, 147, 222),
            125: (18, 181, 222),
            625: (18, 222, 222),
            3125: (18, 222, 181),
            15625: (18, 222, 137),
            78125: (24, 201, 83),
            390625: (35, 201, 24),
            1953125: (142, 201, 24),
            9765625: (212, 234, 72),
            48828125: (254, 226, 47),
            244140625: (254, 147, 47),
            1220703125: (254, 85, 47),
            6103515625: (254, 1, 1),
            30517578125: (255, 0, 35),
            152587890625: (250, 0, 62)}


def calculate_centres(hex_size, spacing): # Funkce pro navrácení středů všech šestiúhelníků
    hex_centres = []
    n = 3
    vyska_y = 0
    indent = 3
    for row in range(3):
        for col in range(n):
                souradnice_x = col * (1.5 * hex_size + spacing * 3) + 45 * indent + col * 10 + 5 * (3-row)
                souradnice_y = row * (1.5 * hex_size + spacing) + 55 + 5 * row
                center = (souradnice_x, souradnice_y)
                hex_centres.append(center)
        n += 1
        vyska_y += souradnice_y
        indent -= 1

    # Dolní polovina hexagonální sítě
    n = 4
    for row in range(2):
        for col in range(n):
                souradnice_x = col * (1.5 * hex_size + spacing * 3) + 45 * (2+row) + 5 + col * 10 + (row+1) * 5
                souradnice_y = row * (1.5 * hex_size + spacing) + vyska_y - 110 + 5 * row
                center = (souradnice_x, souradnice_y)
                hex_centres.append(center)
        n -= 1
    return hex_centres

# Button - třída pro tlačítka v menu, ve hře, apod.
class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.pole = self.image.get_rect()
        self.pole.topleft = (x, y)
        self.clicked = False

    def make_button(self, screen):
        screen.blit(self.image, (self.pole.x, self.pole.y))

    def button_clicked(self):
        mouse_pos = pg.mouse.get_pos()
        akce = False
        if self.pole.collidepoint(mouse_pos):
            if pg.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                akce = True

        if pg.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return akce

# HexagonTile - třída pro vlastnosti hexagonálního políčka
class HexagonTile:
    def __init__(self, center, size, color):
        self.center = center
        self.size = size
        self.color = color
        self.orientation_angle = 30  # Rotace hexagonu o 30 stupňů
        self.vertices = self.calculate_vertices()

    def calculate_vertices(self):
        vertices = []
        for i in range(6):
            angle = math.radians(60 * i + self.orientation_angle)
            x = self.center[0] + self.size * math.cos(angle)
            y = self.center[1] + self.size * math.sin(angle)
            vertices.append((x, y))
        return vertices

    def draw(self, surface):
        pg.draw.polygon(surface, self.color, self.vertices, width=5)

# MainGame - TŘÍDA PRO SAMOTNOU HRU
class MainGame():
    def __init__(self):
        self.num = 5
        self.hex_size = 50
        self.spacing = 5
        self.hex_centres = calculate_centres(self.hex_size, self.spacing)

        self.highest_number = 0

        self.base = 2

        self.sirka_okna = 5 * self.hex_size * 2
        self.vyska_okna = self.sirka_okna + 125

        pg.init()

        # self.okno = pg.display.set_mode((800,800)) # Příkaz na tvrobu okna - slouží pouze k testovacím účelům
        self.okno = pg.display.set_mode((self.sirka_okna, self.vyska_okna))
        pg.display.set_caption("Hexagonal 2048")

        hex_2 = pg.image.load(resource_path("images/hex_2_button.png")).convert_alpha()
        hex_3 = pg.image.load(resource_path("images/hex_3_button.png")).convert_alpha()
        hex_5 = pg.image.load(resource_path("images/hex_5_button.png")).convert_alpha()
        menu_b = pg.image.load(resource_path("images/menu_button.png")).convert_alpha()
        end_try = pg.image.load(resource_path("images/end_try_button.png")).convert_alpha()
        small_menu = pg.image.load(resource_path("images/small_menu_button.png")).convert_alpha()
        rules = pg.image.load(resource_path("images/rules_button.png")).convert_alpha()
        out = pg.image.load(resource_path("images/exit_button.png")).convert_alpha()
        win = pg.image.load(resource_path("images/win_button.png")).convert_alpha()

        self.hex_2_button = Button(100, 150, hex_2)
        self.hex_3_button = Button(200, 150, hex_3)
        self.hex_5_button = Button(300, 150, hex_5)
        self.menu_button = Button(125, 360, menu_b)
        self.end_try_button = Button(175, 460, end_try)
        self.small_menu_button = Button(175, 450, small_menu)
        self.rules_button = Button(175, 275, rules)
        self.exit_button = Button(175, 450, out)
        self.win_button = Button(175, 460, win)

        # Blok pro načtení fontu - pokud má hráč font již nainstalovaný, stačí použít zakomentované příkazy
        self.font_big = pg.font.Font(resource_path("zektonbo.ttf"), 49) # self.font_big = pg.font.SysFont("zekton", 49, True)
        self.font_medium = pg.font.Font(resource_path("zektonbo.ttf"), 25) # self.font_medium = pg.font.SysFont("zekton", 25, True)
        self.font_small = pg.font.Font(resource_path("zektonbo.ttf"), 16) # self.font_small = pg.font.SysFont("zekton", 16, True)


    def WriteText(self, hod_pole, y, x): # Funkce pro vypsání textu do středu všech šestiúhelníků
        if hod_pole != 0 and hod_pole != 1: # Zobrazuje všechna čísla z self.herni_pole POUZE pokud nejsou rovna 0 nebo 1
            delka_hod = len(str(hod_pole))
            if delka_hod < 9:
                m = 41 - delka_hod * 3
            elif 8 < delka_hod and delka_hod < 13:
                m = 14 - (24 - 9) * 2
            else:
                m = 7 - (delka_hod - 13)

            # Blok pro vypsání textu - zobrazí text na konkrétní souřadnice
            # fnt = pg.font.SysFont("zekton", m, True) # Příkaz pokud má dotyčný hráč font předinstalovaný na svém PC
            fnt = pg.font.Font(resource_path("zektonbo.ttf"), m)
            napis_co = fnt.render(f"{hod_pole}", True, colors[hod_pole])

            if x == 0:
                napis_kam = napis_co.get_rect(center = (self.hex_centres[y][0],self.hex_centres[y][1]))
                self.okno.blit(source = napis_co, dest = napis_kam)

            elif x == 1:
                napis_kam = napis_co.get_rect(center = (self.hex_centres[y+3][0],self.hex_centres[y+3][1]))
                self.okno.blit(source = napis_co, dest = napis_kam)

            elif x == 2:
                napis_kam = napis_co.get_rect(center = (self.hex_centres[y+7][0],self.hex_centres[y+7][1]))
                self.okno.blit(source = napis_co, dest = napis_kam)

            elif x == 3:
                napis_kam = napis_co.get_rect(center = (self.hex_centres[y+12][0],self.hex_centres[y+12][1]))
                self.okno.blit(source = napis_co, dest = napis_kam)

            elif x == 4:
                napis_kam = napis_co.get_rect(center = (self.hex_centres[y+16][0],self.hex_centres[y+16][1]))
                self.okno.blit(source = napis_co, dest = napis_kam)
        

    def Make_a_board(self): # Funkce pro vytvoření herní plochy (jednotlivých šestiúhelníků) a jejich vybarvení na základě čísla, které obsahují
        i = 0
        for x in range(self.num):
            for y in range(self.num):
                tiles = []
                hod_pole = int(self.herni_pole[y][x])
                barevnost = int(self.herni_pole[x][y])

                if self.base == 2 and barevnost != 1:
                    center = (self.hex_centres[i][0], self.hex_centres[i][1])
                    tiles.append(HexagonTile(center, self.hex_size, colors[barevnost]))
                    i += 1
                
                if self.base == 3 and barevnost != 1:
                    center = (self.hex_centres[i][0], self.hex_centres[i][1])
                    tiles.append(HexagonTile(center, self.hex_size, colors[barevnost]))
                    i += 1
                
                if self.base == 5 and barevnost != 1:
                    center = (self.hex_centres[i][0], self.hex_centres[i][1])
                    tiles.append(HexagonTile(center, self.hex_size, colors[barevnost]))
                    i += 1

                # Cyklus na vykreslení herního pole na self.okno
                for tile in tiles:
                    tile.draw(self.okno)

                self.WriteText(hod_pole,x,y)


    def Update_highest_num(self): # Funkce pro vracení hodnoty nevyššího čísla v herním poli
        for x in range(self.num):
            for y in range(self.num):
                if int(self.herni_pole[x][y]) > self.highest_number:
                    self.highest_number = int(self.herni_pole[x][y])


    def Add_number(self): # Funkce přidávající číslo do herního pole - JE ZDE VÝSTUP HERNÍHO POLE DO KONZOLE!
            null_ctverce = list(zip(*np.where(self.herni_pole == 0)))

            for pozice in r.sample(null_ctverce, 1):
                self.herni_pole[pozice] = self.base
            # print(self.herni_pole, "\n") # Tisk herního pole při každém tahu


    def Move_diagonal_LR(self, direction): # Pohyb čísel v diagonále zleva doprava
        zeros = 3
        for souradnice in range(0, 5):
            diagonal = []

            # Blok pro vytvoření diagonál šestíúhelníku
            if souradnice == 0:
                for i in range (3):
                    diagonal.append(self.herni_pole[i+2][0])

            elif souradnice == 1:
                diagonal.append(self.herni_pole[1][0])
                for i in range(3):
                    diagonal.append(self.herni_pole[i+2][1])

            elif souradnice == 2:
                diagonal.append(self.herni_pole[0][0])
                diagonal.append(self.herni_pole[1][1])
                for i in range(3):
                    diagonal.append(self.herni_pole[i+2][2])

            elif souradnice == 3:
                diagonal.append(self.herni_pole[0][1])
                diagonal.append(self.herni_pole[1][2])
                for i in range(2):
                    diagonal.append(self.herni_pole[i+2][3])

            elif souradnice == 4:
                for i in range(3):
                    diagonal.append(self.herni_pole[i][i+2])

            obracene = False
            if direction in "D":
                obracene = True
                diagonal = diagonal[::-1]

            diagonal = self.Combine(diagonal)

            diagonal = diagonal + (zeros - len(diagonal)) * [0]

            if obracene:
                diagonal = diagonal[::-1]

            # Blok pro navrácení vyhodnocené diagonály na správné indexy herního pole
            if souradnice == 0:
                for i in range(3):
                    self.herni_pole[i+2][0] = diagonal[i]
            elif souradnice == 1:
                self.herni_pole[1][0] = diagonal[0]
                for i in range(3):
                    self.herni_pole[i+2][1] = diagonal[i+1]
            elif souradnice == 2:
                self.herni_pole[0][0] = diagonal[0]
                self.herni_pole[1][1] = diagonal[1]
                for i in range(3):
                    self.herni_pole[i+2][2] = diagonal[i+2]
            elif souradnice == 3:
                self.herni_pole[0][1] = diagonal[0]
                self.herni_pole[1][2] = diagonal[1]
                for i in range(2):
                    self.herni_pole[i+2][3] = diagonal[i+2]
            elif souradnice == 4:
                for i in range(3):
                    self.herni_pole[i][i+2] = diagonal[i]
            
            # Výpočet pro řádky 3 a 4 (druhá půlka herního pole)
            zeros += 1
            if souradnice == 2:
                zeros = 4
            if souradnice == 3:
                zeros = 3


    def Move_diagonal_RL(self, direction): # Pohyb čísel v diagonále zprava doleva
        zeros = 3
        for souradnice in range(0, 5):
            diagonal = []

            # Blok pro vytvoření diagonál šestíúhelníku
            if souradnice == 0:
                for i in range (3):
                    diagonal.append(self.herni_pole[i][0])

            elif souradnice == 1:
                for i in range(3):
                    diagonal.append(self.herni_pole[i][1])
                diagonal.append(self.herni_pole[3][0])

            elif souradnice == 2:
                for i in range(3):
                    diagonal.append(self.herni_pole[i][2])
                diagonal.append(self.herni_pole[3][1])
                diagonal.append(self.herni_pole[4][0])

            elif souradnice == 3:
                for i in range(2):
                    diagonal.append(self.herni_pole[i+1][3])
                diagonal.append(self.herni_pole[3][2])
                diagonal.append(self.herni_pole[4][1])

            elif souradnice == 4:
                for i in range(3):
                    diagonal.append(self.herni_pole[i+2][4-i])

            obracene = False
            if direction in "G":
                obracene = True
                diagonal = diagonal[::-1]

            diagonal = self.Combine(diagonal)

            diagonal = diagonal + (zeros - len(diagonal)) * [0]

            if obracene:
                diagonal = diagonal[::-1]

            # Blok pro navrácení vyhodnocené diagonály na správné indexy herního pole
            if souradnice == 0:
                for i in range(3):
                    self.herni_pole[i][0] = diagonal[i]
            elif souradnice == 1:
                for i in range(3):
                    self.herni_pole[i][1] = diagonal[i]
                self.herni_pole[3][0] = diagonal[3]
            elif souradnice == 2:
                for i in range(3):
                    self.herni_pole[i][2] = diagonal[i]
                self.herni_pole[3][1] = diagonal[3]
                self.herni_pole[4][0] = diagonal[4]
            elif souradnice == 3:
                for i in range(2):
                    self.herni_pole[i+1][3] = diagonal[i]
                self.herni_pole[3][2] = diagonal[2]
                self.herni_pole[4][1] = diagonal[3]
            elif souradnice == 4:
                for i in range(3):
                    self.herni_pole[i+2][4-i] = diagonal[i]
            
            # Výpočet pro řádky 3 a 4 (druhá půlka herního pole)
            zeros += 1
            if souradnice == 2:
                zeros = 4
            if souradnice == 3:
                zeros = 3


    def Move_LR(self, direction): # Pohyb čísel v horizontálním směru
        ones = 2
        zeros = 3
        for souradnice in range(0, 5):

            line = self.herni_pole[souradnice, :zeros]

            obracene = False
            if direction in "R":
                obracene = True
                line = line[::-1]

            line = self.Combine(line)

            line = line + (zeros - len(line)) * [0]

            if obracene:
                line = line[::-1]

            self.herni_pole[souradnice, :zeros] = line

            ones -= 1
            zeros += 1

            if souradnice == 2: # Výpočet pro řádky 2 a 3 (druhá půlka herního pole)
                zeros = 4
                ones = 1
            if souradnice == 3:
                zeros = 3
                ones = 2


    def Combine(self, line): # Kombinování čísel v "line" - pomocná funkce, kterou si zavolají "move_XX", vrátí zkobinovaný segment
        outcome = [0]

        line = [cislo for cislo in line if cislo != 0]

        for i in line:
            if i == outcome[len(outcome) - 1]:
                outcome[len(outcome) - 1] *= int(self.base)
                outcome.append(0)

            else:
                outcome.append(i)

        outcome = [cislo for cislo in outcome if cislo != 0]
        return outcome


    def Is_game_over(self): # Funkce pro kontrolu zda hra může ještě pokračovat (zda hráč má k dispozici validní tah)

        kopie_pole = self.herni_pole.copy()

        for direction in "LRUDQG":
            if direction in "LR":
                self.Move_LR(direction)
            elif direction in "UD":
                self.Move_diagonal_LR(direction)
            elif direction in "QG":
                self.Move_diagonal_RL(direction)

            if (self.herni_pole == kopie_pole).all() == False:
                self.herni_pole = kopie_pole
                return False
            
        return True


    def Game_over(self): # Ukončuje hru v případě, že nejsou k dispozici validní tahy
        self.okno.fill((50,50,50))

        self.okno.blit(self.font_big.render("Game Over!", True, (255,255,255)), (100, 50))
        self.okno.blit(self.font_medium.render("Your highest number was: ", True, (255, 255, 255)), (75, 150))
        self.menu_button.make_button(self.okno)

        # Kód pro vykreslení šestiúhelníku a vysnání nejvyšší dosažené hodnoty v právě ukončené hře
        pg.draw.polygon(self.okno,colors[self.highest_number],[(250,200),(315,238),(315,312),(250,350),(184,312),(184,238),],width=5)
        delka_hod = len(str(self.highest_number))
        if delka_hod < 9:
            m = 51 - delka_hod * 3
        elif 8 < delka_hod and delka_hod < 13:
            m = 24 - (24 - 9) * 2
        else:
            m = 17 - (delka_hod - 13)
        
        # fnt = pg.font.SysFont("zekton", m, True)
        fnt = pg.font.Font(resource_path("zektonbo.ttf"), m)
        napis_co = fnt.render(f"{self.highest_number}", True, colors[self.highest_number])
        napis_kam = napis_co.get_rect(center = (250,275))
        self.okno.blit(source = napis_co, dest = napis_kam)


        pg.display.update()
        pg.time.wait(500)


        running_game_over = True
        while running_game_over:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running_game_over = False

            if self.menu_button.button_clicked():
                running_game_over = False
                self.highest_number = 0 # Resetování nevyššího dosaženého čísla
                self.Menu()


    def PLAY(self): # HLAVNÍ FUNKCE HRY - zajišťuje fungování a samotnou hru
        # Vytvoření herního pole
        self.herni_pole = np.zeros((self.num, self.num))
        self.herni_pole[0][3], self.herni_pole[0][4] = 1, 1
        self.herni_pole[1][4], self.herni_pole [3][4] = 1, 1
        self.herni_pole[4][3], self.herni_pole [4][4] = 1, 1

        self.Add_number() # Přidání čísla

        helping = pg.image.load(resource_path("images/helping_movement.png")).convert_alpha()

        pg.display.update()

        running_play = True
        while running_play: # Game loop
            
            self.end_try_button.make_button(self.okno) # Vytvoření tlačítka pro konec hry
            self.okno.blit(helping,(10,460)) # Vytvoření nápovědy pro hráče (ovládání hry)
            self.Make_a_board() # Vytvoří tabulku (herní pole)
            pg.display.update()

            for event in pg.event.get():
                
                puvodni_tabulka = self.herni_pole.copy()

                if event.type == pg.QUIT:
                    running_play = False
                    self.Exit()

                elif event.type == pg.KEYDOWN:
                    
                    # Blok příkazů pro validní pohyby
                    if event.key == pg.K_a:
                        self.Move_LR("L")

                    elif event.key == pg.K_d:
                        self.Move_LR("R")

                    elif event.key == pg.K_w:
                        self.Move_diagonal_LR("U")

                    elif event.key == pg.K_x:
                        self.Move_diagonal_LR("D")

                    elif event.key == pg.K_e:
                        self.Move_diagonal_RL("Q")
                
                    elif event.key == pg.K_y:
                        self.Move_diagonal_RL("G")
                    
                    # Kontrola zda hra může pokračovat - zda jsou k dispozici validní tahy a herní pole není zaplněné
                    if self.Is_game_over():
                        running_play = False
                        self.Game_over() # Konec hry
                    
                    if (self.herni_pole == puvodni_tabulka).all() == False:
                        self.Add_number()
                        self.Update_highest_num()
            
            if self.highest_number == 65536 or self.highest_number == 43046721 or self.highest_number == 152587890625: # Spouští easteregg funkci - obrazovku výhry
                running_play = False
                self.highest_number = 0
                self.Win_num()

            if self.end_try_button.button_clicked():
                running_play = False
                self.Game_over()

            self.okno.fill((50,50,50))


    def Menu(self): # Funkce pro tvorbu menu samotné hry - první obrazovka, co hráč vidí
        pg.display.flip()
        self.okno.fill((50,50,50))

        self.hex_2_button.make_button(self.okno)
        self.hex_3_button.make_button(self.okno)
        self.hex_5_button.make_button(self.okno)
        self.rules_button.make_button(self.okno)
        self.exit_button.make_button(self.okno)

        self.okno.blit(self.font_big.render("HEXAGONAL 2048", True, (255, 255, 255)), (7.5, 10))
        self.okno.blit(self.font_medium.render("Choose your base number:", True, (255, 255, 255)), (75,100))

        pg.display.update()
        pg.time.wait(500) # Tohle tady musí být kvůli funkčnosti pygame - když na dvou různých obrazovkách jsou tlačítka na stejných
                            # pozicích a jedno překlikává z jedné obrazovky na druhou, tak se bez tohoto příkazu zmačknout oboje (například z obrazovky RULES -> MENU -> dojde k EXITU)
        running_menu = True

        while running_menu:
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running_menu = False
                    self.Exit()


            if self.hex_2_button.button_clicked():
                self.base = 2
                self.PLAY()
                running_menu = False

            elif self.hex_3_button.button_clicked():
                self.base = 3
                self.PLAY()
                running_menu = False

            elif self.hex_5_button.button_clicked():
                self.base = 5
                self.PLAY()
                running_menu = False
            
            elif self.rules_button.button_clicked():
                self.Rules()
                running_menu = False
            
            elif self.exit_button.button_clicked():
                running_menu = False
                self.Exit()

            pg.display.update()


    def Rules(self): # Funkce pro obrazovku s pravidly
        pg.display.flip()
        self.okno.fill((50,50,50))

        self.small_menu_button.make_button(self.okno)
        picture = pg.image.load(resource_path("images/directions.png")).convert_alpha()
        self.okno.blit(picture, (125, 175))
        self.okno.blit(self.font_medium.render("RULES OF THE GAME", True, (255, 255, 255)), (120, 10))
        self.okno.blit(self.font_small.render("Each letter indicates a direction for the movement", True, (255, 255, 255)), (50, 50))
        self.okno.blit(self.font_small.render("of the tiles on the board", True, (255, 255, 255)), (155, 75))
        self.okno.blit(self.font_small.render("The goal is to get as high number as possible.", True, (255, 255, 255)), (60, 100))
        self.okno.blit(self.font_small.render("The point is to stack numbers on each other,", True, (255, 255, 255)), (70,125))
        self.okno.blit(self.font_small.render("for example 2x2=4 or 9x9=27", True, (255, 255, 255)), (125, 150))

        pg.display.update()

        running_rules = True

        while running_rules:
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running_rules = False

            if self.small_menu_button.button_clicked():
                self.Menu()
            
        pg.display.update()


    def Exit(self): # Funkce pro ukončení hry
        pg.quit()
        sys.exit()


    def Win_num(self): # Easteregg funkce, když hráč dosáhne čísla self.base^16
        self.okno.fill((50,50,50))
        self.win_button.make_button(self.okno)
        self.Make_a_board()

        pg.display.update()

        running_win = True
        while running_win:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running_win = False

            if self.win_button.button_clicked():
                self.Easteregg()
                running_win = False


    def Easteregg(self): # V souvislosti na Win_num() funkci - zobrazí custom výherní obrazovku
        self.okno.fill((50,50,50))
        self.small_menu_button.make_button(self.okno)
        self.okno.blit(self.font_big.render("YOU WIN,", True, (255,255,255)), (130, 25))
        self.okno.blit(self.font_big.render("CONGRATULATION!", True, (255,255,255)), (10, 100))
        self.okno.blit(self.font_small.render("You achieve 16th power of the base number.", True, (255,255,255)), (70,175))
        self.okno.blit(self.font_small.render("Here is your reward from pyjokes:", True, (9,246,112)), (105,225))

        joke = pyjokes.get_joke(language='en', category='all')
        linky = joke.split(" ")

        if len(linky) > 7:
            index = 0
            for i in range(len(linky) // 7):
                radek = []
                for j in range(0,7):
                    radek.append(linky[j+7*i])
                    index += 1
                segment = " ".join(map(str, radek))
                self.okno.blit(self.font_small.render(segment, True, (255,201,14)), (75,300+25*i))
                i = 7*i

            zbytek = []
            for i in range(len(linky) % 7):
                zbytek.append(linky[index + i])
            segment_zb = " ".join(map(str, zbytek))
            self.okno.blit(self.font_small.render(segment_zb, True, (255,201,14)), (75,300 + len(linky) // 7 * 25))
        
        else:
            self.okno.blit(self.font_small.render(joke, True, (255,201,14)), (75,300))

        pg.display.update()
        pg.time.wait(500)

        running_easteregg = True
        while running_easteregg:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running_easteregg = False

            if self.small_menu_button.button_clicked():
                running_easteregg = False
                self.Menu()


if __name__ == "__main__":
    game = MainGame()
    game.Menu()
