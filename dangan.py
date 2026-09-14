import pygame as py, time, sys, json, math, csv, os
from pygame import mixer

py.init()
mixer.init()

# screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
screen = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
py.display.set_caption('Dangan')

font = py.font.Font("assets/fonts/VCR_OSD_MONO_1.001.ttf", 28)
title_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 42)

border_img = py.image.load("assets/backgrounds/game_art.png").convert_alpha()
player_img = py.image.load("assets/entities/player.png").convert_alpha()
player_bullet_img = py.image.load("assets/entities/player_bullet.png").convert_alpha()
cover_img = py.image.load("assets/backgrounds/mainmenu_art.png").convert_alpha()
levels_bg_img = py.image.load("assets/backgrounds/level_art_behind.png").convert_alpha()
levels_fg_img = py.image.load("assets/backgrounds/level_art_front.png").convert_alpha()
options_img = py.image.load("assets/backgrounds/options_art.png").convert_alpha()
win_level_bg_img = py.image.load("assets/backgrounds/win_level_art.png").convert_alpha()
lose_level_bg_img = py.image.load("assets/backgrounds/lose_level_art.png").convert_alpha()
manual_img = py.image.load("assets/backgrounds/manual_art.png").convert_alpha()
spinningblade_img = py.image.load("assets/entities/blade.png").convert_alpha()
spinningblade_gray_img = py.transform.grayscale(spinningblade_img)
spinningblade_red_img = spinningblade_img.copy()
spinningblade_red_img.fill((255, 60, 60, 255), special_flags=py.BLEND_RGBA_MULT)
fullheart_img = py.image.load("assets/entities/full_heart.png").convert_alpha()
halfheart_img = py.image.load("assets/entities/half_heart.png").convert_alpha()
haku_img = py.image.load("assets/entities/haku.png").convert_alpha()
mei_img = py.image.load("assets/entities/mei.png").convert_alpha()
gutsu_img = py.image.load("assets/entities/gutsu.png").convert_alpha()
kuu_img = py.image.load("assets/entities/kuu.png").convert_alpha()
shii_img = py.image.load("assets/entities/shii.png").convert_alpha()
RANK_IMAGES = {"HAKU": haku_img, "MEI": mei_img, "GUTSU": gutsu_img, "KUU": kuu_img, "SHII": shii_img}

keyboard_w_unpressed_img = py.image.load("assets/entities/keyboard_w_unpressed.png").convert_alpha()
keyboard_w_pressed_img = py.image.load("assets/entities/keyboard_w_pressed.png").convert_alpha()
keyboard_a_unpressed_img = py.image.load("assets/entities/keyboard_a_unpressed.png").convert_alpha()
keyboard_a_pressed_img = py.image.load("assets/entities/keyboard_a_pressed.png").convert_alpha()
keyboard_s_unpressed_img = py.image.load("assets/entities/keyboard_s_unpressed.png").convert_alpha()
keyboard_s_pressed_img = py.image.load("assets/entities/keyboard_s_pressed.png").convert_alpha()
keyboard_d_unpressed_img = py.image.load("assets/entities/keyboard_d_unpressed.png").convert_alpha()
keyboard_d_pressed_img = py.image.load("assets/entities/keyboard_d_pressed.png").convert_alpha()
keyboard_space_unpressed_img = py.image.load("assets/entities/keyboard_space_unpressed.png").convert_alpha()
keyboard_space_pressed_img = py.image.load("assets/entities/keyboard_space_pressed.png").convert_alpha()

KEY_DISPLAY_IMAGES = {
    "w": (keyboard_w_unpressed_img, keyboard_w_pressed_img),
    "a": (keyboard_a_unpressed_img, keyboard_a_pressed_img),
    "s": (keyboard_s_unpressed_img, keyboard_s_pressed_img),
    "d": (keyboard_d_unpressed_img, keyboard_d_pressed_img),
    "space": (keyboard_space_unpressed_img, keyboard_space_pressed_img),
}

KEY_DISPLAY_POSITIONS = {
    "w": (775, 462),
    "a": (730, 507),
    "s": (775, 507),
    "d": (820, 507),
    "space": (575, 507),
}

PLAYER_HITBOX_INSET = 1

def _build_player_hitbox_mask(image, inset):
    width, height = image.get_size()
    hitbox_surf = py.Surface((width, height), py.SRCALPHA)
    inset_rect = py.Rect(inset, inset, max(1, width - inset * 2), max(1, height - inset * 2))
    py.draw.rect(hitbox_surf, (255, 255, 255, 255), inset_rect)
    return py.mask.from_surface(hitbox_surf)

player_mask = _build_player_hitbox_mask(player_img, PLAYER_HITBOX_INSET)
player_bullet_mask = py.mask.from_surface(player_bullet_img)

player_flash_img = player_img.copy()
player_flash_img.fill((220, 90, 90, 255), special_flags=py.BLEND_RGBA_MULT)

py.key.set_repeat(250, 50)

