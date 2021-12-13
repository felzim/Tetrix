import sys
import pygame               #
import pygame.freetype      # für Textfelder
import random               #
import glob                 # zum Laden von Bildern in den Chache


####################### Tetrix 1.0
########## Autor: Felix Zimmermann
#
#
#     Klassen und Funktionen
#
#     @@@ Klasse Tetris @@@
#     -------------------------------------------------------
#               - create_new_block()            |  Blocks erstellen und zeichnen
#               - draw_block()                  |
#               - draw_next_block()             |
#     ------------------------------------------------------
#               - move_left_ok()                |  Prüfung ob Bewegung nach links/rechts/unten bzw Rotation möglich
#               - move_right_ok()               |
#               - vertical_clash()              |
#               - rotate_block_ok()             |
#     ------------------------------------------------------
#               - block_finished()              |  wenn ein Block heruntergefallen ist:
#               - calc_points()                 |  Verarbeiten, Punkte berechnen, Zeilen löschen
#               - delete_rows()                 |
#               - game_over_check()             |
#               - reset()                       |  alle Felder löschen
#     ------------------------------------------------------
#               - update()                      |  wird von der main()-Funktion aus 25x pro Sekunde aufgerufen
#
#    @@@ Klasse Tetriblock @@@
#    -------------------------------------------------------
#               - give_blocks()                 |  Block abfragen und Block bewegen
#               - give_blocks_nextrotation()    |
#               - move_left()                   |
#               - move_right()                  |
#               - rotate()                      |
#               - rotate_jumpright()            |
#               - rotate_jumpleft()             |
#               - move_down()                   |
#    -------------------------------------------------------
#
#               - main()                          Steuerungsfunktion
#

