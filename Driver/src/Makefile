# Variables pasadas desde el Makefile principal
MODULE_NAME ?= driver_gpio_teclado
KERNEL_DIR  ?= /lib/modules/$(shell uname -r)/build
# OBJ_DIR y BIN_DIR no son directamente necesarios en este Makefile
# porque el sistema de build del kernel los maneja.

# Archivos fuente del módulo
# 'obj-m' le dice al sistema de build del kernel que construya un módulo
obj-m += $(MODULE_NAME).o

# Los archivos C que forman el módulo.
# Aquí simplemente nombras el archivo fuente principal.
$(MODULE_NAME)-objs := driver_gpio_teclado.o # Asegúrate que este sea el nombre de tu archivo .c

# La regla 'all' para construir el módulo del kernel
# Esto le dice al sistema de build del kernel que compile y enlace tu módulo.
all:
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) modules

# Regla 'clean' para el módulo del kernel
clean:
	@echo "Limpiando en src..."
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) clean
	@echo "Limpieza de src completa."