# colors
BACKGROUND_COLOR = (16, 15, 22)
FONT_COLOR = (214, 255, 255)
HIGHLIGHT_COLOR = (255, 215, 0)
DISABLED_COLOR = (143, 122, 122)
HUD_DISABLED_COLOR = (150, 165, 165)

BASE_SPEED = 250

DEBUG_END_SCREEN_SKIP = True
DEBUG_TEST_SCORE = 66000
DEBUG_TEST_GRAZE = 250
DEBUG_TEST_HEALTH = 8

HIT_TIMEOUT_DURATION = 2.0
HIT_FADE_WINDOW = 0.4
SURVIVAL_SCORE_RATE = 40.0
SURVIVAL_SCORE_DOUBLE_TIME = 12 # 15 originally
SPINNING_BLADE_INACTIVE_ALPHA = 45
PLAYER_MAX_HEALTH = 8
DAMAGE_PENALTY_PER_HIT = 1000

previous_time = time.time()

STATISTICS_CSV_PATH = "statistics.csv"
STATISTICS_FIELDNAMES = ["level", "rank", "highscore", "plays"]
RANK_ORDER = ["HAKU", "MEI", "GUTSU", "KUU", "SHII", "NONE"]

OPTIONS_FILE = "options.csv"
def load_options():
    defaults = {"music_volume": 50, "sfx_volume": 50}
    if not os.path.exists(OPTIONS_FILE):
        return defaults
    with open(OPTIONS_FILE, newline="") as f:
        for key, value in csv.reader(f):
            if key in defaults:
                defaults[key] = int(value)
    return defaults

def save_options(music_volume, sfx_volume):
    with open(OPTIONS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["music_volume", music_volume])
        writer.writerow(["sfx_volume", sfx_volume])

LEVEL_UNLOCK_REQUIREMENTS = {
    "level1": None,
    "level2": ("level1", "MEI"),
    "level3": ("level2", "MEI"),
    "level4": ("level3", "MEI"),
    "level5": ("level4", "MEI"),
}

def is_level_unlocked(level_key, stats_manager):
    requirement = LEVEL_UNLOCK_REQUIREMENTS.get(level_key)
    if requirement is None:
        return True
    required_level_key, required_rank = requirement
    current_rank = stats_manager.get(required_level_key)["rank"]
    if current_rank not in RANK_ORDER or required_rank not in RANK_ORDER:
        return False
    return RANK_ORDER.index(current_rank) <= RANK_ORDER.index(required_rank)

LEVEL_BOSS_NAMES = {
    "level1": "Sheru",
    "level2": "Kiero",
    "level3": "---",
    "level4": "---",
    "level5": "---",
}

LEVEL_BOSS_IMAGE_PATHS = {
    "level1": "assets/entities/boss_level1.png",
    "level2": "assets/entities/boss_level2.png",
    "level3": "assets/entities/boss_level3.png",
    "level4": "assets/entities/boss_level4.png",
    "level5": "assets/entities/boss_level5.png",
}

LEVEL_STAT_DISPLAY_CONFIG = [
    {
        "font_path": "assets/fonts/VCR_OSD_MONO_1.001.ttf",
        "font_size": 24,
        "color": (226, 190, 189),
        "rank_pos": (730, 510),
        "rank_font_path": "assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf",
        "rank_font_size": 28,
        "rank_image_pos": (650, 300),
        "rank_image_size": (190, 190),
        "highscore_pos": (579, 148),
        "plays_pos": (635, 186),
        "boss_name_pos": (448, 148),
        "boss_image_pos": (560, 400),
        "locked_message_pos": (560, 268),
    },
    {
        "font_path": "assets/fonts/VCR_OSD_MONO_1.001.ttf",
        "font_size": 24,
        "color": (226, 190, 189),
        "rank_pos": (730, 510),
        "rank_font_path": "assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf",
        "rank_font_size": 28,
        "rank_image_pos": (650, 300),
        "rank_image_size": (190, 190),
        "highscore_pos": (579, 148),
        "plays_pos": (635, 186),
        "boss_name_pos": (448, 148),
        "boss_image_pos": (560, 400),
        "locked_message_pos": (500, 330),
    },
    {
        "font_path": "assets/fonts/VCR_OSD_MONO_1.001.ttf",
        "font_size": 24,
        "color": (226, 190, 189),
        "rank_pos": (730, 510),
        "rank_font_path": "assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf",
        "rank_font_size": 28,
        "rank_image_pos": (650, 300),
        "rank_image_size": (190, 190),
        "highscore_pos": (579, 148),
        "plays_pos": (635, 186),
        "boss_name_pos": (448, 148),
        "boss_image_pos": (560, 400),
        "locked_message_pos": (560, 330),
    },
    {
        "font_path": "assets/fonts/VCR_OSD_MONO_1.001.ttf",
        "font_size": 24,
        "color": (226, 190, 189),
        "rank_pos": (730, 510),
        "rank_font_path": "assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf",
        "rank_font_size": 28,
        "rank_image_pos": (650, 300),
        "rank_image_size": (190, 190),
        "highscore_pos": (579, 148),
        "plays_pos": (635, 186),
        "boss_name_pos": (448, 148),
        "boss_image_pos": (560, 400),
        "locked_message_pos": (560, 330),
    },
    {
        "font_path": "assets/fonts/VCR_OSD_MONO_1.001.ttf",
        "font_size": 24,
        "color": (226, 190, 189),
        "rank_pos": (730, 510),
        "rank_font_path": "assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf",
        "rank_font_size": 28,
        "rank_image_pos": (650, 300),
        "rank_image_size": (190, 190),
        "highscore_pos": (579, 148),
        "plays_pos": (635, 186),
        "boss_name_pos": (448, 148),
        "boss_image_pos": (560, 400),
        "locked_message_pos": (560, 330),
    },
]