# Die Hauptklasse des Spiels: zeichnet und löscht das Feld, prüft alle möglichen Bewegungen, berechnet Statistiken, verwaltet die Modi etc.
class Tetris():

    def __init__(self):

        # Pygame starten und Bildschirm definieren
        self.screen = pygame.display.set_mode((600, 700)) # Größe des gesamten Spiels
        pygame.display.set_caption("Tetrix 1.0")

        # Verschachtelte Liste für Zustände der Felder.
        # Hier kommen alle Blöcke rein, die bereits platziert wurden
        self.belegte_felder = []
        for i in range(20):                         # Spielfeld: 20 Zeilen x 10 Spalten
            new_line = [0] * 10                     # alle Felder zu Beginn mit Nullen füllen
            self.belegte_felder.append(new_line)

        images = glob.glob('/img/*.png')             # alle Bilder in den Cache vorladen
        for image in images:
            self.get_image(image)

        # Zum Schluss: Spiel starten, indem ein Block generiert wird
        self.create_new_block()


    # Zustände und Statistiken
    state = 'run'               # In welchem Status befindet sich das Spiel?
                                #       run:        Spiel startet
                                #       demo:       Spiel ohne Clock
                                #       pause:      Pause-Bildschirm
                                #       gameover:   Game Over-Screen

    with_graphic = True         # mit oder ohne Grafikelemente spielen

    game_speed = 800            # Millisekunden, die es dauert, bis der Stein ein Feld weiter herunter fällt
    rows_last = []              # zuletzt abgebaute Reihen. Liste, um Reihennummer zu haben
    rows_gesamt = 0             # Anzahl der insgesamt schon abgebauten Reihen (zur Levelberechnung)
    points = 0                  # Punktezähler
    level = 1                   # Level-Zähler
    tetriblock = None           # Block, der aktuell im Spiel ist. Wird bei Spielbeginn generiert
    next_tetriblock = None      # nächster Block, zur Vorschau

    # Pixel-Größe des Tetris-Spielfelds (nicht des gesamten Spiel-Displays!)
    width = 300                 # Größe des Spielfelds
    height = 600                #
    margin_left = 40            # Abstand links vom Display zum Spielfeld
    margin_top = 40             # Abstand oben vom Display zum Spielfeld

    # Farben definieren - Farben für die Blöcke werden in Klasse Tetriblock definiert
    bg_color = (237, 246, 249)      # Hintergrundfarbe des Hauptfensters
    bg_color_field = (38, 70, 83)   # Hintergrundfarbe des Spielfelds
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Speicher für Statusmeldungen
    global msg
    msg = [""]                   # für den Demo-Modus

    # Cache, um Bilder schneller zu laden
    image_cache = {}

    # Funktion, um Bild aus dem Cache zu laden
    def get_image(self, key):
        if not key in self.image_cache:
            self.image_cache[key] = pygame.image.load(key)
        return self.image_cache[key]


    # neuen Baustein generieren & immer einen im Voraus generieren für Preview
    def create_new_block(self):

        if self.next_tetriblock is None:
            self.next_tetriblock = Tetriblock(3, 0)

        self.tetriblock = self.next_tetriblock
        self.next_tetriblock = Tetriblock(3, 0)


    # Funktion, um den aktuellen Stein auf das Spielfeld zeichnen
    def draw_block(self):

        temp = self.tetriblock.give_blocks()
        self.color = self.tetriblock.colors[self.tetriblock.type]

        for block in range(4):
            #Hintergrundfarbe der Blöcke zeichnen
            pygame.draw.rect(self.screen, self.color, [(temp[block][1] + self.tetriblock.x) * 30 + self.margin_left,
                                                  (temp[block][0] + self.tetriblock.y) * 30 + self.margin_top, 30, 30], 0)

            # nur, wenn wenn Grafik eingeschaltet ist. Bilder statt Hintergrundfarbe verwenden
            if self.with_graphic == True:
                self.img = self.tetriblock.img[self.tetriblock.type]
                block1_img = self.get_image(f'{self.img}')
                self.screen.blit(block1_img, ((temp[block][1] + self.tetriblock.x) * 30 + self.margin_left,
                                                  (temp[block][0] + self.tetriblock.y) * 30 + self.margin_top))

            # Umrandung der Blöcke zeichnen
            pygame.draw.rect(self.screen, self.black, [(temp[block][1] + self.tetriblock.x) * 30 + self.margin_left,
                                                       (temp[block][0] + self.tetriblock.y) * 30 + self.margin_top, 30,
                                                       30], 1)

    # wie draw_block(), allerdings für Preview
    def draw_next_block(self):

        margin_preview_left = 400
        margin_preview_top = 350

        temp = self.next_tetriblock.give_blocks()
        color = self.next_tetriblock.colors[self.next_tetriblock.type]

        for block in range(4):
            # Hintergrundfarbe der Blöcke zeichnen
            pygame.draw.rect(self.screen, color, [temp[block][1]*30 + margin_preview_left , temp[block][0]*30 + margin_preview_top, 30, 30], 0)

            # nur, wenn wenn Grafik eingeschaltet ist. Bilder statt Hintergrundfarbe verwenden
            if self.with_graphic == True:
                self.img = self.next_tetriblock.img[self.next_tetriblock.type]
                block1_img = self.get_image(f'{self.img}')
                self.screen.blit(block1_img, (temp[block][1] * 30 + margin_preview_left,
                                          temp[block][0] * 30 + margin_preview_top))

            # Umrandung der Blöcke zeichnen
            pygame.draw.rect(self.screen, (24,24,24),
                             [temp[block][1] * 30 + margin_preview_left, temp[block][0] * 30 + margin_preview_top, 30,
                              30], 1)


    # Prüfen, ob bei Bewegung nach links Kollision mit anderen Steinen horizontal auftritt
    def move_left_ok(self):

        temp = self.tetriblock.give_blocks()

        # Kollision mit linker Wand?
        for i in range(4):
            if (temp[i][1] + self.tetriblock.x) <= 0:
                msg.append("Bewegung nach links nicht möglich, Wand")
                return False

        # Kollision mit anderen Steinen horizontal links?
        for i in range(20):
            for a in range(10):
                if self.belegte_felder[i][a] > 0:
                    for x in range(4):
                        if [temp[x][0] + self.tetriblock.y, temp[x][1] + self.tetriblock.x] == [i, a + 1]:
                            msg.append("Bewegung nach links nicht möglich, belegtes Feld")
                            return False

        # keine Kollisionen, alles ok
        return True

    # Prüfen, ob bei Bewegung nach rechts Kollision mit anderen Steinen horizontal auftritt
    def move_right_ok(self):

        temp = self.tetriblock.give_blocks()

        # Kollision mit rechter Wand?
        for i in range(4):
            if (temp[i][1] + self.tetriblock.x) >= 9:
                msg.append("Bewegung nach rechts nicht möglich, Wand")
                return False

        # Kollision mit anderen Steinen horizontal rechts?
        for i in range(20):
            for a in range(10):
                if self.belegte_felder[i][a] > 0:
                    for x in range(4):
                        if [temp[x][0] + self.tetriblock.y, temp[x][1] + self.tetriblock.x] == [i, a - 1]:
                            msg.append("Bewegung nach rechts nicht möglich, belegtes Feld")
                            return False

        # keine Kollisionen, alles ok
        return True


    # Prüfen, ob eine Rotation möglich ist.
    def rotate_block_ok(self):

        result = "true"
        msg_for_debug = ""
        temp_next = self.tetriblock.give_blocks_nextrotation()  # nicht Daten vom jetzigen Block, sondern vom nächsten holen

        # gäbe es nach der Drehung eine Kollision mit anderen Feldern?
        for i in range(20):
            for a in range(10):
                if self.belegte_felder[i][a] > 0:
                    for x in range(4):
                        if [temp_next[x][0] + self.tetriblock.y, temp_next[x][1] + self.tetriblock.x] == [i, a]:
                            result = "false"
                            msg_for_debug = "Rotation verhindert, Kollision"

        # Drehung an der linken Wand verhindern, bei der ein Teil des Blocks außerhalb des Spielfelds liegt
        # Rückmeldung: entweder Rotation mit 1 Feld nach links springen möglich, oder gar nicht
        for x in range(4):
            if temp_next[x][1] + self.tetriblock.x < 0:
                result = "jump-right"
                msg_for_debug = "jump nach rechts"
                for i in range(20):
                    for a in range(10):
                        if self.belegte_felder[i][a] > 0:
                            for x in range(4):
                                if [temp_next[x][0] + self.tetriblock.y, temp_next[x][1] + self.tetriblock.x +1] == [i,a]:
                                    msg_for_debug = "Rotation mit jump nach rechts verhindert, Kollision"
                                    result="false"

        # Drehung an der rechten Wand verhindern, bei der ein Teil des Blocks außerhalb des Spielfelds liegt
        # Rückmeldung: entweder Rotation mit 1 oder 2 Felder nach links springen möglich, oder gar nicht
        for x in range(4):
            if temp_next[x][1] + self.tetriblock.x > 9:
                result = "jump-left"
                msg_for_debug = "Rotation mit jump nach links"
                if temp_next[x][1] + self.tetriblock.x > 10:
                    result = "jump-left2"
                    msg_for_debug = "Rotation mit 2x jump nach links"

                for i in range(20):
                    for a in range(10):
                        if self.belegte_felder[i][a] > 0:
                            for x in range(4):
                                if [temp_next[x][0] + self.tetriblock.y, temp_next[x][1] + self.tetriblock.x -1] == [i,a]:
                                    result="false"
                                    msg_for_debug = "Rotation mit jump nach links verhindert, Kollision"

        # Drehung am unteren Rand verhindern
        for x in range(4):
            if temp_next[x][0] + self.tetriblock.y > 19:
                result = "false"
                msg_for_debug = "Rotation verhindert, unterer Rand"

        # Debug-Messages filtern, sodass keine dopppelten Meldungen mit aufgenommen werden (Schleifen werden oft durchlaufen)
        if msg_for_debug != "":
            if msg[-1] != msg_for_debug:
                    msg.append(msg_for_debug)

        # String mit "true", "false", "jump-left", "jump-left2" oder "jump-right"
        return result


    # Prüfen, ob eine vertikale Kollision stattfindet. Entweder am unteren Rand angekommen oder es liegen bereits Steine
    def vertical_clash(self):

        msg_for_debug = ""
        temp = self.tetriblock.give_blocks()

        for i in range(4):

            # am unteren Rand angekommen?
            if (temp[i][0] + self.tetriblock.y) >= 19:
                self.block_finished()
                self.create_new_block()
                msg.append("Stein am unteren Rand angekommen")

                return True

            # vertikale Kollision mit bereits liegenden Bausteinen?
            # wenn ja, aktuellen Block sofort in das Raster übertragen und neuen Block erstellen
            for i in range(20):
                for a in range(10):
                    if self.belegte_felder[i][a] > 0:
                        for x in range(4):
                            if [temp[x][0] + self.tetriblock.y, temp[x][1] + self.tetriblock.x] == [i - 1, a]:
                                self.block_finished()
                                self.create_new_block()
                                msg.append("Stein auf anderem Stein gelandet")
                                return True

        # keine Kollision, aktueller Block kann nach unten verschoben werden
        return False


    # Baustein ist heruntergefallen: nun alle nötigen Prüfungen ausführen, ggf. Reihen löschen und Punkte berechnen
    def block_finished(self):

        temp = self.tetriblock.give_blocks()

        # heruntergefallenen Block in die Feldmatrix eintragen
        for i in range(20):
            for a in range(10):
                for x in range(4):
                    if [i,a] == [temp[x][0] + self.tetriblock.y, temp[x][1] + self.tetriblock.x]:
                            self.belegte_felder[i][a] = self.tetriblock.type

        # komplettierte Reihen zählen
        counter_fields = 0
        counter_rows = []
        for i in range(20):
            for a in range(10):
                if self.belegte_felder[i][a] > 0:
                    counter_fields += 1
                if counter_fields >= 10:
                    counter_rows.append(i)
            counter_fields = 0

        self.rows_last = counter_rows

        # wenn Reihen komplettiert wurden, Punkte berechnen und Reihen löschen
        if len(self.rows_last) > 0:
            self.calc_points()
            self.delete_rows()


    # Punkteberechnung bei komplettierten Reihen
    def calc_points(self):

        self.rows_gesamt += len(self.rows_last)

        # Level berechnen: alle 5 Reihen ein Level aufsteigen
        if self.rows_gesamt >= 5:
            self.level = int((self.rows_gesamt + 5) / 5)   # float in int. Bei Umwandlung wird Nachkommastelle abgeschnitten

            # Geschwindigkeit des Spiels neu berechnen - mit jedem Level fallen die Steine schneller
            self.game_speed = int(1000 * (0.80 **self.level))
            pygame.time.set_timer(falling_event, self.game_speed)

        # Punkte berechnen: Scoring-System nach dem Vorbild des Game-Boy-Tetris:
        if len(self.rows_last) == 1:                         # Das Scoring-System des Game-Boy-Tetris benutzte folgende Formel zur Berechnung von Punkten:
            self.points += 40 * (self.level + 1)             #
        elif len(self.rows_last) == 2:                       #     Level    1 Reihe         2 Reihen        3 Reihen        4 Reihen
            self.points += 100 * (self.level + 1)            #     n 	    40 * (n + 1) 	100 * (n + 1) 	300 * (n + 1) 	1200 * (n + 1)
        elif len(self.rows_last) == 3:
            self.points += 300 * (self.level + 1)
        elif len(self.rows_last) == 4:
            self.points += 1200 * (self.level + 1)
        else:
            pass # darf eigentlich nicht passieren


    # komplettierte Reihen löschen und an index 0 eine neue, mit Nullen gefüllt Liste anlegen
    def delete_rows(self):

        self.img = self.tetriblock.img[self.tetriblock.type]

        for i in range(20):
            if i in self.rows_last:
                del self.belegte_felder[i]
                new_line = [0] * 10
                self.belegte_felder.insert(0, new_line)

        # Fade-Effekt benutzen, wenn mit Bildern gearbeitet wird
        if self.with_graphic == True:

                for i in self.rows_last:

                    for x in range(50):  # für Fade-Effekt

                        for a in range(10):

                            # nachträglich Bilder für die gelöschten Felder erstellen, um sie dann auszublenden

                            block1_img = pygame.image.load("img/bg.png")
                            block1_img.set_alpha(x)
                            self.screen.blit(block1_img, (a * 30 + self.margin_left, i * 30 + self.margin_top))

                            pygame.draw.rect(self.screen, self.black,
                                         [a * 30 + self.margin_left, i * 30 + self.margin_top, 30, 30], 1)

                        # Bildschirm aktualisieren und 5 MS warten -> Fade-Effekt + Runterfallen
                        pygame.display.flip()
                        pygame.time.delay(5)


    # Prüfen, ob Game Over
    def game_over_check(self):

        for i in range(10):
            if self.belegte_felder[0][i] > 0:
                self.state = "gameover"


    # für Neustart des Spiels: Spielfeld, alle Statistiken und Geschwindigkeit zurücksetzen
    def reset(self):

        # Spielfeld zurücksetzen
        self.belegte_felder = []
        for i in range(20):
            new_line = [0] * 10
            self.belegte_felder.append(new_line)

        # Punkte, Level und Geschwindigkeit zurücksetzen
        self.points = 0
        self.rows_last = []
        self.rows_gesamt = 0
        self.level = 1
        self.game_speed = 800

        # Geschwindigkeit zurücksetzen
        pygame.time.set_timer(falling_event, self.game_speed)


    # Koordinationsschleife, die aus der Main-Funktion 25x/Sek. aufgerufen wird
    def update(self):

        # Während das Spiel läuft oder sich im Demo-Modus befindet
        if self.state == 'run' or self.state == "demo":

            # Hintergrund zeichnen
            self.screen.fill(self.bg_color)

            # Hintergrundbild laden
            block1_img = pygame.image.load("img/bg-gesamt.png")
            self.screen.blit(block1_img, (0,0))

            # Falls Demo-Modus aktiviert wird: Timer anhalten, Schriftzug und Log einblenden
            if self.state == "demo":
                # Timer stoppen
                pygame.time.set_timer(falling_event, 0)

                # Schriftzug einbleinden
                font_demo = pygame.font.SysFont(None, 36)
                self.show_demo = font_demo.render(f'Demo-Modus', True, (255, 255, 255))
                self.show_demo = pygame.transform.rotozoom(self.show_demo, 17,1)
                self.screen.blit(self.show_demo, (370, 550))

                # Log-Daten einblenden
                font_status = pygame.font.SysFont(None, 30)
                self.show_status = font_status.render(f'Log', True, self.black)
                self.screen.blit(self.show_status, (40, 660))
                font_status = pygame.font.SysFont(None, 22)
                self.show_status = font_status.render(f'# {len(msg)-1}:    {msg[-1]}', True, self.black)
                self.screen.blit(self.show_status, (120, 662))

            # Tetris Schriften, Punktestand, Statistiken
            font_tetris = pygame.font.SysFont(None, 40)
            font = pygame.font.SysFont(None, 24)
            self.show_title = font_tetris.render('Tetrix', True, self.black)
            self.show_level = font.render(f'Level: {self.level}', True, self.black)
            self.show_rows = font.render(f'Reihen: {self.rows_gesamt}', True, self.black)
            self.show_points = font.render(f'Punkte: {self.points}', True, self.black)
            self.show_speed = font.render(f'Intervall: {self.game_speed} ms', True, self.black)

            self.screen.blit(self.show_title, (390, 60))
            self.screen.blit(self.show_level, (400, 110))
            self.screen.blit(self.show_rows, (400, 140))
            self.screen.blit(self.show_points, (400, 170))
            self.screen.blit(self.show_speed, (400, 200))

            # Umrandung des Spielfelds zeichnen
            pygame.draw.rect(self.screen, (20,20,20),
                             [self.margin_left, self.margin_top, 300, 600], 5)

            # Spielfeld zeichnen in der Größe 10x20, ein ist 30x30 px
            for i in range(20):

                for a in range(10):

                    # wenn das Feld nicht leer ist, d.h. bereits ein Stein liegt - diesen zeichnen
                    if self.belegte_felder[i][a] > 0:

                        temp = self.belegte_felder[i][a]
                        self.color = self.tetriblock.colors[temp]

                        # hier zwei Rechtecke übereinander zeichnen:
                        # 1) Füllfarbe 2) Kontur zeichnen
                        pygame.draw.rect(self.screen, self.color,
                                         [a * 30 + self.margin_left, i * 30 + self.margin_top, 30, 30], 0)

                        # falls Grafik-Modus aktiviert ist, Hintergrund durch Bild ersetzen. Muss vor zweitem draw-Befehl kommen
                        if self.with_graphic == True:
                            self.img = self.tetriblock.img[temp]
                            block1_img = self.get_image(f'{self.img}')
                            self.screen.blit(block1_img, (a * 30 + self.margin_left, i * 30 + self.margin_top))

                        pygame.draw.rect(self.screen, self.black,
                                         [a * 30 + self.margin_left, i * 30 + self.margin_top, 30, 30], 1)

                    # wenn Feld = 0, also leer ist
                    else:
                        # hier ebenfalls zwei Rechtecke übereinander zeichnen:
                        # 1) Hintergrund 2) Kontur zeichnen
                        pygame.draw.rect(self.screen, self.bg_color_field,
                                        [a * 30 + self.margin_left, i * 30 + self.margin_top, 30, 30], 0)

                        # falls Grafik-Modus aktiviert ist, Hintergrund durch Bild ersetzen. Muss vor zweitem draw-Befehl kommen
                        if self.with_graphic == True:
                            block2_img = self.get_image('img/bg.png')
                            self.screen.blit(block2_img, (a * 30 + self.margin_left, i * 30 + self.margin_top))

                        pygame.draw.rect(self.screen, self.black,
                                        [a * 30 + self.margin_left, i * 30 + self.margin_top, 30, 30], 1)


            # Zeichnen der Blöcke: aktueller und nächster Block
            self.draw_block()
            self.draw_next_block()

            # Prüfen, ob Game Over
            self.game_over_check()


        # Falls Pause aktiviert wurde: Pause-Bildschim einblenden (Zeit wird bei Events angehalten)
        if self.state == 'pause':
            self.screen.fill((30,30,30))

            font = pygame.font.SysFont(None, 64)
            gameoverscreen = font.render('Pause', True, self.white)
            text_rect = gameoverscreen.get_rect(center=(600 / 2, 700 / 2)) # mittig platzieren
            self.screen.blit(gameoverscreen, text_rect)

            font_again = pygame.font.SysFont(None, 24)
            on_text_surface = font_again.render("Weiter mit [SPACE]", True, pygame.Color((0, 240, 240)))
            text_rect = on_text_surface.get_rect(center=(600 / 2, 500))  # mittig platzieren
            self.screen.blit(on_text_surface, text_rect)

        # Falls Game Over: Gameover-Screen und Statistiken einblenden (Reset wird bei Events durchgeführt)
        if self.state == 'gameover':
            self.screen.fill((30,30,30))

            font_gameover = pygame.font.SysFont(None, 64)
            font_level = pygame.font.SysFont(None, 32)
            font_points = pygame.font.SysFont(None, 32)
            font_rows = pygame.font.SysFont(None, 32)
            show_font_gameover = font_gameover.render('GAME OVER', True, self.white)
            text_rect = show_font_gameover.get_rect(center=(600 / 2, 100))  # mittig platzieren
            self.screen.blit(show_font_gameover, text_rect)

            show_level = font_points.render(f'Level: {self.level}', True, self.white)
            show_points = font_points.render(f'Punkte: {self.points}', True, self.white)
            show_rows = font_rows.render(f'Reihen: {self.rows_gesamt}', True, self.white)

            self.screen.blit(show_points, (100, 240))
            self.screen.blit(show_level, (100, 200))
            self.screen.blit(show_rows, (100, 280))

            font_again = pygame.font.SysFont(None, 26)
            on_text_surface = font_again.render("Neues Spiel mit [SPACE]", True, pygame.Color((0, 240, 240)))
            text_rect = on_text_surface.get_rect(center=(600 / 2, 400))  # mittig platzieren
            self.screen.blit(on_text_surface, text_rect)


