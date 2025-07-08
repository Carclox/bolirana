# Variables pasadas desde el Makefile principal
MODULE_NAME ?= driver_gpio_teclado
KERNEL_DIR  ?= /lib/modules/$(shell uname -r)/build
OBJ_DIR     ?= ../obj
BIN_DIR     ?= ../bin

# Archivos fuente del módulo
obj-m += $(MODULE_NAME).o

$(MODULE_NAME)-objs := $(OBJ_DIR)/driver_gpio_teclado.o

# Reglas de compilación para el módulo del kernel
all: $(MODULE_NAME).ko

$(MODULE_NAME).ko: $(OBJ_DIR)/driver_gpio_teclado.o
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) modules

$(OBJ_DIR)/driver_gpio_teclado.o: driver_gpio_teclado.c
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	@echo "Limpiando en src..."
	@rm -f *.o *.ko *.mod.c .*.cmd *.symvers modules.order
	@rm -rf .tmp_versions
	@echo "Limpieza de src completa."