LEVEL_BACKGROUND_IMAGE_PATHS = {
    "level1": "assets/backgrounds/level_one_behind.png",
    "level2": "assets/backgrounds/level_two_behind.png",
    "level3": "assets/backgrounds/level_three_behind.png",
    "level4": "assets/backgrounds/level_four_behind.png",
    "level5": "assets/backgrounds/level_five_behind.png",
}

class StatisticsManager:
    def __init__(self, filepath=STATISTICS_CSV_PATH, level_keys=None):
        self.filepath = filepath
        self.level_keys = level_keys or ["level1", "level2", "level3", "level4", "level5"]
        self.data = {}
        self._load()

    def _default_row(self):
        return {"rank": "NONE", "highscore": 0, "plays": 0}

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    key = row.get("level")
                    if not key:
                        continue
                    self.data[key] = {
                        "rank": row.get("rank", "NONE") or "NONE",
                        "highscore": int(row.get("highscore", 0) or 0),
                        "plays": int(row.get("plays", 0) or 0)
                    }

        for key in self.level_keys:
            if key not in self.data:
                self.data[key] = self._default_row()

        self._save()

    def _save(self):
        with open(self.filepath, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=STATISTICS_FIELDNAMES)
            writer.writeheader()
            for key in self.level_keys:
                row = self.data[key]
                writer.writerow({
                    "level": key,
                    "rank": row["rank"],
                    "highscore": row["highscore"],
                    "plays": row["plays"]
                })

    def get(self, level_key):
        return self.data.get(level_key, self._default_row())

    def record_play(self, level_key):
        row = self.data.setdefault(level_key, self._default_row())
        row["plays"] += 1
        self._save()

    def record_result(self, level_key, score, rank):
        row = self.data.setdefault(level_key, self._default_row())
        if score > row["highscore"]:
            row["highscore"] = score
        current_rank = row["rank"] if row["rank"] in RANK_ORDER else "NONE"
        if rank in RANK_ORDER and RANK_ORDER.index(rank) < RANK_ORDER.index(current_rank):
            row["rank"] = rank
        self._save()

# logic
class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState
        self.states = {}
        self.menu_states = {'splash', 'main_menu', 'level_select', 'settings', 'manual'}
        self.menu_music_path = "assets/audio/lobby_music.ogg"

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
        self.options = ["LEVEL", "OPTIONS", "MANUAL", "QUIT"]
        self.selected_index = 0
        self.menu_font = py.font.Font("assets/fonts/VCR_OSD_MONO_1.001.ttf", 45)

    def on_enter(self):
        self.selected_index = 0

    def handle_input(self, events):
        for event in events:
            if event.type == py.KEYDOWN:
                if event.key in (py.K_UP, py.K_w):
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key in (py.K_DOWN, py.K_s):
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key in (py.K_SPACE, py.K_RETURN):
                    if self.selected_index == 0:
                        self.gameStateManager.set_state('level_select')
                    elif self.selected_index == 1:
                        self.gameStateManager.set_state('settings')
                    elif self.selected_index == 2:
                        self.gameStateManager.set_state('manual')
                    elif self.selected_index == 3:
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
            y_pos = 397 + i * 48
            self.display.blit(opt_surf, (x_pos, y_pos))

class Manual:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.esc_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 25)

    def handle_input(self, events):
        for event in events:
            if event.type == py.KEYDOWN:
                if event.key in (py.K_SPACE, py.K_RETURN, py.K_ESCAPE):
                    self.gameStateManager.set_state('main_menu')

    def run(self, dt):
        self.display.blit(manual_img, (0, 0))

        back_surf = self.esc_font.render("<BACK>", True, (255, 255, 255))
        back_x = 81 - back_surf.get_width() // 2
        back_y = 546
        self.display.blit(back_surf, (back_x, back_y))

