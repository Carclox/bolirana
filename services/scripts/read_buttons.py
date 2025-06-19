import RPi.GPIO as GPIO
import uinput
import time
import threading
import subprocess
import os

#===============================================================
# configuracion de pines gpio y teclas virtuales
#===============================================================

BUTTONS_MAPPING ={
    18: uinput.KEY_UP,
    23: uinput.KEY_DOWN,
    24: uinput.KEY_TAB,
    25: uinput.KEY_ENTER,
    8:  uinput.KEY_S,
    7:  uinput.KEY_1,
    1:  uinput.KEY_2,
    12: uinput.KEY_3,
    16: uinput.KEY_4,
    20: uinput.KEY_5,
    21: uinput.KEY_6,
    26: uinput.KEY_7,
    19: uinput.KEY_8,
}

# Tiempo de debounce en segundos
DEBOUNCE_TIME = 0.050
#===============================================================
# variables globales para la logica de suspension y apagado
#===============================================================
s_key_press_time = 0
s_key_down_flag = False
running_script = True
suspend_proscess = None



all_keycodes = list(set(BUTTONS_MAPPING.values()))

try:
    virtual_keyboard = uinput.Device(all_keycodes, name = "RPi_GPIO_Virtual_keyboard")
    print("Teclado virtual creado exitosamente")
except Exception as e:
    print(f"ERROR: No se pudo crear el teclado virtual uinput: {e}")
    print("Asegúrate de que el módulo 'uinput' esté cargado: 'sudo modprobe uinput'")
    print("Asegúrate de que tu usuario esté en los grupos 'input' y 'uinput':")
    print("  sudo usermod -a -G input $(whoami)")
    print("  sudo usermod -a -G uinput $(whoami)")
    print("Y luego reinicia tu Raspberry Pi: 'sudo reboot'")
    exit(1)

#===============================================================
# funcion de manejo de GPIO (callback de interrupcion)
#===============================================================

#almacenar el ultimo tiempo de pulsacion para cada GPIO
last_gpio_press_time = {}

def gpio_callback(channel):
    global s_key_press_time, s_key_down, suspend_proscess

    keycode = BUTTONS_MAPPING.get(channel)

    if keycode is None:
        print(f"Advertencia: GPIO {channel} no mapeado a ninguna tecla")
        return
    # obtener el estado actual del pin, asumiendo pull down por hardware
    button_state = GPIO.input(channel)
    current_time = time.time()

    # control de antirebote
    if (channel in last_gpio_press_time and
        current_time - last_gpio_press_time[channel] < DEBOUNCE_TIME):
        return
    
    last_gpio_press_time[channel] = current_time #actualiza el tiempo de la ultima pulsacion

    # Logica de emision de teclas virtuales
    if button_state == GPIO.HIGH:
        if not s_key_down_flag:
            s_key_press_time = current_time
            s_key_down_flag = True
            print("tecla s presionada, monitoreando para suspension y apagado")
        elif suspend_proscess is not None:
            if suspend_proscess.poll() is not None:
                print("sistema reanudado por suspension de otra tecla")
                suspend_proscess = None
            else:
                print("proceso de suspension activo")
    else:
        virtual_keyboard.emit(keycode, 0) # 0 = KEY_UP

        # logica para la tecla s
        if keycode == uinput.KEY_S:
            if s_key_down_flag:
                duration = current_time - s_key_press_time
                if duration < 3:
                    print("pulsacion corta de tecla s, entrando en modo de bajo consumo")
                    try:
                        suspend_proscess = subprocess.Popen(['sudo','systemctl', 'suspend'])
                        if os.environ.get('DISPLAY'):
                            subprocess.Popen(['xset', 'dpms', 'force', 'off'])
                            subprocess.Popen(['xscreensaver-command', '-lock']) # si se usa screensaver
                    except Exception as e:
                        print("Error al intentar suspender el sistema")
            s_key_down_flag = False
            s_key_press_time = 0 # reinicia el temporizador

#==================================================================
# hilo de monitoreo de tecla s para pulsacion larga
#==================================================================

def monitor_s_key_poweroff():
    global s_key_press_time, s_key_down_flag, running_script

    while running_script:
        if s_key_down_flag and (time.time() - s_key_press_time >= 3):
            print("Apagando el sistema...")
            try:
                subprocess.Popen(['sudo','systemctl', 'poweroff'])
                running_script = False
            except Exception as e:
                print(f"error al intentar apagar el sistema: {e}")
            break #salir del hilo despues de iniciar el apgado
        time.sleep(0.1)

#==================================================================
# configuracion inicial de GPIO y bucle principal
#==================================================================

if __name__ == "main":
    GPIO.setmode(GPIO.BCM)
    print("configurando pines GPIO...")
    for gpio_pin in BUTTONS_MAPPING.keys():
        GPIO.setup(gpio_pin, GPIO.IN)

        GPIO.add_event_detect(gpio_pin, GPIO.BOTH, callback = gpio_callback, bouncetime=20)
    print("GPIOs configurados y escuchando pulsaciones")

    #iniciar hilo de monitoreo para apagado
    s_monitor_thread = threading.Thread(target = monitor_s_key_poweroff)
    s_monitor_thread.daemon = True
    s_monitor_thread.start

    try:
        #mantener ejecucion del script mientras running_script sea True
        while running_script:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDetectando ctrl + c Limpiando GPIOs y saliendo")
    finally:
        running_script = False
        s_monitor_thread.join(timeout = 1)
        GPIO.cleanup()
        print("proceso terminado")


"""
REQUERIMIENTOS
sudo apt install python3-rpi.gpio python3-uinput # 'git' ya lo tienes
sudo modprobe uinput
echo uinput | sudo tee -a /etc/modules # Para cargar uinput automáticamente en cada reinicio
sudo usermod -a -G input $(whoami) # Asegura permisos para tu usuario
sudo usermod -a -G uinput $(whoami) # Asegura permisos para tu usuario
sudo reboot # ¡MUY IMPORTANTE! Reinicia para que los cambios de grupo y el módulo uinput surtan efecto.


configuracion de sudoers para que no solicite contraseña de desde el script

sudo visudo
# añadir la siguiente linea al final del archivo
pi ALL=(ALL) NOPASSWD: /usr/bin/systemctl suspend, /usr/bin/systemctl poweroff


guardar y salir


 EJECUTAR EL SCRIPT
navegar al path donde este el script
 python read_buttons.py
 python3 readbuttons.py


"""