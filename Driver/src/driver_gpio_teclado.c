#include "GPIO_driver.h"



// --- Variables Globales ---
int fifo_fd; // File descriptor de la tubería
volatile int running = 1; // Bandera para controlar el bucle principal
volatile uint32_t power_button_pressed_tick = 0; // Tiempo (tick de pigpio) en que se presionó el botón de encendido
volatile int system_awake = 1; // 1 for awake, 0 for sleep. Controla el estado del sistema para el botón ON/OFF.

// --- Funciones para manejo de GPIO ---

// Callback para pines de puntuación (pulso HIGH)
// Los eventos de puntuación son impulsos cortos que queremos detectar de inmediato.
void score_gpio_callback(int gpio, int level, uint32_t tick) {
    // Solo nos interesa el flanco de subida (HIGH)
    if (level == PI_HIGH) {
        char event_msg[32];
        switch (gpio) {
            case GPIO_SCORE_500: snprintf(event_msg, sizeof(event_msg), "SCORE_500\n"); break;
            case GPIO_SCORE_300: snprintf(event_msg, sizeof(event_msg), "SCORE_300\n"); break;
            case GPIO_SCORE_250: snprintf(event_msg, sizeof(event_msg), "SCORE_250\n"); break;
            case GPIO_SCORE_100: snprintf(event_msg, sizeof(event_msg), "SCORE_100\n"); break;
            default: return; // No es un pin de puntuación conocido
        }
        // Se puede añadir un manejo de error para write si es necesario (EAGAIN, EPIPE)
        write(fifo_fd, event_msg, strlen(event_msg));
        printf("Evento puntuación: %s", event_msg);
    }
}

// Callback para pulsadores de control (con debounce software)
void button_gpio_callback(int gpio, int level, uint32_t tick) {
    if (gpio == GPIO_BTN_ON_OFF) {
        if (level == PI_HIGH) { // Botón ON/OFF presionado
            power_button_pressed_tick = tick;
            printf("Botón ON/OFF PRESIONADO (tick: %u)\n", tick);
            // No enviar evento de "PRESSED" aquí directamente para el juego,
            // ya que la acción depende de la duración.
        } else { // Botón ON/OFF soltado
            if (power_button_pressed_tick != 0) { // Si estaba presionado
                uint32_t hold_duration_us = tick - power_button_pressed_tick;
                printf("Botón ON/OFF SOLTADO (duración: %u us)\n", hold_duration_us);

                if (hold_duration_us >= (POWER_OFF_HOLD_TIME_MS * 1000)) {
                    printf("¡Apagando el sistema (pulso largo)!\n");
                    char event_msg[] = "SYSTEM_SHUTDOWN\n";
                    write(fifo_fd, event_msg, strlen(event_msg));
                    // Darle tiempo al Python para recibir y actuar (0.5s)
                    // Considera si este delay es suficiente o si el shutdown debe ser manejado por el servicio de Python.
                    // Ejecutar system() bloquea el driver hasta que el comando termina.
                    usleep(500000);
                    system("sudo shutdown -h now");
                    running = 0; // Detener el bucle principal ya que el sistema se apagará.
                } else { // Pulso corto
                    if (system_awake) {
                        printf("Botón ON/OFF: Pulso corto, entrando en modo de bajo consumo.\n");
                        char event_msg[] = "SYSTEM_SLEEP\n";
                        write(fifo_fd, event_msg, strlen(event_msg));
                        system_awake = 0; // Actualizar estado del driver
                    } else {
                        printf("Botón ON/OFF: Pulso corto, saliendo de modo de bajo consumo.\n");
                        char event_msg[] = "SYSTEM_WAKEUP\n";
                        write(fifo_fd, event_msg, strlen(event_msg));
                        system_awake = 1; // Actualizar estado del driver
                    }
                }
                power_button_pressed_tick = 0; // Reset
            }
        }
        return;
    }

    // Para los otros botones de control
    if (level == PI_HIGH) { // Botón presionado (flanco de subida)
        char event_msg[32];
        switch (gpio) {
            case GPIO_BTN_UP:    snprintf(event_msg, sizeof(event_msg), "KEY_UP_PRESSED\n"); break;
            case GPIO_BTN_DOWN:  snprintf(event_msg, sizeof(event_msg), "KEY_DOWN_PRESSED\n"); break;
            case GPIO_BTN_LEFT:  snprintf(event_msg, sizeof(event_msg), "KEY_LEFT_PRESSED\n"); break;
            case GPIO_BTN_RIGHT: snprintf(event_msg, sizeof(event_msg), "KEY_RIGHT_PRESSED\n"); break;
            case GPIO_BTN_INTRO: snprintf(event_msg, sizeof(event_msg), "KEY_INTRO_PRESSED\n"); break;
            default: return;
        }
        write(fifo_fd, event_msg, strlen(event_msg));
        printf("Evento pulsador: %s", event_msg);
    } else { // Botón soltado (flanco de bajada)
        char event_msg[32];
        switch (gpio) {
            case GPIO_BTN_UP:    snprintf(event_msg, sizeof(event_msg), "KEY_UP_RELEASED\n"); break;
            case GPIO_BTN_DOWN:  snprintf(event_msg, sizeof(event_msg), "KEY_DOWN_RELEASED\n"); break;
            case GPIO_BTN_LEFT:  snprintf(event_msg, sizeof(event_msg), "KEY_LEFT_RELEASED\n"); break;
            case GPIO_BTN_RIGHT: snprintf(event_msg, sizeof(event_msg), "KEY_RIGHT_RELEASED\n"); break;
            case GPIO_BTN_INTRO: snprintf(event_msg, sizeof(event_msg), "KEY_INTRO_RELEASED\n"); break;
            default: return;
        }
        write(fifo_fd, event_msg, strlen(event_msg));
        // printf("Evento pulsador: %s", event_msg); // Puedes comentar esto si no necesitas el evento de soltado
    }
}

