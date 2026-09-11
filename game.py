import pygame as py, time, sys, json, random
from pygame import mixer

py.init()
mixer.init()

# screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
screen = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
py.display.set_caption('Dangan')

font = py.font.Font("assets/fonts/VCR_OSD_MONO_1.001.ttf", 28)
title_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 42)

border_img = py.image.load("assets/gamebackground.png").convert_alpha()
player_img = py.image.load("assets/player.png").convert_alpha()
player_bullet_img = py.image.load("assets/player_bullet.png").convert_alpha()
cover_img = py.image.load("assets/dangan1_cover.png").convert_alpha()
levels_bg_img = py.image.load("assets/dangan1_levels_behind.png").convert_alpha()
levels_fg_img = py.image.load("assets/dangan1_levels_front.png").convert_alpha()
options_img = py.image.load("assets/dangan_options.png").convert_alpha()

player_mask = py.mask.from_surface(player_img)
player_bullet_mask = py.mask.from_surface(player_bullet_img)
py.key.set_repeat(250, 50)

# colors
BACKGROUND_COLOR = (16, 15, 22)
FONT_COLOR = (214, 255, 255)
HIGHLIGHT_COLOR = (255, 215, 0)
DISABLED_COLOR = (143, 122, 122)

DEBUG = False
BASE_SPEED = 250

previous_time = time.time()

# logic
class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState
        self.states = {}
        self.menu_states = {'splash', 'main_menu', 'level_select', 'settings'}
        self.menu_music_path = "assets/audio/Crystal-Waver.ogg"

        self.is_transitioning = True
        self.fade_alpha = 255.0
        self.fade_speed = 255 / 0.15
        self.fade_mode = 'in'
        self.target_state = None
        self.fade_surface = py.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_surface.fill((0, 0, 0))

    def register_states(self, states):
        self.states = states
        if self.currentState in self.menu_states:
            self.play_menu_music()

    def play_menu_music(self):
        try:
            mixer.music.load(self.menu_music_path)
            mixer.music.play(-1)
        except py.error as e:
            print(f"Could not load menu music: {e}")

    def get_state(self):
        return self.currentState

    def set_state(self, state):
        if state == self.currentState or self.is_transitioning:
            return
        self.target_state = state
        self.is_transitioning = True
        self.fade_mode = 'out'
        self.fade_alpha = 0.0

    def _perform_state_change(self):
        if self.target_state == 'quit':
            py.quit()
            sys.exit()

        prev_state = self.currentState

        if prev_state in self.states:
            current_obj = self.states[prev_state]
            if hasattr(current_obj, 'on_exit'):
                current_obj.on_exit()

        self.currentState = self.target_state

        if self.currentState in self.menu_states:
            if prev_state not in self.menu_states or not mixer.music.get_busy():
                self.play_menu_music()
        else:
            mixer.music.stop()

        if self.currentState in self.states:
            new_obj = self.states[self.currentState]
            if hasattr(new_obj, 'on_enter'):
                new_obj.on_enter()

    def draw_transition(self, display, dt):
        if not self.is_transitioning:
            return

        if self.fade_mode == 'out':
            self.fade_alpha += self.fade_speed * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self._perform_state_change()
                self.fade_mode = 'in'
        elif self.fade_mode == 'in':
            self.fade_alpha -= self.fade_speed * dt
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.is_transitioning = False

        self.fade_surface.set_alpha(int(self.fade_alpha))
        display.blit(self.fade_surface, (0, 0))


class Splash:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.timer = 0.0

    def handle_input(self, events):
        for event in events:
            if event.type == py.KEYDOWN:
                if event.key in (py.K_SPACE, py.K_ESCAPE, py.K_RETURN):
                    self.gameStateManager.set_state('main_menu')

    def run(self, dt):
        self.timer += dt
        if self.timer >= 3.0:
            self.gameStateManager.set_state('main_menu')
        self.display.blit(cover_img, (0, 0))


