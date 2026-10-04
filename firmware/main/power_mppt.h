/**
 * @file power_mppt.h
 * @brief High-Speed Incremental Conductance MPPT & Synchronous Buck Power Stage
 * @target ESP32-S3 (Xtensa Dual-Core LX7)
 * @company Team TECHTONICS | Schneider Electric Yuva Yodha Hackathon
 */

#ifndef POWER_MPPT_H
#define POWER_MPPT_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    float v_pv;             // Instantaneous PV voltage (Volts)
    float i_pv;             // Instantaneous PV current (Amperes)
    float p_pv;             // Instantaneous PV power (Watts)
    float v_bus;            // Regulated output bus voltage (Volts)
    float duty_cycle;       // Synchronous Buck PWM duty cycle (0.0 to 1.0)
    bool is_throttled;      // True if dynamic fluidic throttling is active
} mppt_telemetry_t;

/**
 * @brief Initialize the Synchronous Buck MCPWM hardware and ADC DMA channels
 */
void power_mppt_init(void);

/**
 * @brief Execute one iteration of the 10 kHz Incremental Conductance MPPT algorithm
 * @param v_now Current measured panel voltage (V)
 * @param i_now Current measured panel current (A)
 * @return float Updated PWM duty cycle (0.0 to 0.95)
 */
float power_mppt_update(float v_now, float i_now);

/**
 * @brief Get the latest MPPT telemetry snapshot
 */
void power_mppt_get_telemetry(mppt_telemetry_t *out_telem);

/**
 * @brief Force dynamic power throttling when cloud cover is detected
 * @param target_power_limit_w Max power ceiling to enforce (Watts)
 */
void power_mppt_throttle_power(float target_power_limit_w);

#ifdef __cplusplus
}
#endif

#endif // POWER_MPPT_H
