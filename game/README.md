# Bolirrana Arcade Game

A simple arcade-style game developed with Pygame, designed to simulate a "Bolirrana" (Frog Game) experience with customizable player counts, score targets, and a state-based system for different game screens.

## Table of Contents

-   [Description](#description)
-   [Features](#features)
-   [How to Play](#how-to-play)
-   [Installation](#installation)
-   [Game States](#game-states)
-   [Input Mapping](#input-mapping)
-   [Project Structure](#project-structure)
-   [Acknowledgements](#acknowledgements)
-   [To-Do / Improvements](#to-do--improvements)

## Description

This project is a Pygame-based simulation of a Bolirrana (Frog Game), an arcade game where players aim to score points by hitting targets. The game features a modular design, separating concerns into configuration, resource management, drawing utilities, and distinct game states. It includes player selection, score target customization, gameplay, pause functionality, and a game over screen. A "sleep mode" is also implemented for low-power consumption.

## Features

* **Configurable Game Options:** Easily adjust screen dimensions, FPS, colors, target scores, and number of players.
* **Multiple Game States:**
    * **Menu:** Navigate between game setup options or start a new game.
    * **Select Players:** Choose the number of participants (2 to 6).
    * **Select Score:** Set the winning score target (1000 to 5000 points).
    * **Gameplay:** Active game session with score tracking and player turns.
    * **Pause:** Temporarily halt the game with options to continue or exit.
    * **Game Over:** Displays winners and final scores.
    * **Sleep Mode:** A low-power state with reduced visual activity.
* **Dynamic Player Management:** Supports multiple players with individual score tracking.
* **Animated Backgrounds:** Each game state can have a unique animated background for a richer visual experience.
* **Sound Effects and Music:** Includes sound effects for points, button presses, game over, and background music.
* **Arcade Input Simulation:** Designed to work with arcade-like inputs (UP, DOWN, ENTER, TAB, and score sensors 1-8), simulated via keyboard keys for local development.
* **System Power Control:** Toggle between active and low-power "sleep" modes.
* **Graceful Exit:** Long-press 'S' to exit the application.

## How to Play

### Basic Controls (Keyboard Simulation)

The game is designed for arcade inputs, but for local testing and development, the following keyboard keys are mapped:

* **UP Arrow**: Navigate up in menus.
* **DOWN Arrow**: Navigate down in menus.
* **ENTER (Return)**: Select an option in menus, confirm selections.
* **TAB**: In Gameplay, switch to the next player's turn.
* **Number Keys (1-8)**: In Gameplay, simulate score sensor inputs.
    * `1`: 500 points
    * `2`: 300 points
    * `3`: 200 points
    * `4`: 150 points
    * `5`: 100 points
    * `6`: 50 points
    * `7`: 30 points
    * `8`: 15 points
* **S Key**:
    * **Short Press (while awake)**: Enter Sleep Mode.
    * **Long Press (3 seconds)**: Exit the entire program.
* **W Key**: Wake up from Sleep Mode.

### Gameplay Flow

1.  **Main Menu:**
    * Use **UP/DOWN** to select "Seleccionar jugadores" (Select Players), "Seleccionar puntaje" (Select Score), or "Jugar" (Play).
    * Press **ENTER** to confirm your choice.
2.  **Select Players / Select Score:**
    * Use **UP/DOWN** to choose your desired number of players or target score.
    * Press **ENTER** to return to the Main Menu.
3.  **Start Game (Jugar):**
    * The game begins with the selected number of players and target score.
    * The current player's turn and score are displayed prominently.
    * Press **TAB** to switch to the next player'.
    * Press number keys **1-8** to add points to the current player's score.
    * Press **ENTER** to pause the game.
4.  **Pause Menu:**
    * Use **UP/DOWN** to select "Continuar" (Continue) or "Salir" (Exit).
    * Press **ENTER** to confirm. "Continue" resumes the game, "Exit" returns to the Main Menu.
5.  **Game Over:**
    * The screen displays the winners.
    * Press **ENTER** to return to the Main Menu.
6.  **Sleep Mode:**
    * Press **S** (short press) to enter sleep mode. The screen will go dark, showing "Modo de Bajo Consumo...".
    * Press **W** to wake up and return to the Main Menu.

## Installation

To run this game, you'll need Python 3 and Pygame.

1.  **Clone the repository (or download `game.py`):**

    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

2.  **Install Pygame:**

    ```bash
    pip install pygame
    ```

3.  **Create the `assets` directory and its subdirectories:**

    The game expects the following directory structure within your project folder:

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
        ├── state_inicio/    # Images for MenuState background (e.g., frame001.png, frame002.png)
        ├── state_jugadores/ # Images for SelectPlayersState background
        ├── state_puntos/    # Images for SelectScoreState background
        ├── state_play/      # Images for GameplayState background
        ├── state_pause/     # Images for PauseState background (likely single image)
        ├── state_win/       # Images for GameOverState background
        └── state_sleep/     # Images for SleepState background (likely single image)
    ```

    You will need to provide your own font, image, and sound files for the game to run with its intended visuals and audio. Placeholder files can be used for initial setup.

4.  **Run the game:**

    ```bash
    python game.py
    ```

## Game States

The game operates using a state machine pattern, with each state managing its own input, update logic, and drawing:

* `Config.STATE_MENU` (0): `MenuState` - Main menu.
* `Config.STATE_SELECT_PLAYERS` (1): `SelectPlayersState` - Player count selection.
* `Config.STATE_SELECT_SCORE` (2): `SelectScoreState` - Target score selection.
* `Config.STATE_GAMEPLAY` (3): `GameplayState` - The core game loop.
* `Config.STATE_PAUSE` (4): `PauseState` - Game paused menu.
* `Config.STATE_GAME_OVER` (5): `GameOverState` - End game screen showing winners.
* `Config.STATE_SLEEP` (6): `SleepState` - Low-power display mode.

## Input Mapping

The `Config.KEY_MAPPING` dictionary defines the standard keyboard keys used to simulate arcade inputs. This allows for easy testing and development without a physical arcade setup.

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
## Requerimientos


