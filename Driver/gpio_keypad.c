#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/gpio.h>
#include <linux/interrupt.h>
#include <linux/input.h>
#include <linux/semaphore.h>
#include <linux/jiffies.h> // ¡Nueva inclusión para jiffies!

#define MODULE_NAME "gpio_keypad"
#define NUM_KEYS 13
#define DEBOUNCE_JIFFIES msecs_to_jiffies(50) // 50 ms de antirebote

//===========================================================
// Estructura para las interrupciones
//===========================================================
struct gpio_key_map {
    int gpio;
    int irq;
    int keycode;
    const char *name;
    unsigned long last_jiffie; // ¡Nuevo campo para el timestamp del antirebote!
};
//===========================================================
// arreglo de teclas
//===========================================================
static struct gpio_key_map key_map[NUM_KEYS] = {
    {  3, -1, KEY_1,   "KEY_1", 0 }, // Inicializar last_jiffie a 0
    {  4, -1, KEY_2,   "KEY_2", 0 },
    {  5, -1, KEY_3,   "KEY_3", 0 },
    {  6, -1, KEY_4,   "KEY_4", 0 },
    {  7, -1, KEY_5,   "KEY_5", 0 },
    {  8, -1, KEY_6,   "KEY_6", 0 },
    {  9, -1, KEY_7,   "KEY_7", 0 },
    { 10, -1, KEY_8,   "KEY_8", 0 },
    { 11, -1, KEY_UP,   "KEY_UP", 0 },
    { 12, -1, KEY_DOWN, "KEY_DOWN", 0 },
    { 13, -1, KEY_ENTER,"KEY_ENTER", 0 },
    { 14, -1, KEY_TAB,  "KEY_TAB", 0 },
    { 15, -1, KEY_BACKSPACE, "KEY_S", 0 },
};

//===========================================================
// puntero al dispositivo de entrada
//===========================================================
static struct input_dev *gpio_input_dev;

//===========================================================
// Handler de interrupciones
//===========================================================
static irqreturn_t gpio_irq_handler(int irq, void *dev_id)
{
    struct gpio_key_map *key = dev_id;
    unsigned long now = jiffies; // Obtener el jiffie actual

    if (!key)
        return IRQ_NONE;

    // Implementación del antirebote
    // Comprueba si ha pasado el tiempo DEBOUNCE_JIFFIES desde la última pulsación válida
    if (time_before(now, key->last_jiffie + DEBOUNCE_JIFFIES)) {
        // Si no ha pasado suficiente tiempo, ignora esta interrupción
        return IRQ_HANDLED;
    }

    // Actualiza el timestamp de la última pulsación válida
    key->last_jiffie = now;

    input_report_key(gpio_input_dev, key->keycode, 1); // Reporta la pulsación de la tecla (presionada)
    input_sync(gpio_input_dev);                       // Sincroniza el subsistema de entrada
    input_report_key(gpio_input_dev, key->keycode, 0); // Reporta la liberación de la tecla (soltada)
    input_sync(gpio_input_dev);                       // Sincroniza el subsistema de entrada

    printk(KERN_INFO "Tecla %s activada (GPIO %d), Jiffies: %lu\n", key->name, key->gpio, now);

    return IRQ_HANDLED;
}

//===========================================================
// Funcion de inicializacion del modulo
//===========================================================
static int __init gpio_keyboard_init(void)
{
    int i, ret;

    gpio_input_dev = input_allocate_device();
    if (!gpio_input_dev) {
        printk(KERN_ERR "No se pudo asignar input device\n");
        return -ENOMEM;
    }

    gpio_input_dev->name = "gpio-keyboard";
    gpio_input_dev->phys = "gpio/input0";
    gpio_input_dev->id.bustype = BUS_HOST;
    gpio_input_dev->evbit[0] = BIT_MASK(EV_KEY);

    for (i = 0; i < NUM_KEYS; i++)
        __set_bit(key_map[i].keycode, gpio_input_dev->keybit);

    ret = input_register_device(gpio_input_dev);
    if (ret) {
        printk(KERN_ERR "No se pudo registrar input device\n");
        input_free_device(gpio_input_dev);
        return ret;
    }

    for (i = 0; i <= NUM_KEYS; i++) {
        ret = gpio_request(key_map[i].gpio, key_map[i].name);
        if (ret) {
            printk(KERN_ERR "gpio_request fallo para GPIO %d\n", key_map[i].gpio);
            continue;
        }

        ret = gpio_direction_input(key_map[i].gpio);
        if (ret) {
            printk(KERN_ERR "gpio_direction_input fallo para GPIO %d\n", key_map[i].gpio);
            gpio_free(key_map[i].gpio);
            continue;
        }

        key_map[i].irq = gpio_to_irq(key_map[i].gpio);
        ret = request_irq(key_map[i].irq, gpio_irq_handler, IRQF_TRIGGER_RISING,
                          key_map[i].name, &key_map[i]);
        if (ret) {
            printk(KERN_ERR "request_irq fallo para GPIO %d\n", key_map[i].gpio);
            gpio_free(key_map[i].gpio);
        }
        // No necesitamos inicializar last_jiffie aquí, ya lo hacemos en la declaración del arreglo.
        // Pero si no lo inicializamos en la declaración, podríamos hacer:
        // key_map[i].last_jiffie = jiffies; // O cualquier valor inicial razonable.
    }

    printk(KERN_INFO "Modulo gpio_keyboard_driver cargado con antirebote de %d ms\n",
           jiffies_to_msecs(DEBOUNCE_JIFFIES)); // Muestra el tiempo de antirebote en ms
    return 0;
}

//===========================================================
// Funcion de salida del modulo
//===========================================================
static void __exit gpio_keyboard_exit(void)
{
    int i;
    for (i = 0; i < NUM_KEYS; i++) {
        if (key_map[i].irq >= 0)
            free_irq(key_map[i].irq, &key_map[i]);
        gpio_free(key_map[i].gpio);
    }

    if (gpio_input_dev)
        input_unregister_device(gpio_input_dev);

    printk(KERN_INFO "Modulo gpio_keyboard_driver descargado\n");
}

//===========================================================
// macros para registrar inicializacion y salida del modulo
//===========================================================
module_init(gpio_keyboard_init);
module_exit(gpio_keyboard_exit);


//===========================================================
// Metadatos del modulo
//===========================================================
MODULE_AUTHOR("Carlos, Gepeto y un repositorio ya olvidado");
MODULE_DESCRIPTION("GPIO  Keyboard Driver with Debouncing"); 
MODULE_ALIAS("Platform:rpi-Keyboard-ctrl");
MODULE_LICENSE("GPL");
MODULE_VERSION("0.03"); 