/*
Dispositivo : Driver GPIO Teclado estandar
Autor :  Carlos Daniel Silva
Fecha :  2023-10-05
Descripcion :  Controlador para la lectura de un teclado utilizando GPIO (Polling)
*/

#include <linux/module.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/gpio.h>
#include <linux/gpio/consumer.h>
#include <linux/input.h>
#include <linux/jiffies.h>
#include <linux/delay.h>
#include <linux/timer.h> // Necesario para el temporizador del kernel

//=====================================================
// Definicion de tiempo de antirebote y polling
//=====================================================

#define DEBOUNCE_DELAY_JIFFIES msecs_to_jiffies(50) // 50 ms de antirebote
#define POLLING_INTERVAL_JIFFIES msecs_to_jiffies(10) // Frecuencia de polling: 10 ms
#define OFFSET 512

//=====================================================
// Estructura para almacenar la informacion de cada tecla
//=====================================================

struct gpio_button {
    int gpio;               // BCM gpio number
    unsigned int keycode;   // codigo evdev asociado al boton
    char name[32];          // nombre del boton
    unsigned long last_jiffies; // Para el control de antirebote (debounce)
    struct gpio_desc *desc; // Descriptor del GPIO para la API
    int last_value;         // Estado anterior del GPIO para detectar transiciones
};

//=====================================================
// Arreglo de las teclas
//=====================================================

static struct gpio_button gpio_buttons[] = {
    { .gpio = 22+OFFSET, .keycode = KEY_UP, .name = "UP"},
    { .gpio = 23+OFFSET, .keycode = KEY_DOWN, .name = "DOWN"},
    { .gpio = 24+OFFSET, .keycode = KEY_TAB, .name = "TAB"},
    { .gpio = 25+OFFSET, .keycode = KEY_ENTER, .name = "ENTER"},
    { .gpio = 8+OFFSET,  .keycode = KEY_S, .name = "S"},
    { .gpio = 7+OFFSET,  .keycode = KEY_1, .name = "NUM_1"},
    { .gpio = 1+OFFSET,  .keycode = KEY_2, .name = "NUM_2"},
    { .gpio = 12+OFFSET, .keycode = KEY_3, .name = "NUM_3"},
    { .gpio = 16+OFFSET, .keycode = KEY_4, .name = "NUM_4"},
    { .gpio = 20+OFFSET, .keycode = KEY_5, .name = "NUM_5"},
    { .gpio = 21+OFFSET, .keycode = KEY_6, .name = "NUM_6"},
    { .gpio = 26+OFFSET, .keycode = KEY_7, .name = "NUM_7"},
    { .gpio = 19+OFFSET, .keycode = KEY_8, .name = "NUM_8"},
};

#define NUM_BUTTONS ARRAY_SIZE(gpio_buttons)

//=====================================================
// Puntero global al dispositivo de entrada
//=====================================================

static struct input_dev *custom_input_dev;

//=====================================================
// Temporizador para el polling
//=====================================================
static struct timer_list button_poll_timer;

//=====================================================
// Función auxiliar para liberar los recursos de un solo botón
//=====================================================
static void gpio_free_button_desc(struct gpio_button *button) {
    if (button->desc && !IS_ERR(button->desc)) {
        gpiod_put(button->desc);
        button->desc = NULL; // Resetear para evitar liberaciones dobles
    }
}

//=====================================================
// Callback del temporizador para el polling
//=====================================================
static void button_poll_callback(struct timer_list *t) {
    int i;
    unsigned long current_jiffies = jiffies; // Capturar jiffies una vez para consistencia

    for (i = 0; i < NUM_BUTTONS; i++) {
        struct gpio_button *button = &gpio_buttons[i];
        int value;

        // Asegurarse de que el descriptor sea válido antes de intentar leer
        if (IS_ERR_OR_NULL(button->desc)) {
            pr_err("%s: Descriptor de GPIO inválido para %s\n", KBUILD_MODNAME, button->name);
            continue;
        }

        value = gpiod_get_value(button->desc);

        // Lógica de detección de flanco de subida (LOW a HIGH) y antirebote
        if (value == 1 && button->last_value == 0) { // Transición de LOW a HIGH (presionado)
            if (time_after(current_jiffies, button->last_jiffies + DEBOUNCE_DELAY_JIFFIES)) {
                input_report_key(custom_input_dev, button->keycode, 1); // Reportar presionado
                input_sync(custom_input_dev);
                pr_info("%s: Button %s (GPIO %d, keycode %d) PRESIONADO\n",
                    KBUILD_MODNAME, button->name, button->gpio, button->keycode);
                button->last_jiffies = current_jiffies; // Actualizar tiempo del último evento
            }
        } else if (value == 0 && button->last_value == 1) { // Transición de HIGH a LOW (soltado)
            // Reportar el evento de soltar la tecla
            input_report_key(custom_input_dev, button->keycode, 0); // Reportar soltado
            input_sync(custom_input_dev);
            pr_info("%s: Button %s (GPIO %d, keycode %d) SOLTADO\n",
                KBUILD_MODNAME, button->name, button->gpio, button->keycode);
            button->last_jiffies = current_jiffies; // Actualizar tiempo del último evento
        }
        button->last_value = value; // Actualizar el estado anterior
    }

    // Volver a encolar el temporizador para la próxima lectura
    mod_timer(&button_poll_timer, jiffies + POLLING_INTERVAL_JIFFIES);
}


