# Nombre del módulo de kernel
MODULE_NAME := driver_gpio_teclado
# directorios de recursos y objetivo
SRC_DIR := src
OBJ_DIR := obj


obj-m := $(OBJ_DIR)/$(MODULE_NAME).o

KDIR := /lib/modules/$(shell uname -r)/build

# Regla 'all' para compilar el módulo
all:
	@echo "Compilando el módulo del kernel..."
	# La bandera -C dirige a 'make' para que opere en el directorio KDIR
	# M=$(PWD) le dice a 'make' dónde buscar nuestros archivos fuente
	# modules es el objetivo para construir módulos
	$(MAKE) -C $(KDIR) M=$(PWD) modules

# Regla para limpiar los archivos de compilación
clean:
	@echo "Limpiando archivos de compilación..."
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	# Eliminar los directorios generados por el sistema de construcción si existen
	rm -rf $(OBJ_DIR)/*.o $(OBJ_DIR)/*.ko $(OBJ_DIR)/.tmp_versions \
	       $(OBJ_DIR)/*.mod.c $(OBJ_DIR)/*.symvers $(OBJ_DIR)/*.order
	@echo "Limpieza completada."

# Esto le indica a make que el directorio fuente y de objeto están anidados
# y cómo construir el .o dentro del OBJ_DIR
$(OBJ_DIR)/$(MODULE_NAME).o: $(SRC_DIR)/$(MODULE_NAME).c
	@mkdir -p $(OBJ_DIR) # Asegurarse de que el directorio obj exista
	$(MAKE) -C $(KDIR) M=$(PWD) \
	  $(addprefix $(OBJ_DIR)/, $(notdir $(MODULE_NAME).o))