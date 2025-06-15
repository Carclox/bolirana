import pygame
import sys
import os
import time

# --- Módulo de Constantes y Configuraciones ---
# Centralizamos las constantes para fácil acceso y modificación.
class Config:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60

    # Colores
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    GRAY = (150, 150, 150)

    # Opciones de juego
    PUNTAJE_OBJETIVO_OPTIONS = [1000, 2000, 3000, 4000, 5000]
    NUM_JUGADORES_OPTIONS = [2, 3, 4, 5, 6]

    # Mapeo de puntajes para los sensores 1-8
    SCORE_MAPPING = {
        "1": 500, "2": 300, "3": 200, "4": 150,
        "5": 100, "6": 50, "7": 30, "8": 15
    }

    # Estados del Juego (ahora como constantes dentro de la configuración)
    STATE_MENU = 0
    STATE_SELECT_PLAYERS = 1
    STATE_SELECT_SCORE = 2
    STATE_GAMEPLAY = 3
    STATE_PAUSE = 4
    STATE_GAME_OVER = 5
    STATE_SLEEP = 6 # Nuevo estado para el modo de bajo consumo

    # Mapeo de Teclas Estándar para simular inputs de Arcade
    KEY_MAPPING = {
        pygame.K_UP: "UP",
        pygame.K_DOWN: "DOWN",
        pygame.K_RETURN: "ENTER",
        pygame.K_TAB: "TAB",
        pygame.K_1: "1", pygame.K_2: "2", pygame.K_3: "3", pygame.K_4: "4",
        pygame.K_5: "5", pygame.K_6: "6", pygame.K_7: "7", pygame.K_8: "8",
        pygame.K_s: "SLEEP",
        pygame.K_w: "WAKEUP"
    }

    # Eventos Personalizados (ahora definidos directamente aquí)
    EVENT_ARCADE_INPUT = pygame.USEREVENT + 1
    EVENT_SCORE = pygame.USEREVENT + 2
    EVENT_SYSTEM_CONTROL = pygame.USEREVENT + 3


# --- Módulo de Recursos ---
class ResourceManager:
    def __init__(self):
        self.fonts = {}
        self.images = {}
        self.sounds = {}
        self.animated_backgrounds = {} 
        self._load_fonts()
        self._load_sounds()
   

    def _load_fonts(self):
        try:
            # Carga de las fuentes específicas desde la carpeta 'assets/fonts'
            self.fonts['large'] = pygame.font.Font(os.path.join('assets', 'fonts', 'predataur.ttf'), 74)
            self.fonts['medium'] = pygame.font.Font(os.path.join('assets', 'fonts', 'electromagnetic.otf'), 50)
            self.fonts['small'] = pygame.font.Font(os.path.join('assets', 'fonts', 'electromagnetic.otf'), 36) # arcade.ttf para texto pequeño
        except Exception as e:
            print(f"Error cargando fuentes: {e}")
            # Puedes considerar cargar una fuente por defecto si falla
            # self.fonts['large'] = pygame.font.Font(None, 74)

    def _load_sounds(self):
        try:

            self.sounds['points'] = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'points.wav'))
            self.sounds['game_over'] = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'gameover.wav'))
            self.sounds['button'] = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'button.wav'))
            self.sounds['fanfare'] = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'fanfare.mp3'))
        except pygame.error as e:
            print(f"Advertencia: No se pudieron cargar los sonidos. Asegúrate de que los archivos existan en 'assets/sounds/'. Error: {e}")
            # Si un sonido no se carga, se establece a None para evitar errores posteriores.
            # self.sounds['background'] = self.sounds['points'] = self.sounds['game_over'] = None # <--- Removido
            self.sounds['points'] = self.sounds['game_over'] = None
            self.sounds['button'] = self.sounds['fanfare'] = None

    def load_animated_background(self, state_name, screen_width, screen_height):
        """
        Carga una secuencia de imágenes para un fondo animado de un estado dado.
        state_name debe corresponder al nombre de la carpeta (ej. 'state_inicio', 'state_pause').
        """
        # Si ya se cargaron los frames para este estado, los devuelve directamente.
        if state_name in self.animated_backgrounds:
            return self.animated_backgrounds[state_name]

        path = os.path.join('assets', state_name)
        images_list = []
        try:
            # Lista todos los archivos en la carpeta del estado y los ordena
            # Esto es crucial para que la animación se vea en orden y para estados con una sola imagen.
            files = sorted([f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))])

            if not files:
                print(f"Advertencia: No se encontraron imágenes en la carpeta '{path}'. Asegúrate de que existan y sean PNG/JPG.")
                self.animated_backgrounds[state_name] = [] # Almacena una lista vacía para evitar reintentos.
                return []

            for filename in files:
                img_path = os.path.join(path, filename)
                image = pygame.image.load(img_path).convert_alpha()  
                # Escala la imagen al tamaño de la pantalla
                image = pygame.transform.scale(image, (screen_width, screen_height))
                images_list.append(image)

            # Almacena la lista de imágenes para no tener que cargarlas de nuevo
            self.animated_backgrounds[state_name] = images_list
            return images_list
        except pygame.error as e:
            print(f"Advertencia: No se pudieron cargar las imágenes para el estado '{state_name}'. Error: {e}")
            self.animated_backgrounds[state_name] = []
            return []
        except FileNotFoundError:
            print(f"Advertencia: La carpeta de estado '{path}' no fue encontrada. Error: {e}")
            self.animated_backgrounds[state_name] = []
            return []


    def get_font(self, font_size):
        """Devuelve una fuente por su clave (ej. 'large', 'medium', 'small')."""
        return self.fonts.get(font_size)

    def get_sound(self, sound_name):
        """Devuelve un objeto Sound por su clave (ej. 'background', 'button')."""
        return self.sounds.get(sound_name)


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


