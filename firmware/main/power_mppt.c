/**
 * @file power_mppt.c
 * @brief Implementation of 10 kHz Incremental Conductance MPPT for ESP32-S3
 */

#include "power_mppt.h"
#include <math.h>

#define MPPT_PWM_FREQ_HZ        100000  // 100 kHz Synchronous Buck Switching
#define MPPT_VOLTAGE_EPSILON    0.05f   // 50 mV threshold for delta V
#define MPPT_DUTY_STEP_FAST     0.015f  // Fast step when far from MPP
#define MPPT_DUTY_STEP_FINE     0.003f  // Fine step near MPP
#define DUTY_MIN                0.05f
#define DUTY_MAX                0.92f

static mppt_telemetry_t s_telem = {0};
static float s_v_prev = 0.0f;
static float s_i_prev = 0.0f;
static float s_duty = 0.50f;
static float s_power_cap_w = 500.0f; // Max nominal PV power

void power_mppt_init(void) {
    s_telem.v_pv = 0.0f;
    s_telem.i_pv = 0.0f;
    s_telem.p_pv = 0.0f;
    s_telem.v_bus = 12.0f;
    s_telem.duty_cycle = s_duty;
    s_telem.is_throttled = false;
    s_v_prev = 0.0f;
    s_i_prev = 0.0f;
}

float power_mppt_update(float v_now, float i_now) {
    float delta_v = v_now - s_v_prev;
    float delta_i = i_now - s_i_prev;
    float p_now = v_now * i_now;

    s_telem.v_pv = v_now;
    s_telem.i_pv = i_now;
    s_telem.p_pv = p_now;

    // Check if external fluidic power cap is exceeded (cloud throttle active)
    if (p_now > s_power_cap_w) {
        s_duty -= MPPT_DUTY_STEP_FAST;
        s_telem.is_throttled = true;
    } else {
        s_telem.is_throttled = false;

        // Incremental Conductance Algorithm:
        // dP/dV = 0 <=> dI/dV = -I/V
        if (fabsf(delta_v) < MPPT_VOLTAGE_EPSILON) {
            // Delta V is near zero: check delta I
            if (delta_i > 0.01f) {
                s_duty += MPPT_DUTY_STEP_FINE; // Operating left of MPP
            } else if (delta_i < -0.01f) {
                s_duty -= MPPT_DUTY_STEP_FINE; // Operating right of MPP
            }
        } else {
            float inc_conductance = delta_i / delta_v;     // dI/dV
            float inst_conductance = - (i_now / v_now);    // -I/V

            float error = inc_conductance - inst_conductance;

            if (fabsf(error) < 0.02f) {
                // At Maximum Power Point: maintain duty cycle
            } else if (inc_conductance > inst_conductance) {
                // dP/dV > 0: Left of MPP -> Increase duty
                float step = (fabsf(error) > 0.1f) ? MPPT_DUTY_STEP_FAST : MPPT_DUTY_STEP_FINE;
                s_duty += step;
            } else {
                // dP/dV < 0: Right of MPP -> Decrease duty
                float step = (fabsf(error) > 0.1f) ? MPPT_DUTY_STEP_FAST : MPPT_DUTY_STEP_FINE;
                s_duty -= step;
            }
        }
    }

    // Clamp duty cycle to safe bounds
    if (s_duty > DUTY_MAX) s_duty = DUTY_MAX;
    if (s_duty < DUTY_MIN) s_duty = DUTY_MIN;

    s_telem.duty_cycle = s_duty;
    s_v_prev = v_now;
    s_i_prev = i_now;

    return s_duty;
}

void power_mppt_get_telemetry(mppt_telemetry_t *out_telem) {
    if (out_telem) {
        *out_telem = s_telem;
    }
}

void power_mppt_throttle_power(float target_power_limit_w) {
    s_power_cap_w = target_power_limit_w;
}