class LevelSelect:
    def __init__(self, display, gameStateManager, level_ref, stats_manager, level_keys, playable_level_keys):
        self.display = display
        self.gameStateManager = gameStateManager
        self.level_ref = level_ref
        self.stats_manager = stats_manager
        self.level_keys = level_keys
        self.playable_level_keys = playable_level_keys
        self.options = ["LEVEL 1", "LEVEL 2", "LEVEL 3", "LEVEL 4", "LEVEL 5", "BACK"]
        self.selected_index = 0

        self.level_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 35)
        self.esc_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 25)

        self._stat_font_cache = {}
        self._boss_image_cache = {}

    def _get_stat_font(self, font_path, font_size):
        cache_key = (font_path, font_size)
        if cache_key not in self._stat_font_cache:
            self._stat_font_cache[cache_key] = py.font.Font(font_path, font_size)
        return self._stat_font_cache[cache_key]

    def _get_boss_image(self, level_key):
        if level_key not in self._boss_image_cache:
            image = None
            path = LEVEL_BOSS_IMAGE_PATHS.get(level_key)
            if path and os.path.exists(path):
                image = py.image.load(path).convert_alpha()
            self._boss_image_cache[level_key] = image
        return self._boss_image_cache[level_key]

    def _get_rank_image(self, rank, size):
        base_image = RANK_IMAGES.get(rank)
        if base_image is None:
            return None
        cache_key = (rank, size)
        if cache_key not in self._boss_image_cache:
            self._boss_image_cache[cache_key] = py.transform.smoothscale(base_image, size)
        return self._boss_image_cache[cache_key]

    def _is_level_clickable(self, level_key):
        return level_key in self.playable_level_keys and is_level_unlocked(level_key, self.stats_manager)

    def on_enter(self):
        self.selected_index = 0

    def handle_input(self, events):
        for event in events:
            if event.type == py.KEYDOWN:
                if event.key in (py.K_UP, py.K_w):
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key in (py.K_DOWN, py.K_s):
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == py.K_ESCAPE:
                    self.gameStateManager.set_state('main_menu')
                elif event.key in (py.K_SPACE, py.K_RETURN):
                    if self.selected_index < len(self.level_keys):
                        level_key = self.level_keys[self.selected_index]
                        if self._is_level_clickable(level_key):
                            self.gameStateManager.set_state(level_key)
                    elif self.selected_index == 5:
                        self.gameStateManager.set_state('main_menu')

    def run(self, dt):
        self.display.fill(BACKGROUND_COLOR)
        self.display.blit(levels_bg_img, (0, 0))

        if self.selected_index < len(self.level_keys):
            level_key = self.level_keys[self.selected_index]
            config = LEVEL_STAT_DISPLAY_CONFIG[self.selected_index]
            stat_font = self._get_stat_font(config["font_path"], config["font_size"])
            color = config["color"]

            if level_key not in self.playable_level_keys:
                message_surf = stat_font.render("COMING SOON", True, (112, 100, 100))
                self.display.blit(message_surf, config["locked_message_pos"])
            elif not is_level_unlocked(level_key, self.stats_manager):
                message_surf = stat_font.render("MEI (LVL 1) REQUIRED", True, (112, 100, 100))
                self.display.blit(message_surf, config["locked_message_pos"])
            else:
                stats = self.stats_manager.get(level_key)

                rank_font = self._get_stat_font(config["rank_font_path"], config["rank_font_size"])
                rank_surf = rank_font.render(stats["rank"], True, color)
                self.display.blit(rank_surf, config["rank_pos"])

                rank_image = self._get_rank_image(stats["rank"], config["rank_image_size"])
                if rank_image is not None:
                    self.display.blit(rank_image, config["rank_image_pos"])

                highscore_surf = stat_font.render(f"HIGHSCORE: {stats['highscore']:07d}", True, color)
                self.display.blit(highscore_surf, config["highscore_pos"])

                plays_surf = stat_font.render(f"PLAYS: {stats['plays']}", True, color)
                self.display.blit(plays_surf, config["plays_pos"])

                boss_name = LEVEL_BOSS_NAMES.get(level_key, "???")
                boss_name_surf = stat_font.render(boss_name, True, color)
                self.display.blit(boss_name_surf, config["boss_name_pos"])

                boss_image = self._get_boss_image(level_key)
                if boss_image is not None:
                    self.display.blit(boss_image, config["boss_image_pos"])

        self.display.blit(levels_fg_img, (0, 0))

        for i in range(5):
            option = self.options[i]
            is_selected = (i == self.selected_index)
            is_clickable = self._is_level_clickable(self.level_keys[i])

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
        opts = load_options(); self.music_volume = opts["music_volume"]; self.sfx_volume = opts["sfx_volume"]
        mixer.music.set_volume(self.music_volume / 100.0)

        self.options_font = py.font.Font("assets/fonts/VCR_OSD_MONO_1.001.ttf", 40)
        self.esc_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 25)

    def on_enter(self):
        self.selected_index = 0

    def handle_input(self, events):
        for event in events:
            if event.type == py.KEYDOWN:
                if event.key in (py.K_UP, py.K_w):
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key in (py.K_DOWN, py.K_s):
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
                        save_options(self.music_volume, self.sfx_volume)
                elif event.key == py.K_RETURN:
                    if self.selected_index == 2:
                        self.gameStateManager.set_state('main_menu')
                        save_options(self.music_volume, self.sfx_volume)
                elif event.key == py.K_ESCAPE:
                    self.gameStateManager.set_state('main_menu')
                    save_options(self.music_volume, self.sfx_volume)
                elif event.key in (py.K_LEFT, py.K_a):
                    if self.selected_index == 0:
                        self.music_volume = max(0, self.music_volume - 5)
                        mixer.music.set_volume(self.music_volume / 100.0)
                    elif self.selected_index == 1:
                        self.sfx_volume = max(0, self.sfx_volume - 5)
                elif event.key in (py.K_RIGHT, py.K_d):
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
    def __init__(self, display, gameStateManager, level_file, settings_ref, enemy_image_path, rank_thresholds=None, level_key=None, stats_manager=None):
        self.display = display
        self.gameStateManager = gameStateManager
        self.level_file = level_file
        self.settings = settings_ref
        self.rank_thresholds = rank_thresholds
        self.level_key = level_key
        self.stats_manager = stats_manager

        self.enemy_img = py.image.load(enemy_image_path).convert_alpha()
        self.enemy_mask = py.mask.from_surface(self.enemy_img)

        with open(self.level_file, "r") as file:
            self.level_data = json.load(file)

        self.music_path = self.level_data["music"]
        self.bullet_mask_cache = {}
        self.bullet_sprite_cache = {}
        self.background_img_cache = {}
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
        if radius not in self.bullet_mask_cache:
            surf = py.Surface((radius * 2, radius * 2), py.SRCALPHA)
            py.draw.circle(surf, (255, 255, 255), (radius, radius), radius)
            self.bullet_mask_cache[radius] = py.mask.from_surface(surf)
        return self.bullet_mask_cache[radius]

    def get_bullet_sprite(self, sprite_path):
        if sprite_path not in self.bullet_sprite_cache:
            image = py.image.load(sprite_path).convert_alpha()
            mask = py.mask.from_surface(image)
            self.bullet_sprite_cache[sprite_path] = (image, mask)
        return self.bullet_sprite_cache[sprite_path]

    def _get_level_background(self):
        if self.level_key not in self.background_img_cache:
            path = LEVEL_BACKGROUND_IMAGE_PATHS.get(self.level_key)
            image = py.image.load(path).convert_alpha()
            self.background_img_cache[self.level_key] = image
        return self.background_img_cache[self.level_key]

    def preload_bullet_sprites(self):
        for event in self.level_data.get("timeline", []):
            sprite = event.get("sprite")
            if sprite:
                self.get_bullet_sprite(sprite)

    def _rotate_blade_image(self, image, pivot_pos, angle):
        origin_local = (image.get_width() / 2, image.get_height())
        image_rect = image.get_rect(topleft=(pivot_pos[0] - origin_local[0], pivot_pos[1] - origin_local[1]))
        offset_center_to_pivot = py.math.Vector2(pivot_pos) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-angle)
        rotated_center = (pivot_pos[0] - rotated_offset.x, pivot_pos[1] - rotated_offset.y)
        rotated_image = py.transform.rotate(image, angle)
        rotated_rect = rotated_image.get_rect(center=rotated_center)
        return rotated_image, rotated_rect

    def take_damage(self):
        self.hit_timer = HIT_TIMEOUT_DURATION
        self.survival_timer = 0.0
        self.health = max(0, self.health - 1)
        self.damage_taken += 1
        if self.health <= 0:
            self.gameStateManager.set_state(f"{self.level_key}_lose")

