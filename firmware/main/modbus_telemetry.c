/**
 * @file modbus_telemetry.c
 * @brief Implementation of Modbus-RTU Holding Registers for Schneider EcoStruxure
 */

#include "modbus_telemetry.h"

#define TOTAL_HOLDING_REGS  16

static uint16_t s_holding_registers[TOTAL_HOLDING_REGS] = {0};
static uint8_t s_slave_addr = 1;

void modbus_telemetry_init(uint8_t slave_address, uint32_t baud_rate) {
    s_slave_addr = slave_address;
    for (int i = 0; i < TOTAL_HOLDING_REGS; i++) {
        s_holding_registers[i] = 0;
    }
}

void modbus_telemetry_update_registers(float v_pv, float i_pv, float p_pv, 
                                       float pressure_psi, float pump_duty, 
                                       uint32_t water_liters, uint32_t energy_wh,
                                       uint8_t clog_score, uint16_t alarms) {
    s_holding_registers[REG_SOLAR_VOLTAGE_X10]  = (uint16_t)(v_pv * 10.0f);
    s_holding_registers[REG_SOLAR_CURRENT_X100] = (uint16_t)(i_pv * 100.0f);
    s_holding_registers[REG_SOLAR_POWER_W]      = (uint16_t)(p_pv);
    s_holding_registers[REG_LINE_PRESSURE_X10]  = (uint16_t)(pressure_psi * 10.0f);
    s_holding_registers[REG_PUMP_DUTY_PCT]      = (uint16_t)(pump_duty * 100.0f);
    s_holding_registers[REG_DAILY_WATER_L]      = (uint16_t)(water_liters & 0xFFFF);
    s_holding_registers[REG_DAILY_ENERGY_WH]    = (uint16_t)(energy_wh & 0xFFFF);
    s_holding_registers[REG_CLOG_RISK_INDEX]    = (uint16_t)(clog_score);
    s_holding_registers[REG_SYSTEM_ALARM_FLAGS] = alarms;
}

void modbus_telemetry_poll(void) {
    // In real hardware, parses incoming RS-485 byte stream via UART FIFO,
    // computes 16-bit CRC, and transmits response packet when slave address matches.
}
