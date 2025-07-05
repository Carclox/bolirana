import uinput
import time
import signal
import sys
from gpiozero import Button
from signal import pause

# Mapeo de pines a teclas
pin_key_map = {
    22: uinput.KEY_A,
    23: uinput.KEY_B,
    24: uinput.KEY_C,
    8:  uinput.KEY_D,
    7:  uinput.KEY_E,
    1:  uinput.KEY_F,
    12: uinput.KEY_G,
    16: uinput.KEY_H,
    20: uinput.KEY_I,
    21: uinput.KEY_J,
    26: uinput.KEY_K,
    19: uinput.KEY_L
}

# Crear el dispositivo uinput con todas las teclas
device = uinput.Device(list(pin_key_map.values()))

# Cierre limpio
def handle_exit(signum, frame):
    print("Liberando dispositivo uinput...")
    device.close()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Crear botones GPIO
for pin, key in pin_key_map.items():
    button = Button(pin, pull_up=False)
    button.when_pressed = lambda k=key: device.emit_click(k)

print("Monitoreando pines... (presiona Ctrl+C para salir)")
pause()
