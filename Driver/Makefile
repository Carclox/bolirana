SRC_DIR := src
BIN_DIR := bin
OBJ_DIR := obj

all:
	@$(MAKE) -C $(SRC_DIR)
	@mkdir -p $(BIN_DIR) $(OBJ_DIR)
	@mv -v $(SRC_DIR)/driver_gpio_teclado.ko $(SRC_DIR)/driver_gpio_teclado.mod $(BIN_DIR)/
	@mv -v $(SRC_DIR)/driver_gpio_teclado.o $(SRC_DIR)/driver_gpio_teclado.mod.o $(OBJ_DIR)/

clean:
	@$(MAKE) -C $(SRC_DIR) clean
	@rm -rf $(BIN_DIR) $(OBJ_DIR)
