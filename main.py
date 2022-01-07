import pygame
import os
import sys
import sqlite3
import time

connection = sqlite3.connect("data/wins.db")
cursor = connection.cursor()

pygame.init()
size = 500, 500
screen = pygame.display.set_mode(size)

game_running = False


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Board:
    def __init__(self, width, height):
        self.amount = width
        self.have_zero = True
        self.have_winner = False
        self.win_pos1 = ()
        self.win_pos2 = ()
        self.width = width
        self.height = height
        self.board = [[0] * width for i in range(height)]
        self.left = 0
        self.top = 0
        self.turn = 1
        self.cell_size = 50
        self.colors = {1: pygame.Color(0, 0, 255), -1: pygame.Color(255, 0, 0)}

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, pygame.Color(0, 214, 255), (
                    x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size, self.cell_size),
                                 1)
                if self.board[y][x] == 1:

                    pygame.draw.line(screen, self.colors[self.board[y][x]],
                                     (x * self.cell_size + self.left + 2, y * self.cell_size + self.top + 2),
                                     ((x + 1) * self.cell_size + self.left - 4,
                                      (y + 1) * self.cell_size + self.top - 4), 2)

                    pygame.draw.line(screen, self.colors[self.board[y][x]],
                                     ((x + 1) * self.cell_size + self.left - 4, y * self.cell_size + self.top + 2),
                                     (x * self.cell_size + self.left + 2,
                                      (y + 1) * self.cell_size + self.top - 4), 2)

                elif self.board[y][x] == -1:

                    pygame.draw.circle(screen, self.colors[self.board[y][x]], ((x + 0.5) * self.cell_size + self.left,
                                                                               (y + 0.5) * self.cell_size + self.top),
                                       self.cell_size / 2 - 2, 2)

    def set_view(self, left, top, cell_size):

        self.left = left
        self.top = top
        self.cell_size = cell_size

    def win_detect(self, cell):

        global game_running

        sign = (self.board[cell[1]][cell[0]])
        x_signs_x = []
        x_signs_y = []
        y_signs_y = []
        y_signs_x = []
        diagonal_signs_tl_br_x = []
        diagonal_signs_tl_br_y = []
        diagonal_signs_bl_tr_x = []
        diagonal_signs_bl_tr_y = []

        # получаем фигурки в диапазоне 5 клеток

        # по х

        for i in range(cell[0] - 2, cell[0] + 3):
            if 0 <= i <= self.amount - 1:
                if self.board[cell[1]][i] == sign:
                    x_signs_x.append(i)
                    x_signs_y.append(cell[1])

        # по y

        for i in range(cell[1] - 2, cell[1] + 3):
            if 0 <= i <= self.amount - 1:
                if self.board[i][cell[0]] == sign:
                    y_signs_y.append(i)
                    y_signs_x.append(cell[0])

        # по диагонали лево верх - право низ

        x_tl_br = cell[0] - 2
        y_tl_br = cell[1] - 2
        for i in range(5):
            if 0 <= x_tl_br <= self.amount - 1 and 0 <= y_tl_br <= self.amount - 1:
                if self.board[y_tl_br][x_tl_br] == sign:
                    diagonal_signs_tl_br_x.append(x_tl_br)
                    diagonal_signs_tl_br_y.append(y_tl_br)
            x_tl_br += 1
            y_tl_br += 1

        # по диагонали лево низ - право верх

        x_bl_tr = cell[0] - 2
        y_bl_tr = cell[1] + 2
        for i in range(5):
            if 0 <= x_bl_tr <= self.amount - 1 and 0 <= y_bl_tr <= self.amount - 1:
                if self.board[y_bl_tr][x_bl_tr] == sign:
                    diagonal_signs_bl_tr_x.append(x_bl_tr)
                    diagonal_signs_bl_tr_y.append(y_bl_tr)
            x_bl_tr += 1
            y_bl_tr -= 1

        # проверка по X

        if len(x_signs_x) >= 3:
            for i in range(1, len(x_signs_x) - 1):
                if x_signs_x[i - 1] + 1 == x_signs_x[i] and x_signs_x[i] == x_signs_x[i + 1] - 1:
                    if sign == -1:
                        print("круг победил по X")
                        zeros = cursor.execute(f"SELECT zero FROM wins").fetchone()[0]
                        cursor.execute(f"UPDATE wins SET zero = {zeros} + 1")
                        connection.commit()
                    elif sign == 1:
                        print("крестик победил по X")
                        crosses = cursor.execute(f"SELECT cross FROM wins").fetchone()[0]
                        cursor.execute(f"UPDATE wins SET cross = {crosses} + 1")
                        connection.commit()
                    self.win_animation(x_signs_x, x_signs_y, i)
                    game_running = False
                    if sign == 1:
                        verdict("cross")
                    if sign == -1:
                        verdict("zero")
                    return

        # проверка по Y

        if len(y_signs_y) >= 3:
            for i in range(1, len(y_signs_y) - 1):
                if y_signs_y[i - 1] + 1 == y_signs_y[i] and y_signs_y[i] == y_signs_y[i + 1] - 1:
                    if sign == -1:
                        print("круг победил по Y")
                        zeros = cursor.execute(f"SELECT zero FROM wins").fetchone()[0]
                        cursor.execute(f"UPDATE wins SET zero = {zeros} + 1")
                        connection.commit()
                    elif sign == 1:
                        print("крестик победил по Y")
                        crosses = cursor.execute(f"SELECT cross FROM wins").fetchone()[0]
                        cursor.execute(f"UPDATE wins SET cross = {crosses} + 1")
                        connection.commit()
                    self.win_animation(y_signs_x, y_signs_y, i)
                    game_running = False
                    if sign == 1:
                        verdict("cross")
                    if sign == -1:
                        verdict("zero")
                    return

        # провека по диагонали топ лефт - боттом райт

        if len(diagonal_signs_tl_br_x) >= 3:
            for i in range(1, len(diagonal_signs_tl_br_x) - 1):
                if diagonal_signs_tl_br_x[i - 1] + 1 == diagonal_signs_tl_br_x[i] and diagonal_signs_tl_br_x[i] == \
                        diagonal_signs_tl_br_x[i + 1] - 1:
                    if sign == -1:
                        print("круг победил по диагонали топ лефт - боттом райт")
                        zeros = cursor.execute(f"SELECT zero FROM wins").fetchone()[0]
                        cursor.execute(f"UPDATE wins SET zero = {zeros} + 1")
                        connection.commit()
                    elif sign == 1:
                        print("крестик победил по диагонали топ лефт - боттом райт")
                        crosses = cursor.execute(f"SELECT cross FROM wins").fetchone()[0]
                        cursor.execute(f"UPDATE wins SET cross = {crosses} + 1")
                        connection.commit()
                    self.win_animation(diagonal_signs_tl_br_x, diagonal_signs_tl_br_y, i)
                    game_running = False
                    if sign == 1:
                        verdict("cross")
                    if sign == -1:
                        verdict("zero")
                    return

        # проверка по диагонали боттом лефт - топ райт

        if len(diagonal_signs_bl_tr_x) >= 3:
            for i in range(1, len(diagonal_signs_bl_tr_x) - 1):
                if diagonal_signs_bl_tr_x[i - 1] + 1 == diagonal_signs_bl_tr_x[i] and diagonal_signs_bl_tr_x[i] == \
                        diagonal_signs_bl_tr_x[i + 1] - 1:
                    if sign == -1:
                        print("круг победил по диагонали боттом лефт - топ райт")
                        zeros = cursor.execute(f"SELECT zero FROM wins").fetchone()[0]
                        cursor.execute(f"UPDATE wins SET zero = {zeros} + 1")
                        connection.commit()
                    elif sign == 1:
                        print("крестик победил по диагонали боттом лефт - топ райт")
                        crosses = cursor.execute(f"SELECT cross FROM wins").fetchone()[0]
                        cursor.execute(f"UPDATE wins SET cross = {crosses} + 1")
                        connection.commit()
                    self.win_animation(diagonal_signs_bl_tr_x, diagonal_signs_bl_tr_y, i)
                    game_running = False
                    if sign == 1:
                        verdict("cross")
                    if sign == -1:
                        verdict("zero")
                    return

        self.have_zero = False
        for x in range(self.amount):
            for y in range(self.amount):
                if self.board[x][y] == 0:
                    self.have_zero = True

        if not self.have_zero:
            print("Ничья")
            draws = cursor.execute(f"SELECT draw FROM wins").fetchone()[0]
            cursor.execute(f"UPDATE wins SET draw = {draws} + 1")
            connection.commit()
            self.render()
            pygame.display.flip()
            time.sleep(2)
            game_running = False
            verdict("draw")
            return

    def win_animation(self, coordinates_x, coordinates_y, num):

        self.have_winner = True

        self.win_pos1 = ((coordinates_x[num - 1] + 0.5) * self.cell_size + self.left,
                         (coordinates_y[num - 1] + 0.5) * self.cell_size + self.top)
        self.win_pos2 = ((coordinates_x[num + 1] + 0.5) * self.cell_size + self.left,
                         (coordinates_y[num + 1] + 0.5) * self.cell_size + self.top)
        self.render()

        pygame.draw.line(screen, pygame.Color(0, 0, 0), self.win_pos1, self.win_pos2, 7)
        pygame.display.flip()
        time.sleep(2)

    def on_click(self, cell):

        if self.board[cell[1]][cell[0]] == 0:
            self.board[cell[1]][cell[0]] = self.turn
            self.turn *= - 1
            self.win_detect(cell)

    def get_cell(self, mouse_pos):

        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if cell_x < 0 or cell_x >= self.width or cell_y < 0 or cell_y >= self.height:
            return None
        return cell_x, cell_y

    def get_click(self, mouse_pos):

        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)


