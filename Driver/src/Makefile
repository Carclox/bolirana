# Makefile en Driver/src/

# Nombre del módulo de kernel (pasado desde el Makefile superior)
MODULE_NAME ?= driver_gpio_teclado
# Valor por defecto si se llama directamente

# Directorio de los headers del kernel
KDIR ?= /usr/src/linux-headers-$(shell uname -r)
PWD := $(shell pwd)

# Configuración para el Kbuild del kernel
# obj-m le dice al Kbuild qué módulo (.ko) construir.
obj-m := $$module_name.o

# Si el módulo principal depende de otros archivos .c en src/, se listarían aquí:
# Por ejemplo:
# $$module_name-objs := $$module_name.o otro_archivo_asociado.o

all:
	@echo "Compilando el módulo '$$module_name' desde Driver/src/..."
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	@echo "Limpiando archivos de compilación para '$$module_name' desde Driver/src/..."
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	# Asegúrate de limpiar solo los archivos generados por kbuild para este módulo específico
	rm -f $$module_name.o $$module_name.ko $$module_name.mod.c $$module_name.mod *.cmd Module.symvers modules.order
	@echo "Limpieza de Driver/src/ para '$$module_name' completada."

.PHONY: all clean