# Die Klasse Tetriblock repräsentiert einen Tetris-Baustein mit seinen Eigenschaften (Formen, Rotationen, Farben, Bilder)
# Auch die Bewegung des Steins wird über Funktionen dieser Klasse gesteuert
class Tetriblock():

    x = 0       # Position des Steins - (Versatzwerte für das Spielfeld)
    y = 0       #

    # Formen der verschiedenen Steine
    blocks = {
        1:    [[[0,1], [1,1], [2,1], [3,1]],   [[1,0], [1,1], [1,2], [1,3]]],
        2:    [[[0,0], [1,0], [1,1], [1,2]],   [[0,1], [0,2], [1,1], [2,1]],   [[1,0], [1,1], [1,2], [2,2]],   [[0,1], [1,1], [2,0], [2,1]]],
        3:    [[[0,2], [1,0], [1,1], [1,2]],   [[0,1], [1,1], [2,1], [2,2]],   [[1,0], [1,1], [1,2], [2,0]],   [[0,0], [0,1], [1,1], [2,1]]],
        4:    [[[0,1], [0,2], [1,1], [1,2]]],
        5:    [[[0,2], [0,3], [1,1], [1,2]],   [[0,1], [1,1], [1,2], [2,2]]],
        6:    [[[0,1], [1,0], [1,1], [1,2]],   [[0,1], [1,1], [1,2], [2,1]],   [[1,0], [1,1], [1,2], [2,1]],   [[0,1], [1,0], [1,1], [2,1]]],
        7:    [[[0,0], [0,1], [1,1], [1,2]],   [[0,2], [1,1], [1,2], [2,1]]]
    }

    # zugehörige Farben, gleiche Key-Werte
    colors = {
        1: (0, 240, 240),           # Farbe des I-Bausteins, cyan
        2: (0,127,255),             # Farbe des J-Bausteins, blau
        3: (253,174,50),            # Farbe des L-Bausteins, orange
        4: (240, 240, 0),           # Farbe des O-Bausteins, gelb
        5: (0, 240, 0),             # Farbe des S-Bausteins, grün
        6: (246,43,253),            # Farbe des T-Bausteins, lila
        7: (255,0,70 )              # Farbe des Z-Bausteins, rot
    }

    # zugehörige Bilder, gleiche Key-Werte
    img = {                         #
        1: 'img/1.png',
        2: 'img/2.png',
        3: 'img/3.png',
        4: 'img/4.png',
        5: 'img/5.png',
        6: 'img/6.png',
        7: 'img/7.png',
    }

    # neuen Stein bauen, zufällige Form
    def __init__(self, x_koord, y_koord):
        self.x = x_koord                                            # Startkoordinaten x
        self.y = y_koord                                            # Startkoordinaten y
        self.rotation = 0                                           # default: erster value im dict
        self.type = random.choice(list(self.blocks.keys()))         # zufälligen Key für Typ auswählen


    # gib die Felder des Bausteins zurück. Wird für Berechnungen aufgerufen
    def give_blocks(self):
        return self.blocks[self.type][self.rotation] # liefert zurück: Liste mit vier Listen mit je zwei Einträgen


    # Felder für Baustein nach Rotation zurückgeben. Zur Berechnung, ob eine Rotation möglich ist
    def give_blocks_nextrotation(self):
        if self.rotation < len(self.blocks[self.type])-1:
            return self.blocks[self.type][self.rotation + 1]
        else:
            return self.blocks[self.type][0]

    # nach links bewegen
    def move_left(self):
        self.x -= 1

    # nach rechts bewegen
    def move_right(self):
        self.x += 1

    # nach unten bewegen
    def move_down(self):
        self.y += 1


    # Rotationsfunktion: Inkrement solange noch weitere Rotationen in Liste, ansonsten wieder bei 0 beginnen
    def rotate(self):

        if self.rotation < len(self.blocks[self.type]):
            self.rotation += 1
        if self.rotation == len(self.blocks[self.type]):
            self.rotation = 0

        msg.append("Normale Rotation")

    # rotieren und dabei einen nach rechts springen
    def rotate_jumpright1(self):

        self.x += 1
        if self.rotation < len(self.blocks[self.type]):
            self.rotation += 1
        if self.rotation == len(self.blocks[self.type]):
            self.rotation = 0

    # rotieren und dabei einen nach links springen
    def rotate_jumpleft1(self):

        self.x -= 1
        if self.rotation < len(self.blocks[self.type]):
            self.rotation += 1
        if self.rotation == len(self.blocks[self.type]):
            self.rotation = 0

    # rotieren und dabei zwei nach links springen (für Vierer-Block an rechter Wand)
    def rotate_jumpleft2(self):

        self.x -= 2
        if self.rotation < len(self.blocks[self.type]):
            self.rotation += 1
        if self.rotation == len(self.blocks[self.type]):
            self.rotation = 0

