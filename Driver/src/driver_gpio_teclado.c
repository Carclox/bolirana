/*
Dispositivo : Driver GPIO Teclado estandar
Autor :  Carlos Daniel Silva
Fecha :  2023-10-05
Descripcion :  Controlador para la lectura de un teclado utilizando GPIO
*/

#include <linux/module.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/gpio.h>
#include <linux/gpio/consumer.h>
#include <linux/interrupt.h>
#include <linux/input.h>
#include <linux/jiffies.h>
#include <linux/delay.h>

//=====================================================
//Definicion de tiempo de antirebote
//=====================================================

#define DEBOUNCE_DELAY_JIFFIES msecs_to_jiffies(50) // 50 ms de antirebote

//=====================================================
// Estructura para almacenar la informacion de cada tecla
//=====================================================

struct gpio_button {
    int gpio;               // BCM gpio number
    int irq;                // interrupcion asociada al gpio
    unsigned int keycode;   // codigo evdev asociado al boton
    char name[32];          // nombre del boton
    unsigned long last_jiffies; // Para el control de antirebote (debounce)
    struct gpio_desc *desc; // Descriptor del GPIO para la API
};

// Declaración de prototipo para la función auxiliar de liberación de recursos
// Esto evita el error de declaración implícita y conflictos de tipo.
static void gpio_free_button_desc(struct gpio_button *button);


//=====================================================
// Arreglo de las teclas
//=====================================================

static struct gpio_button gpio_buttons[] = {
    { .gpio = 18, .keycode = KEY_UP, .name = "UP"},
    { .gpio = 23, .keycode = KEY_DOWN, .name = "DOWN"},
    { .gpio = 24, .keycode = KEY_TAB, .name = "TAB"},
    { .gpio = 25, .keycode = KEY_ENTER, .name = "ENTER"},
    { .gpio = 8,  .keycode = KEY_S, .name = "S"},
    { .gpio = 7,  .keycode = KEY_1, .name = "NUM_1"},
    { .gpio = 1,  .keycode = KEY_2, .name = "NUM_2"},
    { .gpio = 12, .keycode = KEY_3, .name = "NUM_3"},
    { .gpio = 16, .keycode = KEY_4, .name = "NUM_4"},
    { .gpio = 20, .keycode = KEY_5, .name = "NUM_5"},
    { .gpio = 21, .keycode = KEY_6, .name = "NUM_6"},
    { .gpio = 26, .keycode = KEY_7, .name = "NUM_7"},
    { .gpio = 19, .keycode = KEY_8, .name = "NUM_8"},
};


#define NUM_BUTTONS ARRAY_SIZE(gpio_buttons)
//=====================================================
// Puntero global al dispositivo de entrada
//=====================================================

static struct input_dev *custom_input_dev;
//=====================================================
// manejador de interrupciones ISR
//=====================================================
static irqreturn_t gpio_isr(int irq, void *data){
    struct gpio_button *button = (struct gpio_button *)data;
    int value;
    unsigned long flags;

    local_irq_save(flags);

    if (time_before(jiffies, button->last_jiffies + DEBOUNCE_DELAY_JIFFIES)) {
        local_irq_restore(flags);
        return IRQ_HANDLED;
    }

    value = gpiod_get_value(button->desc);

    button->last_jiffies = jiffies;

    // Con pull-down externo, un pulso LOW a HIGH significa 'presionado'.
    // Entonces, `value` será 1 (HIGH) cuando el botón esté presionado.
    input_report_key(custom_input_dev, button->keycode, value);
    input_sync(custom_input_dev);


    // pr_info es una funcion que ya tiene concatenado el nivel de registro KERN_INFO, por lo que funciona igual que printk()
    pr_info("%s: Button %s (GPIO %d, IRQ %d, keycode %d)\n",
        KBUILD_MODNAME, value ? "pressed" : "released", // Si `value` es 1 (HIGH), está presionado
        button->gpio, button->irq, button->keycode);

    local_irq_restore(flags);
    return IRQ_HANDLED;
}


//=====================================================
// Inicializacion y salida del modulo
//=====================================================

