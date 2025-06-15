/*
Dispositivo : Driver GPIO Teclado estandar
Autor :  Carlos Daniel Silva
Fecha :  2023-10-05
Descripcion :  Controlador para la lectura de un teclado matricial utilizando GPIO
*/

#include <linux/module.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/gpio.h>
#include <linux/interrupt.h>
#include <linux/input.h>
#include <linux/jiffies.h>
#include <linux/delay.h>






//=====================================================
//Definicion de tiempo de antirebote
//=====================================================

#define DEBOUNCE_DELAY_US 50000 // 50 ms en microsegundos

//=====================================================
// Estructura para almacenar la informacion de cada tecla
//=====================================================

struct gpio_button {
    int gpio; //BCM gpio number
    int irq; //interrupcion asociada al gpio
    unsigned int keycode; //codigo evdev asociado al boton
    char name[32]; // nombre del boton
};

//=====================================================
// Arreglo de las teclas
//=====================================================

static struct gpio_button gpio_buttons[] ={
    { .gpio = 18, .keycode = KEY_UP, .name = "UP"},
    { .gpio = 23, .keycode = KEY_DOWN, .name = "DOWN"},
    { .gpio = 24, .keycode = KEY_TAB, .name = "TAB"},
    { .gpio = 25, .keycode = KEY_ENTER, .name = "ENTER"},
    { .gpio = 8, .keycode = KEY_S, .name = "S"},
    { .gpio = 7, .keycode = KEY_1, .name = "NUM_1"},
    { .gpio = 1. .keycode = KEY_2, .name = "NUM_2"},
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
    /*
     * Manejo de la interrupcion
     */
    struct gpio_button *button = (struct gpio_button *)data;
    int value; // estado actual del pin GPIO
    value = gpio_get_value(button->gpio); // leer el estado del GPIO
    // enviar evento de tecla al sistma de entrada
    // value sera 1 si se presiona (gpio HIGH) y 0 si se libera (gpio LOW)
    input_report_key(custom_input_dev, button->keycode, value);
    input_sync(custom_input_dev); // sincroniza el evento
    pr_info("%s: Button %s %s (GPIO %d, IRQ %d, keycode %d)\n",
        KBUILD_MODNAME, button->name ? "pressed" : "released",
        button->gpio, button->irq, button->keycode);

    return IRQ_HANDLED; // indica que la interrupcion fue manejada
}


//=====================================================
// Inicializacion y salida del modulo
//=====================================================

static int __init custom_gpio_driver_init(void){
    int ret;
    int i;

    pr_info("%s: Inicializando custom GPIO driver\n", KBUILD_MODNAME);

    // crear el dispositivo de entrada
    custom_input_dev = input_allocate_device();
    if (!custom_input_dev){
        pr_err("%s: no se pudo asignar el dispositivo de entrada\n");
        return -ENOMEM;
    }
    custom_input_dev->name = "custom_gpio_keyboard";
    custom_input_dev->id.bustype = BUS_VIRTUAL;
    custom_input_dev->id.vendor = 0xAAAA;
    custom_input_dev->id.product = 0xBBBB;
    custom_input_dev->id.version = 0x0001;

    //indicar que el dispositivo soporta eventos de teclas
    __set_bit(EV_KEY, custom_input_dev->evbit);

    //indicar los keycodes que soporta
    for (i=0;i < NUM_BUTTONS; i++){
        __set_bit(gpio_buttons[i].keycode, custom_input_dev->keybit);
    }
    ret = input_register_device(custom_input_dev);
    if (ret){
        pr_err("%s: no se pudo registrar el dispositivo de entrada\n", KBUILD_MODNAME);
        input_free_device(custom_input_dev);
        return ret;
    }

    // configurar los GPIOs y las interrupciones
    for (i=0; i < NUM_BUTTONS; i++){
        struct gpio_button *button = &gpio_buttons[i];
        // configurar el GPIO como entrada
        ret = gpio_request(button->gpio, GPIO_IN, button->name);
        if (ret) {
            pr_err("%s: no se pudo solicitar el GPIO %d\n", KBUILD_MODNAME, button->gpio);
            goto err_gpio_request;
        }
        //obtener el numero irq asociado al GPIO
        button->irq = gpio_to_irq(button->gpio);
        if (button->irq < 0) {
            pr_err("%s: no se pudo obtener el IRQ para GPIO %d\n", KBUILD_MODNAME, button->gpio);
            ret = button->irq;
            goto err_gpio_to_irq;
        }
        //solicitar interrupcion en modo ascendente  y descendente
        ret = request_irq(button->irq, gpio_isr,
            IRQF_TRIGGER_RISING |IRQF_TRIGGER_FALLING |IRQF_SHARED,
            button->name, button);
        if (ret) {
            pr_err("%s: no se pudo solicitar el IRQ %d\n", KBUILD_MODNAME, button->irq);
            goto err_request_irq;
        }
    }
    pr_info("%s: custom gpio driver loaded successfully\n", KBUILD_MODNAME);
    return 0; // exito

    err_request_irq:
        if (button->irq >=0){
            free_irq(button->irq, button);
        }

    err_gpio_irq:
        gpio_free(button->gpio);
    
    err_gpio_request:
    //liberar los gpio e irqs ya configurados
    for(i--; i>=0;i--){
        free_irq(gpio_buttons[i].irq, &gpio_buttons[i]);
        gpio_free(gpio_buttons[i].gpio);
    }
    input_unregister_device(custom_input_dev);
    input_free_device(custom_input_dev);
    return ret;
}



static void __exit custom_gpio_driver_exit(void){
    int i;
    pr_info("%s: Desactivando custom GPIO driver\n", KBUILD_MODNAME);
    // liberar los GPIOs e interrupciones
    for (i = 0; i < NUM_BUTTONS; i++) {
        free_irq(gpio_buttons[i].irq, &gpio_buttons[i]);
        gpio_free(gpio_buttons[i].gpio);
    }

    //desregistrar el dispositivo de entrada
    input_unregister_device(custom_input_dev);
    input_free_device(custom_input_dev);
    pr_info("%s: custom GPIO driver descargado correctamente\n", KBUILD_MODNAME);
}

//=====================================================
// macros para registarr inicializacion y salida del modulo 
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