// --- Manejo de Señales (para salir limpiamente) ---
void sigint_handler(int signo) {
    if (signo == SIGINT || signo == SIGTERM) {
        printf("\nSeñal recibida, cerrando el driver...\n");
        running = 0; // Detiene el bucle principal
    }
}

// --- Función de inicialización y limpieza ---
void setup_gpios() {
    // Puntuación
    gpioSetMode(GPIO_SCORE_500, PI_INPUT);
    gpioSetPullResistor(GPIO_SCORE_500, PI_PUD_DOWN); // Asegura estado LOW
    // No usamos gpioSetAlertFuncEx aquí para score porque queremos cada pulso sin debounce
    gpioSetAlertFunc(GPIO_SCORE_500, score_gpio_callback);

    gpioSetMode(GPIO_SCORE_300, PI_INPUT);
    gpioSetPullResistor(GPIO_SCORE_300, PI_PUD_DOWN);
    gpioSetAlertFunc(GPIO_SCORE_300, score_gpio_callback);

    gpioSetMode(GPIO_SCORE_250, PI_INPUT);
    gpioSetPullResistor(GPIO_SCORE_250, PI_PUD_DOWN);
    gpioSetAlertFunc(GPIO_SCORE_250, score_gpio_callback);

    gpioSetMode(GPIO_SCORE_100, PI_INPUT);
    gpioSetPullResistor(GPIO_SCORE_100, PI_PUD_DOWN);
    gpioSetAlertFunc(GPIO_SCORE_100, score_gpio_callback);

    // Pulsadores (con debounce)
    gpioSetMode(GPIO_BTN_UP, PI_INPUT);
    gpioSetPullResistor(GPIO_BTN_UP, PI_PUD_DOWN);
    // gpioSetAlertFuncEx permite pasar un puntero de usuario, pero para estos callbacks simples, gpioSetAlertFunc es suficiente si no necesitas el puntero de usuario.
    // gpioSetAlertFunc solo pasa gpio, level, tick. Si quieres el mismo callback para todos y usar el gpio ID, es mejor.
    // gpioSetAlertFuncEx se usa para pasar el puntero a la función, que en tu código original ya es el GPIO ID
    // Simplificando a gpioSetAlertFunc ya que el GPIO ID es pasado directamente.
    gpioSetAlertFunc(GPIO_BTN_UP, button_gpio_callback);
    gpioSetDebounce(GPIO_BTN_UP, DEBOUNCE_TIME_MS * 1000); // Debounce en microsegundos

    gpioSetMode(GPIO_BTN_DOWN, PI_INPUT);
    gpioSetPullResistor(GPIO_BTN_DOWN, PI_PUD_DOWN);
    gpioSetAlertFunc(GPIO_BTN_DOWN, button_gpio_callback);
    gpioSetDebounce(GPIO_BTN_DOWN, DEBOUNCE_TIME_MS * 1000);

    gpioSetMode(GPIO_BTN_LEFT, PI_INPUT);
    gpioSetPullResistor(GPIO_BTN_LEFT, PI_PUD_DOWN);
    gpioSetAlertFunc(GPIO_BTN_LEFT, button_gpio_callback);
    gpioSetDebounce(GPIO_BTN_LEFT, DEBOUNCE_TIME_MS * 1000);

    gpioSetMode(GPIO_BTN_RIGHT, PI_INPUT);
    gpioSetPullResistor(GPIO_BTN_RIGHT, PI_PUD_DOWN);
    gpioSetAlertFunc(GPIO_BTN_RIGHT, button_gpio_callback);
    gpioSetDebounce(GPIO_BTN_RIGHT, DEBOUNCE_TIME_MS * 1000);

    gpioSetMode(GPIO_BTN_INTRO, PI_INPUT);
    gpioSetPullResistor(GPIO_BTN_INTRO, PI_PUD_DOWN);
    gpioSetAlertFunc(GPIO_BTN_INTRO, button_gpio_callback);
    gpioSetDebounce(GPIO_BTN_INTRO, DEBOUNCE_TIME_MS * 1000);

    // Botón ON/OFF
    gpioSetMode(GPIO_BTN_ON_OFF, PI_INPUT);
    gpioSetPullResistor(GPIO_BTN_ON_OFF, PI_PUD_DOWN);
    gpioSetAlertFunc(GPIO_BTN_ON_OFF, button_gpio_callback);
    // No usamos debounce de pigpio aquí para el ON/OFF, ya que queremos el tiempo de pulsación exacto.
    // El debounce físico es importante, el software de pigpio no lo usaremos para la duración.

    printf("GPIOs configurados y callbacks registrados.\n");
}

void cleanup_gpios() {
    printf("Desactivando callbacks y cerrando pigpio...\n");
    // Desactivar callbacks
    gpioSetAlertFunc(GPIO_SCORE_500, NULL);
    gpioSetAlertFunc(GPIO_SCORE_300, NULL);
    gpioSetAlertFunc(GPIO_SCORE_250, NULL);
    gpioSetAlertFunc(GPIO_SCORE_100, NULL);
    gpioSetAlertFunc(GPIO_BTN_UP, NULL);
    gpioSetAlertFunc(GPIO_BTN_DOWN, NULL);
    gpioSetAlertFunc(GPIO_BTN_LEFT, NULL);
    gpioSetAlertFunc(GPIO_BTN_RIGHT, NULL);
    gpioSetAlertFunc(GPIO_BTN_INTRO, NULL);
    gpioSetAlertFunc(GPIO_BTN_ON_OFF, NULL);

    gpioTerminate(); // Desconecta de pigpiod
    printf("pigpio terminado.\n");
}


//libinput




