obj-m := gpio_keypad.o

KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

BIN_DIR := $(PWD)/bin
OBJ_DIR := $(PWD)/obj

all:
	@mkdir -p $(BIN_DIR) $(OBJ_DIR)
	$(MAKE) -C $(KDIR) M=$(PWD) modules
	@mv -v gpio_keypad.ko gpio_keypad.mod $(BIN_DIR)/
	@mv -v gpio_keypad.o gpio_keypad.mod.o $(OBJ_DIR)/

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	@rm -rf $(BIN_DIR) $(OBJ_DIR)