static int __init custom_gpio_driver_init(void){
    int ret;
    int i; // Declarar 'i' aquí para que su valor persista en el goto y el bucle de limpieza.

    pr_info("%s: Inicializando custom GPIO driver\n", KBUILD_MODNAME);

    custom_input_dev = input_allocate_device();
    if (!custom_input_dev){
        pr_err("%s: no se pudo asignar el dispositivo de entrada\n", KBUILD_MODNAME);
        return -ENOMEM;
    }

    // CUSTOM porque es personalizado
    custom_input_dev->name = "custom_gpio_keyboard";
    custom_input_dev->id.bustype = BUS_VIRTUAL;
    custom_input_dev->id.vendor = 0xAAAA;
    custom_input_dev->id.product = 0xBBBB;
    custom_input_dev->id.version = 0x0001;

    __set_bit(EV_KEY, custom_input_dev->evbit);

    for (i = 0; i < NUM_BUTTONS; i++){
        __set_bit(gpio_buttons[i].keycode, custom_input_dev->keybit);
        gpio_buttons[i].last_jiffies = 0;
    }
    ret = input_register_device(custom_input_dev);
    if (ret){
        pr_err("%s: no se pudo registrar el dispositivo de entrada\n", KBUILD_MODNAME);
        input_free_device(custom_input_dev);
        return ret;
    }

    for (i = 0; i < NUM_BUTTONS; i++){
        // No declarar 'button' aquí de nuevo si se usa en los gotos fuera del ámbito del bucle.
        // En su lugar, usamos &gpio_buttons[i] directamente.
        // Pero si prefieres usar 'button' para mayor legibilidad dentro del bucle,
        // asegúrate de que el 'goto' salte a un punto donde 'i' sea válido para liberar.
        // La mejor práctica es que el goto se encargue de la limpieza de lo que *ya* se asignó.

        // 1. Solicitar GPIO usando la nueva API gpio_consumer. Sin pull-up/down interno.
        gpio_buttons[i].desc = gpio_request_one(gpio_buttons[i].gpio, GPIOD_IN, gpio_buttons[i].name);
        if (IS_ERR(gpio_buttons[i].desc)) {
            ret = PTR_ERR(gpio_buttons[i].desc);
            pr_err("%s: no se pudo solicitar el GPIO %d (%s)\n", KBUILD_MODNAME, gpio_buttons[i].gpio, gpio_buttons[i].name);
            goto err_gpiod_request;
        }

        // 2. Obtener el numero irq asociado al GPIO
        gpio_buttons[i].irq = gpiod_to_irq(gpio_buttons[i].desc);
        if (gpio_buttons[i].irq < 0) {
            pr_err("%s: no se pudo obtener el IRQ para GPIO %d (%s)\n", KBUILD_MODNAME, gpio_buttons[i].gpio, gpio_buttons[i].name);
            ret = gpio_buttons[i].irq;
            goto err_gpio_to_irq;
        }

        // 3. Solicitar interrupcion en modo ascendente y descendente
        ret = request_irq(gpio_buttons[i].irq, gpio_isr,
            IRQF_TRIGGER_RISING | IRQF_TRIGGER_FALLING | IRQF_SHARED,
            gpio_buttons[i].name, &gpio_buttons[i]); // Pasa la dirección del elemento actual
        if (ret) {
            pr_err("%s: no se pudo solicitar el IRQ %d para %s\n", KBUILD_MODNAME, gpio_buttons[i].irq, gpio_buttons[i].name);
            goto err_request_irq;
        }
    }
    pr_info("%s: Custom GPIO driver loaded successfully\n", KBUILD_MODNAME);
    return 0;

    // --- Manejo de Errores ---
    // 'i' contendrá el índice del botón que causó el error.

err_request_irq:
    // Falló request_irq para gpio_buttons[i]. Liberar recursos de gpio_buttons[i].
    gpio_free_button_desc(&gpio_buttons[i]);

err_gpio_to_irq:
    // Falló gpiod_to_irq para gpio_buttons[i]. Solo liberar el descriptor del GPIO.
    // gpio_free_button_desc ya es robusta, pero gpiod_put(desc) es más directo si sabemos que solo eso existe.
    if (gpio_buttons[i].desc) {
        gpiod_put(gpio_buttons[i].desc);
        gpio_buttons[i].desc = NULL; // Evitar doble liberación
    }

err_gpiod_request:
    // Falló gpio_request_one para gpio_buttons[i]. No hay nada que liberar para este botón.

    // Bucle de limpieza para liberar recursos de los botones PREVIOS que se configuraron correctamente.
    for(i--; i >= 0; i--){ // Decrementar 'i' para empezar desde el último botón exitoso
        gpio_free_button_desc(&gpio_buttons[i]);
    }
    input_unregister_device(custom_input_dev);
    input_free_device(custom_input_dev);
    return ret;
}

// Función auxiliar para liberar los recursos de un solo botón
static void gpio_free_button_desc(struct gpio_button *button) {
    if (button->irq > 0) {
        free_irq(button->irq, button);
        button->irq = 0; // Resetear para evitar liberaciones dobles
    }
    if (button->desc) {
        gpiod_put(button->desc);
        button->desc = NULL; // Resetear para evitar liberaciones dobles
    }
}


static void __exit custom_gpio_driver_exit(void){
    int i;
    pr_info("%s: Desactivando custom GPIO driver\n", KBUILD_MODNAME);
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
MODULE_DESCRIPTION("GPIO  Keyboard Driver");
MODULE_ALIAS("platform:rpi-Keyboard-ctrl");
MODULE_VERSION("0.01");