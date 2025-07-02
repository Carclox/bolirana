# Makefile en Driver/

# Nombres de los módulos de kernel
MODULE_NAMES := driver_gpio_teclado driver_gpio_teclado_polling

# Rutas relativas desde Driver/
SRC_DIR := src
OBJ_DIR := obj
BIN_DIR := bin

# Directorio de los headers del kernel
KDIR := /usr/src/linux-headers-$(shell uname -r)

# Regla 'all' para compilar todos los módulos
all: $(OBJ_DIR) $(BIN_DIR)
	@echo "--- Compilando los módulos del kernel desde Driver/ ---"
	@for module_name in $(MODULE_NAMES); do \
        echo "Compilando $$module_name..."; \
        $(MAKE) -C $(SRC_DIR) KDIR=$(KDIR) MODULE_NAME=$$module_name; \
        \
        echo "Moviendo archivos generados para $$module_name ---"; \
        if [ -f "$(SRC_DIR)/$$module_name.ko" ]; then \
           echo "Moviendo $$module_name.ko a $(BIN_DIR)/"; \
           mv "$(SRC_DIR)/$$module_name.ko" "$(BIN_DIR)/"; \
        else \
           echo "Advertencia: No se encontró $$module_name.ko en $(SRC_DIR)."; \
        fi; \
        \
        echo "Moviendo archivos .o, .mod.c, .cmd, Module.symvers, modules.order a $(OBJ_DIR)/$$module_name/"; \
        mkdir -p "$(OBJ_DIR)/$$module_name/"; \
        mv $(SRC_DIR)/$$module_name.o "$(OBJ_DIR)/$$module_name/" 2>/dev/null || true; \
        mv $(SRC_DIR)/$$module_name.mod.c "$(OBJ_DIR)/$$module_name/" 2>/dev/null || true; \
        mv $(SRC_DIR)/$$module_name.mod "$(OBJ_DIR)/$$module_name/" 2>/dev/null || true; \
        mv $(SRC_DIR)/$(MODULE_NAME)*.cmd "$(OBJ_DIR)/$$module_name/" 2>/dev/null || true; \
        mv $(SRC_DIR)/Module.symvers "$(OBJ_DIR)/$$module_name/" 2>/dev/null || true; \
        mv $(SRC_DIR)/modules.order "$(OBJ_DIR)/$$module_name/" 2>/dev/null || true; \
    done

	@echo "--- Compilación y movimiento completos ---"

# Reglas para crear los directorios si no existen
$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)
	@echo "Creado directorio: $(OBJ_DIR)"

$(BIN_DIR):
	mkdir -p $(BIN_DIR)
	@echo "Creado directorio: $(BIN_DIR)"

# Regla para limpiar los archivos de compilación
clean:
	@echo "--- Limpiando archivos de compilación desde Driver/ ---"
	@for module_name in $(MODULE_NAMES); do \
        echo "Limpiando $$module_name..."; \
        $(MAKE) -C $(SRC_DIR) clean MODULE_NAME=$$module_name; \
    done

    # Elimina los directorios de salida de forma recursiva
	@echo "Eliminando directorios de salida: $(OBJ_DIR) y $(BIN_DIR)"
	rm -rf $(OBJ_DIR)
	rm -rf $(BIN_DIR)

    # Además, elimina cualquier archivo .ko que pueda haber quedado en Driver/ (si no se movió bien)
	@echo "Eliminando cualquier .ko residual en el directorio actual."
	rm -f $(MODULE_NAMES:=.ko)

	@echo "--- Limpieza completa en Driver/ ---"

.PHONY: all clean