def verdict(verdict):
    size = 500, 500
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color(255, 255, 255))
    pygame.display.flip()

    need1 = ["g", "a", "m", "e"]
    need2 = ["o", "v", "e2", "r"]
    start_coord = 50
    time.sleep(0.5)

    for i in need1:
        letter = pygame.sprite.Sprite()
        image = load_image(f"letter_{i}.png", -1)
        letter.image = image
        rect = letter.image.get_rect()
        rect[0] = start_coord
        rect[1] = 100
        screen.blit(image, rect)
        start_coord += 20 + rect[2]
        pygame.display.flip()
        time.sleep(0.5)

    start_coord = 50
    time.sleep(0.5)

    for i in need2:
        letter = pygame.sprite.Sprite()
        image = load_image(f"letter_{i}.png", -1)
        letter.image = image
        rect = letter.image.get_rect()
        rect[0] = start_coord
        rect[1] = 230
        screen.blit(image, rect)
        start_coord += 20 + rect[2]
        pygame.display.flip()
        time.sleep(0.5)

    pygame.display.flip()
    end_running = True
    size = 500, 500
    screen = pygame.display.set_mode(size)
    fon = pygame.transform.scale(load_image('menu.png'), (500, 500))
    screen.blit(fon, (0, 0))

    if verdict == "cross":
        font = pygame.font.Font(None, 50)
        string_render = font.render("КРЕСТИКИ ВЫИГРАЛИ!", 1, pygame.Color("red"))
        intro_rect = string_render.get_rect()
        intro_rect.top = 223.5
        intro_rect.left = 40
        screen.blit(string_render, intro_rect)
    if verdict == "draw":
        font = pygame.font.Font(None, 50)
        string_render = font.render("НИЧЬЯ!", 1, pygame.Color("red"))
        intro_rect = string_render.get_rect()
        intro_rect.top = 223.5
        intro_rect.left = 180
        screen.blit(string_render, intro_rect)
    if verdict == "zero":
        font = pygame.font.Font(None, 50)
        string_render = font.render("НОЛИКИ ВЫИГРАЛИ!", 1, pygame.Color("red"))
        intro_rect = string_render.get_rect()
        intro_rect.top = 223.5
        intro_rect.left = 40
        screen.blit(string_render, intro_rect)

    pygame.draw.rect(screen, "black", (165, 300, 170, 80), 2)
    pygame.draw.rect(screen, "white", (167, 302, 166, 76), 0)
    font = pygame.font.Font(None, 49)
    string_render = font.render("ЗАНОВО", 1, pygame.Color("red"))
    intro_rect = string_render.get_rect()
    intro_rect.top = 325
    intro_rect.left = 177.5
    screen.blit(string_render, intro_rect)

    while end_running:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 167 <= event.pos[0] <= 333 and 302 <= event.pos[1] <= 378:
                    end_running = False
                    start_screen()


