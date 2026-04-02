#include <stdint.h>
#include <stdio.h>
#include "common.h"

static const uint8_t boot_block[] = {
    0xBE, 0xEF, 0xCA, 0xFE, 0x05, 0x06, 0x07, 0x08,
    0x91, 0x92, 0x93, 0x94, 0xA1, 0xA2, 0xA3, 0xA4
};

uint32_t checksum32(const uint8_t *buf, uint32_t len) {
    uint32_t acc = 5381u;
    for (uint32_t i = 0; i < len; ++i) {
        acc = ((acc << 5u) + acc) ^ buf[i];
    }
    return acc;
}

const char *firmware_component_name(void) {
    return "bootloader";
}

int main(void) {
    uint32_t digest = checksum32(boot_block, (uint32_t) sizeof(boot_block));
    printf("component=%s\n", firmware_component_name());
    printf("board=%s\n", FW_BOARD);
    printf("version=%s\n", FW_VERSION);
    printf("digest=%u\n", digest);
    return FW_OK;
}