# action library
    def _fire_single_bullet(self, b_params):
        x = b_params.get("x", self.enemy_x + self.enemy_img.get_width() / 2)
        y = b_params.get("y", self.enemy_y + self.enemy_img.get_height() / 2)
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
        x = event.get("x", self.enemy_x + self.enemy_img.get_width() / 2)
        y = event.get("y", self.enemy_y + self.enemy_img.get_height() / 2)
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
        x = event.get("x", self.enemy_x + self.enemy_img.get_width() / 2)
        y = event.get("y", self.enemy_y + self.enemy_img.get_height() / 2)
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
        if self.stats_manager is not None and self.level_key is not None:
            self.stats_manager.record_play(self.level_key)

    def on_exit(self):
        mixer.music.stop()

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

        self.graze_margin = 12 # originally was 6
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
        self.survival_timer = 0.0
        self.graze_score = 0
        self.health = PLAYER_MAX_HEALTH
        self.damage_taken = 0
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
                elif DEBUG_END_SCREEN_SKIP and event.key == py.K_F1:
                    self.score = DEBUG_TEST_SCORE
                    self.graze_score = DEBUG_TEST_GRAZE
                    self.health = DEBUG_TEST_HEALTH
                    self.gameStateManager.set_state(f"{self.level_key}_win")
                elif DEBUG_END_SCREEN_SKIP and event.key == py.K_F2:
                    self.score = DEBUG_TEST_SCORE
                    self.graze_score = DEBUG_TEST_GRAZE
                    self.health = 0
                    self.gameStateManager.set_state(f"{self.level_key}_lose")

    def draw_player(self):
        self.display.blit(player_img, (self.player.x, self.player.y))
        intensity = self._hit_flash_intensity()
        if intensity > 0:
            player_flash_img.set_alpha(int(255 * intensity))
            self.display.blit(player_flash_img, (self.player.x, self.player.y))

    def draw_enemy(self):
        self.display.blit(self.enemy_img, (self.enemy_x, self.enemy_y))

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
            mixer.music.play(0)
            self.music_started = True

        if self.music_started:
            self.level_time += dt

        if self.music_started and self.level_time > 0.2 and self.health > 0 and not mixer.music.get_busy():
            self.gameStateManager.set_state(f"{self.level_key}_win")

        if self.hit_timer > 0:
            self.hit_timer = max(0.0, self.hit_timer - dt)

        if self.hit_timer <= 0:
            self.survival_timer += dt
            rate_multiplier = 2.3 ** (self.survival_timer / SURVIVAL_SCORE_DOUBLE_TIME)
            self.score_accum += SURVIVAL_SCORE_RATE * rate_multiplier * dt
            tick_score = int(self.score_accum)
            if tick_score > 0:
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
        right_pressed = keys[py.K_RIGHT] or keys[py.K_d]
        left_pressed = keys[py.K_LEFT] or keys[py.K_a]
        up_pressed = keys[py.K_UP] or keys[py.K_w]
        down_pressed = keys[py.K_DOWN] or keys[py.K_s]

        if (right_pressed and up_pressed) or (right_pressed and down_pressed) or (left_pressed and up_pressed) or (left_pressed and down_pressed):
            self.player_speed = round(self.BASE_SPEED * 0.707)
        else:
            self.player_speed = self.BASE_SPEED

        if left_pressed and self.player.left > 50:
            self.player_x -= self.player_speed * dt
            self.player.x = round(self.player_x)
            if self.player.left < 50:
                self.player.x = 50
        if right_pressed and self.player.right < 550:
            self.player_x += self.player_speed * dt
            self.player.x = round(self.player_x)
            if self.player.right > 550:
                self.player.x = 550 - self.player_width
        if up_pressed and self.player.top > 50:
            self.player_y -= self.player_speed * dt
            self.player.y = round(self.player_y)
            if self.player.top < 50:
                self.player.y = 50
        if down_pressed and self.player.bottom < 550:
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
        screen.blit(self._get_level_background(), (0, 0))

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
                blade_center_x = self.enemy_x + self.enemy_img.get_width() / 2
            if spinner["center_y"] is not None:
                blade_center_y = spinner["center_y"]
            else:
                blade_center_y = self.enemy_y + self.enemy_img.get_height() / 2

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
                    self.take_damage()

        for b in self.player_bullets[:]:
            b[1] -= self.player_bullet_speed * dt
            if self.enemy_mask.overlap(player_bullet_mask, (b[0] - self.enemy_x, b[1] - self.enemy_y)):
                self.score += 100
                self.player_bullets.remove(b)
                continue
            if b[1] < 0:
                self.player_bullets.remove(b)
        for b in self.player_bulletsl[:]:
            b[1] -= self.player_bullet_speed * dt
            b[0] -= self.player_bullet_speed / 10 * dt
            if self.enemy_mask.overlap(player_bullet_mask, (b[0] - self.enemy_x, b[1] - self.enemy_y)):
                self.score += 100
                self.player_bulletsl.remove(b)
                continue
            if b[1] < 0:
                self.player_bulletsl.remove(b)
        for b in self.player_bulletsr[:]:
            b[1] -= self.player_bullet_speed * dt
            b[0] += self.player_bullet_speed / 10 * dt
            if self.enemy_mask.overlap(player_bullet_mask, (b[0] - self.enemy_x, b[1] - self.enemy_y)):
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
                    self.take_damage()
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
            if self.player_mask.overlap(self.enemy_mask, (enemy_offset_x, enemy_offset_y)):
                self.take_damage()

        for b in self.enemy_bullets:
            if b["image"] is not None:
                screen.blit(b["image"], (b["x"] - b["width"] / 2, b["y"] - b["height"] / 2))
            else:
                py.draw.circle(screen, b["color"], (int(b["x"]), int(b["y"])), b["radius"])

        self.draw_enemy()
        self.draw_player_bullets()
        self.draw_player()

        self.display.blit(border_img, (0, 0))

        hud_color = HUD_DISABLED_COLOR if self.hit_timer > 0 else (226, 190, 189)

        score_surf = self.title_font.render(f"SCORE:", True, hud_color)
        screen.blit(score_surf, (585, 116))
        score_surf_main = self.subtitle_font.render(f"{self.score:07d}", True, hud_color)
        screen.blit(score_surf_main, (720, 120))

        graze_surf = self.title_font.render(f"GRAZE:", True, hud_color)
        screen.blit(graze_surf, (585, 156))
        graze_surf_main = self.subtitle_font.render(f"{self.graze_score}", True, hud_color)
        screen.blit(graze_surf_main, (720, 160))

        health_surf = self.title_font.render(f"PLAYER:", True, (226, 190, 189))
        screen.blit(health_surf, (585, 226))
        for i in range(4):
            heart_remaining = self.health - (3 - i) * 2
            if heart_remaining >= 2:
                screen.blit(fullheart_img, (740 + i * 30, 230))
            elif heart_remaining == 1:
                screen.blit(halfheart_img, (740 + i * 30, 230))

        key_states = {
            "w": up_pressed,
            "a": left_pressed,
            "s": down_pressed,
            "d": right_pressed,
            "space": keys[py.K_SPACE],
        }
        for key_name, is_pressed in key_states.items():
            unpressed_img, pressed_img = KEY_DISPLAY_IMAGES[key_name]
            key_img = pressed_img if is_pressed else unpressed_img
            screen.blit(key_img, KEY_DISPLAY_POSITIONS[key_name])

