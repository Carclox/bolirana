Esta carpeta contiene una aplicación de juego arcade implementada en Python utilizando la biblioteca `pygame`, así como un script para generar un gráfico de llamadas del flujo de ejecución mediante `pycallgraph`.

---

## 📁 Archivos principales

### `game.py`

Este archivo contiene la implementación del juego "Bolirrana", un juego tipo arcade que simula una interfaz de múltiples jugadores, utilizando sensores (o teclas mapeadas) para sumar puntajes.

### `callgraph.py`

Este script ejecuta el archivo `game.py` y genera un gráfico de llamadas (`game_call_graph.png`) utilizando la biblioteca `pycallgraph`. El resultado es una visualización de las funciones invocadas durante la ejecución del juego.

---

## 🎮 Descripción del juego

El juego permite configurar el número de jugadores, el puntaje objetivo, y visualizar animaciones de fondo. Los eventos del juego se basan en entradas simuladas por teclado, mapeadas como si fueran pulsadores físicos conectados a una Raspberry Pi.

### Características

- Animaciones de fondo por estado del juego.
- Soporte de 2 a 6 jugadores.
- Sonido, música y efectos incluidos.
- Control por teclado (simulación de sensores arcade).
- Estados del juego: Menú principal, selección de jugadores, selección de puntaje, juego, pausa y fin del juego.

---

## 🎮 Controles

El juego utiliza las siguientes teclas del teclado como entradas arcade:

| Tecla           | Acción              |
|-----------------|---------------------|
| Flecha ↑        | Mover hacia arriba  |
| Flecha ↓        | Mover hacia abajo   |
| Enter           | Confirmar / Pausar  |
| Tab             | Siguiente jugador   |
| 1–8             | Disparar sensor / sumar puntaje |
| S               | Salida forzada tras 3 segundos |

---

## 🖼️ Recursos

El juego hace uso de recursos gráficos y de sonido ubicados en la carpeta `assets/`:

- `assets/images`: íconos e imágenes.
- `assets/fonts`: fuentes personalizadas.
- `assets/sounds`: efectos de sonido y música de fondo.
- `assets/state_*`: imágenes animadas de fondo por estado.

---

## 🧱 Estructura del proyecto

```plaintext
.
├── game.py              # Código principal del juego
├── callgraph.py         # Script para generar gráfico de llamadas
├── game_call_graph.png  # Salida del gráfico generado (creado al ejecutar callgraph.py)
└── assets/              # Recursos gráficos, fuentes y sonidos
