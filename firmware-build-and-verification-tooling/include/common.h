#ifndef COMMON_H
#define COMMON_H

#include <stdint.h>

#define FW_OK 0
#define FW_ERR 1

#ifndef FW_VERSION
#define FW_VERSION "0.1.0"
#endif

#ifndef FW_BOARD
#define FW_BOARD "demo-board"
#endif

uint32_t checksum32(const uint8_t *buf, uint32_t len);
const char *firmware_component_name(void);

#endif
