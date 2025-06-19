# Makefile en Driver/src/

# Nombre del módulo de kernel (pasado desde el Makefile superior)
MODULE_NAME ?= driver_gpio_teclado

# Directorio de los headers del kernel (pasado desde el Makefile superior)
KDIR ?= /lib/modules/$(shell uname -r)/build
# PWD aquí será el directorio actual (Driver/src/)
PWD := $(shell pwd)

# Configuración para el Kbuild del kernel
# obj-m le dice al Kbuild qué módulo (.ko) construir.
# Aquí, simplemente nombramos el .o, Kbuild lo generará en PWD.
obj-m := $(MODULE_NAME).o

# Si tienes otros archivos .c en src/ que contribuyen a este módulo, los listarías aquí:
# $(MODULE_NAME)-objs := $(MODULE_NAME).o otro_archivo.o

all:
	@echo "Compilando el módulo del kernel desde Driver/src/..."
    # Llamamos al make del kernel. M=$(PWD) indica que Kbuild compile aquí (Driver/src/)
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	@echo "Limpiando archivos de compilación desde Driver/src/..."
	$(MAKE) -C $(KDIR) M=$(PWD) clean
    # Asegúrate de limpiar los archivos generados por kbuild en este directorio (driver/src/)
	rm -f *.o *.ko *.mod.c *.cmd *.symvers *.order
	@echo "Limpieza de Driver/src/ completada."

.PHONY: all clean