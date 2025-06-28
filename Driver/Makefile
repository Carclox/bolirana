# Makefile en Driver/

# Nombre del módulo de kernel
MODULE_NAME := driver_gpio_teclado

# Rutas relativas desde Driver/
SRC_DIR := src
OBJ_DIR := obj
BIN_DIR := bin # Si quieres una carpeta para el .ko final, como el ejemplo anterior

# Directorio de los headers del kernel
KDIR := /usr/src/linux-headers-$(shell uname -r)
#KDIR := /lib/modules/linux-headers-$(shell uname -r)/build

# Regla 'all' para compilar el módulo
all: $(OBJ_DIR) $(BIN_DIR) # Asegúrate de que los directorios existan
	@echo "Compilando el módulo del kernel desde Driver/..."
    # Entra en el directorio SRC_DIR y ejecuta su Makefile
    # NO le pasamos OBJ_DIR_REL o PWD_ROOT al make de src, ya que queremos que compile en src/
	$(MAKE) -C $(SRC_DIR) KDIR=$(KDIR) MODULE_NAME=$(MODULE_NAME)

    # MOVER los archivos generados desde SRC_DIR a OBJ_DIR y BIN_DIR
	mv $(SRC_DIR)/*.ko $(BIN_DIR)/ 2>/dev/null || true
	mv $(SRC_DIR)/*.o $(OBJ_DIR)/ 2>/dev/null || true
	mv $(SRC_DIR)/*.mod.c $(OBJ_DIR)/ 2>/dev/null || true
	mv $(SRC_DIR)/*.cmd $(OBJ_DIR)/ 2>/dev/null || true
	mv $(SRC_DIR)/Module.symvers $(OBJ_DIR)/ 2>/dev/null || true
	mv $(SRC_DIR)/modules.order $(OBJ_DIR)/ 2>/dev/null || true
	@echo "Moviendo archivos del driver a sus directorios destino."


# Reglas para crear los directorios si no existen
$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

# Regla para limpiar los archivos de compilación
clean:
	@echo "Limpiando archivos de compilación desde Driver/..."
    # Limpia el directorio SRC_DIR (llama al clean de src/Makefile)
	$(MAKE) -C $(SRC_DIR) clean MODULE_NAME=$(MODULE_NAME)

    # Elimina los directorios de salida de forma recursiva
    # Esto eliminará los directorios obj/ y bin/ y todo su contenido
	rm -rf $(OBJ_DIR)
	rm -rf $(BIN_DIR)

    # Además, elimina cualquier archivo .ko que pueda haber quedado en Driver/ (si no se movió bien)
	rm -f $(MODULE_NAME).ko

	@echo "Limpieza completa en Driver/."


.PHONY: all clean