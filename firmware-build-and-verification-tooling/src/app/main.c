#include <stdint.h>
#include <stdio.h>
#include "common.h"

static const uint8_t sample_payload[] = {
    0x11, 0x42, 0xA5, 0x7D, 0x01, 0x02, 0x03, 0x04,
    0x55, 0x66, 0x77, 0x88, 0x10, 0x20, 0x30, 0x40
};

uint32_t checksum32(const uint8_t *buf, uint32_t len) {
    uint32_t acc = 0;
    for (uint32_t i = 0; i < len; ++i) {
        acc = (acc * 33u) ^ buf[i];
    }
    return acc;
}

const char *firmware_component_name(void) {
    return "application";
}

int main(void) {
    uint32_t digest = checksum32(sample_payload, (uint32_t) sizeof(sample_payload));
    printf("component=%s\n", firmware_component_name());
    printf("board=%s\n", FW_BOARD);
    printf("version=%s\n", FW_VERSION);
    printf("digest=%u\n", digest);
    return FW_OK;
}
