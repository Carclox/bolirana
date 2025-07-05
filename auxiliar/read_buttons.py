import RPi.GPIO as GPIO
import uinput
import time
import sys

# Mapeo de pines GPIO a códigos de tecla uinput
BUTTONS_MAPPING = {
    22: uinput.KEY_UP,
    23: uinput.KEY_DOWN,
    24: uinput.KEY_TAB,
    25: uinput.KEY_ENTER,
    7:  uinput.KEY_1,
    1:  uinput.KEY_2,
    12: uinput.KEY_3,
    16: uinput.KEY_4,
    20: uinput.KEY_5,
    21: uinput.KEY_6,
    26: uinput.KEY_7,
    19: uinput.KEY_8,
}

S_KEY_GPIO = 8  # GPIO para la tecla especial 'S' (y 'Q')
LONG_PRESS_TIME = 0.5  # Tiempo en segundos para considerar una pulsación larga

# Diccionario para almacenar el estado de los botones (tiempo de inicio de pulsación)
button_press_times = {}

# Definir los eventos de teclado que nuestro dispositivo virtual soportará
events = [
    uinput.KEY_UP,
    uinput.KEY_DOWN,
    uinput.KEY_TAB,
    uinput.KEY_ENTER,
    uinput.KEY_1,
    uinput.KEY_2,
    uinput.KEY_3,
    uinput.KEY_4,
    uinput.KEY_5,
    uinput.KEY_6,
    uinput.KEY_7,
    uinput.KEY_8,
    uinput.KEY_S,
    uinput.KEY_Q, # Añadir KEY_Q ya que también se generará
]

# Inicializar el dispositivo uinput como None
device = None

def setup_gpio():
    """Configura los pines GPIO."""
    GPIO.setmode(GPIO.BCM) # Usar la numeración de pines BCM
    for gpio_pin in BUTTONS_MAPPING.keys():
        GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(gpio_pin, GPIO.BOTH, callback=button_callback, bouncetime=50)
        print(f"GPIO {gpio_pin} configurado como entrada con pull-up.")

    # Configurar el GPIO para la tecla 'S'/'Q'
    GPIO.setup(S_KEY_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(S_KEY_GPIO, GPIO.BOTH, callback=s_key_callback, bouncetime=50)
    print(f"GPIO {S_KEY_GPIO} (S/Q) configurado como entrada con pull-up.")

def button_callback(channel):
    """Función de callback para los botones estándar."""
    global device
    if device is None:
        return # Si el dispositivo no está inicializado, no hacer nada

    if GPIO.input(channel) == GPIO.LOW:  # Botón presionado (pull-up, por lo tanto LOW)
        print(f"Botón en GPIO {channel} presionado.")
        device.emit(BUTTONS_MAPPING[channel], 1) # Evento de pulsación
    else:  # Botón liberado
        print(f"Botón en GPIO {channel} liberado.")
        device.emit(BUTTONS_MAPPING[channel], 0) # Evento de liberación

def s_key_callback(channel):
    """Función de callback para la tecla especial 'S'/'Q'."""
    global device
    if device is None:
        return # Si el dispositivo no está inicializado, no hacer nada

    if GPIO.input(channel) == GPIO.LOW:  # Botón presionado
        button_press_times[channel] = time.time() # Registrar el tiempo de inicio de la pulsación
        print(f"Tecla 'S'/'Q' en GPIO {channel} presionado.")
        # No emitimos el evento todavía, esperamos la liberación
    else:  # Botón liberado
        if channel in button_press_times:
            press_duration = time.time() - button_press_times[channel]
            print(f"Tecla 'S'/'Q' en GPIO {channel} liberado. Duración: {press_duration:.2f}s")
            if press_duration < LONG_PRESS_TIME:
                print("Pulsación corta: Emite KEY_S")
                device.emit(uinput.KEY_S, 1) # Pulsación
                device.emit(uinput.KEY_S, 0) # Liberación
            else:
                print("Pulsación larga: Emite KEY_Q")
                device.emit(uinput.KEY_Q, 1) # Pulsación
                device.emit(uinput.KEY_Q, 0) # Liberación
            del button_press_times[channel] # Limpiar el tiempo de inicio

def cleanup():
    """Limpia los recursos de GPIO y cierra el dispositivo uinput."""
    global device
    print("\nCerrando el script y limpiando recursos...")
    if device:
        device.close()
        print("Dispositivo uinput cerrado.")
    GPIO.cleanup() # Resetea la configuración de los pines GPIO
    print("Pines GPIO limpiados.")

if __name__ == "__main__":
    try:
        # 1. Crear el dispositivo virtual uinput
        # Es importante que el usuario que ejecuta el script tenga permisos para escribir en /dev/uinput.
        # Generalmente, esto se logra añadiendo el usuario al grupo 'input'.
        # sudo usermod -a -G input <your_username>
        # (y reiniciando la sesión)
        device = uinput.Device(events)
        print("Dispositivo uinput virtual creado exitosamente.")

        # 2. Configurar los pines GPIO
        setup_gpio()

        print("Script en ejecución. Presiona Ctrl+C para salir.")

        # Mantener el script en ejecución
        while True:
            time.sleep(1) # Pequeña pausa para no consumir CPU innecesariamente

    except uinput.UInputError as e:
        print(f"Error al inicializar uinput: {e}")
        print("Asegúrate de que el módulo uinput del kernel esté cargado (sudo modprobe uinput)")
        print("Y de que el usuario tenga permisos para escribir en /dev/uinput (sudo usermod -a -G input <tu_usuario> y reinicia la sesión).")
    except KeyboardInterrupt:
        pass # Captura Ctrl+C para una salida limpia
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    finally:
        cleanup() # Asegurarse de que la limpieza se ejecute siempre