/**
 * @file hydraulic_control.h
 * @brief Closed-Loop Pressure Regulation (38-42 PSI) with Anti-Windup PI Controller
 * @target ESP32-S3 Core 0 (1 kHz loop)
 */

#ifndef HYDRAULIC_CONTROL_H
#define HYDRAULIC_CONTROL_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    float measured_psi;         // Real-time line pressure (PSI)
    float target_psi;           // Pressure setpoint (Nominal: 40.0 PSI)
    float pump_pwm_duty;        // Commanded pump motor PWM duty (0.0 to 1.0)
    float motor_current_a;      // Pump motor current draw (Amperes)
    bool is_cavitating;         // True if dry-run / cavitation is flagged
    bool overpressure_trip;     // True if line exceeds 50 PSI safety limit
} hydraulic_telemetry_t;

/**
 * @brief Initialize the hydraulic PI controller and MCPWM motor driver
 * @param target_pressure_psi Default setpoint (e.g. 40.0 PSI)
 */
void hydraulic_control_init(float target_pressure_psi);

/**
 * @brief Update the PI pressure loop (called at 1 kHz from hardware timer interrupt)
 * @param current_pressure_psi Measured line pressure from transducer (PSI)
 * @param motor_current_a Measured motor current (A)
 * @return float Commanded motor PWM duty cycle (0.0 to 1.0)
 */
float hydraulic_control_update(float current_pressure_psi, float motor_current_a);

/**
 * @brief Set the target pressure setpoint
 */
void hydraulic_control_set_target(float target_psi);

/**
 * @brief Get a snapshot of hydraulic metrics
 */
void hydraulic_control_get_telemetry(hydraulic_telemetry_t *out_telem);

/**
 * @brief Emergency shutdown of the pump motor
 */
void hydraulic_control_emergency_stop(void);

#ifdef __cplusplus
}
#endif

#endif // HYDRAULIC_CONTROL_H
