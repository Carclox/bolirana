# Bolirrana Arcade

Simulador arcade de Bolirana implementado en Pygame, diseñado para replicar la experiencia del juego tradicional colombiano "rana" o "bolirana" a través de entradas de teclado estándar o personalizadas.

An arcade-style Bolirana (Frog Game) simulator implemented in Pygame, designed to replicate the traditional Colombian game experience via standard or custom keyboard inputs.

# :video_game: Demo
![Vista previa:](https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNjFmdWF5a3lpbGw5d3Qyanc0aTV3cTd1YzhndHFrZGd0MzNlcHRhcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/50pw4rhiug0Fm2y5DS/giphy.gif)




# :package:  Descripcion

Este proyecto es una simulación basada en Pygame de una Bolirrana (Juego de la Rana), un juego arcade en el que los jugadores intentan conseguir puntos lanzando una esfera metalica hacia los objetivos. El juego cuenta con un diseño modular, separando las preocupaciones en la configuración, gestión de recursos, utilidades de dibujo, y los distintos estados del juego. Incluye la selección del jugador, la personalización del objetivo de puntuación, la jugabilidad, la funcionalidad de pausa y una pantalla de finalización de la partida. También se ha implementado un «modo de reposo» para reducir el consumo de energía.


This project is a Pygame-based simulation of a Bolirrana (Frog Game), an arcade game where players aim to score points by hitting targets. The game features a modular design, separating concerns into configuration, resource management, drawing utilities, and distinct game states. It includes player selection, score target customization, gameplay, pause functionality, and a game over screen. A "sleep mode" is also implemented for low-power consumption.

# :star: Caracteristicas destacadas

* **Juego modular y extensible.** Arquitectura basada en maquina de estados (```menu```, ```gameplay```, ```pause```, ```gameover```, etc) para una gestion del juego clara y facil de mantener.
* **Gestion de entradas personalizadas.** Diseñado para integrarse con hardware arcade, simulado a través de mapeo de teclado configurable para flexibilidad en el desarrollo y pruebas.
* **Configuracion dinamica** Permite al usuario configurar el numero de jugadores y total de puntos objetivo, garantizando una experiencia mas personalizada.

* **Gestion de datos de juego.** Rastrea y gestiona puntajes para multiples jugadores, muestra en pantalla los puntajes actuales y nuevos de cada jugador.



# :joystick: Como jugar

### Control basico (Keyboard Simulation)

Juego diseñado para entradas GPIO, mapeadas a eventos de teclado estandar definidas de la siguiente manera:

* **UP Arrow**: Navegar hacia arriba por el menu.
* **DOWN Arrow**: Navegar hacia abajo en el menu.
* **ENTER (select)**: Seleccionar y confirmar opciones del menu.
* **TAB**: Durante el juego, cambiar al siguiente turno.
* **Number Keys (1-8)**: Durante el juego, mapear entradas de sensores a teclas numericas.
    * `1`: 500 puntos
    * `2`: 300 puntos
    * `3`: 200 puntos
    * `4`: 150 puntos
    * `5`: 100 puntos
    * `6`: 50 puntos
    * `7`: 30 puntos
    * `8`: 15 puntos


# :video_game: Flujo de juego

1.  **Menu principal:**
    * Use **UP/DOWN** Para navegar sobre las opciones: "Seleccionar jugadores", "Seleccionar puntaje", o "Jugar".
    * Presione **ENTER / select** para confirmar.
2.  **Seleccionar jugadores / Seleccionar puntaje:**
    * Use **UP/DOWN** Para navegar sobre las distintas opciones de los sub menus.
    * Presione **ENTER** para confirmar y regresar al menu principal.
3.  **Start (Jugar):**
    * El juego inicia con el numero de jugadores y puntos seleccionados.
    * En pantalla se muestra el jugador actual y el puntaje total.
    * Presione**TAB** para cambiar al siguiente jugador'.
    * presione las teclas numericas **1-8** para anotar puntos y añadirlos al jugador actual.
    * Presione **ENTER** para pausar el juego.
    *  **Menu de pausa:**
    * Use **UP/DOWN** para navegar y seleccionar las opciones "pausa" o "continuar".
    * Presione **ENTER** para confirmar. "Continuar" vuelve al juego, "salir" retorna al menu principal.
5.  **Juego terminado:**
    * Se muestra en pantalla 2 ganadores (primeros 2 en completar el objetivo).
    * Presione **ENTER** para regresar al menu principal.


## Instalacion

Para ejecutar este juego necsitas python 3 y la libreria pygame.

1.  **Clonar el repositorio (o descargar `game.exe`):**

    ```bash
    git clone https://github.com/Carclox/bolirana.git
    cd <directorio-del-repositorio>
    ```

2.  **Instalar pygame:**

    ```bash
    pip install pygame
    ```

3.  **Directorio raiz y estructura:**

    Verificar que le directorio del juego coincida con lo siguiente, y que existan los respectivos archivos.

    ```
    .
    ├── game.py
    └── assets/
        ├── fonts/
        │   ├── predataur.ttf
        │   └── electromagnetic.otf
        ├── sounds/
        │   ├── background.wav
        │   ├── points.wav
        │   ├── gameover.wav
        │   ├── button.wav
        │   ├── fanfare.mp3
        │   └── gameplay_music.wav
        ├── state_inicio/    # Images for MenuState background (e.g.,       frame001.png, ... frame060.png)
        ├── state_jugadores/ # Images for SelectPlayersState background
        ├── state_puntos/    # Images for SelectScoreState background
        ├── state_play/      # Images for GameplayState background
        ├── state_pause/     # Images for PauseState background (likely single image)
        ├── state_win/       # Images for GameOverState background
        └── state_sleep/     # Images for SleepState background (likely single image)
    ```



4.  **Run the game:**

    ```bash
    python game.py
    ```



# :space_invader: Mapeo de entradas:

`Config.KEY_MAPPING` es un diccionario que define las entradas de teclado estandar usadas para simular los eventos de entrada arcade, eventualmente se puede desarrollar una configuracion fisica arcade.

```python
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

```


# Mejoras futuras
**:memo: Inteligencia en turnos** optimizar el flujo de turnos durante el juego, para que salte automaticamente a los jugadores que no han completado el objetivo.

**:memo: Teclado virtual** Implementar interfaz de teclado virtual que permita personalizar nombres de jugadores y puntos objetivo dentro de un limite especifico, por ejemplo: (0-20000), dentro del menu principal.



# **:slot_machine: generar ejecutable:**
En caso de requerirlo, ejecute:
```bash
pyinstaller --onefile --windowed --icon=assets/images/icono.png --add-data "assets;assets" rana.py
```