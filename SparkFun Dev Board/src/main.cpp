#include <Arduino.h>
#include <c2.h>
#include <stdlib.h>   // For strtol()
#include <stdio.h>    // For sprintf()

#define BAUD_RATE   (115200)
#define C2_NO_COMMAND  (0xff)
#define C2_INIT  ('i')
#define C2_RESET  ('r')
#define C2_ERASE_DEVICE  ('e')
#define C2_PAGE_WRITE  ('p')
#define C2_PAGE_READ  ('P')
#define C2_BYTE_WRITE  ('b')
#define C2_BYTE_READ  ('B')
#define C2_GET_DEVICE_ID  ('?')
#define C2_ACK  ('*')
#define C2_NACK  ('?')

#define HEX_REC_TYPE_DATA  (0x00)
#define HEX_REC_TYPE_EOF  (0x01)
#define HEX_REC_TYPE_EXTENDED_SEGMENT_ADDRESS  (0x02)
#define HEX_REC_TYPE_START_SEGMENT_ADDRESS  (0x03)
#define HEX_REC_TYPE_EXTENDED_LINEAR_ADDRESS  (0x04)
#define HEX_REC_TYPE_START_LINEAR_ADDRESS  (0x05)
#define HEX_REC_TYPE_READ  (0x80)
#define HEX_REC_TYPE_ERASE  (0x81)

const uint8_t led_pin = 13;

struct c2_command_t {
  uint16_t data_size;
  uint16_t address;
  uint8_t command;
  uint8_t data[256];
  uint8_t checksum;
};

c2_command_t c2_command;
static uint8_t c2_pi_state = 0;

void print_hex(uint16_t value, uint8_t digits);
void print_intel_hex(uint8_t record_type);
uint8_t hex2bin(uint8_t value);
void dump(uint8_t *p_data, uint16_t data_size);
void set_c2_pi_state(uint8_t value);
uint8_t get_c2_pi_state(void);
void acknowledge(void);
void execute_c2_command(uint8_t cmd, uint8_t ack);
uint8_t hex_state_machine(uint8_t value);
void test(void);
void setup(void);
void loop(void);
char nibble2hex(uint8_t nibble);

// Implementation of functions...
// Convert a 4-bit value (0-15) to a hex character
char nibble2hex(uint8_t nibble) {
  return (nibble < 10) ? ('0' + nibble) : ('A' + (nibble - 10));
}

// Print a uint16_t in hex with a fixed number of digits
void print_hex(uint16_t value, uint8_t digits) {
  // Ensure digits is between 1 and 4 (since uint16_t has max 4 hex digits)
  digits = (digits > 4) ? 4 : digits;

  uint8_t offset = 4 * (digits - 1);
  while (digits != 0) {
    uint8_t nibble = (value >> offset) & 0xF;
    Serial.print(nibble2hex(nibble));
    offset -= 4;
    digits--;
  }
}

void print_intel_hex(uint8_t record_type) {
  uint8_t checksum = 0;
  Serial.print(':');
  checksum += c2_command.data_size;
  print_hex(c2_command.data_size, 2);
  checksum += (c2_command.address >> 8) & 0xff;
  checksum += c2_command.address & 0xff;
  print_hex(c2_command.address, 4);
  checksum += record_type;
  print_hex(record_type, 2);
  for (int i = 0; i < c2_command.data_size; i++) {
    checksum += c2_command.data[i];
    print_hex(c2_command.data[i], 2);
  }
  print_hex(-1 * checksum, 2);
  Serial.println();
}

uint8_t hex2bin(uint8_t value) {
  if (value >= '0' && value <= '9') return value - '0';
  else if (value >= 'A' && value <= 'F') return value - 'A' + 10;
  else if (value >= 'a' && value <= 'f') return value - 'a' + 10;
  return 0;
}

void dump(uint8_t *p_data, uint16_t data_size) {
  for (int i = 0; i < data_size; i += 16) {
    for (int j = 0; j < 16; j++) {
      print_hex(p_data[i + j], 2);
    }
    Serial.println();
  }
}

void set_c2_pi_state(uint8_t value) {
  c2_pi_state = value;
  digitalWrite(led_pin, c2_pi_state);
}

