import RPi.GPIO as GPIO
import uinput
import time
import threading
import subprocess
import os

# ===============================================================
# Configuración global
# ===============================================================

# Tiempo de debounce en segundos
DEBOUNCE_TIME = 0.050

# Variables globales para la lógica de suspensión y apagado (se podrían encapsular mejor, pero por simplicidad inicial)
s_key_press_time = 0
s_key_down_flag = False
running_script = True # Controla el bucle principal del script
suspend_process = None # Renombrado para evitar conflicto con la función 'suspend_proscess' en el código original

# ===============================================================
# Clases para el manejo de botones
# ===============================================================

class GpioButton:
    """
    Clase base para representar un botón GPIO y manejar su estado.
    """
    def __init__(self, gpio_pin):
        self.gpio_pin = gpio_pin
        self.last_press_time = 0
        GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_OFF) # Asumiendo pull-down por hardware
        GPIO.add_event_detect(self.gpio_pin, GPIO.BOTH, callback=self._gpio_callback, bouncetime=20) # bouncetime inicial, el debounce principal es por tiempo

    def _gpio_callback(self, channel):
        """
        Callback interno para la detección de eventos GPIO.
        Gestiona el antirrebote y llama al método abstracto 'on_button_event'.
        """
        current_time = time.time()
        if (current_time - self.last_press_time) < DEBOUNCE_TIME:
            return

        self.last_press_time = current_time
        button_state = GPIO.input(channel)
        self.on_button_event(button_state, current_time)

    def on_button_event(self, state, current_time):
        """
        Método abstracto que debe ser implementado por las subclases.
        Será llamado cuando se detecte un evento de botón (después del debounce).
        'state' es GPIO.HIGH o GPIO.LOW.
        """
        raise NotImplementedError("Las subclases deben implementar 'on_button_event'")

class VirtualKeyButton(GpioButton):
    """
    Clase para un botón GPIO que emula una tecla virtual.
    """
    def __init__(self, gpio_pin, keycode, virtual_keyboard_device):
        super().__init__(gpio_pin)
        self.keycode = keycode
        self.device = virtual_keyboard_device
        self.is_pressed = False # Para rastrear el estado actual de la tecla virtual

    def on_button_event(self, state, current_time):
        if state == GPIO.HIGH and not self.is_pressed:
            # Botón presionado
            self.device.emit(self.keycode, 1) # 1 = KEY_DOWN
            self.is_pressed = True
            # print(f"DEBUG: GPIO {self.gpio_pin} (Key: {self.keycode}) - PRESSED")
        elif state == GPIO.LOW and self.is_pressed:
            # Botón liberado
            self.device.emit(self.keycode, 0) # 0 = KEY_UP
            self.is_pressed = False
            # print(f"DEBUG: GPIO {self.gpio_pin} (Key: {self.keycode}) - RELEASED")

class SKeyPowerButton(GpioButton):
    """
    Clase para la tecla 'S' con lógica de suspensión y apagado.
    """
    def __init__(self, gpio_pin):
        super().__init__(gpio_pin)
        global s_key_press_time, s_key_down_flag, suspend_process # Acceso a globales para mantener la compatibilidad con la lógica original
        self.keycode = uinput.KEY_S # Aseguramos que esta clase maneja KEY_S

    def on_button_event(self, state, current_time):
        global s_key_press_time, s_key_down_flag, suspend_process

        if state == GPIO.HIGH: # Botón S presionado
            if not s_key_down_flag:
                s_key_press_time = current_time
                s_key_down_flag = True
                print("Tecla S presionada, monitoreando para suspensión y apagado")
            elif suspend_process is not None:
                if suspend_process.poll() is not None:
                    print("Sistema reanudado por suspensión de otra tecla")
                    suspend_process = None
                else:
                    print("Proceso de suspensión activo")
            # Adicionalmente, emitir KEY_DOWN para la tecla S virtual
            virtual_keyboard.emit(self.keycode, 1)
            self.is_pressed = True
        else: # Botón S liberado
            virtual_keyboard.emit(self.keycode, 0) # Emitir KEY_UP para la tecla S
            self.is_pressed = False

            if s_key_down_flag:
                duration = current_time - s_key_press_time
                if duration < 3:
                    print("Pulsación corta de tecla S, intentando suspender el sistema")
                    try:
                        suspend_process = subprocess.Popen(['sudo','systemctl', 'suspend'])
                        if os.environ.get('DISPLAY'):
                            subprocess.Popen(['xset', 'dpms', 'force', 'off'])
                            # subprocess.Popen(['xscreensaver-command', '-lock']) # Si se usa screensaver
                    except Exception as e:
                        print(f"Error al intentar suspender el sistema: {e}")
            s_key_down_flag = False
            s_key_press_time = 0 # Reinicia el temporizador


