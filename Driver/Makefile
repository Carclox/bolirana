# Nombre del módulo del kernel
MODULE_NAME := driver_gpio_teclado

# Ruta a los directorios de compilación del kernel (Kernel build directory)
# Asegúrate de que esta ruta sea correcta para tu Raspberry Pi Zero 2W.
# Puedes verificarla con 'uname -r' y luego buscar la ruta correspondiente
# en /lib/modules/$(uname -r)/build o similar.
KERNEL_DIR := /lib/modules/$(shell uname -r)/build

# Directorio de salida para los archivos .o
OBJ_DIR := obj

# Directorio de salida para el módulo .ko
BIN_DIR := bin

# Fuente del módulo (en el subdirectorio src)
SRC_DIR := src

.PHONY: all clean

all: directories $(SRC_DIR)
	@echo "Construcción completada. Módulo en $(BIN_DIR)/$(MODULE_NAME).ko"

directories:
	@mkdir -p $(OBJ_DIR)
	@mkdir -p $(BIN_DIR)

$(SRC_DIR):
	$(MAKE) -C $(SRC_DIR) \
	    KERNEL_DIR=$(KERNEL_DIR) \
	    MODULE_NAME=$(MODULE_NAME) \
	    OBJ_DIR=../$(OBJ_DIR) \
	    BIN_DIR=../$(BIN_DIR)

clean:
	@echo "Limpiando..."
	$(MAKE) -C $(SRC_DIR) clean \
	    KERNEL_DIR=$(KERNEL_DIR) \
	    MODULE_NAME=$(MODULE_NAME) \
	    OBJ_DIR=../$(OBJ_DIR) \
	    BIN_DIR=../$(BIN_DIR)
	@rm -rf $(OBJ_DIR)
	@rm -rf $(BIN_DIR)
	@rm -f modules.order Module.symvers
	@echo "Limpieza completa."