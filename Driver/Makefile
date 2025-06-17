# Nombre del módulo de kernel
MODULE_NAME := driver_gpio_teclado

SRC_DIR := src
OBJ_DIR := obj


obj-m := $(MODULE_NAME).o

$(MODULE_NAME)-objs := $(SRC_DIR)/$(MODULE_NAME).o

# Directorio de los headers del kernel
KDIR := /lib/modules/$(shell uname -r)/build

# Regla 'all' para compilar el módulo
all:
	@echo "Compilando el módulo del kernel..."

	$(MAKE) -C $(KDIR) M=$(PWD) modules

# Regla para limpiar los archivos de compilación
clean:
	@echo "Limpiando archivos de compilación..."
	$(MAKE) -C $(KDIR) M=$(PWD) clean

	rm -f *.o *.ko *.mod.c *.symvers *.order *.markers
	rm -rf .tmp_versions
	@echo "Limpieza completada."

.PHONY: all clean