//=====================================================
// Inicializacion y salida del modulo
//=====================================================

static int __init custom_gpio_driver_init(void){
    int ret;
    int i;

    pr_info("%s: Inicializando custom GPIO driver (Polling Mode)\n", KBUILD_MODMODNAME);

    custom_input_dev = input_allocate_device();
    if (!custom_input_dev){
        pr_err("%s: no se pudo asignar el dispositivo de entrada\n", KBUILD_MODNAME);
        return -ENOMEM;
    }

    custom_input_dev->name = "custom_gpio_keyboard";
    custom_input_dev->id.bustype = BUS_VIRTUAL;
    custom_input_dev->id.vendor = 0xAAAA;
    custom_input_dev->id.product = 0xBBBB;
    custom_input_dev->id.version = 0x0001;

    __set_bit(EV_KEY, custom_input_dev->evbit);

    for (i = 0; i < NUM_BUTTONS; i++){
        __set_bit(gpio_buttons[i].keycode, custom_input_dev->keybit);
        gpio_buttons[i].last_jiffies = 0; // Inicializar para antirebote
        gpio_buttons[i].last_value = -1; // Inicializar a un valor que no sea 0 ni 1
    }

    ret = input_register_device(custom_input_dev);
    if (ret){
        pr_err("%s: no se pudo registrar el dispositivo de entrada\n", KBUILD_MODNAME);
        input_free_device(custom_input_dev);
        return ret;
    }

    for (i = 0; i < NUM_BUTTONS; i++){
        // 1. Solicitar GPIO usando la nueva API gpio_consumer. Como entrada.
        gpio_buttons[i].desc = gpio_request_one(gpio_buttons[i].gpio, GPIOD_IN, gpio_buttons[i].name);
        if (IS_ERR(gpio_buttons[i].desc)) {
            ret = PTR_ERR(gpio_buttons[i].desc);
            pr_err("%s: no se pudo solicitar el GPIO %d (%s)\n", KBUILD_MODNAME, gpio_buttons[i].gpio, gpio_buttons[i].name);
            goto err_gpiod_request;
        }
        // Leer el valor inicial para evitar detección de flanco falso en el primer polling
        gpio_buttons[i].last_value = gpiod_get_value(gpio_buttons[i].desc);
    }

    // Inicializar y añadir el temporizador
    timer_setup(&button_poll_timer, button_poll_callback, 0);
    mod_timer(&button_poll_timer, jiffies + POLLING_INTERVAL_JIFFIES);

    pr_info("%s: Custom GPIO driver loaded successfully (Polling Mode)\n", KBUILD_MODNAME);
    return 0;

    // --- Manejo de Errores ---
    // 'i' contendrá el índice del botón que causó el error.

err_gpiod_request:
    // Bucle de limpieza para liberar recursos de los botones PREVIOS que se configuraron correctamente.
    for(i--; i >= 0; i--){
        gpio_free_button_desc(&gpio_buttons[i]);
    }
    input_unregister_device(custom_input_dev);
    input_free_device(custom_input_dev);
    return ret;
}

static void __exit custom_gpio_driver_exit(void){
    int i;
    pr_info("%s: Desactivando custom GPIO driver\n", KBUILD_MODNAME);

    // Detener el temporizador antes de liberar otros recursos
    del_timer_sync(&button_poll_timer);

    for (i = 0; i < NUM_BUTTONS; i++) {
        gpio_free_button_desc(&gpio_buttons[i]);
    }

    input_unregister_device(custom_input_dev);
    input_free_device(custom_input_dev);
    pr_info("%s: custom GPIO driver descargado correctamente\n", KBUILD_MODNAME);
}

//=====================================================
// macros para registrar inicializacion y salida del modulo
//=====================================================
module_init(custom_gpio_driver_init);
module_exit(custom_gpio_driver_exit);

//=====================================================
// Metadatos del modulo
//=====================================================
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Carlos Daniel Silva");
MODULE_DESCRIPTION("GPIO Keyboard Driver (Polling Mode)");
MODULE_ALIAS("platform:rpi-Keyboard-ctrl");
MODULE_VERSION("0.02"); // Versión actualizada para reflejar el cambio a polling//
// Created by el_carclox on 29/06/2025.
//
