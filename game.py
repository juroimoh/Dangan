import pygame as py, time, sys, csv, random
from pygame import mixer

py.init()
mixer.init()

    # screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
screen = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
py.display.set_caption('Dangan')

font = py.font.SysFont("Arial", 28)

border_img = py.image.load("assets/gamebackground.png").convert_alpha()
player_img = py.image.load("assets/player.png").convert_alpha()
player_bullet_img = py.image.load("assets/player_bullet.png").convert_alpha()
cover_idea_img = py.image.load("assets/dangan_cover_idea.png").convert_alpha()

player_mask = py.mask.from_surface(player_img)
player_bullet_mask = py.mask.from_surface(player_bullet_img)

    # colors
BACKGROUND_COLOR = (16, 15, 22)
FONT_COLOR = (214, 255, 255)

    # miscellaneous
DEBUG = True
BASE_SPEED = 250

previous_time = time.time()

class Game:
    def __init__(self):
        self.screen = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = py.time.Clock()

        self.gameStateManager = GameStateManager('menu')
        self.menu = Menu(self.screen, self.gameStateManager)
        self.levelone = LevelOne(self.screen, self.gameStateManager)

        self.states = {'menu': self.menu, 'levelone': self.levelone}

    def run(self):
        global dt, previous_time
        flag = True
        while flag:
            # self.clock.tick(30)
            dt = time.time() - previous_time
            previous_time = time.time()

            for event in py.event.get():
                if event.type == py.QUIT:
                    flag = False
                if event.type == py.KEYDOWN:
                    keys = py.key.get_pressed()
                    if keys[py.K_y]:
                        self.gameStateManager.set_state('levelone')

            self.states[self.gameStateManager.get_state()].run()
            py.display.flip()

class LevelOne:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        self.player = py.Rect(290, 290, 14, 14)
        self.player_mask = player_mask

        self.BASE_SPEED = 300
        self.player_speed = BASE_SPEED
        self.player_x = self.player.x
        self.player_y = self.player.y
        self.player_width = 14

        self.player_bullets = []
        self.player_bulletsl = []
        self.player_bulletsr = []
        self.player_bullet_mask = player_bullet_mask
        self.player_bullet_reload = 0.5
        self.player_bullet_width = 6
        self.player_bullet_height = 16
        self.player_bullet_speed = 550

        self.music_started = False

    def draw_player(self):
        self.player = py.Rect(self.player.x, self.player.y, 14, 14)
        self.display.blit(player_img, (self.player.x, self.player.y))

    def draw_player_bullets(self):
        for b in self.player_bullets:
            screen.blit(player_bullet_img, (b[0], b[1]))
        for b in self.player_bulletsl:
            screen.blit(player_bullet_img, (b[0], b[1]))
        for b in self.player_bulletsr:
            screen.blit(player_bullet_img, (b[0], b[1]))

    def run(self):

        if not self.music_started:
            # mixer.music.load("assets/Ready.mp3")
            mixer.music.load("assets/Skyrider.mp3")
            mixer.music.set_volume(0.2)
            mixer.music.play()
            self.music_started = True

        keys = py.key.get_pressed()
        if keys[py.K_LEFT] and self.player.left > 50:
            self.player_x -= self.player_speed * dt
            self.player.x = round(self.player_x)
            if self.player.left < 50:
                self.player.x = 50
        if keys[py.K_RIGHT] and self.player.right < 550:
            self.player_x += self.player_speed * dt
            self.player.x = round(self.player_x)
            if self.player.right > 550:
                self.player.x = 550 - self.player_width
        if keys[py.K_UP] and self.player.top > 50:
            self.player_y -= self.player_speed * dt
            self.player.y = round(self.player_y)
            if self.player.top < 50:
                self.player.y = 50
        if keys[py.K_DOWN] and self.player.bottom < 550:
            self.player_y += self.player_speed * dt
            self.player.y = round(self.player_y)
            if self.player.bottom > 550:
                self.player.y = 550 - self.player_width
        if keys[py.K_RIGHT] and keys[py.K_UP] or keys[py.K_RIGHT] and keys[py.K_DOWN] or keys[py.K_LEFT] and keys[
            py.K_UP] or keys[py.K_LEFT] and keys[py.K_DOWN]:
            player_speed = round(BASE_SPEED * 0.707)
        else:
            player_speed = BASE_SPEED
        if keys[py.K_SPACE] and self.player_bullet_reload <= 0:
            self.player_bullet_reload = 0.15
            player_bullet_x = self.player.x + self.player_width / 2 - self.player_bullet_width / 2
            player_bullet_y = self.player.y - 5
            self.player_bullets.append([player_bullet_x, player_bullet_y])
            self.player_bulletsl.append([player_bullet_x, player_bullet_y])
            self.player_bulletsr.append([player_bullet_x, player_bullet_y])
        if keys[py.K_ESCAPE]:
            self.gameStateManager.set_state('menu')

        if self.player_bullet_reload > -1:
            self.player_bullet_reload -= 1 * dt

        screen.fill(BACKGROUND_COLOR)

        for b in self.player_bullets[:]:
            b[1] -= self.player_bullet_speed * dt
            if b[1] < 0:
                self.player_bullets.remove(b)
        for b in self.player_bulletsl[:]:
            b[1] -= self.player_bullet_speed * dt
            b[0] -= self.player_bullet_speed / 10 * dt
            if b[1] < 0:
                self.player_bulletsl.remove(b)
        for b in self.player_bulletsr[:]:
            b[1] -= self.player_bullet_speed * dt
            b[0] += self.player_bullet_speed / 10 * dt
            if b[1] < 0:
                self.player_bulletsr.remove(b)

        self.draw_player_bullets()
        self.draw_player()

        self.display.blit(border_img, (0, 0))  # Keep this rendering last.

        # \/ debug \/
        if DEBUG:
            debug_text = font.render(
                f"debug:   x {self.player.x}   y {self.player.y}   |   {player_speed}, {len(self.player_bullets)}x3", True, FONT_COLOR)
            screen.blit(debug_text, (10, 10))

            debug_top = font.render(f"{self.player.top}", True, FONT_COLOR)
            screen.blit(debug_top, (660, 20))
            debug_right = font.render(f"{self.player.right}", True, FONT_COLOR)
            screen.blit(debug_right, (700, 60))
            debug_left = font.render(f"{self.player.left}", True, FONT_COLOR)
            screen.blit(debug_left, (620, 60))
            debug_bottom = font.render(f"{self.player.bottom}", True, FONT_COLOR)
            screen.blit(debug_bottom, (660, 100))
        # /\ end debug /\

        py.display.flip()

class Menu:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
    def run(self):
        self.display.blit(cover_idea_img, (0, 0))

class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState
    def get_state(self):
        return self.currentState
    def set_state(self, state):
        self.currentState = state

if __name__ == '__main__':
    game = Game()
    game.run()