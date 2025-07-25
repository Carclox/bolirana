## ⚙️ Servicios del sistema (systemd)

A continuación se describen los pasos para configurar tres servicios `systemd` que automatizan la carga del módulo del teclado GPIO, la ejecución del monitor de entradas, y el inicio del juego arcade al arrancar la Raspberry Pi.

---

### 🔧 Servicio: `driver_init.service`

Este servicio carga el módulo del kernel `driver_gpio_teclado.ko` al iniciar el sistema.

#### 📥 Instalación

1. Copiar el módulo compilado a una ubicación estándar del sistema:

```bash
sudo cp /ruta_al_proyecto/bolirana/Driver/obj/driver_gpio_teclado.ko /usr/local/bin/


###  driver_init.service
importante copiar este script desde su ubicacion en la carpeta services
```bash
sudo cp /etc/systemd/system/driver_init.service
```

O desde la carpeta de usuario
```bash
sudo cp /ruta_al_proyecto/bolirana/Driver/obj/driver_gpio_teclado.ko /usr/local/bin/
```
habilitar el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable driver_init.service
```

para probar que el servicio funciona correctamente sin tener que reiniciar la raspberry
```bash
sudo systemctl start driver_init.service
```


### keyboard_monitor.service

compilar el script si estas en la carpeta raiz del proyecto
```bash
cd ./services/scripts/
gcc keyboard_monitor.c -o keyboard_monitor
```

copiar el ejecutable desde scripts hacia ```/bin``` del sistema  lo ideal es que los ejecutables asociados a los servicios esten en la carpeta. /usr/local/bin
```bash
sudo cp services/scripts/keyboard_monitor /usr/local/bin/
```
copiar el script del servicio desde su ubicacion en la carpeta services
```bash
sudo cp /etc/systemd/system/keyboard_monitor.service
```
habilitar el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable keyboard_monitor.service
```

### arcade_game.service
copiar el archivo a:
```bash
sudo cp /home/pi/bolirana/services/game_init.service /etc/systemd/system/arcade_game.service
```
reiniciar daemon y habilitar el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable arcade_game.service
sudo systemctl start arcade_game.service 
```