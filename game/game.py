import pygame
import sys
import os

# --- Función para manejar rutas de recursos en PyInstaller ---
"""
def resource_path(relative_path):
    
    #Obtiene la ruta absoluta a un recurso, funciona tanto en desarrollo como en PyInstaller.
    #PyInstaller crea una carpeta temporal y almacena su ruta en _MEIPASS.
    #Esto se hace con objetivo de crar un archivo ejecutable en caso de que se requiera.
    
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_ppython.exeath, relative_path)
"""
def resource_path(relative_path):
    """
    Obtiene la ruta absoluta a un recurso, funciona tanto en desarrollo como en PyInstaller.
    PyInstaller crea una carpeta temporal y almacena su ruta en _MEIPASS.
    Esto se hace con objetivo de crear un archivo ejecutable en caso de que se requiera.
    """
    try:
        # Intenta obtener la ruta base de PyInstaller
        base_path = sys._MEIPASS
    except AttributeError:
        # Si no se está ejecutando desde PyInstaller, usa la ruta actual del script
        base_path = os.path.abspath(".")
    # Une la ruta base con la ruta relativa del recurso
    return os.path.join(base_path, relative_path)

# --- Módulo de Constantes y Configuraciones ---
class Config:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60

    # Colores
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    GRAY = (150, 150, 150)

    # Opciones de juego
    PUNTAJE_OBJETIVO_OPTIONS = [1000, 2000, 3000, 4000, 5000,8000]
    NUM_JUGADORES_OPTIONS = [2, 3, 4, 5, 6]

    # Mapeo de puntajes para los sensores 1-8
    SCORE_MAPPING = {
        "1": 500, "2": 300, "3": 200, "4": 150,
        "5": 100, "6": 50, "7": 30, "8": 15
    }

    # Estados del Juego
    STATE_MENU = 0
    STATE_SELECT_PLAYERS = 1
    STATE_SELECT_SCORE = 2
    STATE_GAMEPLAY = 3
    STATE_PAUSE = 4
    STATE_GAME_OVER = 5

    # Mapeo de Teclas Estándar para simular inputs de Arcade
    KEY_MAPPING = {
        pygame.K_UP: "UP",
        pygame.K_DOWN: "DOWN",
        pygame.K_RETURN: "ENTER",
        pygame.K_TAB: "TAB",
        pygame.K_1: "1", pygame.K_2: "2", pygame.K_3: "3", pygame.K_4: "4",
        pygame.K_5: "5", pygame.K_6: "6", pygame.K_7: "7", pygame.K_8: "8",
        pygame.K_s: "S_KEY",
        pygame.K_w: "W_KEY"
    }

    # Eventos Personalizados
    EVENT_ARCADE_INPUT = pygame.USEREVENT + 1
    EVENT_SCORE = pygame.USEREVENT + 2
    EVENT_SYSTEM_CONTROL = pygame.USEREVENT + 3


