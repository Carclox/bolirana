Este código C implementa un módulo del kernel de Linux que actúa como controlador para un teclado matricial conectado mediante pines de Entrada/Salida de Propósito General (GPIO), el cual traduce las pulsaciones de las teclas físicas del teclado en eventos de entrada estándar que el kernel de Linux puede comprender, imitando así un teclado convencional.

## requerimientos
**Headers**
Es necesario tener instalados en la tarjeta los headers del nucleo para que la compilacion funcione.
```bash
sudo apt update
sudo apt install raspberrypi-kernel-headers
```
**Compilar el modulo**
Navega hasta el directorio raiz del driver, donde esta ubucado el archivo makefile y ejecuta:
```bash
make
```

utiliza: ```make all``` para compilar el driver, ```make clean``` para limpiar archivos de compilacion anteriores


**Cargar el modulo**
Una vez hayas generado el archivo ```gpio_teclado.ko``` ejecuta en bash desde la carpeta raiz del driver:
```bash
sudo insmod obj/gpio_keypad.ko
```
***Descargar el modulo***
Desde la carpeta raiz del driver ejecuta:
```bash
sudo rmmod gpio_keypad
```

***probar modulo***
```bash
sudo evtest
```
esto mostrara eventos de presion y liberacion de teclado estandar cuando presiones un  boton.

***Buscar el dispositivo***
```bash
cat /proc/bus/input/devices | grep -A5 "custom_gpio_keyboard"
```

# Descripcion del Modulo
- **gpio_button:** Esta estructura define las propiedades de cada botón individual del teclado.
- **gpio:** El número de pin GPIO de Broadcom (BCM) al que está conectado el botón.
- **irq:** El número de solicitud de interrupción (IRQ) asociado con el pin GPIO, utilizado para el manejo asincrónico de eventos.
- **keycode:** El código de tecla del subsistema de entrada de Linux (por ejemplo, KEY_UP, KEY_ENTER) que este botón informará cuando se presione.
- **name:** Un nombre descriptivo para el botón.
- **last_jiffies:** Se utiliza para eliminar rebotes , almacenando los jiffies del sistema (una medida de tiempo) cuando ocurrió el último evento de botón para evitar lecturas múltiples de una sola pulsación.
- **desc:** Un puntero a un gpio_descobjeto, que es parte de la API de consumidor GPIO moderna en el kernel de Linux para administrar GPIO.
**gpio_buttons:** Una matriz de gpio_buttonestructuras que define todos los botones del teclado personalizado y sus correspondientes pines GPIO y códigos de tecla. Esta matriz asigna GPIO específicos a funciones específicas del teclado.
**custom_input_dev:** Un puntero global a un struct input_dev, que representa el dispositivo de entrada (nuestro teclado personalizado) al subsistema de entrada de Linux.
**DEBOUNCE_DELAY_JIFFIES** Una macro que define un retardo de 50 milisegundos para la eliminación de rebotes . Esto es crucial para los botones físicos, ya que evita que se registren múltiples pulsaciones rápidas al presionar un botón una vez.