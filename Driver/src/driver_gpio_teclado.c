/*
Dispositivo : Driver GPIO Teclado estandar
Autor :   Carlos Daniel Silva
Fecha :   2023-10-05
Descripcion :   Controlador para la lectura de un teclado utilizando GPIO
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

// Mantener el OFFSET de 512, ya que se ha confirmado su relevancia en tu sistema.
#define OFFSET 512 

//=====================================================
// Estructura para almacenar la informacion de cada tecla
//=====================================================

struct gpio_button {
    int gpio;              // BCM gpio number (con offset aplicado para el kernel global)
    int irq;               // interrupcion asociada al gpio
    unsigned int keycode;  // codigo evdev asociado al boton
    char name[32];         // nombre del boton
    unsigned long last_jiffies; // Para el control de antirebote (debounce)
    struct gpio_desc *desc; // Descriptor del GPIO para la API gpio_consumer
};

// Declaración de prototipo para la función auxiliar de liberación de recursos
static void gpio_free_button_desc(struct gpio_button *button);


//=====================================================
// Arreglo de las teclas
//=====================================================

static struct gpio_button gpio_buttons[] = {
    { .gpio = 4 + OFFSET, .keycode = KEY_UP, .name = "UP"},
    { .gpio = 23 + OFFSET, .keycode = KEY_DOWN, .name = "DOWN"},
    { .gpio = 24 + OFFSET, .keycode = KEY_TAB, .name = "TAB"},
    { .gpio = 25 + OFFSET, .keycode = KEY_ENTER, .name = "ENTER"},
    { .gpio = 8  + OFFSET, .keycode = KEY_S, .name = "S"},
    { .gpio = 7  + OFFSET, .keycode = KEY_1, .name = "NUM_1"},
    { .gpio = 1  + OFFSET, .keycode = KEY_2, .name = "NUM_2"},
    { .gpio = 12 + OFFSET, .keycode = KEY_3, .name = "NUM_3"},
    { .gpio = 16 + OFFSET, .keycode = KEY_4, .name = "NUM_4"},
    { .gpio = 20 + OFFSET, .keycode = KEY_5, .name = "NUM_5"},
    { .gpio = 21 + OFFSET, .keycode = KEY_6, .name = "NUM_6"},
    { .gpio = 26 + OFFSET, .keycode = KEY_7, .name = "NUM_7"},
    { .gpio = 19 + OFFSET, .keycode = KEY_8, .name = "NUM_8"},
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

    // Deshabilita interrupciones locales para proteger el acceso a jiffies
    local_irq_save(flags);

    // Lógica de antirrebote: si el tiempo transcurrido desde la última vez es muy corto, ignorar
    if (time_before(jiffies, button->last_jiffies + DEBOUNCE_DELAY_JIFFIES)) {
        local_irq_restore(flags); // Restaurar interrupciones antes de salir
        return IRQ_HANDLED;
    }

    // Obtener el valor actual del GPIO.
    // gpiod_get_value es la forma recomendada con la API gpio_consumer.
    value = gpiod_get_value(button->desc);

    // Actualizar el tiempo de la última interrupción para el antirrebote
    button->last_jiffies = jiffies;

    // Reportar el evento de teclado:
    // Un valor de 1 (HIGH) significa que el botón está presionado (asumiendo pull-down externo).
    // Un valor de 0 (LOW) significa que el botón está liberado.
    input_report_key(custom_input_dev, button->keycode, value);
    input_sync(custom_input_dev); // Sincronizar para que el evento sea procesado

    // Mensaje de depuración en el kernel log
    pr_info("%s: Button %s (GPIO %d, IRQ %d, keycode %d)\n",
        KBUILD_MODNAME, value ? "pressed" : "released",
        button->gpio, button->irq, button->keycode);

    // Habilita interrupciones locales
    local_irq_restore(flags);
    return IRQ_HANDLED; // Indica que la interrupción fue manejada
}


//=====================================================
// Inicializacion del modulo
//=====================================================

static int __init custom_gpio_driver_init(void){
    int ret;
    int i;
    // Nueva bandera para rastrear si custom_input_dev ha sido registrado
    bool input_dev_registered = false; 

    pr_info("%s: Inicializando custom GPIO driver\n", KBUILD_MODNAME);

    // 1. Asignar el dispositivo de entrada
    custom_input_dev = input_allocate_device();
    if (!custom_input_dev){
        pr_err("%s: no se pudo asignar el dispositivo de entrada\n", KBUILD_MODNAME);
        return -ENOMEM; // No hay memoria disponible
    }

    // Configurar propiedades del dispositivo de entrada
    custom_input_dev->name = "custom_gpio_keyboard";
    custom_input_dev->id.bustype = BUS_VIRTUAL; // Dispositivo virtual, no un bus físico
    custom_input_dev->id.vendor = 0xAAAA;
    custom_input_dev->id.product = 0xBBBB;
    custom_input_dev->id.version = 0x0001;

    // Establecer que este dispositivo puede generar eventos de tipo KEY (tecla)
    __set_bit(EV_KEY, custom_input_dev->evbit);

    // Establecer qué códigos de tecla específicos puede generar este dispositivo
    for (i = 0; i < NUM_BUTTONS; i++){
        __set_bit(gpio_buttons[i].keycode, custom_input_dev->keybit);
        gpio_buttons[i].last_jiffies = 0; // Inicializar tiempo de antirrebote
    }

    // 2. Registrar el dispositivo de entrada en el subsistema Input
    ret = input_register_device(custom_input_dev);
    if (ret){
        pr_err("%s: no se pudo registrar el dispositivo de entrada\n", KBUILD_MODNAME);
        input_free_device(custom_input_dev); // Liberar si falla el registro
        return ret;
    }
    input_dev_registered = true; // Marcar que el dispositivo de entrada se registró con éxito

    // 3. Configurar cada botón GPIO
    for (i = 0; i < NUM_BUTTONS; i++){
        // Solicitar el GPIO usando la API gpio_consumer. GPIOD_IN para entrada.
        // No se especifica pull-up/down aquí, asumiendo manejo externo.
        gpio_buttons[i].desc = gpio_request_one(gpio_buttons[i].gpio, GPIOD_IN, gpio_buttons[i].name);
        if (IS_ERR(gpio_buttons[i].desc)) {
            ret = PTR_ERR(gpio_buttons[i].desc); // Obtener el código de error
            // Cambiado %ld a %d para el tipo int de 'ret'
            pr_err("%s: no se pudo solicitar el GPIO %d (%s). Error: %d\n", 
                   KBUILD_MODNAME, gpio_buttons[i].gpio, gpio_buttons[i].name, ret);
            goto err_gpiod_request; // Saltar a la limpieza de errores
        }

        // Obtener el número de interrupción asociado al descriptor GPIO
        gpio_buttons[i].irq = gpiod_to_irq(gpio_buttons[i].desc);
        if (gpio_buttons[i].irq < 0) {
            pr_err("%s: no se pudo obtener el IRQ para GPIO %d (%s). Error: %d\n", 
                   KBUILD_MODNAME, gpio_buttons[i].gpio, gpio_buttons[i].name, gpio_buttons[i].irq);
            ret = gpio_buttons[i].irq; // Usar el error devuelto por gpiod_to_irq
            goto err_gpio_to_irq; // Saltar a la limpieza
        }

        // Solicitar la interrupción:
        // IRQF_TRIGGER_RISING | IRQF_TRIGGER_FALLING: Detecta flancos de subida y bajada.
        // IRQF_SHARED: Indica que la IRQ puede ser compartida (seguro para GPIOs).
        // &gpio_buttons[i]: Puntero al dato que se pasará a la ISR (este botón específico).
        ret = request_irq(gpio_buttons[i].irq, gpio_isr,
                          IRQF_TRIGGER_RISING | IRQF_TRIGGER_FALLING | IRQF_SHARED,
                          gpio_buttons[i].name, &gpio_buttons[i]);
        if (ret) {
            pr_err("%s: no se pudo solicitar el IRQ %d para %s. Error: %d\n", 
                   KBUILD_MODNAME, gpio_buttons[i].irq, gpio_buttons[i].name, ret);
            goto err_request_irq; // Saltar a la limpieza
        }
    }

    pr_info("%s: Custom GPIO driver loaded successfully\n", KBUILD_MODNAME);
    return 0; // Éxito

// --- Manejo de Errores: Saltos y Limpieza ---
// Los errores se manejan en orden inverso a la asignación de recursos
// 'i' contendrá el índice del botón que causó el error.

err_request_irq:
    // Si request_irq falló para gpio_buttons[i], liberar su IRQ (aunque realmente no se asignó si falló)
    // y su descriptor GPIO.
    gpio_free_button_desc(&gpio_buttons[i]);

err_gpio_to_irq:
    // Si gpiod_to_irq falló para gpio_buttons[i], solo el descriptor GPIO necesita ser liberado.
    // gpio_free_button_desc ya se encarga de esto si no hay IRQ asignada.
    if (gpio_buttons[i].desc && !IS_ERR(gpio_buttons[i].desc)) {
        gpiod_put(gpio_buttons[i].desc);
        gpio_buttons[i].desc = NULL; // Prevenir doble liberación
    }

err_gpiod_request:
    // Si gpio_request_one falló para gpio_buttons[i], no hay nada que liberar para este botón.
    // Ahora, liberar los recursos de los botones PREVIOS que se configuraron correctamente.
    for(i--; i >= 0; i--){ // Decrementar 'i' para empezar desde el último botón exitoso
        gpio_free_button_desc(&gpio_buttons[i]);
    }
    
    // Si el dispositivo de entrada se registró exitosamente, desregistrarlo.
    if (input_dev_registered) {
        input_unregister_device(custom_input_dev);
    }
    // Siempre liberar la memoria asignada para el dispositivo de entrada.
    input_free_device(custom_input_dev); 
    return ret; // Retornar el código de error original
}

// Función auxiliar para liberar los recursos de un solo botón
static void gpio_free_button_desc(struct gpio_button *button) {
    // Liberar la interrupción si fue solicitada válidamente
    if (button->irq > 0) { 
        free_irq(button->irq, button);
        button->irq = 0; // Resetear para evitar liberaciones dobles
    }
    // Liberar el descriptor GPIO si fue asignado válidamente
    if (button->desc && !IS_ERR(button->desc)) {
        gpiod_put(button->desc);
        button->desc = NULL; // Resetear para evitar liberaciones dobles
    }
}

//=====================================================
// Salida del modulo
//=====================================================
static void __exit custom_gpio_driver_exit(void){
    int i;
    pr_info("%s: Desactivando custom GPIO driver\n", KBUILD_MODNAME);

    // Liberar recursos de todos los botones
    for (i = 0; i < NUM_BUTTONS; i++) {
        gpio_free_button_desc(&gpio_buttons[i]);
    }

    // Desregistrar y liberar el dispositivo de entrada
    // custom_input_dev debería existir si se llegó hasta aquí con éxito.
    // Aunque el kernel suele manejar la liberación si el módulo no se desregistró,
    // es buena práctica hacerlo explícitamente.
    if (custom_input_dev) { 
        input_unregister_device(custom_input_dev);
        input_free_device(custom_input_dev);
    }
    
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
MODULE_DESCRIPTION("GPIO Keyboard Driver");
MODULE_ALIAS("platform:rpi-Keyboard-ctrl");
MODULE_VERSION("0.01");