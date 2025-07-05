#include <linux/module.h>
#include <linux/init.h>
#include <linux/gpio.h>
#include <linux/interrupt.h>
#include <linux/input.h> // Required for input device
#include <linux/delay.h> // For debouncing (optional, but good practice)

/* Meta Information */
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Johannes 4 GNU/Linux - Modified by Silva Carlos"); // You can add your name here
MODULE_DESCRIPTION("A simple LKM for multiple gpio buttons acting as keyboard inputs");

/* --- Button Configuration --- */
// Structure to hold button information
struct gpio_button {
    unsigned int gpio;
    unsigned int keycode;
    const char *name;
    unsigned int irq_number; // To store the IRQ number for each GPIO
    bool pressed; // To track button state for debouncing and key release
};

// Array of buttons with their GPIOs, keycodes, and names
static struct gpio_button gpio_buttons[] = {
    { .gpio = 22, .keycode = KEY_UP, .name = "UP"},
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

#define NUM_BUTTONS ARRAY_SIZE(gpio_buttons) // Get the number of buttons in the array

static struct input_dev *button_input_dev; // Pointer to the input device

/* --- Interrupt Service Routine (ISR) --- */
/**
 * @brief Interrupt service routine is called when an interrupt is triggered
 * @param irq The IRQ number that triggered the interrupt
 * @param dev_id A pointer to the gpio_button structure for the button that triggered the interrupt
 */
static irqreturn_t gpio_button_isr(int irq, void *dev_id)
{
    struct gpio_button *button = (struct gpio_button *)dev_id;
    int gpio_value;

    // Small delay for debouncing, adjust as needed
    mdelay(10);

    // Read the current state of the GPIO
    gpio_value = gpio_get_value(button->gpio);

    // Check if the button state has changed (press or release)
    if (gpio_value && !button->pressed) {
        // Button pressed (assuming active high for simplicity, adjust if active low)
        input_report_key(button_input_dev, button->keycode, 1); // Report key press
        input_sync(button_input_dev); // Synchronize input device
        button->pressed = true;
        printk(KERN_INFO "gpio_buttons: Button '%s' (GPIO %d) pressed.\n", button->name, button->gpio);
    } else if (!gpio_value && button->pressed) {
        // Button released
        input_report_key(button_input_dev, button->keycode, 0); // Report key release
        input_sync(button_input_dev); // Synchronize input device
        button->pressed = false;
        printk(KERN_INFO "gpio_buttons: Button '%s' (GPIO %d) released.\n", button->name, button->gpio);
    }

    return IRQ_HANDLED;
}

/* --- Module Initialization --- */
/**
 * @brief This function is called when the module is loaded into the kernel
 */
static int __init ModuleInit(void) {
    int i;
    int ret = 0;

    printk(KERN_INFO "gpio_buttons: Loading module...\n");

    // 1. Create a new input device
    button_input_dev = input_allocate_device();
    if (!button_input_dev) {
        printk(KERN_ERR "gpio_buttons: Failed to allocate input device.\n");
        return -ENOMEM;
    }

    // Set up input device properties
    button_input_dev->name = "GPIO Buttons Keyboard";
    button_input_dev->id.bustype = BUS_VIRTUAL;
    button_input_dev->id.vendor = 0xABCD; // Example vendor ID
    button_input_dev->id.product = 0xEFGH; // Example product ID
    button_input_dev->id.version = 0x0001;

    // Set which events the input device can generate (keyboard events)
    __set_bit(EV_KEY, button_input_dev->evbit);
    __set_bit(EV_SYN, button_input_dev->evbit);

    // Set which keys the input device supports
    for (i = 0; i < NUM_BUTTONS; i++) {
        __set_bit(gpio_buttons[i].keycode, button_input_dev->keybit);
    }

    // Register the input device
    ret = input_register_device(button_input_dev);
    if (ret) {
        printk(KERN_ERR "gpio_buttons: Failed to register input device.\n");
        input_free_device(button_input_dev);
        return ret;
    }

    // 2. Iterate through each button, request GPIO, set direction, and request IRQ
    for (i = 0; i < NUM_BUTTONS; i++) {
        struct gpio_button *button = &gpio_buttons[i];

        printk(KERN_INFO "gpio_buttons: Setting up button '%s' on GPIO %d...\n", button->name, button->gpio);

        // Request the GPIO
        ret = gpio_request(button->gpio, button->name);
        if (ret) {
            printk(KERN_ERR "gpio_buttons: Error! Cannot allocate GPIO %d for button '%s'.\n", button->gpio, button->name);
            // Free previously requested GPIOs and return
            goto err_gpio_request;
        }

        // Set GPIO direction to input
        ret = gpio_direction_input(button->gpio);
        if (ret) {
            printk(KERN_ERR "gpio_buttons: Error! Cannot set GPIO %d to input for button '%s'.\n", button->gpio, button->name);
            gpio_free(button->gpio);
            goto err_gpio_request;
        }

        // Get the IRQ number for the GPIO
        button->irq_number = gpio_to_irq(button->gpio);
        if (button->irq_number < 0) {
            printk(KERN_ERR "gpio_buttons: Error! Cannot get IRQ for GPIO %d.\n", button->gpio);
            gpio_free(button->gpio);
            goto err_gpio_request;
        }

        // Request the interrupt for this GPIO
        // Using IRQF_TRIGGER_RISING | IRQF_TRIGGER_FALLING to detect both press and release
        ret = request_irq(button->irq_number, gpio_button_isr,
                          IRQF_TRIGGER_RISING | IRQF_TRIGGER_FALLING | IRQF_SHARED,
                          button->name, button); // Pass the button structure as dev_id
        if (ret != 0) {
            printk(KERN_ERR "gpio_buttons: Error! Cannot request interrupt nr.: %d for button '%s'.\n", button->irq_number, button->name);
            gpio_free(button->gpio);
            goto err_gpio_request;
        }
        printk(KERN_INFO "gpio_buttons: Button '%s' (GPIO %d) is mapped to IRQ Nr.: %d.\n", button->name, button->gpio, button->irq_number);
    }

    printk(KERN_INFO "gpio_buttons: Module loaded successfully.\n");
    return 0;

err_gpio_request:
    // Cleanup in case of an error during initialization
    for (i--; i >= 0; i--) {
        struct gpio_button *button = &gpio_buttons[i];
        if (button->irq_number > 0) { // Only free if IRQ was successfully requested
            free_irq(button->irq_number, button);
        }
        gpio_free(button->gpio);
    }
    input_unregister_device(button_input_dev);
    input_free_device(button_input_dev); // Free input device if registration failed or cleanup is needed
    return ret;
}

/* --- Module Exit --- */
/**
 * @brief This function is called when the module is removed from the kernel
 */
static void __exit ModuleExit(void) {
    int i;

    printk(KERN_INFO "gpio_buttons: Unloading module...\n");

    // Free all requested IRQs and GPIOs
    for (i = 0; i < NUM_BUTTONS; i++) {
        struct gpio_button *button = &gpio_buttons[i];
        if (button->irq_number > 0) { // Ensure IRQ was successfully requested before freeing
            free_irq(button->irq_number, button);
            printk(KERN_INFO "gpio_buttons: Freeing IRQ %d for button '%s'.\n", button->irq_number, button->name);
        }
        gpio_free(button->gpio);
        printk(KERN_INFO "gpio_buttons: Freeing GPIO %d for button '%s'.\n", button->gpio, button->name);
    }

    // Unregister and free the input device
    if (button_input_dev) {
        input_unregister_device(button_input_dev);
        input_free_device(button_input_dev);
        printk(KERN_INFO "gpio_buttons: Input device unregistered and freed.\n");
    }

    printk(KERN_INFO "gpio_buttons: Module unloaded.\n");
}

module_init(ModuleInit);
module_exit(ModuleExit);