uint8_t get_c2_pi_state(void) {
  return c2_pi_state;
}

void acknowledge(void) {
  Serial.print(C2_ACK);
  delay(2);
}

void execute_c2_command(uint8_t cmd, uint8_t ack) {
  switch (cmd) {
    case C2_INIT:
      c2_init_programming_interface();
      set_c2_pi_state(1);
      if (ack != 0) acknowledge();
      break;
    case C2_RESET:
      c2_reset();
      C2_CK_INPUT;
      C2_D_INPUT;
      set_c2_pi_state(0);
      if (ack != 0) acknowledge();
      break;
    case C2_GET_DEVICE_ID:
      print_hex(c2_read_sfr(0), 2);
      print_hex(c2_read_sfr(1), 2);
      if (ack != 0) acknowledge();
      break;
    case C2_ERASE_DEVICE:
      c2_erase_device();
      if (ack != 0) acknowledge();
      break;
    case C2_PAGE_WRITE:
      c2_write_flash_block(c2_command.address, c2_command.data, c2_command.data_size);
      if (ack != 0) acknowledge();
      break;
    case C2_PAGE_READ:
      if (ack != 0) acknowledge();
      c2_read_flash_block(c2_command.address, c2_command.data, c2_command.data_size);
      print_intel_hex(HEX_REC_TYPE_DATA);
      break;
    default:
      Serial.println(C2_NACK);
  }
}

// Hex record parsing state machine
uint8_t hex_state_machine(uint8_t value) {
  static uint8_t state = 0;
  static uint8_t byte_count = 0;
  static uint8_t checksum = 0;
  static uint8_t temp_byte = 0;

  switch(state) {
    case 0: // Waiting for start character
      if(value == ':') {
        state = 1;
        byte_count = 0;
        checksum = 0;
        memset(&c2_command, 0, sizeof(c2_command));
      }
      break;

    case 1: // Reading byte count (2 chars)
      if(++byte_count == 2) {
        c2_command.data_size = (temp_byte << 4) | hex2bin(value);
        checksum += c2_command.data_size;
        state = 2;
        byte_count = 0;
      } else {
        temp_byte = hex2bin(value);
      }
      break;

    case 2: // Reading address (4 chars)
      if(++byte_count == 4) {
        c2_command.address = (c2_command.address << 4) | hex2bin(value);
        checksum += (c2_command.address >> 8);
        checksum += (c2_command.address & 0xFF);
        state = 3;
        byte_count = 0;
      } else {
        c2_command.address = (c2_command.address << 4) | hex2bin(value);
      }
      break;

    case 3: // Reading record type (2 chars)
      if(++byte_count == 2) {
        c2_command.command = (temp_byte << 4) | hex2bin(value);
        checksum += c2_command.command;
        state = 4;
        byte_count = 0;
      } else {
        temp_byte = hex2bin(value);
      }
      break;

    case 4: // Reading data (2n chars)
      if(++byte_count == (c2_command.data_size * 2)) {
        state = 5;
        byte_count = 0;
      }
      // Handle data assembly here
      break;

    case 5: // Reading checksum (2 chars)
      if(++byte_count == 2) {
        // Verify checksum
        uint8_t calculated = (~checksum + 1) & 0xFF;
        uint8_t received = (temp_byte << 4) | hex2bin(value);
        state = 0;
        return (calculated == received) ? c2_command.command : C2_NACK;
      } else {
        temp_byte = hex2bin(value);
      }
      break;
  }
  
  return C2_NO_COMMAND;
}

void setup(void) {
  C2_CK_INPUT;
  C2_D_INPUT;
  pinMode(led_pin, OUTPUT);
  Serial.begin(9600);
  Serial.println("C2 programmer ready...");
  set_c2_pi_state(0);
  delay(300);
}

void loop(void) {
  if (Serial.available()) {
    uint8_t ch = Serial.read();
    uint8_t hex_cmd = hex_state_machine(ch);
    if (hex_cmd != C2_NO_COMMAND) {
      execute_c2_command(hex_cmd, 1);
    }
  }
}
