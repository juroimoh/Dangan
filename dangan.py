import pygame as py, time, sys, json, math
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
enemy_img = py.image.load("assets/sherumini.png").convert_alpha()
spinningblade_img = py.image.load("assets/spinningblade.png").convert_alpha()
spinningblade_gray_img = py.transform.grayscale(spinningblade_img)
spinningblade_red_img = spinningblade_img.copy()
spinningblade_red_img.fill((255, 60, 60, 255), special_flags=py.BLEND_RGBA_MULT)

player_mask = py.mask.from_surface(player_img)
player_bullet_mask = py.mask.from_surface(player_bullet_img)
enemy_mask = py.mask.from_surface(enemy_img)

player_flash_img = player_img.copy()
player_flash_img.fill((220, 90, 90, 255), special_flags=py.BLEND_RGBA_MULT)

py.key.set_repeat(250, 50)

# colors
BACKGROUND_COLOR = (16, 15, 22)
FONT_COLOR = (214, 255, 255)
HIGHLIGHT_COLOR = (255, 215, 0)
DISABLED_COLOR = (143, 122, 122)

DEBUG = False
BASE_SPEED = 250

HIT_TIMEOUT_DURATION = 2.0
HIT_FADE_WINDOW = 0.4
SURVIVAL_SCORE_RATE = 60.0
SPINNING_BLADE_INACTIVE_ALPHA = 45

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

        right_x = 840

        for i, option in enumerate(self.options):
            if i == self.selected_index:
                text_str = f"<{option}>"
                color = 255, 238, 253
            else:
                text_str = f" {option} "
                color = 219, 203, 216

            opt_surf = self.menu_font.render(text_str, True, color)
            x_pos = right_x - opt_surf.get_width()
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
        self.music_volume = 50
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
                elif event.key == py.K_SPACE:
                    if self.selected_index == 0:
                        self.music_volume += 5
                        if self.music_volume > 100:
                            self.music_volume = 0
                        mixer.music.set_volume(self.music_volume / 100.0)
                    elif self.selected_index == 1:
                        self.sfx_volume += 5
                        if self.sfx_volume > 100:
                            self.sfx_volume = 0
                    elif self.selected_index == 2:
                        self.gameStateManager.set_state('main_menu')
                elif event.key == py.K_RETURN:
                    if self.selected_index == 2:
                        self.gameStateManager.set_state('main_menu')
                elif event.key == py.K_ESCAPE:
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
            formatted_text = f"{label + ':':<9}{vol:>3}%"

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

class Level:
    def __init__(self, display, gameStateManager, level_file, settings_ref):
        self.display = display
        self.gameStateManager = gameStateManager
        self.level_file = level_file
        self.settings = settings_ref

        with open(self.level_file, "r") as file:
            self.level_data = json.load(file)

        self.music_path = self.level_data["music"]
        self.bullet_mask_cache = {}
        self.bullet_sprite_cache = {}
        self.preload_bullet_sprites()

        self.action_library = {
            "spawn_bullet": self.action_spawn_bullet,
            "spawn_spread": self.action_spawn_spread,
            "spawn_ring": self.action_spawn_ring,
            "move_enemy": self.action_move_enemy,
            "move_enemy_sine": self.action_move_enemy_sine,
            "move_enemy_path": self.action_move_enemy_path,
            "move_enemy_circle": self.action_move_enemy_circle,
            "move_player": self.action_move_player,
            "spawn_spinning_blades": self.action_spawn_spinning_blades
        }

        self.reset_level()

        self.title_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 30)
        self.subtitle_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 25)

    def get_bullet_mask(self, radius):
        """Generates and caches sprite masks for circular enemy bullets."""
        if radius not in self.bullet_mask_cache:
            surf = py.Surface((radius * 2, radius * 2), py.SRCALPHA)
            py.draw.circle(surf, (255, 255, 255), (radius, radius), radius)
            self.bullet_mask_cache[radius] = py.mask.from_surface(surf)
        return self.bullet_mask_cache[radius]

    def get_bullet_sprite(self, sprite_path):
        """Loads and caches bullet images along with their sprite masks."""
        if sprite_path not in self.bullet_sprite_cache:
            image = py.image.load(sprite_path).convert_alpha()
            mask = py.mask.from_surface(image)
            self.bullet_sprite_cache[sprite_path] = (image, mask)
        return self.bullet_sprite_cache[sprite_path]

    def preload_bullet_sprites(self):
        """Scans the level JSON timeline for sprite paths and loads them all upfront."""
        for event in self.level_data.get("timeline", []):
            sprite = event.get("sprite")
            if sprite:
                self.get_bullet_sprite(sprite)

    def _rotate_blade_image(self, image, pivot_pos, angle):
        """Rotates image around its bottom-middle point instead of its center, keeping pivot_pos fixed on screen."""
        origin_local = (image.get_width() / 2, image.get_height())
        image_rect = image.get_rect(topleft=(pivot_pos[0] - origin_local[0], pivot_pos[1] - origin_local[1]))
        offset_center_to_pivot = py.math.Vector2(pivot_pos) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-angle)
        rotated_center = (pivot_pos[0] - rotated_offset.x, pivot_pos[1] - rotated_offset.y)
        rotated_image = py.transform.rotate(image, angle)
        rotated_rect = rotated_image.get_rect(center=rotated_center)
        return rotated_image, rotated_rect

