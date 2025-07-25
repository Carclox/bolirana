# gpio_keypad

Este proyecto implementa un módulo del kernel de Linux que actúa como controlador de teclado utilizando pines GPIO. Está diseñado para plataformas embebidas como Raspberry Pi, y permite detectar la pulsación de teclas conectadas físicamente mediante interrupciones y lógica de antirebote por software.

---

## Descripción general

El módulo permite mapear 13 pines GPIO a códigos de tecla definidos en el sistema (por ejemplo, `KEY_1`, `KEY_ENTER`, etc.). Al detectar un flanco de subida en alguno de estos pines, se genera un evento de entrada que puede ser interpretado por el sistema operativo como una pulsación real de teclado. Para evitar rebotes eléctricos (falsos positivos), el controlador incorpora un mecanismo de antirebote utilizando `jiffies`.

---

## Características principales

- Registro de 13 teclas diferentes mediante pines GPIO.
- Manejo de interrupciones (IRQ) con flanco de subida.
- Antirebote por software con retardo configurable (por defecto, 50 ms).
- Registro de un dispositivo de entrada en el subsistema `input` de Linux.
- Mensajes de depuración visibles mediante `dmesg`.

---

## Asignación de teclas (GPIO ↔ KEYCODE)

| GPIO | Código de tecla (`input.h`) | Nombre asignado |
|------|-----------------------------|------------------|
| 3    | `KEY_1`                     | "KEY_1"          |
| 4    | `KEY_2`                     | "KEY_2"          |
| 5    | `KEY_3`                     | "KEY_3"          |
| 6    | `KEY_4`                     | "KEY_4"          |
| 7    | `KEY_5`                     | "KEY_5"          |
| 8    | `KEY_6`                     | "KEY_6"          |
| 9    | `KEY_7`                     | "KEY_7"          |
| 10   | `KEY_8`                     | "KEY_8"          |
| 11   | `KEY_UP`                    | "KEY_UP"         |
| 12   | `KEY_DOWN`                  | "KEY_DOWN"       |
| 13   | `KEY_ENTER`                 | "KEY_ENTER"      |
| 14   | `KEY_TAB`                   | "KEY_TAB"        |
| 15   | `KEY_BACKSPACE`             | "KEY_S"          |

---

## Requisitos

- Sistema Linux con soporte para módulos del kernel.
- Acceso root para compilar e instalar el módulo.
- Herramientas de compilación (`make`, `gcc`, `linux-headers`).
- GPIOs accesibles (por ejemplo, en Raspberry Pi).

---

## Compilación

Para compilar el módulo, se debe contar con el siguiente archivo `Makefile`:

```makefile
obj-m := gpio_keypad.o
KDIR := /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
