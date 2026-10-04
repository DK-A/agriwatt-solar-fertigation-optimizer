/**
 * @file hydraulic_control.c
 * @brief Discrete-time PI controller implementation with anti-windup clamping
 */

#include "hydraulic_control.h"

#define KP_PRESSURE             0.045f   // Proportional gain
#define KI_PRESSURE             0.012f   // Integral gain
#define INTEGRAL_MAX            0.50f    // Anti-windup integral clamp
#define INTEGRAL_MIN           -0.50f
#define PRESSURE_SAFETY_MAX_PSI 50.0f    // Emergency over-pressure cutoff
#define CAVITATION_MIN_PSI      12.0f    // Dry run threshold
#define CAVITATION_MAX_SECONDS  3.5f     // Max seconds below threshold before trip

static hydraulic_telemetry_t s_h_telem = {0};
static float s_integral_err = 0.0f;
static float s_cavitation_timer_s = 0.0f;
static bool s_active = true;

void hydraulic_control_init(float target_pressure_psi) {
    s_h_telem.measured_psi = 0.0f;
    s_h_telem.target_psi = target_pressure_psi;
    s_h_telem.pump_pwm_duty = 0.0f;
    s_h_telem.motor_current_a = 0.0f;
    s_h_telem.is_cavitating = false;
    s_h_telem.overpressure_trip = false;
    s_integral_err = 0.0f;
    s_cavitation_timer_s = 0.0f;
    s_active = true;
}

float hydraulic_control_update(float current_pressure_psi, float motor_current_a) {
    if (!s_active) {
        s_h_telem.pump_pwm_duty = 0.0f;
        return 0.0f;
    }

    s_h_telem.measured_psi = current_pressure_psi;
    s_h_telem.motor_current_a = motor_current_a;

    // 1. Safety Check: Hard Over-Pressure Trip
    if (current_pressure_psi >= PRESSURE_SAFETY_MAX_PSI) {
        s_h_telem.overpressure_trip = true;
        s_h_telem.pump_pwm_duty = 0.0f;
        s_active = false;
        return 0.0f;
    }

    // 2. Safety Check: Cavitation / Dry-Run Detection
    // If motor is drawing nominal current but pressure stays < 12 PSI for > 3.5 seconds
    if (current_pressure_psi < CAVITATION_MIN_PSI && motor_current_a > 1.2f) {
        s_cavitation_timer_s += 0.001f; // 1 kHz tick = 1 ms
        if (s_cavitation_timer_s >= CAVITATION_MAX_SECONDS) {
            s_h_telem.is_cavitating = true;
            s_h_telem.pump_pwm_duty = 0.0f;
            s_active = false;
            return 0.0f;
        }
    } else {
        s_cavitation_timer_s = 0.0f;
    }

    // 3. Discrete PI Control Loop with Anti-Windup
    float error = s_h_telem.target_psi - current_pressure_psi;
    s_integral_err += error * 0.001f; // dt = 1 ms

    // Anti-windup clamping
    if (s_integral_err > INTEGRAL_MAX) s_integral_err = INTEGRAL_MAX;
    if (s_integral_err < INTEGRAL_MIN) s_integral_err = INTEGRAL_MIN;

    float output_duty = (KP_PRESSURE * error) + (KI_PRESSURE * s_integral_err);

    // Baseline bias for holding 40 PSI in steady-state (feedforward)
    output_duty += 0.45f;

    // Clamp duty cycle to safe bounds
    if (output_duty > 0.95f) output_duty = 0.95f;
    if (output_duty < 0.0f)  output_duty = 0.0f;

    s_h_telem.pump_pwm_duty = output_duty;
    return output_duty;
}

void hydraulic_control_set_target(float target_psi) {
    s_h_telem.target_psi = target_psi;
}

void hydraulic_control_get_telemetry(hydraulic_telemetry_t *out_telem) {
    if (out_telem) {
        *out_telem = s_h_telem;
    }
}

void hydraulic_control_emergency_stop(void) {
    s_active = false;
    s_h_telem.pump_pwm_duty = 0.0f;
}