def main():

    # Pygame starten
    pygame.init()

    # Uhr definieren
    clock = pygame.time.Clock()
    fps = 25  # Geschwindigkeit

    # eigenes Event bauen, alle 0,xx Sekunden soll der Stein ein Feld weiter runter - unabhängig von der Refresh-Rate!
    global falling_event
    falling_event = pygame.USEREVENT + 1
    pygame.time.set_timer(falling_event, 800)

    # Instanz der Tetris-Klasse erstellen.
    tetris_game = Tetris()

    # Loop, in dem
    # 1) Benutzerangaben abgefragt werden
    # 2) die Update-Funktion der Tetris-Klasse aufgerufen wird
    done = False
    while not done:

        # Spiel beenden = Schleife beenden
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            # eigenes Event: Baustein wird ein Feld hinuntergesetzt
            if event.type == falling_event:
                if tetris_game.vertical_clash() is not True:
                    tetris_game.tetriblock.move_down()

            # Bei der Rotation nur einzelnen Tastendruck entgegennehmen
            if event.type == pygame.KEYDOWN:

                # Tastendruck "up": Rotation
                if event.key == pygame.K_UP:
                    if tetris_game.rotate_block_ok() == "jump-right":
                        tetris_game.tetriblock.rotate_jumpright1()
                    elif tetris_game.rotate_block_ok() == "jump-left":
                        tetris_game.tetriblock.rotate_jumpleft1()
                    elif tetris_game.rotate_block_ok() == "jump-left2":
                        tetris_game.tetriblock.rotate_jumpleft2()
                    elif tetris_game.rotate_block_ok() == "false":
                        pass
                    elif tetris_game.rotate_block_ok() == "true":
                        tetris_game.tetriblock.rotate()

                # Tastendruck "d": Wechsel in Demo-Modus
                if event.key == pygame.K_d:
                    if tetris_game.state == "run":
                        tetris_game.state = "demo"
                    elif tetris_game.state == "demo":
                        tetris_game.state = "run"
                        pygame.time.set_timer(falling_event, tetris_game.game_speed)

                # Tastendruck "g": Wechsel mit/ohne Grafikelemente
                if event.key == pygame.K_g:
                    if tetris_game.with_graphic == False:
                        tetris_game.with_graphic = True
                    elif tetris_game.with_graphic == True:
                        tetris_game.with_graphic = False

                # Tastendruck "space": Pause-Modus
                if event.key == pygame.K_SPACE:
                    if tetris_game.state == "run":
                        tetris_game.state = "pause"
                        pygame.time.set_timer(falling_event, 0)
                    elif tetris_game.state == "pause":
                        tetris_game.state = "run"
                        pygame.time.set_timer(falling_event, tetris_game.game_speed)

                    # wenn bereits Gameover, dann mit Space daten resetten und neues Spiel
                    elif tetris_game.state == "gameover":
                        tetris_game.reset()
                        tetris_game.state = "run"

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    pass

        # bei links und rechts schnelle Bewegung ermöglichen durch dauerhaft gedrückte Taste
        key_input = pygame.key.get_pressed()
        if key_input[pygame.K_LEFT]:
            if tetris_game.move_left_ok():
                tetris_game.tetriblock.move_left()

        if key_input[pygame.K_RIGHT]:
            if tetris_game.move_right_ok():
                tetris_game.tetriblock.move_right()

        if key_input[pygame.K_DOWN]:
            if tetris_game.vertical_clash() is not True:
                tetris_game.tetriblock.move_down()

        # Update-Funktion innerhalb der Tetris-Klasse aufrufen
        tetris_game.update()

        # den ganzen Screen updaten
        pygame.display.flip()

        # Uhr ticken lassen
        clock.tick(fps)

    pygame.quit()

# Main-Funktion starten
if __name__ == '__main__':
    main()