# ===============================================================
# Configuración de pines GPIO y teclas virtuales
# ===============================================================

BUTTONS_MAPPING = {
    18: uinput.KEY_UP,
    23: uinput.KEY_DOWN,
    24: uinput.KEY_TAB,
    25: uinput.KEY_ENTER,
    # 8:  uinput.KEY_S, # La tecla S se manejará por una clase especial
    7:  uinput.KEY_1,
    1:  uinput.KEY_2,
    12: uinput.KEY_3,
    16: uinput.KEY_4,
    20: uinput.KEY_5,
    21: uinput.KEY_6,
    26: uinput.KEY_7,
    19: uinput.KEY_8,
}

S_KEY_GPIO = 8 # GPIO para la tecla especial 'S'

# ===============================================================
# Inicialización del teclado virtual
# ===============================================================

# Recopilar todos los keycodes necesarios, incluyendo KEY_S
all_keycodes = list(set(BUTTONS_MAPPING.values()))
if uinput.KEY_S not in all_keycodes:
    all_keycodes.append(uinput.KEY_S)

try:
    virtual_keyboard = uinput.Device(all_keycodes, name="RPi_GPIO_Virtual_Keyboard")
    print("Teclado virtual creado exitosamente")
except Exception as e:
    print(f"ERROR: No se pudo crear el teclado virtual uinput: {e}")
    print("Asegúrate de que el módulo 'uinput' esté cargado: 'sudo modprobe uinput'")
    print("Asegúrate de que tu usuario esté en los grupos 'input' y 'uinput':")
    print("  sudo usermod -a -G input $(whoami)")
    print("  sudo usermod -a -G uinput $(whoami)")
    print("Y luego reinicia tu Raspberry Pi: 'sudo reboot'")
    exit(1)

# ==================================================================
# Hilo de monitoreo de tecla S para pulsación larga (apagado)
# ==================================================================

def monitor_s_key_poweroff():
    global s_key_press_time, s_key_down_flag, running_script

    while running_script:
        if s_key_down_flag and (time.time() - s_key_press_time >= 3):
            print("Apagando el sistema...")
            try:
                subprocess.Popen(['sudo','systemctl', 'poweroff'])
                running_script = False # Salir del bucle principal
            except Exception as e:
                print(f"Error al intentar apagar el sistema: {e}")
            break # Salir del hilo después de iniciar el apagado
        time.sleep(0.1)

# ==================================================================
# Configuración inicial de GPIO y bucle principal
# ==================================================================

if __name__ == "__main__": # Corregido de "main" a "__main__"
    GPIO.setmode(GPIO.BCM)
    print("Configurando pines GPIO...")

    buttons = []
    # Crear objetos para botones de teclado virtual
    for gpio_pin, keycode in BUTTONS_MAPPING.items():
        buttons.append(VirtualKeyButton(gpio_pin, keycode, virtual_keyboard))

    # Crear objeto para la tecla S especial
    buttons.append(SKeyPowerButton(S_KEY_GPIO))

    print("GPIOs configurados y escuchando pulsaciones")

    # Iniciar hilo de monitoreo para apagado
    s_monitor_thread = threading.Thread(target=monitor_s_key_poweroff)
    s_monitor_thread.daemon = True # Permite que el programa principal termine incluso si este hilo sigue corriendo
    s_monitor_thread.start()

    try:
        # Mantener ejecución del script mientras running_script sea True
        while running_script:
            time.sleep(1) # Pequeña espera para no consumir CPU innecesariamente
    except KeyboardInterrupt:
        print("\nDetectando Ctrl+C. Limpiando GPIOs y saliendo.")
    finally:
        running_script = False # Indicar a los hilos que terminen
        s_monitor_thread.join(timeout=1) # Esperar a que el hilo de monitoreo termine
        GPIO.cleanup()
        print("Proceso terminado.")
