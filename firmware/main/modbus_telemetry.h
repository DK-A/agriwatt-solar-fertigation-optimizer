/**
 * @file modbus_telemetry.h
 * @brief Schneider Electric EcoStruxure Modbus-RTU over RS-485 Interface
 * @target ESP32-S3 Core 1 (UART 1)
 */

#ifndef MODBUS_TELEMETRY_H
#define MODBUS_TELEMETRY_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Schneider EcoStruxure Standard Holding Register Map (Base: 40001)
#define REG_SOLAR_VOLTAGE_X10   0   // Solar PV Voltage (Volts * 10)
#define REG_SOLAR_CURRENT_X100  1   // Solar PV Current (Amps * 100)
#define REG_SOLAR_POWER_W       2   // Instantaneous PV Power (Watts)
#define REG_LINE_PRESSURE_X10   3   // Line Pressure (PSI * 10)
#define REG_PUMP_DUTY_PCT       4   // Pump Motor PWM Duty (%)
#define REG_DAILY_WATER_L       5   // Daily Water Delivered (Liters)
#define REG_DAILY_ENERGY_WH     6   // Daily Solar Energy Consumed (Watt-hours)
#define REG_CLOG_RISK_INDEX     7   // Clog Risk Score (0-100)
#define REG_SYSTEM_ALARM_FLAGS  8   // Bitfield: [0: Cavitation, 1: Overpressure, 2: Clog]
#define REG_COMMAND_CONTROL     9   // R/W: 0=Stop, 1=Auto-Run, 2=Purge

/**
 * @brief Initialize the RS-485 UART peripheral and register space
 * @param slave_address Modbus slave address (1-247)
 * @param baud_rate Communication baud rate (e.g. 19200)
 */
void modbus_telemetry_init(uint8_t slave_address, uint32_t baud_rate);

/**
 * @brief Process incoming Modbus request packets and formulate response
 */
void modbus_telemetry_poll(void);

/**
 * @brief Update holding registers with latest telemetry values
 */
void modbus_telemetry_update_registers(float v_pv, float i_pv, float p_pv, 
                                       float pressure_psi, float pump_duty, 
                                       uint32_t water_liters, uint32_t energy_wh,
                                       uint8_t clog_score, uint16_t alarms);

#ifdef __cplusplus
}
#endif

#endif // MODBUS_TELEMETRY_H