# --- Clase Dummy para ArcadeInputReader ---
class ArcadeInputReader:
    def __init__(self):
        print("ArcadeInputReader (Dummy): Inicializado para entorno local.")

    def start(self):
        print("ArcadeInputReader (Dummy): Método start llamado. No hay GPIO real.")
        pass

    def stop(self):
        print("ArcadeInputReader (Dummy): Método stop llamado. No hay GPIO real.")
        pass


# --- Clases de Pantalla/Estado del Juego ---
class GameState:
    def __init__(self, game):
        self.game = game
        self.background_frames = []
        self.current_frame_index = 0
        self.last_frame_time = 0
        self.animation_speed_ms = 33 # Aproximadamente 30 FPS para la animación
        self.animation_finished = False

    def enter_state(self):
        # Implementar en subclases si se necesita una acción al entrar al estado
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
                    self.animation_finished = True # La animación ha llegado al último frame

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
        # Iniciar la música de fondo del menú
        if os.path.exists(os.path.join('assets', 'sounds', 'background.wav')):
            pygame.mixer.music.load(os.path.join('assets', 'sounds', 'background.wav'))
            pygame.mixer.music.play(-1) # Reproducir en bucle


    def handle_input(self, key_name):
        if key_name == "UP":
            self.selection_index = (self.selection_index - 1 + len(self.options)) % len(self.options)
        elif key_name == "DOWN":
            self.selection_index = (self.selection_index + 1) % len(self.options)
        elif key_name == "ENTER":
            if self.selection_index == 0:
                self.game.set_state(Config.STATE_SELECT_PLAYERS)
            elif self.selection_index == 1:
                self.game.set_state(Config.STATE_SELECT_SCORE)
            elif self.selection_index == 2:
                self.game.reset_game()
                self.game.set_state(Config.STATE_GAMEPLAY)

    def draw(self, screen):
        super().draw(screen) # Dibuja el fondo animado o el último frame

        #DrawingUtils.draw_text(screen, "BOLIRRANA ARCADE", self.game.resources.fonts['large'], Config.YELLOW, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 4)

        y_start = Config.SCREEN_HEIGHT // 2 - 50
        for i, option in enumerate(self.options):
            color = Config.GREEN if self.selection_index == i else Config.WHITE
            DrawingUtils.draw_text(screen, option, self.game.resources.fonts['medium'], color, Config.SCREEN_WIDTH // 2, y_start + i * 60)

        #DrawingUtils.draw_text(screen, "UP/DOWN para navegar, ENTER para seleccionar", self.game.resources.fonts['small'], Config.GRAY, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT * 7 // 8)
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
        # Puedes decidir si quieres una música diferente o silencio en este estado
        # Por ahora, no se reproduce música aquí, se detendrá la música del menú.

    def handle_input(self, key_name):
        if key_name == "UP":
            self.current_idx = (self.current_idx - 1 + len(Config.NUM_JUGADORES_OPTIONS)) % len(Config.NUM_JUGADORES_OPTIONS)
            self.game.num_players_selected = Config.NUM_JUGADORES_OPTIONS[self.current_idx]
        elif key_name == "DOWN":
            self.current_idx = (self.current_idx + 1) % len(Config.NUM_JUGADORES_OPTIONS)
            self.game.num_players_selected = Config.NUM_JUGADORES_OPTIONS[self.current_idx]
        elif key_name == "ENTER":
            print(f"Config: {self.game.num_players_selected} jugadores seleccionados.")
            self.game.set_state(Config.STATE_MENU)

    def draw(self, screen):
        super().draw(screen) # Dibuja el fondo animado o el último frame

        #DrawingUtils.draw_text(screen, "SELECCIONAR JUGADORES", self.game.resources.fonts['large'], Config.YELLOW, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 6)

        y_start = Config.SCREEN_HEIGHT // 3
        for i, num_jug in enumerate(Config.NUM_JUGADORES_OPTIONS):
            color = Config.GREEN if num_jug == self.game.num_players_selected else Config.WHITE
            DrawingUtils.draw_text(screen, f"{num_jug} Jugadores", self.game.resources.fonts['medium'], color, Config.SCREEN_WIDTH // 2, y_start + i * 50)

        #DrawingUtils.draw_text(screen, "UP/DOWN: Seleccionar", self.game.resources.fonts['small'], Config.GRAY, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT * 7 // 8 - 30)
        #DrawingUtils.draw_text(screen, "ENTER: Confirmar", self.game.resources.fonts['small'], Config.YELLOW, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT * 7 // 8)
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
        # Puedes decidir si quieres una música diferente o silencio en este estado

    def handle_input(self, key_name):
        if key_name == "UP":
            self.current_idx = (self.current_idx - 1 + len(Config.PUNTAJE_OBJETIVO_OPTIONS)) % len(Config.PUNTAJE_OBJETIVO_OPTIONS)
            self.game.game_target_score = Config.PUNTAJE_OBJETIVO_OPTIONS[self.current_idx]
        elif key_name == "DOWN":
            self.current_idx = (self.current_idx + 1) % len(Config.PUNTAJE_OBJETIVO_OPTIONS)
            self.game.game_target_score = Config.PUNTAJE_OBJETIVO_OPTIONS[self.current_idx]
        elif key_name == "ENTER":
            print(f"Config: {self.game.game_target_score} puntos objetivo seleccionados.")
            self.game.set_state(Config.STATE_MENU)

    def draw(self, screen):
        super().draw(screen) # Dibuja el fondo animado o el último frame

        #DrawingUtils.draw_text(screen, "SELECCIONAR PUNTAJE", self.game.resources.fonts['large'], Config.YELLOW, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 6)

        y_start = Config.SCREEN_HEIGHT // 3
        for i, score_opt in enumerate(Config.PUNTAJE_OBJETIVO_OPTIONS):
            color = Config.GREEN if score_opt == self.game.game_target_score else Config.WHITE
            DrawingUtils.draw_text(screen, f"{score_opt} Puntos", self.game.resources.fonts['medium'], color, Config.SCREEN_WIDTH // 2, y_start + i * 50)

        #DrawingUtils.draw_text(screen, "UP/DOWN: Seleccionar", self.game.resources.fonts['small'], Config.GRAY, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT * 7 // 8 - 30)
        #DrawingUtils.draw_text(screen, "ENTER: Confirmar", self.game.resources.fonts['small'], Config.YELLOW, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT * 7 // 8)
        pygame.display.flip()


class GameplayState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.display_score_feedback = False
        self.score_feedback_value = 0
        self.score_feedback_start_time = 0
        self.score_feedback_duration_ms = 1000 # Duración de 1 segundo

    def enter_state(self):
        super().enter_state()
        self.background_frames = self.game.resources.load_animated_background('state_play', Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.animation_finished = False
        self.display_score_feedback = False # Reiniciar al entrar al estado
        # Iniciar la música de fondo del juego
        if os.path.exists(os.path.join('assets', 'sounds', 'gameplay_music.wav')): # Asumiendo un archivo de música para gameplay
            pygame.mixer.music.load(os.path.join('assets', 'sounds', 'gameplay_music.wav'))
            pygame.mixer.music.play(-1)
        elif os.path.exists(os.path.join('assets', 'sounds', 'background.wav')): # Fallback si no hay música específica de gameplay
            pygame.mixer.music.load(os.path.join('assets', 'sounds', 'background.wav'))
            pygame.mixer.music.play(-1)


    def handle_input(self, key_name):
        current_player = self.game.players[self.game.current_player_index]

        if key_name == "TAB":
            self._check_for_winner(current_player)
            if self.game.current_game_state == Config.STATE_GAMEPLAY:
                self.game.current_player_index = (self.game.current_player_index + 1) % len(self.game.players)
                print(f"Juego: Turno de: {self.game.players[self.game.current_player_index]['name']}")
            self.display_score_feedback = False # Ocultar feedback al cambiar de turno
        elif key_name == "ENTER":
            self.game.set_state(Config.STATE_PAUSE)
            self.game.pause_menu_selection_index = 0
            pygame.mixer.music.pause() # Pausar la música al entrar en pausa
            print("Juego: Pausado.")
            self.display_score_feedback = False # Ocultar feedback al pausar
        elif key_name in Config.SCORE_MAPPING:
            score_value = Config.SCORE_MAPPING[key_name]
            if not current_player['has_won']:
                current_player['score'] += score_value
                print(f"Juego: {current_player['name']} obtuvo {score_value} puntos. Total: {current_player['score']}")
                if self.game.resources.sounds['points']: self.game.resources.sounds['points'].play()

                # Activar feedback visual de puntuación
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
                pygame.mixer.music.stop() # Detener la música de fondo antes de ir a Game Over
                self.game.set_state(Config.STATE_GAME_OVER)
                if self.game.resources.sounds['fanfare']:
                    self.game.resources.sounds['fanfare'].play()
                print("Juego: Fin de partida alcanzado.")
            elif self.game.resources.sounds['game_over']:
                # Solo reproducir game_over si no se va a game_over state inmediatamente
                if not pygame.mixer.get_busy() or self.game.resources.sounds['game_over'].get_num_channels() == 0:
                    self.game.resources.sounds['game_over'].play()

    def update(self):
        super().update() # Llama al update de la clase base para la animación

        # Lógica para controlar la duración del feedback de puntuación
        if self.display_score_feedback:
            if pygame.time.get_ticks() - self.score_feedback_start_time > self.score_feedback_duration_ms:
                self.display_score_feedback = False # Desactivar feedback después de 1 segundo


    def draw(self, screen):
        super().draw(screen) # Dibuja el fondo animado o el último frame

        current_player = self.game.players[self.game.current_player_index]

        DrawingUtils.draw_text(screen, f"Turno del  {current_player['name']}", self.game.resources.fonts['medium'], Config.YELLOW, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 4)
        DrawingUtils.draw_text(screen, f"Puntaje  {current_player['score']}", self.game.resources.fonts['medium'], Config.WHITE, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 - 50)

        # Dibujar feedback de puntuación si está activo
        if self.display_score_feedback:
            # Puedes ajustar la posición y el color si lo deseas
            feedback_text = f"* {self.score_feedback_value} *"
            DrawingUtils.draw_text(screen, feedback_text, self.game.resources.fonts['large'], Config.GREEN, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 + 50)


        y_offset_start = Config.SCREEN_HEIGHT - 100
        total_width_for_players = Config.SCREEN_WIDTH - 200
        player_spacing = total_width_for_players // len(self.game.players) if len(self.game.players) > 0 else 0
        start_x = 100

        for i, player in enumerate(self.game.players):
            color = Config.YELLOW if i == self.game.current_player_index else Config.WHITE
            DrawingUtils.draw_text(screen, f"{player['name']}  {player['score']}", self.game.resources.fonts['small'], color, start_x + player_spacing * i, y_offset_start, center=False)

        #DrawingUtils.draw_text(screen, "TAB para cambiar de jugador / ENTER para Pausa", self.game.resources.fonts['small'], Config.GRAY, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT * 15 // 16)

        pygame.display.flip()

class PauseState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.selection_index = 0
        self.options = ["Continuar", "Salir"]

    def enter_state(self):
        super().enter_state()
        # Para el estado de pausa, solo hay una imagen, no una secuencia animada.
        # Por lo tanto, cargamos esa única imagen y la marcamos como animación terminada.
        self.background_frames = self.game.resources.load_animated_background('state_pause', Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.animation_finished = True # Siempre es true para una sola imagen

        # La música de fondo del juego debería estar pausada desde GameplayState.handle_input
        # if self.game.resources.sounds['background']: pygame.mixer.music.pause() # <--- Movido a GameplayState

    def handle_input(self, key_name):
        if key_name == "UP":
            self.selection_index = (self.selection_index - 1 + len(self.options)) % len(self.options)
        elif key_name == "DOWN":
            self.selection_index = (self.selection_index + 1) % len(self.options)
        elif key_name == "ENTER":
            if self.selection_index == 0:
                self.game.set_state(Config.STATE_GAMEPLAY)
                pygame.mixer.music.unpause() # Reanudar la música al continuar
                print("Juego: Reanudado.")
            elif self.selection_index == 1:
                self.game.set_state(Config.STATE_MENU)
                self.game.reset_game_state_variables()
                pygame.mixer.music.stop() # Detener la música al salir de la partida (el menú la iniciará de nuevo)
                print("Juego: Saliendo de la partida.")

    def draw(self, screen):
        super().draw(screen) # Dibuja el fondo (la única imagen de pausa)

        #DrawingUtils.draw_text(screen, "PAUSA", self.game.resources.fonts['large'], Config.YELLOW, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 4)

        y_start = Config.SCREEN_HEIGHT // 2 - 30
        for i, option in enumerate(self.options):
            color = Config.GREEN if self.selection_index == i else Config.WHITE
            DrawingUtils.draw_text(screen, option, self.game.resources.fonts['medium'], color, Config.SCREEN_WIDTH // 2, y_start + i * 60)

        #DrawingUtils.draw_text(screen, "UP/DOWN: Seleccionar, ENTER: Confirmar", self.game.resources.fonts['small'], Config.GRAY, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT * 3 // 4)
        pygame.display.flip()

class GameOverState(GameState):
    def __init__(self, game):
        super().__init__(game)
        # No se necesita last_game_over_time ya que no hay dependencia temporal para salir

    def enter_state(self):
        super().enter_state()
        self.background_frames = self.game.resources.load_animated_background('state_win', Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.animation_finished = False # Para la animación de la pantalla de victoria

        # La fanfarria se reproduce al final de GameplayState cuando se detectan 2 ganadores
        # Si se llega aquí y no se reprodujo, es un caso de todos ganando (menos de 2 jugadores) o error.
        # En el caso de que la fanfarria no se haya reproducido antes y haya al menos 2 ganadores
        # O si solo hay un ganador y es el único jugador (o solo hay un jugador)
        if len(self.game.winners) > 0 and 'fanfare' in self.game.resources.sounds and not pygame.mixer.get_busy():
            # Si no hay ningún sonido reproduciéndose, reproduce la fanfarria
            self.game.resources.sounds['fanfare'].play()
        elif len(self.game.winners) == 0 and 'game_over' in self.game.resources.sounds and not pygame.mixer.get_busy():
            # Esto podría ocurrir si el juego termina por alguna razón sin un ganador claro.
            self.game.resources.sounds['game_over'].play()


    def handle_input(self, key_name):
        if key_name == "ENTER":
            # Detener cualquier sonido que se esté reproduciendo (fanfarria o game_over)
            pygame.mixer.stop()
            self.game.set_state(Config.STATE_MENU)
            self.game.reset_game_state_variables()
            # La música de fondo del menú se iniciará en enter_state del MenuState
            print("Juego: Regresando al menú principal.")

    def update(self):
        super().update() # Llama al update de la clase base para la animación

    def draw(self, screen):
        super().draw(screen) # Dibuja el fondo animado o el último frame

        if len(self.game.winners) > 0:
            #DrawingUtils.draw_text(screen, "¡FIN DEL JUEGO!", self.game.resources.fonts['large'], Config.GREEN, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 4)

            y_offset = Config.SCREEN_HEIGHT // 2 - 80
            DrawingUtils.draw_text(screen, "GANADORES ", self.game.resources.fonts['large'], Config.GREEN, Config.SCREEN_WIDTH // 2, y_offset)
            y_offset += 50

            # Asegurarse de que winners[0] exista antes de intentar acceder
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

class SleepState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.long_press_start_time = 0 # Para detectar si la 's' se mantiene presionada

    def enter_state(self):
        # En el modo SLEEP, no se reproduce música de fondo del juego
        self.background_frames = self.game.resources.load_animated_background('state_sleep', Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.animation_finished = True # Probablemente solo una imagen de sleep
        self.long_press_start_time = 0 # Reiniciar al entrar al estado

    def handle_input(self, key_name):
        # En el modo SLEEP, solo la tecla WAKEUP debe ser procesada directamente por el bucle principal.
        # La 's' para salir o apagar se maneja en el bucle principal de Game.
        pass

    def draw(self, screen):
        super().draw(screen) # Dibuja el fondo de sleep (única imagen)
        DrawingUtils.draw_text(screen, "Modo de Bajo Consumo...", self.game.resources.fonts['medium'], Config.WHITE, Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2)
        pygame.display.flip()


# --- Clase Principal del Juego ---
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption("Bolirrana")
        self.clock = pygame.time.Clock()

        self.resources = ResourceManager()
        self.gpio_reader = ArcadeInputReader()

        self.current_game_state = Config.STATE_MENU
        self.players = []
        self.current_player_index = 0
        self.game_target_score = Config.PUNTAJE_OBJETIVO_OPTIONS[0]
        self.num_players_selected = Config.NUM_JUGADORES_OPTIONS[0]
        self.winners = []
        self.is_system_awake = True
        self.s_key_pressed_time = 0 # Para el monitoreo de la tecla 'S'

        self.states = {
            Config.STATE_MENU: MenuState(self),
            Config.STATE_SELECT_PLAYERS: SelectPlayersState(self),
            Config.STATE_SELECT_SCORE: SelectScoreState(self),
            Config.STATE_GAMEPLAY: GameplayState(self),
            Config.STATE_PAUSE: PauseState(self),
            Config.STATE_GAME_OVER: GameOverState(self),
            Config.STATE_SLEEP: SleepState(self)
        }
        self.current_state_handler = self.states[self.current_game_state]
        self.current_state_handler.enter_state() # Llama a enter_state del estado inicial

    def set_state(self, new_state):
        # Detener cualquier música que se esté reproduciendo antes de cambiar de estado
        pygame.mixer.music.stop()
        self.current_game_state = new_state
        self.current_state_handler = self.states[new_state]
        self.current_state_handler.enter_state() # Asegura que el nuevo estado se inicialice correctamente
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

        # La música de fondo se inicia en el enter_state de GameplayState
        print(f"Juego reiniciado. {len(self.players)} jugadores. Objetivo: {self.game_target_score}")

    def handle_system_power(self, key_name):
        if key_name == "SLEEP":
            if self.is_system_awake:
                print("Juego: Entrando en modo de bajo consumo.")
                self.is_system_awake = False
                self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pygame.NOFRAME)
                pygame.mouse.set_visible(False)
                pygame.mixer.music.stop() # Asegúrate de detener la música al entrar en suspensión
                self.set_state(Config.STATE_SLEEP)
        elif key_name == "WAKEUP":
            if not self.is_system_awake:
                print("Juego: Saliendo de modo de bajo consumo.")
                self.is_system_awake = True
                self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
                pygame.mouse.set_visible(False)
                self.set_state(Config.STATE_MENU) # Volver siempre al menú principal al despertar

    def run(self):
        self.gpio_reader.start()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key in Config.KEY_MAPPING:
                        key_name = Config.KEY_MAPPING[event.key]

                        # Lógica para el sonido de pulsación de tecla
                        # Se reproduce si el sistema está despierto y no es una tecla de control de sistema
                        # Y el sonido existe en los recursos.
                        if self.is_system_awake and key_name not in ["SLEEP", "WAKEUP"] and self.resources.get_sound('button'):
                            self.resources.get_sound('button').play()

                        # Manejo de la tecla 's' para suspensión y salida
                        if event.key == pygame.K_s:
                            if self.s_key_pressed_time == 0: # Si no estaba presionada, registrar el inicio
                                self.s_key_pressed_time = pygame.time.get_ticks()

                            # Si el sistema está despierto, intentar dormir; si está dormido, intentar despertar
                            if self.is_system_awake:
                                # Aquí ya se ha detectado el KEYDOWN de 's', así que la transición a SLEEP
                                # la gestiona handle_system_power.
                                # No es necesario llamar a handle_system_power("SLEEP") directamente aquí,
                                # ya que la lógica de la pulsación prolongada tiene prioridad.
                                pass # La acción de SLEEP ya se maneja al soltar la tecla o por pulsación prolongada
                            else: # Si no está despierto, se asume que 's' es para despertar
                                self.handle_system_power("WAKEUP")
                        # Para otras teclas, si el sistema está despierto, se delega al estado actual
                        elif self.is_system_awake:
                            self.current_state_handler.handle_input(key_name)

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_s:
                        # Si la tecla 's' se suelta y NO ha pasado el tiempo de long press (ya que si lo hizo, 'running' sería False)
                        # esto significa que fue una pulsación corta, y si estábamos despiertos, era para dormir.
                        if self.s_key_pressed_time != 0 and self.is_system_awake and (pygame.time.get_ticks() - self.s_key_pressed_time < 3000):
                            self.handle_system_power("SLEEP")
                        self.s_key_pressed_time = 0 # Siempre resetear el tiempo al soltar la tecla

            # Lógica para detectar pulsación prolongada de la tecla 's' (para salir del programa)
            if self.s_key_pressed_time != 0 and pygame.time.get_ticks() - self.s_key_pressed_time > 3000:
                print("Tecla 's' mantenida por 3 segundos. Saliendo del programa.")
                running = False # Esto enviará un QUIT implícito al salir del bucle

            # Lógica del juego y dibujo
            self.current_state_handler.update()
            self.current_state_handler.draw(self.screen)

            self.clock.tick(Config.FPS)

        print("Juego: Saliendo...")
        self.gpio_reader.stop()
        pygame.quit()
        sys.exit()

# --- Punto de Entrada Principal ---
if __name__ == "__main__":
    game = Game()
    game.run()




"""
Notas
arreglar bucle de tecla s una ves se entra al estado 6 no vuelve a salir a menos que se presione durante 3 segundos
arreglar el sonido de la tecla s
eliminar letras feas
cambiar tipografia
arreglar animacion estado 3 playing
"""