# action library
    def _fire_single_bullet(self, b_params):
        x = b_params.get("x", self.enemy_x + enemy_img.get_width() / 2)
        y = b_params.get("y", self.enemy_y + enemy_img.get_height() / 2)
        speed = b_params.get("speed", 200)
        angle = b_params.get("angle", 90) # Default 90 degrees = straight down
        radius = b_params.get("radius", 6)
        color = b_params.get("color", (255, 50, 50))
        movement_type = b_params.get("movement_type", "linear")
        sprite = b_params.get("sprite", None)

        rad = math.radians(angle)
        dx = b_params.get("dx", speed * math.cos(rad))
        dy = b_params.get("dy", speed * math.sin(rad))

        bullet = {
            "x": float(x),
            "y": float(y),
            "dx": float(dx),
            "dy": float(dy),
            "speed": float(speed),
            "angle": float(angle),
            "radius": int(radius),
            "color": color,
            "movement_type": movement_type,
            "time_alive": 0.0,
            "curve_rate": b_params.get("curve_rate", 45.0), # deg/sec
            "zigzag_freq": b_params.get("zigzag_freq", 8.0),
            "zigzag_amp": b_params.get("zigzag_amp", 150.0),
            "accel": b_params.get("accel", 50.0),
            "homing_rate": b_params.get("homing_rate", 90.0),
            "sprite": sprite
        }

        if sprite:
            image, mask = self.get_bullet_sprite(sprite)
            bullet["image"] = image
            bullet["mask"] = mask
            bullet["width"] = image.get_width()
            bullet["height"] = image.get_height()
        else:
            bullet["image"] = None
            bullet["mask"] = self.get_bullet_mask(bullet["radius"])
            bullet["width"] = bullet["radius"] * 2
            bullet["height"] = bullet["radius"] * 2

        self.enemy_bullets.append(bullet)

    def action_spawn_bullet(self, event):
        repetitions = event.get("repetitions", 1)
        delay = event.get("delay", 0.1)

        if repetitions > 1:
            self.active_spawners.append({
                "fire_func": self._fire_single_bullet,
                "event": event,
                "remaining": repetitions,
                "timer": 0.0,
                "interval": delay
            })
        else:
            self._fire_single_bullet(event)

    def _fire_spread_payload(self, event):
        x = event.get("x", self.enemy_x + enemy_img.get_width() / 2)
        y = event.get("y", self.enemy_y + enemy_img.get_height() / 2)
        count = event.get("count", 5)
        spread_angle = event.get("spread_angle", 60.0)
        base_angle = event.get("base_angle", 90.0)

        if count <= 1:
            angles = [base_angle]
        else:
            start_angle = base_angle - (spread_angle / 2.0)
            step = spread_angle / (count - 1)
            angles = [start_angle + i * step for i in range(count)]

        for a in angles:
            bullet_data = dict(event)
            bullet_data["x"] = x
            bullet_data["y"] = y
            bullet_data["angle"] = a
            self._fire_single_bullet(bullet_data)

    def action_spawn_spread(self, event):
        repetitions = event.get("repetitions", 1)
        delay = event.get("delay", 0.1)

        if repetitions > 1:
            self.active_spawners.append({
                "fire_func": self._fire_spread_payload,
                "event": event,
                "remaining": repetitions,
                "timer": 0.0,
                "interval": delay
            })
        else:
            self._fire_spread_payload(event)

    def _fire_ring_payload(self, event):
        x = event.get("x", self.enemy_x + enemy_img.get_width() / 2)
        y = event.get("y", self.enemy_y + enemy_img.get_height() / 2)
        count = event.get("count", 12)
        base_angle = event.get("base_angle", 0.0)

        step = 360.0 / count
        for i in range(count):
            a = base_angle + i * step
            bullet_data = dict(event)
            bullet_data["x"] = x
            bullet_data["y"] = y
            bullet_data["angle"] = a
            self._fire_single_bullet(bullet_data)

    def action_spawn_ring(self, event):
        repetitions = event.get("repetitions", 1)
        delay = event.get("delay", 0.1)

        if repetitions > 1:
            self.active_spawners.append({
                "fire_func": self._fire_ring_payload,
                "event": event,
                "remaining": repetitions,
                "timer": 0.0,
                "interval": delay
            })
        else:
            self._fire_ring_payload(event)

    def action_move_enemy(self, event):
        self.enemy_movement_mode = "linear"
        self.enemy_start_pos = (self.enemy_x, self.enemy_y)
        self.enemy_target_pos = (event.get("x", self.enemy_x), event.get("y", self.enemy_y))
        self.enemy_move_duration = event.get("duration", 1.0)
        self.enemy_move_elapsed = 0.0

    def action_move_enemy_sine(self, event):
        self.enemy_movement_mode = "sine"
        self.enemy_start_pos = (self.enemy_x, self.enemy_y)
        self.enemy_target_pos = (event.get("x", self.enemy_x), event.get("y", self.enemy_y))
        self.enemy_move_duration = event.get("duration", 2.0)
        self.sine_amp = event.get("amplitude", 40.0)
        self.sine_freq = event.get("frequency", 2.0)
        self.enemy_move_elapsed = 0.0

    def action_move_enemy_path(self, event):
        self.enemy_movement_mode = "path"
        self.enemy_path = event.get("path", [])
        self.enemy_path_index = 0

    def action_move_enemy_circle(self, event):
        self.enemy_movement_mode = "circle"
        self.circle_center = (event.get("center_x", 300), event.get("center_y", 150))
        self.circle_radius = event.get("radius", 80.0)
        self.circle_speed = event.get("speed", 90.0)
        self.enemy_move_duration = event.get("duration", 3.0)
        self.enemy_move_elapsed = 0.0

    def action_move_player(self, event):
        self.player.x = event.get("x", self.player.x)
        self.player.y = event.get("y", self.player.y)
        self.player_x = float(self.player.x)
        self.player_y = float(self.player.y)

    def action_spawn_spinning_blades(self, event):
        switch_interval = event.get("switch_interval", 1.5)
        self.spinning_blades.append({
            "rotation": event.get("start_angle", 0.0),
            "spin_speed": event.get("spin_speed", 60.0),
            "spin_direction": event.get("spin_direction", 1),
            "switch_interval": switch_interval,
            "switch_timer": switch_interval,
            "on": event.get("start_active", True),
            "transition_elapsed": 0.0,
            "fade_in_duration": event.get("fade_in_duration", 1.0),
            "spawn_elapsed": 0.0,
            "turn_on_duration": event.get("turn_on_duration", 0.5),
            "turn_off_duration": event.get("turn_off_duration", 0.5),
            "center_x": event.get("x", None),
            "center_y": event.get("y", None),
            "duration": event.get("duration", None),
            "fade_out_duration": event.get("fade_out_duration", event.get("fade_in_duration", 1.0)),
            "lifetime_elapsed": 0.0
        })

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

        self.graze_margin = 6
        self.graze_radius = int(math.hypot(self.player_width, self.player_width) / 2) + self.graze_margin
        graze_surf = py.Surface((self.graze_radius * 2, self.graze_radius * 2), py.SRCALPHA)
        py.draw.circle(graze_surf, (255, 255, 255), (self.graze_radius, self.graze_radius), self.graze_radius)
        self.graze_mask = py.mask.from_surface(graze_surf)

        self.player_bullets = []
        self.player_bulletsl = []
        self.player_bulletsr = []
        self.player_bullet_mask = player_bullet_mask
        self.player_bullet_reload = 0.5
        self.player_bullet_width = 6
        self.player_bullet_speed = 550

        self.score = 0
        self.score_accum = 0.0
        self.graze_score = 0
        self.enemy_x = float(self.level_data.get("enemy_x", 280))
        self.enemy_y = float(self.level_data.get("enemy_y", 80))

        self.level_time = 0.0
        self.timeline = self.level_data.get("timeline", [])
        self.timeline.sort(key=lambda e: e.get("time", 0))
        self.current_event_index = 0

        self.enemy_bullets = []
        self.active_spawners = []
        self.spinning_blades = []

        self.enemy_movement_mode = "idle"
        self.enemy_move_elapsed = 0.0
        self.enemy_move_duration = 1.0
        self.enemy_start_pos = (self.enemy_x, self.enemy_y)
        self.enemy_target_pos = (self.enemy_x, self.enemy_y)
        self.sine_amp = 40.0
        self.sine_freq = 2.0
        self.enemy_path = []
        self.enemy_path_index = 0
        self.circle_center = (300, 150)
        self.circle_radius = 80.0
        self.circle_speed = 90.0

        self.hit_timer = 0.0

    def handle_input(self, events):
        for event in events:
            if event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    self.gameStateManager.set_state('level_select')

    def draw_player(self):
        self.display.blit(player_img, (self.player.x, self.player.y))
        intensity = self._hit_flash_intensity()
        if intensity > 0:
            player_flash_img.set_alpha(int(255 * intensity))
            self.display.blit(player_flash_img, (self.player.x, self.player.y))

    def draw_enemy(self):
        self.display.blit(enemy_img, (self.enemy_x, self.enemy_y))

    def draw_player_bullets(self):
        for b in self.player_bullets:
            screen.blit(player_bullet_img, (b[0], b[1]))
        for b in self.player_bulletsl:
            screen.blit(player_bullet_img, (b[0], b[1]))
        for b in self.player_bulletsr:
            screen.blit(player_bullet_img, (b[0], b[1]))

    def _hit_flash_intensity(self):
        if self.hit_timer <= 0:
            return 0.0
        if self.hit_timer > HIT_FADE_WINDOW:
            return 1.0
        return self.hit_timer / HIT_FADE_WINDOW

    def run(self, dt):
        if not self.music_started:
            mixer.music.load(self.music_path)
            mixer.music.set_volume(self.settings.music_volume / 100.0)
            mixer.music.play(-1)
            self.music_started = True

        if self.music_started:
            self.level_time += dt

        if self.hit_timer > 0:
            self.hit_timer = max(0.0, self.hit_timer - dt)

        self.score_accum += SURVIVAL_SCORE_RATE * dt
        tick_score = int(self.score_accum)
        if tick_score > 0 and self.hit_timer <= 0:
            self.score += tick_score
            self.score_accum -= tick_score

        for spawner in self.active_spawners[:]:
            spawner["timer"] -= dt
            if spawner["timer"] <= 0:
                spawner["fire_func"](spawner["event"])
                spawner["remaining"] -= 1
                spawner["timer"] = spawner["interval"]
                if spawner["remaining"] <= 0:
                    self.active_spawners.remove(spawner)

        while self.current_event_index < len(self.timeline):
            event = self.timeline[self.current_event_index]
            if self.level_time >= event.get("time", 0):
                action_type = event.get("type")
                if action_type in self.action_library:
                    self.action_library[action_type](event)
                else:
                    print(f"Warning: Unknown action type '{action_type}' in JSON.")
                self.current_event_index += 1
            else:
                break

        if self.enemy_movement_mode == "linear":
            self.enemy_move_elapsed += dt
            t = min(1.0, self.enemy_move_elapsed / self.enemy_move_duration)
            self.enemy_x = self.enemy_start_pos[0] + (self.enemy_target_pos[0] - self.enemy_start_pos[0]) * t
            self.enemy_y = self.enemy_start_pos[1] + (self.enemy_target_pos[1] - self.enemy_start_pos[1]) * t
            if t >= 1.0:
                self.enemy_movement_mode = "idle"

        elif self.enemy_movement_mode == "sine":
            self.enemy_move_elapsed += dt
            t = min(1.0, self.enemy_move_elapsed / self.enemy_move_duration)
            base_x = self.enemy_start_pos[0] + (self.enemy_target_pos[0] - self.enemy_start_pos[0]) * t
            base_y = self.enemy_start_pos[1] + (self.enemy_target_pos[1] - self.enemy_start_pos[1]) * t
            sine_offset = math.sin(self.enemy_move_elapsed * self.sine_freq * math.pi * 2) * self.sine_amp
            self.enemy_x = base_x
            self.enemy_y = base_y + sine_offset
            if t >= 1.0:
                self.enemy_movement_mode = "idle"

        elif self.enemy_movement_mode == "path":
            if self.enemy_path_index < len(self.enemy_path):
                target = self.enemy_path[self.enemy_path_index]
                dx = target[0] - self.enemy_x
                dy = target[1] - self.enemy_y
                dist = math.hypot(dx, dy)
                speed = 150.0
                if dist < speed * dt:
                    self.enemy_x, self.enemy_y = target
                    self.enemy_path_index += 1
                else:
                    self.enemy_x += (dx / dist) * speed * dt
                    self.enemy_y += (dy / dist) * speed * dt
            else:
                self.enemy_movement_mode = "idle"

        elif self.enemy_movement_mode == "circle":
            self.enemy_move_elapsed += dt
            angle = math.radians(self.enemy_move_elapsed * self.circle_speed)
            self.enemy_x = self.circle_center[0] + self.circle_radius * math.cos(angle)
            self.enemy_y = self.circle_center[1] + self.circle_radius * math.sin(angle)
            if self.enemy_move_elapsed >= self.enemy_move_duration:
                self.enemy_movement_mode = "idle"

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

        if keys[py.K_SPACE] and self.player_bullet_reload <= 0 and self.hit_timer <= 0:
            self.player_bullet_reload = 0.15
            player_bullet_x = self.player.x + self.player_width / 2 - self.player_bullet_width / 2
            player_bullet_y = self.player.y - 5
            self.player_bullets.append([player_bullet_x, player_bullet_y])
            self.player_bulletsl.append([player_bullet_x, player_bullet_y])
            self.player_bulletsr.append([player_bullet_x, player_bullet_y])

        if self.player_bullet_reload > -1:
            self.player_bullet_reload -= 1 * dt

        screen.fill(BACKGROUND_COLOR)

        for spinner in self.spinning_blades[:]:
            spinner["rotation"] += spinner["spin_speed"] * spinner["spin_direction"] * dt
            spinner["spawn_elapsed"] += dt
            spinner["lifetime_elapsed"] += dt
            spinner["transition_elapsed"] += dt

            if spinner["duration"] is not None:
                remaining = spinner["duration"] - spinner["lifetime_elapsed"]
                if remaining <= 0:
                    self.spinning_blades.remove(spinner)
                    continue
                fade_out_t = 1.0 if spinner["fade_out_duration"] <= 0 else min(1.0, remaining / spinner["fade_out_duration"])
            else:
                fade_out_t = 1.0

            spinner["switch_timer"] -= dt
            if spinner["switch_timer"] <= 0:
                spinner["switch_timer"] += spinner["switch_interval"]
                spinner["on"] = not spinner["on"]
                spinner["transition_elapsed"] = 0.0

            if spinner["center_x"] is not None:
                blade_center_x = spinner["center_x"]
            else:
                blade_center_x = self.enemy_x + enemy_img.get_width() / 2
            if spinner["center_y"] is not None:
                blade_center_y = spinner["center_y"]
            else:
                blade_center_y = self.enemy_y + enemy_img.get_height() / 2

            fade_in_t = 1.0 if spinner["fade_in_duration"] <= 0 else min(1.0, spinner["spawn_elapsed"] / spinner["fade_in_duration"])
            visibility = fade_in_t * fade_out_t

            transition_duration = spinner["turn_on_duration"] if spinner["on"] else spinner["turn_off_duration"]
            transition_t = 1.0 if transition_duration <= 0 else min(1.0, spinner["transition_elapsed"] / transition_duration)
            red_t = transition_t if spinner["on"] else (1.0 - transition_t)

            blade_angle = spinner["rotation"]
            blade_pivot = (blade_center_x, blade_center_y)

            rotated_gray, gray_rect = self._rotate_blade_image(spinningblade_gray_img, blade_pivot, blade_angle)
            rotated_gray.set_alpha(int((1.0 - red_t) * SPINNING_BLADE_INACTIVE_ALPHA * visibility))
            screen.blit(rotated_gray, gray_rect)

            rotated_red, red_rect = self._rotate_blade_image(spinningblade_red_img, blade_pivot, blade_angle)
            rotated_red.set_alpha(int(red_t * 255 * visibility))
            screen.blit(rotated_red, red_rect)

            if red_t >= 1.0 and self.hit_timer <= 0:
                blade_mask = py.mask.from_surface(rotated_red)
                if self.player_mask.overlap(blade_mask, (red_rect.x - self.player.x, red_rect.y - self.player.y)):
                    self.hit_timer = HIT_TIMEOUT_DURATION

        for b in self.player_bullets[:]:
            b[1] -= self.player_bullet_speed * dt
            if enemy_mask.overlap(player_bullet_mask, (b[0] - self.enemy_x, b[1] - self.enemy_y)):
                self.score += 100
                self.player_bullets.remove(b)
                continue
            if b[1] < 0:
                self.player_bullets.remove(b)
        for b in self.player_bulletsl[:]:
            b[1] -= self.player_bullet_speed * dt
            b[0] -= self.player_bullet_speed / 10 * dt
            if enemy_mask.overlap(player_bullet_mask, (b[0] - self.enemy_x, b[1] - self.enemy_y)):
                self.score += 100
                self.player_bulletsl.remove(b)
                continue
            if b[1] < 0:
                self.player_bulletsl.remove(b)
        for b in self.player_bulletsr[:]:
            b[1] -= self.player_bullet_speed * dt
            b[0] += self.player_bullet_speed / 10 * dt
            if enemy_mask.overlap(player_bullet_mask, (b[0] - self.enemy_x, b[1] - self.enemy_y)):
                self.score += 100
                self.player_bulletsr.remove(b)
                continue
            if b[1] < 0:
                self.player_bulletsr.remove(b)