class LevelResultScreen:
    def __init__(self, display, gameStateManager, level_ref, title_text, music_path=None, show_rating=False, background_img=None, level_key=None, stats_manager=None):
        self.display = display
        self.gameStateManager = gameStateManager
        self.level_ref = level_ref
        self.title_text = title_text
        self.music_path = music_path
        self.show_rating = show_rating
        self.background_img = background_img
        self.level_key = level_key
        self.stats_manager = stats_manager
        self.options = ["RETRY", "LEAVE"]
        self.selected_index = 0

        self.title_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 50)
        self.option_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 25)
        self.stat_font = py.font.Font("assets/fonts/VCR_OSD_MONO_1.001.ttf", 45)
        self.stat_font_small = py.font.Font("assets/fonts/VCR_OSD_MONO_1.001.ttf", 26)
        self.stat_small_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 18)
        self.equation_font = py.font.Font("assets/fonts/VCR_OSD_MONO_1.001.ttf", 26)
        self.rank_font = py.font.Font("assets/fonts/DFPOPCorn-W12-WINP-RKSJ-H.ttf", 35)

    def on_enter(self):
        self.selected_index = 0
        keys = py.key.get_pressed()
        self.confirm_ready = not (keys[py.K_SPACE] or keys[py.K_RETURN])
        if self.music_path:
            mixer.music.load(self.music_path)
            mixer.music.play(0)
        if self.show_rating and self.stats_manager is not None and self.level_key is not None:
            _, _, _, _, _, final_score, rank = self._compute_rating()
            self.stats_manager.record_result(self.level_key, final_score, rank)

    def _compute_rating(self):
        score = self.level_ref.score
        graze = self.level_ref.graze_score
        damage_taken = self.level_ref.damage_taken
        graze_bonus = (graze // 100) * 1000
        damage_penalty = damage_taken * DAMAGE_PENALTY_PER_HIT
        final_score = score + graze_bonus - damage_penalty

        if damage_taken == 0:
            rank = "HAKU"
        else:
            rank = "SHII"
            for rank_name, threshold in self.level_ref.rank_thresholds:
                if rank_name == "HAKU":
                    continue
                if final_score >= threshold:
                    rank = rank_name
                    break

        return score, graze, graze_bonus, damage_taken, damage_penalty, final_score, rank

    def handle_input(self, events):
        for event in events:
            if event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    self.gameStateManager.set_state('level_select')
                elif event.key in (py.K_UP, py.K_w, py.K_DOWN, py.K_s):
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key in (py.K_SPACE, py.K_RETURN):
                    if not self.confirm_ready:
                        continue
                    if self.selected_index == 0:
                        self.gameStateManager.set_state(self.level_key)
                    else:
                        self.gameStateManager.set_state('level_select')

    def run(self, dt):
        if not self.confirm_ready:
            keys = py.key.get_pressed()
            if not (keys[py.K_SPACE] or keys[py.K_RETURN]):
                self.confirm_ready = True

        if self.background_img is not None:
            self.display.blit(self.background_img, (0, 0))
        else:
            self.display.fill(BACKGROUND_COLOR)

        if self.show_rating:
            score, graze, graze_bonus, damage_taken, damage_penalty, final_score, rank = self._compute_rating()

            equation_x = 115
            line_height = 32
            line1_y = 160

            line1_text = "   " + f"{score:07d}"
            line2_text = "  +" + f"{graze_bonus:>7d}"
            line3_text = "  -" + f"{damage_penalty:>7d}"

            line1_surf = self.equation_font.render(line1_text, True, (255, 255, 233))
            line2_surf = self.equation_font.render(line2_text, True, (255, 255, 233))
            line3_surf = self.equation_font.render(line3_text, True, (255, 255, 233))

            self.display.blit(line1_surf, (equation_x, line1_y))
            self.display.blit(line2_surf, (equation_x, line1_y + line_height))
            self.display.blit(line3_surf, (equation_x, line1_y + line_height * 2))

            label_x = equation_x + line1_surf.get_width() + 15
            score_label_surf = self.stat_small_font.render("(score)", True, (213, 203, 183))
            graze_label_surf = self.stat_small_font.render("(graze)", True, (213, 203, 183))
            damage_label_surf = self.stat_small_font.render("(damage)", True, (213, 203, 183))
            self.display.blit(score_label_surf, (label_x, line1_y + 6))
            self.display.blit(graze_label_surf, (label_x, line1_y + line_height + 6))
            self.display.blit(damage_label_surf, (label_x, line1_y + line_height * 2 + 6))

            total_surf = self.stat_font.render(f"SCORE: {final_score}", True, (255, 255, 233))
            deaths_surf = self.stat_font_small.render(f"{damage_taken} DAMAGE", True, (213, 203, 183))
            self.display.blit(total_surf, (equation_x - 73, line1_y + line_height * 3 + 20))
            self.display.blit(deaths_surf, (equation_x + 118, line1_y + line_height * 3 + total_surf.get_height() + 24))

            rank_img = RANK_IMAGES[rank]
            RANK_IMAGE_SCALE = 1.3
            scaled_w = int(rank_img.get_width() * RANK_IMAGE_SCALE)
            scaled_h = int(rank_img.get_height() * RANK_IMAGE_SCALE)
            rank_img = py.transform.smoothscale(rank_img, (scaled_w, scaled_h))
            rank_x = 540 # was SCREEN_WIDTH - rank_img.get_width() - 60
            rank_y = 50 # was SCREEN_HEIGHT / 2 - rank_img.get_height() / 2
            self.display.blit(rank_img, (rank_x, rank_y))

            rank_label_surf = self.rank_font.render(rank, True, (255,255,255))
            rank_label_x = rank_x + rank_img.get_width() / 2 - rank_label_surf.get_width() / 2 + 44
            rank_label_y = rank_y + rank_img.get_height() + 80
            self.display.blit(rank_label_surf, (rank_label_x, rank_label_y))

        for i, option in enumerate(self.options):
            is_selected = (i == self.selected_index)

            if is_selected:
                text_str = f"<{option}>"
                color = HIGHLIGHT_COLOR
            else:
                text_str = option
                color = (213, 203, 183)

            opt_surf = self.option_font.render(text_str, True, color)
            opt_x = SCREEN_WIDTH / 2 - opt_surf.get_width() / 2
            opt_y = 500 + i * 40
            self.display.blit(opt_surf, (opt_x, opt_y))

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

        self.level_keys = ["level1", "level2", "level3", "level4", "level5"]
        self.playable_level_keys = ["level1", "level2"]
        self.stats_manager = StatisticsManager(level_keys=self.level_keys)

        self.settings = Settings(self.screen, self.gameStateManager)

        rank_thresholds_1 = [
            ("MEI", 100000),
            ("GUTSU", 80000),
            ("KUU", 50000),
            ("SHII", 0)
        ]

        rank_thresholds_2 = [
            ("MEI", 60000),
            ("GUTSU", 35000),
            ("KUU", 15000),
            ("SHII", 0)
        ]

        self.level1 = Level(self.screen, self.gameStateManager, "levels/level_one_sheru.json", self.settings,
            enemy_image_path="assets/entities/sheru_mini.png",
            rank_thresholds=rank_thresholds_1,
            level_key="level1", stats_manager=self.stats_manager)

        self.level2 = Level(self.screen, self.gameStateManager, "levels/level_two_kiero.json", self.settings,
            enemy_image_path="assets/entities/kiero_mini.png",
            rank_thresholds=rank_thresholds_2,
            level_key="level2", stats_manager=self.stats_manager)

        self.splash = Splash(self.screen, self.gameStateManager)
        self.main_menu = MainMenu(self.screen, self.gameStateManager)
        self.manual = Manual(self.screen, self.gameStateManager)
        self.level_select = LevelSelect(self.screen, self.gameStateManager, self.level1, self.stats_manager, self.level_keys, self.playable_level_keys)

        self.level1_win = LevelResultScreen(self.screen, self.gameStateManager, self.level1, "LEVEL CLEAR", "assets/audio/level_win.ogg", show_rating=True, background_img=win_level_bg_img, level_key="level1", stats_manager=self.stats_manager)
        self.level1_lose = LevelResultScreen(self.screen, self.gameStateManager, self.level1, "GAME OVER", "assets/audio/level_lose.ogg", background_img=lose_level_bg_img, level_key="level1", stats_manager=self.stats_manager)

        self.level2_win = LevelResultScreen(self.screen, self.gameStateManager, self.level2, "LEVEL CLEAR", "assets/audio/level_win.ogg", show_rating=True, background_img=win_level_bg_img, level_key="level2", stats_manager=self.stats_manager)
        self.level2_lose = LevelResultScreen(self.screen, self.gameStateManager, self.level2, "GAME OVER", "assets/audio/level_lose.ogg", background_img=lose_level_bg_img, level_key="level2", stats_manager=self.stats_manager)

        self.states = {
            'splash': self.splash,
            'main_menu': self.main_menu,
            'manual': self.manual,
            'level_select': self.level_select,
            'settings': self.settings,
            'level1': self.level1,
            'level1_win': self.level1_win,
            'level1_lose': self.level1_lose,
            'level2': self.level2,
            'level2_win': self.level2_win,
            'level2_lose': self.level2_lose
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