import os
import time
from evdev import InputDevice, categorize, ecodes, KeyEvent

# =====================================================
# Configuración de las teclas
# Estas deben coincidir con las definidas en tu driver C
# =====================================================

# Mapeo de códigos de teclas de evdev a nombres legibles
# Se puede encontrar los códigos en linux/input-event-codes.h o en la documentación de evdev
KEY_MAP = {
    ecodes.KEY_UP: "UP",
    ecodes.KEY_DOWN: "DOWN",
    ecodes.KEY_TAB: "TAB",
    ecodes.KEY_ENTER: "ENTER",
    ecodes.KEY_S: "S",
    ecodes.KEY_1: "NUM_1",
    ecodes.KEY_2: "NUM_2",
    ecodes.KEY_3: "NUM_3",
    ecodes.KEY_4: "NUM_4",
    ecodes.KEY_5: "NUM_5",
    ecodes.KEY_6: "NUM_6",
    ecodes.KEY_7: "NUM_7",
    ecodes.KEY_8: "NUM_8",
}

# Lista de keycodes que el driver debería manejar
TEST_KEYCODES = [
    ecodes.KEY_UP,
    ecodes.KEY_DOWN,
    ecodes.KEY_TAB,
    ecodes.KEY_ENTER,
    ecodes.KEY_S,
    ecodes.KEY_1,
    ecodes.KEY_2,
    ecodes.KEY_3,
    ecodes.KEY_4,
    ecodes.KEY_5,
    ecodes.KEY_6,
    ecodes.KEY_7,
    ecodes.KEY_8,
]

# Nombre del dispositivo de entrada que el driver crea
DEVICE_NAME = "custom_gpio_keyboard"
EVENT_TIMEOUT = 5  # Tiempo en segundos para esperar cada evento de tecla

def find_input_device(name):
    """
    Busca el dispositivo de entrada por su nombre.
    """
    devices = [InputDevice(fn) for fn in os.listdir('/dev/input') if fn.startswith('event')]
    for dev in devices:
        try:
            dev.open()
            if dev.name == name:
                print(f"Dispositivo encontrado: {dev.path} ({dev.name})")
                return dev
            dev.close()
        except OSError as e:
            # Permiso denegado u otro error, simplemente ignorar
            print(f"Error: {e}")
            pass
    return None

def test_key_event(device, keycode):
    """
    Prueba un evento de tecla específico.
    """
    key_name = KEY_MAP.get(keycode, f"UNKNOWN_KEY_{keycode}")
    print(f"\n--- Probando tecla: {key_name} ---")
    print(f"Por favor, PRESIONA y SUELTA el botón físico conectado a {key_name} (GPIO asociado al keycode {keycode})...")

    pressed = False
    released = False
    start_time = time.time()

    while time.time() - start_time < EVENT_TIMEOUT and not (pressed and released):
        try:
            event = device.read_one()
            if event is None:
                continue

            if event.type == ecodes.EV_KEY and event.code == keycode:
                keyevent = categorize(event)
                if keyevent.keystate == KeyEvent.key_down:
                    print(f"  Evento 'Key Down' detectado para {key_name}.")
                    pressed = True
                elif keyevent.keystate == KeyEvent.key_up:
                    print(f"  Evento 'Key Up' detectado para {key_name}.")
                    released = True
            elif event.type == ecodes.EV_SYN and event.code == ecodes.SYN_REPORT:
                # Sincronización, ignorar
                pass
            # Otros eventos pueden ocurrir, se ignoran si no son EV_KEY del keycode esperado
        except BlockingIOError:
            # No hay eventos por ahora, esperar un poco
            time.sleep(0.01)
        except Exception as e:
            print(f"Error al leer evento: {e}")
            return False

    if pressed and released:
        print(f"  Prueba para {key_name} PASSED.")
        return True
    else:
        print(f"  Prueba para {key_name} FAILED: No se detectaron ambos eventos (down/up) a tiempo.")
        return False

def main():
    print("Iniciando pruebas unitarias para el driver GPIO de teclado.")

    dev = find_input_device(DEVICE_NAME)
    if not dev:
        print(f"Error: No se encontró el dispositivo de entrada '{DEVICE_NAME}'.")
        print("Asegúrate de que el driver del teclado esté cargado y el dispositivo esté disponible.")
        print("Intenta verificar con 'cat /proc/bus/input/devices' o 'ls /dev/input'.")
        return

    # Es importante abrir el dispositivo en modo no bloqueante para poder controlar el timeout
    dev.grab() # Esto "graba" el dispositivo, evitando que otros programas reciban los eventos. Útil para pruebas.
    dev.set_nonblocking(True)

    print(f"\nDispositivo '{dev.name}' abierto para pruebas.")
    print("Preparado para recibir eventos de teclas. Sigue las instrucciones para cada tecla.")

    all_tests_passed = True
    for keycode in TEST_KEYCODES:
        if not test_key_event(dev, keycode):
            all_tests_passed = False
        time.sleep(0.5) # Pequeña pausa entre pruebas

    dev.ungrab() # Libera el dispositivo
    dev.close()

    if all_tests_passed:
        print("\n¡Todas las pruebas PASSED con éxito!")
    else:
        print("\nAlgunas pruebas FAILED. Revisa los mensajes anteriores.")

if __name__ == "__main__":
    main()