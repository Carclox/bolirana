
# Notas

## requerimientos
**Headers**
Es necesario tener instalados en la tarjeta los headers del nucleo para que la compilacion funcione.
```bash
sudo apt update
sudo apt install raspberrypi-kernel-headers
```
**Compilar el modulo**
Navega hasta el directorio raiz del driver, donde esta ubucado el archivo makefile y ejecuta:
```bash
make
```

utiliza: ```make all``` para compilar el driver, ```make clean``` para limpiar archivos de compilacion anteriores


**Cargar el modulo**
Una vez hayas generado el archivo ```driver_gpio_teclado.ko``` ejecuta en bash desde la carpeta raiz del driver:
```bash
sudo insmod obj/driver_gpio_teclado.ko
```
***Descargar el modulo***
Desde la carpeta raiz del driver ejecuta:
```bash
sudo rmmod driver_gpio_teclado
```

***probar modulo***
```bash
sudo evtest
```
esto mostrara eventos de presion y liberacion de teclado estandar cuando presiones un  boton.

# Descripcion del Modulo
