/**
 * @file solenoid_driver.h
 * @brief High-Speed Peak-and-Hold Driver with Active Zener Flyback Demagnetization (<1.2 ms)
 * @target ESP32-S3 Hardware Timers (MCPWM Unit 1)
 */

#ifndef SOLENOID_DRIVER_H
#define SOLENOID_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    VALVE_STATE_OFF = 0,
    VALVE_STATE_PULL_IN,    // 100% duty cycle (3 ms)
    VALVE_STATE_HOLD,       // 30% duty cycle (calibrated duration)
    VALVE_STATE_DISCHARGING // Collapsing inductive flux via Active Zener
} valve_state_t;

typedef struct {
    uint32_t total_shots_fired;     // Lifetime injection cycle counter
    uint32_t total_fluid_ul;        // Integrated micro-liters delivered
    float last_decay_time_ms;       // Measured inductive collapse duration (ms)
    valve_state_t current_state;    // Real-time FSM state
} solenoid_telemetry_t;

/**
 * @brief Initialize the Peak-and-Hold hardware driver GPIOs and MCPWM timer
 */
void solenoid_driver_init(void);

/**
 * @brief Trigger an immediate precision micro-injection pulse
 * @param hold_duration_ms Duration of holding phase in milliseconds (e.g. 5 to 25 ms)
 */
void solenoid_driver_fire_pulse(uint32_t hold_duration_ms);

/**
 * @brief Get solenoid telemetry metrics
 */
void solenoid_driver_get_telemetry(solenoid_telemetry_t *out_telem);

/**
 * @brief Trigger clean water reverse purge cycle (clearing nozzles of debris)
 * @param duration_seconds Purge duration (default: 5 seconds)
 */
void solenoid_driver_reverse_purge(uint8_t duration_seconds);

#ifdef __cplusplus
}
#endif

#endif // SOLENOID_DRIVER_H
