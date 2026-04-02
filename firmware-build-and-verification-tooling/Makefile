SHELL := /bin/bash
BOARD ?= demo-board
VERSION ?= 0.1.0
BUILD_DIR ?= build/$(BOARD)
CACHE_DIR ?= .cache/$(BOARD)
OBJ_DIR := $(BUILD_DIR)/obj
BIN_DIR := $(BUILD_DIR)/bin
SRC_DIR := src
INCLUDE_DIR := include
CFLAGS ?= -O2 -Wall -Wextra -Werror -std=c11 -I$(INCLUDE_DIR) -DFW_BOARD=\"$(BOARD)\" -DFW_VERSION=\"$(VERSION)\"
CC ?= gcc
OBJCOPY ?= objcopy
COMPONENTS := app bootloader

.PHONY: all clean package verify dirs

all: dirs $(BIN_DIR)/app.bin $(BIN_DIR)/bootloader.bin

dirs:
	@mkdir -p $(OBJ_DIR) $(BIN_DIR) $(CACHE_DIR)

$(OBJ_DIR)/app.o: $(SRC_DIR)/app/main.c $(INCLUDE_DIR)/common.h | dirs
	@$(CC) $(CFLAGS) -c $< -o $@

$(OBJ_DIR)/bootloader.o: $(SRC_DIR)/bootloader/main.c $(INCLUDE_DIR)/common.h | dirs
	@$(CC) $(CFLAGS) -c $< -o $@

$(BIN_DIR)/app.elf: $(OBJ_DIR)/app.o | dirs
	@$(CC) $< -o $@

$(BIN_DIR)/bootloader.elf: $(OBJ_DIR)/bootloader.o | dirs
	@$(CC) $< -o $@

$(BIN_DIR)/%.bin: $(BIN_DIR)/%.elf | dirs
	@$(OBJCOPY) -O binary $< $@

clean:
	@rm -rf build .cache dist
