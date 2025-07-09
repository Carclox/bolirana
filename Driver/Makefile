obj-m := driver_gpio_teclado.o

KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

BIN_DIR := $(PWD)/bin
OBJ_DIR := $(PWD)/obj

all:
	@mkdir -p $(BIN_DIR) $(OBJ_DIR)
	$(MAKE) -C $(KDIR) M=$(PWD) modules
	@mv -v driver_gpio_teclado.ko driver_gpio_teclado.mod $(BIN_DIR)/
	@mv -v driver_gpio_teclado.o driver_gpio_teclado.mod.o $(OBJ_DIR)/

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	@rm -rf $(BIN_DIR) $(OBJ_DIR)