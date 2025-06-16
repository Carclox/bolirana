#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/input.h>
#include <string.h>
#include <time.h>
#include <signal.h>
#include <sys/wait.h> // Necesario para waitpid

// =================================================================================
// ¡IMPORTANTE! Configura la ruta de tu dispositivo de teclado y el código de la tecla 's'.
//
// 1. Identifica tu dispositivo de entrada:
//    Después de que tu driver 'driver_gpio_teclado.ko' esté cargado (ya sea manualmente
//    con 'sudo insmod' o automáticamente por tu servicio 'driver_init.service'),
//    ejecuta en la terminal de tu Raspberry Pi:
//    cat /proc/bus/input/devices | grep -A5 "custom_gpio_keyboard"
//    Busca la línea "H: Handlers=... eventX". El 'X' es el número que necesitas.
//    Por ejemplo, si dice "event0", usa "/dev/input/event0".
//
// 2. Verifica el código de la tecla 's':
//    Puedes usar 'sudo evtest' (instálalo con 'sudo apt install evtest' si no lo tienes).
//    Selecciona tu teclado de la lista, presiona la tecla 's' y observa el 'code'.
//    Normalmente es 47, pero es bueno confirmarlo.
// =================================================================================
#define KEYBOARD_DEVICE "/dev/input/event0" // <--- ¡AJUSTA ESTO CON EL VALOR REAL DE TU RASPBERRY PI!
#define KEY_S_CODE 47                       // Código de tecla para 's'.

// Variable global para controlar la ejecución del bucle principal
volatile sig_atomic_t running = 1;

/**
 * @brief Manejador de señales para capturar SIGINT (Ctrl+C) y SIGTERM.
 * Permite una salida limpia del programa.
 * @param signum Número de la señal recibida.
 */
void sig_handler(int signum) {
    if (signum == SIGINT || signum == SIGTERM) {
        running = 0;
        fprintf(stderr, "\nSeñal de terminación recibida. Saliendo...\n");
    }
}

/**
 * @brief Función principal del programa.
 * Abre el dispositivo de teclado y monitorea las pulsaciones.
 */