class MainMenu:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.options = ["LEVEL", "OPTIONS", "QUIT"]
        self.selected_index = 0
        self.menu_font = py.font.Font("assets/fonts/VCR_OSD_MONO_1.001.ttf", 45)

    def on_enter(self):
        self.selected_index = 0

    def handle_input(self, events):
        for event in events:
            if event.type == py.KEYDOWN:
                if event.key == py.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == py.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key in (py.K_SPACE, py.K_RETURN):
                    if self.selected_index == 0:
                        self.gameStateManager.set_state('level_select')
                    elif self.selected_index == 1:
                        self.gameStateManager.set_state('settings')
                    elif self.selected_index == 2:
                        self.gameStateManager.set_state('quit')

    def run(self, dt):
        self.display.fill(BACKGROUND_COLOR)

        self.display.blit(cover_img, (0, 0))

        center_x = 750

        for i, option in enumerate(self.options):
            if i == self.selected_index:
                text_str = f"<{option}>"
                color = 255, 238, 253
            else:
                text_str = option
                color = 219, 203, 216

            opt_surf = self.menu_font.render(text_str, True, color)

            x_pos = center_x - (opt_surf.get_width() // 2)
            y_pos = 410 + i * 60

            self.display.blit(opt_surf, (x_pos, y_pos))


class LevelSelect:
    def __init__(self, display, gameStateManager, level_ref):
        self.display = display
        self.gameStateManager = gameStateManager
        self.level_ref = level_ref
        self.options = ["LEVEL 1", "LEVEL 2", "LEVEL 3", "LEVEL 4", "LEVEL 5", "BACK"]
        self.selected_index = 0

        self.level_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 35)
        self.esc_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 25)

    def on_enter(self):
        self.selected_index = 0

    def handle_input(self, events):
        for event in events:
            if event.type == py.KEYDOWN:
                if event.key == py.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == py.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == py.K_ESCAPE:
                    self.gameStateManager.set_state('main_menu')
                elif event.key in (py.K_SPACE, py.K_RETURN):
                    if self.selected_index == 0:
                        self.gameStateManager.set_state('levelone')
                    elif self.selected_index == 5:
                        self.gameStateManager.set_state('main_menu')

    def run(self, dt):
        self.display.fill(BACKGROUND_COLOR)

        self.display.blit(levels_bg_img, (0, 0))
        self.display.blit(levels_fg_img, (0, 0))

        for i in range(5):
            option = self.options[i]
            is_selected = (i == self.selected_index)
            is_clickable = (i == 0)

            if is_selected:
                text_str = f"<{option}>"
                color = (255, 250, 246) if is_clickable else (178, 152, 152)
            else:
                text_str = option
                color = (229, 207, 207) if is_clickable else DISABLED_COLOR

            opt_surf = self.level_font.render(text_str, True, color)
            self.display.blit(opt_surf, (200 - opt_surf.get_width() // 2, 230 + i * 50))

        esc_option = self.options[5]
        is_esc_selected = (self.selected_index == 5)

        if is_esc_selected:
            esc_text = f"<{esc_option}>"
            esc_color = (255, 250, 246)
        else:
            esc_text = esc_option
            esc_color = (229, 207, 207)

        esc_surf = self.esc_font.render(esc_text, True, esc_color)

        esc_x = 81 - esc_surf.get_width() // 2
        esc_y = 546
        self.display.blit(esc_surf, (esc_x, esc_y))

class Settings:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.options = ["MUSIC", "EFFECTS", "BACK"]
        self.selected_index = 0
        self.music_volume = 20
        self.sfx_volume = 50
        mixer.music.set_volume(self.music_volume / 100.0)

        self.options_font = py.font.Font("assets/fonts/VCR_OSD_MONO_1.001.ttf", 40)
        self.esc_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 25)

    def on_enter(self):
        self.selected_index = 0

    def handle_input(self, events):
        for event in events:
            if event.type == py.KEYDOWN:
                if event.key == py.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == py.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == py.K_ESCAPE:
                    self.gameStateManager.set_state('main_menu')
                elif event.key in (py.K_SPACE, py.K_RETURN):
                    if self.selected_index == 2:
                        self.gameStateManager.set_state('main_menu')
                elif event.key == py.K_LEFT:
                    if self.selected_index == 0:
                        self.music_volume = max(0, self.music_volume - 5)
                        mixer.music.set_volume(self.music_volume / 100.0)
                    elif self.selected_index == 1:
                        self.sfx_volume = max(0, self.sfx_volume - 5)
                elif event.key == py.K_RIGHT:
                    if self.selected_index == 0:
                        self.music_volume = min(100, self.music_volume + 5)
                        mixer.music.set_volume(self.music_volume / 100.0)
                    elif self.selected_index == 1:
                        self.sfx_volume = min(100, self.sfx_volume + 5)

    def run(self, dt):
        self.display.fill(BACKGROUND_COLOR)

        self.display.blit(options_img, (0, 0))

        volume_options = [
            ("MUSIC", self.music_volume),
            ("EFFECTS", self.sfx_volume)
        ]

        for i, (label, vol) in enumerate(volume_options):
            formatted_text = f"{label + ':':<9}{vol:>3}%" # All credit to Gemini for figuring this out.

            if i == self.selected_index:
                text_str = f"<{formatted_text}>"
                color = (255, 255, 255)
            else:
                text_str = f" {formatted_text} "
                color = FONT_COLOR

            opt_surf = self.options_font.render(text_str, True, color)
            self.display.blit(opt_surf, (472, 230 + i * 60))

        esc_option = self.options[2]
        is_esc_selected = (self.selected_index == 2)

        if is_esc_selected:
            esc_text = f"<{esc_option}>"
            esc_color = (255, 255, 255)
        else:
            esc_text = esc_option
            esc_color = FONT_COLOR

        esc_surf = self.esc_font.render(esc_text, True, esc_color)
        esc_x = 81 - esc_surf.get_width() // 2
        esc_y = 546
        self.display.blit(esc_surf, (esc_x, esc_y))

        if is_esc_selected:
            esc_text = f"<{esc_option}>"
            esc_color = (255, 255, 255)
        else:
            esc_text = esc_option
            esc_color = FONT_COLOR

        esc_surf = self.esc_font.render(esc_text, True, esc_color)
        esc_x = 81 - esc_surf.get_width() // 2
        esc_y = 546
        self.display.blit(esc_surf, (esc_x, esc_y))


class Level:
    def __init__(self, display, gameStateManager, level_file, settings_ref):
        self.display = display
        self.gameStateManager = gameStateManager
        self.level_file = level_file
        self.settings = settings_ref

        with open(self.level_file, "r") as file:
            self.level_data = json.load(file)

        self.music_path = self.level_data["music"]
        self.reset_level()

    def on_enter(self):
        self.reset_level()

    def on_exit(self):
        mixer.music.stop()
        self.reset_level()

    def reset_level(self):
        mixer.music.stop()
        self.music_started = False

        self.player = py.Rect(290, 290, 14, 14)
        self.player_mask = player_mask

        self.BASE_SPEED = 300
        self.player_speed = self.BASE_SPEED
        self.player_x = float(self.player.x)
        self.player_y = float(self.player.y)
        self.player_width = 14

        self.player_bullets = []
        self.player_bulletsl = []
        self.player_bulletsr = []
        self.player_bullet_mask = player_bullet_mask
        self.player_bullet_reload = 0.5
        self.player_bullet_width = 6
        self.player_bullet_speed = 550

    def handle_input(self, events):
        for event in events:
            if event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    self.gameStateManager.set_state('level_select')

    def draw_player(self):
        self.display.blit(player_img, (self.player.x, self.player.y))

    def draw_player_bullets(self):
        for b in self.player_bullets:
            screen.blit(player_bullet_img, (b[0], b[1]))
        for b in self.player_bulletsl:
            screen.blit(player_bullet_img, (b[0], b[1]))
        for b in self.player_bulletsr:
            screen.blit(player_bullet_img, (b[0], b[1]))

    def run(self, dt):

        if not self.music_started:
            mixer.music.load(self.music_path)
            mixer.music.set_volume(self.settings.music_volume / 100.0)
            mixer.music.play(-1)
            self.music_started = True

        keys = py.key.get_pressed()

        if (keys[py.K_RIGHT] and keys[py.K_UP]) or (keys[py.K_RIGHT] and keys[py.K_DOWN]) or (keys[py.K_LEFT] and keys[py.K_UP]) or (keys[py.K_LEFT] and keys[py.K_DOWN]):
            self.player_speed = round(self.BASE_SPEED * 0.707)
        else:
            self.player_speed = self.BASE_SPEED

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

        if keys[py.K_SPACE] and self.player_bullet_reload <= 0:
            self.player_bullet_reload = 0.15
            player_bullet_x = self.player.x + self.player_width / 2 - self.player_bullet_width / 2
            player_bullet_y = self.player.y - 5
            self.player_bullets.append([player_bullet_x, player_bullet_y])
            self.player_bulletsl.append([player_bullet_x, player_bullet_y])
            self.player_bulletsr.append([player_bullet_x, player_bullet_y])

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

        self.display.blit(border_img, (0, 0)) # Keep this rendering last.

        if DEBUG:
            debug_text = font.render(
                f"debug:   x {self.player.x}   y {self.player.y}   |   {self.player_speed}, {len(self.player_bullets)}x3", True, FONT_COLOR)
            screen.blit(debug_text, (10, 10))

            debug_top = font.render(f"{self.player.top}", True, FONT_COLOR)
            screen.blit(debug_top, (660, 20))
            debug_right = font.render(f"{self.player.right}", True, FONT_COLOR)
            screen.blit(debug_right, (700, 60))
            debug_left = font.render(f"{self.player.left}", True, FONT_COLOR)
            screen.blit(debug_left, (620, 60))
            debug_bottom = font.render(f"{self.player.bottom}", True, FONT_COLOR)
            screen.blit(debug_bottom, (660, 100))


class Menu:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

    def run(self, dt):
        self.display.blit(cover_img, (0, 0))


class Game:
    def __init__(self):
        self.screen = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = py.time.Clock()

        self.gameStateManager = GameStateManager('main_menu')

        self.settings = Settings(self.screen, self.gameStateManager)
        self.levelone = Level(self.screen, self.gameStateManager, "levels/level1.json", self.settings)
        self.splash = Splash(self.screen, self.gameStateManager)
        self.main_menu = MainMenu(self.screen, self.gameStateManager)
        self.level_select = LevelSelect(self.screen, self.gameStateManager, self.levelone)

        self.states = {
            'splash': self.splash,
            'main_menu': self.main_menu,
            'level_select': self.level_select,
            'settings': self.settings,
            'levelone': self.levelone
        }

        self.gameStateManager.register_states(self.states)

    def run(self):
        global previous_time
        flag = True
        while flag:
            dt = time.time() - previous_time
            previous_time = time.time()

            events = py.event.get()
            for event in events:
                if event.type == py.QUIT:
                    flag = False

            current_state_key = self.gameStateManager.get_state()
            current_state_obj = self.states[current_state_key]

            if not self.gameStateManager.is_transitioning:
                if hasattr(current_state_obj, 'handle_input'):
                    current_state_obj.handle_input(events)

            current_state_key = self.gameStateManager.get_state()
            current_state_obj = self.states[current_state_key]

            run_dt = 0 if self.gameStateManager.is_transitioning else dt
            current_state_obj.run(run_dt)

            self.gameStateManager.draw_transition(self.screen, dt)

            py.display.flip()


if __name__ == '__main__':
    game = Game()
    game.run()