# --- Módulo de Recursos ---
class ResourceManager:
    def __init__(self):
        self.fonts = {}
        self.images = {}
        self.sounds = {}
        self.icon = None
        self.animated_backgrounds = {}
        # Almacenaremos las rutas de los sonidos para pygame.mixer.music
        self._sound_paths = {} 
        self._load_fonts()
        self._load_sounds()
        self._load_icon()

    def _load_icon(self):
        try:
            self.icon = pygame.image.load(resource_path(os.path.join('assets', 'images', 'icono.png')))
        except Exception as e:
            print(f"Error cargando icono: {e}")
            self.icon = None

    def _load_fonts(self):
        try:
            self.fonts['large'] = pygame.font.Font(resource_path(os.path.join('assets', 'fonts', 'predataur.ttf')), 74)
            self.fonts['medium'] = pygame.font.Font(resource_path(os.path.join('assets', 'fonts', 'electromagnetic.otf')), 50)
            self.fonts['small'] = pygame.font.Font(resource_path(os.path.join('assets', 'fonts', 'electromagnetic.otf')), 36)
        except Exception as e:
            print(f"Error cargando fuentes: {e}")
            self.fonts['large'] = pygame.font.Font(None, 74)
            self.fonts['medium'] = pygame.font.Font(None, 50)
            self.fonts['small'] = pygame.font.Font(None, 36)

    def _load_sounds(self):
        self.sounds = {} 
        self._sound_paths = {} 
        try:
            points_path = resource_path(os.path.join('assets', 'sounds', 'points.wav'))
            game_over_path = resource_path(os.path.join('assets', 'sounds', 'gameover.wav'))
            button_path = resource_path(os.path.join('assets', 'sounds', 'button.wav'))
            fanfare_path = resource_path(os.path.join('assets', 'sounds', 'fanfare.mp3'))
            background_music_path = resource_path(os.path.join('assets', 'sounds', 'background.ogg'))

            self.sounds['points'] = pygame.mixer.Sound(points_path)
            self.sounds['game_over'] = pygame.mixer.Sound(game_over_path)
            self.sounds['button'] = pygame.mixer.Sound(button_path)
            self.sounds['fanfare'] = pygame.mixer.Sound(fanfare_path)
            # Aunque no se usa el objeto Sound directamente para pygame.mixer.music.load, lo mantenemos por si acaso.
            self.sounds['background'] = pygame.mixer.Sound(background_music_path)

            # Almacenar las rutas para el mixer.music.load()
            self._sound_paths['background'] = background_music_path

        except pygame.error as e:
            print(f"Advertencia: No se pudieron cargar los sonidos. Asegúrate de que los archivos existan en 'assets/sounds/'. Error: {e}")
            # Asegurar que las claves existan incluso si la carga falla
            for key in ['points', 'game_over', 'button', 'fanfare', 'background']:
                if key not in self.sounds:
                    self.sounds[key] = None
                if key not in self._sound_paths:
                    self._sound_paths[key] = None

    def get_sound_path(self, sound_name):
        return self._sound_paths.get(sound_name)

    def load_animated_background(self, state_name, screen_width, screen_height):
        path = resource_path(os.path.join('assets', state_name))
        images_list = []
        if state_name in self.animated_backgrounds:
            return self.animated_backgrounds[state_name]

        try:
            # os.listdir requiere la ruta que resource_path proporciona
            files = sorted([f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))])

            if not files:
                print(f"Advertencia: No se encontraron imágenes en la carpeta '{path}'. Asegúrate de que existan y sean PNG/JPG.")
                self.animated_backgrounds[state_name] = []
                return []

            for filename in files:
                img_path = resource_path(os.path.join('assets', state_name, filename))
                image = pygame.image.load(img_path).convert_alpha()
                image = pygame.transform.scale(image, (screen_width, screen_height))
                images_list.append(image)

            self.animated_backgrounds[state_name] = images_list
            return images_list
        except pygame.error as e:
            print(f"Advertencia: No se pudieron cargar las imágenes para el estado '{state_name}'. Error: {e}")
            self.animated_backgrounds[state_name] = []
            return []
        except FileNotFoundError as e:
            print(f"Advertencia: La carpeta de estado '{path}' no fue encontrada. Error: {e}")
            self.animated_backgrounds[state_name] = []
            return []

    def get_font(self, font_size):
        return self.fonts.get(font_size)

    def get_sound(self, sound_name):
        return self.sounds.get(sound_name)
    
    def get_icon(self):
        return self.icon


# --- Módulo de Utilidades de Dibujo ---
class DrawingUtils:
    @staticmethod
    def draw_text(surface, text, font, color, x, y, center=True):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_surface, text_rect)

# --- Clases de Pantalla/Estado del Juego ---
class GameState:
    def __init__(self, game):
        self.game = game
        self.background_frames = []
        self.current_frame_index = 0
        self.last_frame_time = 0
        self.animation_speed_ms = 33 #30 FPS para la animación
        self.animation_finished = False

    def enter_state(self):
        self.background_frames = []
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.animation_finished = False

    def handle_input(self, key_name):
        raise NotImplementedError

    def update(self):
        if not self.animation_finished and self.background_frames:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_frame_time > self.animation_speed_ms:
                self.last_frame_time = current_time
                if self.current_frame_index < len(self.background_frames) - 1:
                    self.current_frame_index += 1
                else:
                    self.animation_finished = True

    def draw(self, screen):
        if self.background_frames and self.current_frame_index < len(self.background_frames):
            screen.blit(self.background_frames[self.current_frame_index], (0, 0))
        else:
            screen.fill(Config.BLACK) # Fallback si no hay frames

class MenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.selection_index = 0
        self.options = ["Seleccionar jugadores", "Seleccionar puntaje", "Jugar"]

    def enter_state(self):
        super().enter_state()
        self.background_frames = self.game.resources.load_animated_background('state_inicio', Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.animation_finished = False
        # Solo reproducir la música de fondo si ya está cargada
        if self.game.game_music_loaded:
            pygame.mixer.music.play(-1)

    def handle_input(self, key_name):
        if key_name == "UP":
            self.selection_index = (self.selection_index - 1 + len(self.options)) % len(self.options)
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
        elif key_name == "DOWN":
            self.selection_index = (self.selection_index + 1) % len(self.options)
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
        elif key_name == "ENTER":
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
            if self.selection_index == 0:
                self.game.set_state(Config.STATE_SELECT_PLAYERS)
            elif self.selection_index == 1:
                self.game.set_state(Config.STATE_SELECT_SCORE)
            elif self.selection_index == 2:
                self.game.reset_game()
                self.game.set_state(Config.STATE_GAMEPLAY)

    def draw(self, screen):
        super().draw(screen)

        y_start = Config.SCREEN_HEIGHT // 2 - 50
        for i, option in enumerate(self.options):
            color = Config.GREEN if self.selection_index == i else Config.WHITE
            DrawingUtils.draw_text(screen, option, self.game.resources.fonts['medium'], color, Config.SCREEN_WIDTH // 2, y_start + i * 60)
        pygame.display.flip()

class SelectPlayersState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.current_idx = Config.NUM_JUGADORES_OPTIONS.index(self.game.num_players_selected)

    def enter_state(self):
        super().enter_state()
        self.background_frames = self.game.resources.load_animated_background('state_jugadores', Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.animation_finished = False
        # La música de fondo ya está cargada y reproduciéndose desde MenuState o se iniciará si no lo estaba.
        # No se necesita cargarla de nuevo aquí.

    def handle_input(self, key_name):
        if key_name == "UP":
            self.current_idx = (self.current_idx - 1 + len(Config.NUM_JUGADORES_OPTIONS)) % len(Config.NUM_JUGADORES_OPTIONS)
            self.game.num_players_selected = Config.NUM_JUGADORES_OPTIONS[self.current_idx]
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
        elif key_name == "DOWN":
            self.current_idx = (self.current_idx + 1) % len(Config.NUM_JUGADORES_OPTIONS)
            self.game.num_players_selected = Config.NUM_JUGADORES_OPTIONS[self.current_idx]
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
        elif key_name == "ENTER":
            print(f"Config: {self.game.num_players_selected} jugadores seleccionados.")
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
            self.game.set_state(Config.STATE_MENU)

    def draw(self, screen):
        super().draw(screen)

        y_start = Config.SCREEN_HEIGHT // 3
        for i, num_jug in enumerate(Config.NUM_JUGADORES_OPTIONS):
            color = Config.GREEN if num_jug == self.game.num_players_selected else Config.WHITE
            DrawingUtils.draw_text(screen, f"{num_jug} Jugadores", self.game.resources.fonts['medium'], color, Config.SCREEN_WIDTH // 2, y_start + i * 50)
        pygame.display.flip()

class SelectScoreState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.current_idx = Config.PUNTAJE_OBJETIVO_OPTIONS.index(self.game.game_target_score)

    def enter_state(self):
        super().enter_state()
        self.background_frames = self.game.resources.load_animated_background('state_puntos', Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.animation_finished = False
        # La música de fondo ya está cargada y reproduciéndose desde MenuState o se iniciará si no lo estaba.
        # No se necesita cargarla de nuevo aquí.

    def handle_input(self, key_name):
        if key_name == "UP":
            self.current_idx = (self.current_idx - 1 + len(Config.PUNTAJE_OBJETIVO_OPTIONS)) % len(Config.PUNTAJE_OBJETIVO_OPTIONS)
            self.game.game_target_score = Config.PUNTAJE_OBJETIVO_OPTIONS[self.current_idx]
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
        elif key_name == "DOWN":
            self.current_idx = (self.current_idx + 1) % len(Config.PUNTAJE_OBJETIVO_OPTIONS)
            self.game.game_target_score = Config.PUNTAJE_OBJETIVO_OPTIONS[self.current_idx]
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
        elif key_name == "ENTER":
            print(f"Config: {self.game.game_target_score} puntos objetivo seleccionados.")
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
            self.game.set_state(Config.STATE_MENU)

    def draw(self, screen):
        super().draw(screen)

        y_start = Config.SCREEN_HEIGHT // 4 #3
        for i, score_opt in enumerate(Config.PUNTAJE_OBJETIVO_OPTIONS):
            color = Config.GREEN if score_opt == self.game.game_target_score else Config.WHITE
            DrawingUtils.draw_text(screen, f"{score_opt} Puntos", self.game.resources.fonts['medium'], color, Config.SCREEN_WIDTH // 2, y_start + i * 50)
        pygame.display.flip()

class GameplayState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.display_score_feedback = False
        self.score_feedback_value = 0
        self.score_feedback_start_time = 0
        self.score_feedback_duration_ms = 1000

    def enter_state(self):
        super().enter_state()
        self.background_frames = self.game.resources.load_animated_background('state_play', Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.animation_finished = False
        self.display_score_feedback = False
        # Solo reproducir la música de fondo si ya está cargada
        if self.game.game_music_loaded:
            pygame.mixer.music.play(-1)


    def handle_input(self, key_name):
        current_player = self.game.players[self.game.current_player_index]

        if key_name == "TAB":
            self._check_for_winner(current_player)
            if self.game.current_game_state == Config.STATE_GAMEPLAY:
                self.game.current_player_index = (self.game.current_player_index + 1) % len(self.game.players)
                print(f"Juego: Turno de: {self.game.players[self.game.current_player_index]['name']}")
            self.display_score_feedback = False
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
        elif key_name == "ENTER":
            self.game.set_state(Config.STATE_PAUSE)
            self.game.pause_menu_selection_index = 0
            pygame.mixer.music.pause() # Pausar la música al entrar en pausa
            print("Juego: Pausado.")
            self.display_score_feedback = False
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
        elif key_name in Config.SCORE_MAPPING:
            score_value = Config.SCORE_MAPPING[key_name]
            if not current_player['has_won']:
                current_player['score'] += score_value
                print(f"Juego: {current_player['name']} obtuvo {score_value} puntos. Total: {current_player['score']}")
                if self.game.resources.sounds['points']: self.game.resources.sounds['points'].play()

                self.score_feedback_value = score_value
                self.score_feedback_start_time = pygame.time.get_ticks()
                self.display_score_feedback = True

                self._check_for_winner(current_player)

    def _check_for_winner(self, player):
        if not player['has_won'] and player['score'] >= self.game.game_target_score:
            player['has_won'] = True
            self.game.winners.append(player)
            print(f"¡{player['name']} alcanzó el objetivo! Es el puesto #{len(self.game.winners)}")

            if (len(self.game.winners) >= 2 and self.game.num_players_selected > 2) or all(p['has_won'] for p in self.game.players):
                pygame.mixer.music.stop() # Detener la música de fondo al final del juego
                self.game.set_state(Config.STATE_GAME_OVER)
                if self.game.resources.sounds['fanfare']:
                    self.game.resources.sounds['fanfare'].play()
                print("Juego: Fin de partida alcanzado.")
            elif self.game.resources.sounds['game_over']:
                if not pygame.mixer.get_busy() or self.game.resources.sounds['game_over'].get_num_channels() == 0:
                    self.game.resources.sounds['game_over'].play()

    def update(self):
        super().update()

        if self.display_score_feedback:
            if pygame.time.get_ticks() - self.score_feedback_start_time > self.score_feedback_duration_ms:
                self.display_score_feedback = False

    def draw(self, screen):
        super().draw(screen)

        current_player = self.game.players[self.game.current_player_index]

        DrawingUtils.draw_text(screen, f"Turno del  {current_player['name']}", self.game.resources.fonts['medium'], Config.YELLOW, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 4)
        DrawingUtils.draw_text(screen, f"Puntaje  {current_player['score']}", self.game.resources.fonts['medium'], Config.WHITE, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 - 50)

        if self.display_score_feedback:
            feedback_text = f"* {self.score_feedback_value} *"
            DrawingUtils.draw_text(screen, feedback_text, self.game.resources.fonts['large'], Config.GREEN, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 + 50)

        y_offset_start = Config.SCREEN_HEIGHT - 100
        total_width_for_players = Config.SCREEN_WIDTH - 200
        player_spacing = total_width_for_players // len(self.game.players) if len(self.game.players) > 0 else 0
        start_x = 100

        for i, player in enumerate(self.game.players):
            color = Config.YELLOW if i == self.game.current_player_index else Config.WHITE
            DrawingUtils.draw_text(screen, f"{player['name']}  {player['score']}", self.game.resources.fonts['small'], color, start_x + player_spacing * i, y_offset_start, center=False)

        pygame.display.flip()

class PauseState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.selection_index = 0
        self.options = ["Continuar", "Salir"]

    def enter_state(self):
        super().enter_state()
        self.background_frames = self.game.resources.load_animated_background('state_pause', Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.animation_finished = True

    def handle_input(self, key_name):
        if key_name == "UP":
            self.selection_index = (self.selection_index - 1 + len(self.options)) % len(self.options)
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
        elif key_name == "DOWN":
            self.selection_index = (self.selection_index + 1) % len(self.options)
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
        elif key_name == "ENTER":
            if self.game.resources.get_sound('button'): self.game.resources.get_sound('button').play()
            if self.selection_index == 0:
                self.game.set_state(Config.STATE_GAMEPLAY)
                pygame.mixer.music.unpause() # Reanudar la música al continuar
                print("Juego: Reanudado.")
            elif self.selection_index == 1:
                self.game.set_state(Config.STATE_MENU)
                self.game.reset_game_state_variables()
                pygame.mixer.music.stop() # Detener la música al salir de la partida
                print("Juego: Saliendo de la partida.")

    def draw(self, screen):
        super().draw(screen)

        y_start = Config.SCREEN_HEIGHT // 2 + 80
        for i, option in enumerate(self.options):
            color = Config.GREEN if self.selection_index == i else Config.WHITE
            DrawingUtils.draw_text(screen, option, self.game.resources.fonts['medium'], color, Config.SCREEN_WIDTH // 2, y_start + i * 60)
        pygame.display.flip()

class GameOverState(GameState):
    def __init__(self, game):
        super().__init__(game)

    def enter_state(self):
        super().enter_state()
        self.background_frames = self.game.resources.load_animated_background('state_win', Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.animation_finished = False

        if len(self.game.winners) > 0 and 'fanfare' in self.game.resources.sounds and self.game.resources.sounds['fanfare'] and not pygame.mixer.get_busy():
            self.game.resources.sounds['fanfare'].play()
        elif len(self.game.winners) == 0 and 'game_over' in self.game.resources.sounds and self.game.resources.sounds['game_over'] and not pygame.mixer.get_busy():
            self.game.resources.sounds['game_over'].play()

    def handle_input(self, key_name):
        if key_name == "ENTER":
            pygame.mixer.stop()
            self.game.set_state(Config.STATE_MENU)
            self.game.reset_game_state_variables()
            print("Juego: Regresando al menú principal.")

    def update(self):
        super().update()

    def draw(self, screen):
        super().draw(screen)

        if len(self.game.winners) > 0:
            y_offset = Config.SCREEN_HEIGHT // 2 + 60
            DrawingUtils.draw_text(screen, "GANADORES ", self.game.resources.fonts['large'], Config.GREEN, Config.SCREEN_WIDTH // 2, y_offset)
            y_offset += 50

            if len(self.game.winners) > 0:
                DrawingUtils.draw_text(screen, f"1er Puesto: {self.game.winners[0]['name']}     {self.game.winners[0]['score']} puntos", self.game.resources.fonts['medium'], Config.YELLOW, Config.SCREEN_WIDTH // 2, y_offset)
                y_offset += 40

            if len(self.game.winners) > 1 and self.game.num_players_selected > 2:
                DrawingUtils.draw_text(screen, f"2do Puesto: {self.game.winners[1]['name']}     {self.game.winners[1]['score']} puntos", self.game.resources.fonts['medium'], Config.WHITE, Config.SCREEN_WIDTH // 2, y_offset)

            y_offset += 60
            DrawingUtils.draw_text(screen, "Presiona SELECT para Juego Nuevo", self.game.resources.fonts['small'], Config.YELLOW, Config.SCREEN_WIDTH // 2, y_offset)
        else:
            DrawingUtils.draw_text(screen, "JUEGO TERMINADO", self.game.resources.fonts['large'], Config.WHITE, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2)
            DrawingUtils.draw_text(screen, "Presiona SELECT para Nuevo Juego", self.game.resources.fonts['small'], Config.YELLOW, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT * 3 // 4)

        pygame.display.flip()

# --- Clase Principal del Juego ---
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.resources = ResourceManager()

        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption("Bolirrana")
        pygame.display.set_icon(self.resources.get_icon())
        
        self.clock = pygame.time.Clock()
        pygame.mouse.set_visible(False) # Oculta el cursor del ratón

        self.current_game_state = Config.STATE_MENU
        self.players = []
        self.current_player_index = 0
        self.game_target_score = Config.PUNTAJE_OBJETIVO_OPTIONS[0]
        self.num_players_selected = Config.NUM_JUGADORES_OPTIONS[0]
        self.winners = []
        self.s_key_pressed_time = 0

        # --- MODIFICACIÓN: Cargar la música de fondo UNA SOLA VEZ al inicio ---
        self.game_music_loaded = False
        background_music_path = self.resources.get_sound_path('background')
        if background_music_path:
            try:
                pygame.mixer.music.load(background_music_path)
                self.game_music_loaded = True
                print("Música de fondo cargada exitosamente.")
            except pygame.error as e:
                print(f"Error cargando música de fondo principal: {e}")
                self.game_music_loaded = False
        # -------------------------------------------------------------------

        self.states = {
            Config.STATE_MENU: MenuState(self),
            Config.STATE_SELECT_PLAYERS: SelectPlayersState(self),
            Config.STATE_SELECT_SCORE: SelectScoreState(self),
            Config.STATE_GAMEPLAY: GameplayState(self),
            Config.STATE_PAUSE: PauseState(self),
            Config.STATE_GAME_OVER: GameOverState(self),
        }
        self.current_state_handler = self.states[self.current_game_state]
        self.current_state_handler.enter_state()

    def set_state(self, new_state):
        # --- MODIFICACIÓN: Se elimina el stop() general aquí. ---
        # Ahora cada estado es responsable de controlar pygame.mixer.music
        # (play, pause, unpause, stop) según su lógica.
        self.current_game_state = new_state
        self.current_state_handler = self.states[new_state]
        self.current_state_handler.enter_state()
        print(f"Cambio de estado a: {new_state}")

    def reset_game_state_variables(self):
        self.players = []
        self.current_player_index = 0
        self.winners = []
        print("Variables de estado de la partida reiniciadas.")

    def reset_game(self):
        self.reset_game_state_variables()
        for i in range(self.num_players_selected):
            self.players.append({"name": f"Jugador {i+1}", "score": 0, "has_won": False})

        print(f"Juego reiniciado. {len(self.players)} jugadores. Objetivo: {self.game_target_score}")

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    key_name = None
                    if event.key in Config.KEY_MAPPING:
                        key_name = Config.KEY_MAPPING[event.key]

                    if event.key == pygame.K_s:
                        if self.s_key_pressed_time == 0:
                            self.s_key_pressed_time = pygame.time.get_ticks()
                    else:
                        self.s_key_pressed_time = 0

                    if key_name:
                        # Se asegura que el sonido de botón solo se reproduzca para los inputs de juego y navegación.
                        # No para las teclas 'S' o 'W' que tienen funciones especiales.
                        if self.resources.get_sound('button') and key_name not in ["S_KEY", "W_KEY"]:
                            self.resources.get_sound('button').play()
                        self.current_state_handler.handle_input(key_name)

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_s:
                        self.s_key_pressed_time = 0

            if self.s_key_pressed_time != 0 and pygame.time.get_ticks() - self.s_key_pressed_time > 3000:
                print("Tecla 's' mantenida por 3 segundos. Saliendo del programa.")
                running = False

            self.current_state_handler.update()
            self.current_state_handler.draw(self.screen)

            self.clock.tick(Config.FPS)

        print("Juego: Saliendo limpiamente...")
        pygame.quit()
        sys.exit()

# --- Punto de Entrada Principal ---
if __name__ == "__main__":
    DrawingUtils = DrawingUtils() # Asegúrate de que DrawingUtils esté definida o importada correctamente
    game = Game()
    game.run()