int main() {
    int fd;
    struct input_event ev;
    time_t s_press_start_time = 0; // Marca de tiempo cuando la 's' fue presionada
    pid_t suspend_pid = -1;       // PID del proceso hijo que ejecuta la suspensión

    // Configura el manejador de señales para una salida ordenada al recibir Ctrl+C o señales de terminación.
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    fprintf(stdout, "Intentando abrir el dispositivo de teclado: %s\n", KEYBOARD_DEVICE);
    // Abre el dispositivo de entrada en modo de solo lectura.
    fd = open(KEYBOARD_DEVICE, O_RDONLY);
    if (fd == -1) {
        perror("Error al abrir el dispositivo de teclado");
        fprintf(stderr, "Asegúrate de que el driver esté cargado y de tener permisos de lectura (intenta 'sudo ./keyboard_monitor').\n");
        fprintf(stderr, "Para identificar tu teclado, usa 'cat /proc/bus/input/devices' y busca 'Handlers=sysrq kbd eventX' bajo 'custom_gpio_keyboard'.\n");
        return EXIT_FAILURE;
    }

    fprintf(stdout, "Monitoreando el teclado.\n");
    fprintf(stdout, " - Pulsa 's' brevemente para que el sistema entre en suspensión.\n");
    fprintf(stdout, " - Presiona cualquier otra tecla para salir de la suspensión.\n");
    fprintf(stdout, " - Mantén 's' presionado por 3 segundos para apagar el sistema.\n");
    fflush(stdout); // Asegura que los mensajes se muestren en la consola.

    // Bucle principal para leer eventos del teclado mientras el programa esté en ejecución.
    while (running) {
        fd_set fds;        // Conjunto de descriptores de archivo para select.
        struct timeval tv; // Estructura para el timeout de select.
        int ret;           // Valor de retorno de select.

        // Inicializa el conjunto de descriptores de archivo y añade el descriptor del teclado.
        FD_ZERO(&fds);
        FD_SET(fd, &fds);

        // Configura el timeout para select.
        // Si la tecla 's' está siendo presionada, el timeout es corto para verificar rápidamente la duración.
        // De lo contrario, espera hasta 1 segundo por un evento.
        if (s_press_start_time != 0) {
            tv.tv_sec = 0;
            tv.tv_usec = 100000; // 100 milisegundos
        } else {
            tv.tv_sec = 1; // 1 segundo
            tv.tv_usec = 0;
        }

        // Espera por la disponibilidad de datos para leer del descriptor de archivo.
        ret = select(fd + 1, &fds, NULL, NULL, &tv);

        if (ret == -1) {
            perror("Error en select");
            break; // Sale del bucle en caso de error.
        } else if (ret == 0) {
            // Se agotó el tiempo de espera (timeout), no hubo eventos.
            if (s_press_start_time != 0) {
                // Si la 's' estaba presionada y no hubo eventos, verifica si ya pasaron 3 segundos.
                if ((time(NULL) - s_press_start_time) >= 3) {
                    fprintf(stdout, "Tecla 's' mantenida por 3 segundos. Iniciando apagado...\n");
                    fflush(stdout); // Asegura que el mensaje se muestre antes del apagado.
                    // Ejecuta el comando de apagado del sistema.
                    system("sudo systemctl poweroff");
                    running = 0; // Establece la bandera para salir del bucle.
                    break;       // Sale del bucle.
                }
            }
            continue; // Continúa esperando si no hay eventos o el timeout es por 's'.
        }

        // Lee el evento de entrada del dispositivo.
        if (read(fd, &ev, sizeof(struct input_event)) == -1) {
            perror("Error al leer el evento de entrada");
            break; // Sale del bucle en caso de error de lectura.
        }

        // Procesa solo eventos de tipo KEY (pulsaciones de teclas).
        if (ev.type == EV_KEY) {
            if (ev.value == 1) { // Evento de pulsación de tecla (key down).
                fprintf(stdout, "Pulsación de tecla: Código = %d\n", ev.code);
                if (ev.code == KEY_S_CODE) {
                    if (s_press_start_time == 0) {
                        // Registra el tiempo de inicio de la pulsación de 's'.
                        s_press_start_time = time(NULL);
                    }
                } else {
                    // Si se presiona cualquier otra tecla, reinicia el temporizador de 's'.
                    if (s_press_start_time != 0) {
                        s_press_start_time = 0;
                    }
                    // Si el sistema está suspendido y se presiona otra tecla,
                    // el evento de teclado generalmente lo despierta.
                    // Si un proceso de suspensión estaba activo (suspend_pid != -1),
                    // intenta limpiar su estado.
                    if (suspend_pid != -1) {
                        fprintf(stdout, "Otra tecla presionada. Asumiendo reanudación del sistema.\n");
                        // Verifica el estado del proceso hijo de suspensión sin bloquearse.
                        waitpid(suspend_pid, NULL, WNOHANG);
                        suspend_pid = -1; // Resetea el PID del proceso de suspensión.
                    }
                }
            } else if (ev.value == 0) { // Evento de liberación de tecla (key up).
                if (ev.code == KEY_S_CODE) {
                    if (s_press_start_time != 0) {
                        // Si la tecla 's' fue liberada antes de los 3 segundos, se suspende el sistema.
                        if ((time(NULL) - s_press_start_time) < 3) {
                            fprintf(stdout, "Tecla 's' pulsada brevemente. Entrando en modo de bajo consumo (suspensión)...\n");
                            fflush(stdout); // Asegura que el mensaje se muestre.
                            suspend_pid = fork(); // Crea un proceso hijo para ejecutar el comando de suspensión.
                            if (suspend_pid == 0) { // Proceso hijo
                                system("sudo systemctl suspend");
                                exit(EXIT_SUCCESS); // El hijo termina después de suspender.
                            } else if (suspend_pid > 0) { // Proceso padre
                                fprintf(stdout, "Sistema en suspensión. Presiona cualquier otra tecla para reanudar.\n");
                            } else {
                                perror("Error al hacer fork para suspender");
                            }
                        }
                        s_press_start_time = 0; // Reinicia el temporizador de 's'.
                    }
                }
            }
        }
    }

    // Cierra el descriptor de archivo del dispositivo de teclado al finalizar.
    close(fd);
    fprintf(stdout, "Programa 'keyboard_monitor' terminado.\n");
    return EXIT_SUCCESS;
}