# bullet library
        for b in self.enemy_bullets[:]:
            b["time_alive"] += dt
            m_type = b["movement_type"]

            if m_type == "curved":
                b["angle"] += b["curve_rate"] * dt
                rad = math.radians(b["angle"])
                b["dx"] = b["speed"] * math.cos(rad)
                b["dy"] = b["speed"] * math.sin(rad)
                b["x"] += b["dx"] * dt
                b["y"] += b["dy"] * dt

            elif m_type == "zigzag":
                rad = math.radians(b["angle"])
                forward_x = b["speed"] * math.cos(rad)
                forward_y = b["speed"] * math.sin(rad)
                perp_x = -math.sin(rad)
                perp_y = math.cos(rad)
                side_speed = math.cos(b["time_alive"] * b["zigzag_freq"]) * b["zigzag_amp"]
                b["x"] += (forward_x + perp_x * side_speed) * dt
                b["y"] += (forward_y + perp_y * side_speed) * dt

            elif m_type == "accelerating":
                b["speed"] += b["accel"] * dt
                rad = math.radians(b["angle"])
                b["dx"] = b["speed"] * math.cos(rad)
                b["dy"] = b["speed"] * math.sin(rad)
                b["x"] += b["dx"] * dt
                b["y"] += b["dy"] * dt

            elif m_type == "homing":
                target_x = self.player.x + self.player_width / 2
                target_y = self.player.y + self.player_width / 2
                desired_rad = math.atan2(target_y - b["y"], target_x - b["x"])
                desired_angle = math.degrees(desired_rad)
                diff = (desired_angle - b["angle"] + 180) % 360 - 180
                max_turn = b["homing_rate"] * dt
                if abs(diff) < max_turn:
                    b["angle"] = desired_angle
                else:
                    b["angle"] += max_turn if diff > 0 else -max_turn
                rad = math.radians(b["angle"])
                b["dx"] = b["speed"] * math.cos(rad)
                b["dy"] = b["speed"] * math.sin(rad)
                b["x"] += b["dx"] * dt
                b["y"] += b["dy"] * dt

            else:
                b["x"] += b["dx"] * dt
                b["y"] += b["dy"] * dt

            b_mask = b["mask"]
            offset_x = int(b["x"] - b["width"] / 2 - self.player.x)
            offset_y = int(b["y"] - b["height"] / 2 - self.player.y)

            if self.hit_timer <= 0:
                if self.player_mask.overlap(b_mask, (offset_x, offset_y)):
                    self.hit_timer = HIT_TIMEOUT_DURATION
                else:
                    graze_x = int(b["x"] - b["width"] / 2 - (self.player.x + self.player_width / 2 - self.graze_radius))
                    graze_y = int(b["y"] - b["height"] / 2 - (self.player.y + self.player_width / 2 - self.graze_radius))
                    if self.graze_mask.overlap(b_mask, (graze_x, graze_y)):
                        self.graze_score += 1

            half_w = b["width"] / 2
            half_h = b["height"] / 2
            if b["x"] + half_w < 50 or b["x"] - half_w > 550 or b["y"] + half_h < 50 or b["y"] - half_h > 550:
                self.enemy_bullets.remove(b)

        if self.hit_timer <= 0:
            enemy_offset_x = int(self.enemy_x - self.player.x)
            enemy_offset_y = int(self.enemy_y - self.player.y)
            if self.player_mask.overlap(enemy_mask, (enemy_offset_x, enemy_offset_y)):
                self.hit_timer = HIT_TIMEOUT_DURATION

        for b in self.enemy_bullets:
            if b["image"] is not None:
                screen.blit(b["image"], (b["x"] - b["width"] / 2, b["y"] - b["height"] / 2))
            else:
                py.draw.circle(screen, b["color"], (int(b["x"]), int(b["y"])), b["radius"])

        self.draw_enemy()
        self.draw_player_bullets()
        self.draw_player()

        self.display.blit(border_img, (0, 0))

        score_surf = self.title_font.render(f"SCORE:", True, FONT_COLOR)
        screen.blit(score_surf, (585, 116))
        score_surf_main = self.subtitle_font.render(f"{self.score:07d}", True, FONT_COLOR)
        screen.blit(score_surf_main, (720, 120))

        graze_surf = self.title_font.render(f"GRAZE:", True, FONT_COLOR)
        screen.blit(graze_surf, (585, 156))
        graze_surf_main = self.subtitle_font.render(f"{self.graze_score}", True, FONT_COLOR)
        screen.blit(graze_surf_main, (720, 160))

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