def start_screen():
    running = True
    size = 500, 500
    screen = pygame.display.set_mode(size)
    fon = pygame.transform.scale(load_image('menu.png'), (500, 500))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    string_render = font.render("КРЕСТИКИ - НОЛИКИ", 1, pygame.Color("red"))
    intro_rect = string_render.get_rect()
    intro_rect.top = 30
    intro_rect.left = 64
    screen.blit(string_render, intro_rect)
    pygame.draw.rect(screen, "black", (64, 200, 170, 80), 2)
    pygame.draw.rect(screen, "white", (66, 202, 166, 76), 0)
    font = pygame.font.Font(None, 49)
    string_render = font.render("НАЧАТЬ", 1, pygame.Color("red"))
    intro_rect = string_render.get_rect()
    intro_rect.top = 223.5
    intro_rect.left = 84
    screen.blit(string_render, intro_rect)
    size_choice = ["Выберите поле:",
                   "3 на 3",
                   "5 на 5",
                   "7 на 7"]
    font = pygame.font.Font(None, 30)
    text_y_coord = 100

    for line in size_choice:
        string_render = font.render(line, 1, pygame.Color("red"))
        intro_rect = string_render.get_rect()
        intro_rect.top = text_y_coord
        intro_rect.left = 300
        text_y_coord += 40
        screen.blit(string_render, intro_rect)

    for i in range(3):
        pygame.draw.rect(screen, "black", (380, 140 + i * 40, 20, 20), 0)
        pygame.draw.rect(screen, "white", (382, 142 + i * 40, 16, 16), 0)
    pygame.display.flip()

    amount = 3
    all_sprites = pygame.sprite.Group()
    sprite_tick = pygame.sprite.Sprite()
    sprite_tick.image = load_image("tick.png")
    sprite_tick.rect = sprite_tick.image.get_rect()
    sprite_tick.rect.x = 382
    sprite_tick.rect.y = 142
    all_sprites.add(sprite_tick)
    all_sprites.draw(screen)
    string_render = font.render("Статистика:", 1, pygame.Color("red"))
    intro_rect = string_render.get_rect()
    intro_rect.top = 300
    intro_rect.left = 64
    screen.blit(string_render, intro_rect)
    string_render = font.render(f"Победы крестиков:  {cursor.execute(f'SELECT cross FROM wins').fetchone()[0]}", 1,
                                pygame.Color("red"))
    intro_rect = string_render.get_rect()
    intro_rect.top = 340
    intro_rect.left = 64
    screen.blit(string_render, intro_rect)
    string_render = font.render(f"Победы ноликов:  {cursor.execute(f'SELECT zero FROM wins').fetchone()[0]}", 1,
                                pygame.Color("red"))
    intro_rect = string_render.get_rect()
    intro_rect.top = 380
    intro_rect.left = 64
    screen.blit(string_render, intro_rect)
    string_render = font.render(f"Ничьи:  {cursor.execute(f'SELECT draw FROM wins').fetchone()[0]}", 1,
                                pygame.Color("red"))
    intro_rect = string_render.get_rect()
    intro_rect.top = 420
    intro_rect.left = 64
    screen.blit(string_render, intro_rect)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 382 <= event.pos[0] <= 396 and 142 <= event.pos[1] <= 156:
                    amount = 3
                    all_sprites = pygame.sprite.Group()
                    for i in range(3):
                        pygame.draw.rect(screen, "white", (382, 142 + i * 40, 16, 16), 0)
                    sprite_tick.rect.x = 382
                    sprite_tick.rect.y = 142
                    all_sprites.add(sprite_tick)
                    all_sprites.draw(screen)

                if 382 <= event.pos[0] <= 396 and 182 <= event.pos[1] <= 196:
                    amount = 5
                    all_sprites = pygame.sprite.Group()
                    for i in range(3):
                        pygame.draw.rect(screen, "white", (382, 142 + i * 40, 16, 16), 0)
                    sprite_tick.rect.x = 382
                    sprite_tick.rect.y = 182
                    all_sprites.add(sprite_tick)
                    all_sprites.draw(screen)

                if 382 <= event.pos[0] <= 396 and 222 <= event.pos[1] <= 236:
                    amount = 7
                    all_sprites = pygame.sprite.Group()
                    for i in range(3):
                        pygame.draw.rect(screen, "white", (382, 142 + i * 40, 16, 16), 0)
                    sprite_tick.rect.x = 382
                    sprite_tick.rect.y = 222
                    all_sprites.add(sprite_tick)
                    all_sprites.draw(screen)

                if 66 <= event.pos[0] <= 232 and 202 <= event.pos[1] <= 278:
                    game(amount)
                    return

        pygame.display.flip()


def game(amount):
    pygame.init()
    size = amount * 50 + 40, amount * 50 + 40
    screen = pygame.display.set_mode(size)
    board = Board(amount, amount)
    board.set_view(20, 20, 50)

    global game_running

    game_running = True
    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.get_click(event.pos)
        screen.fill((255, 255, 255))
        board.render()
        pygame.display.flip()
    pygame.quit()


start_screen()
