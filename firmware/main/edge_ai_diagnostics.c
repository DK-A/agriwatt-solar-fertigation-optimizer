/**
 * @file edge_ai_diagnostics.c
 * @brief Implementation of Edge-AI Anomaly Detection and Evapotranspiration Estimation
 */

#include "edge_ai_diagnostics.h"
#include <math.h>

static ai_diagnostics_t s_ai_diag = {0};

void edge_ai_init(void) {
    s_ai_diag.clog_risk_score = 0;
    s_ai_diag.estimated_et0_mm_day = 4.5f; // Baseline nominal tropical rate
    s_ai_diag.recommended_pulse_ms = 15;
    s_ai_diag.leak_detected = false;
    s_ai_diag.purge_recommended = false;
}

uint8_t edge_ai_analyze_pressure_decay(const float *pressure_buffer) {
    if (!pressure_buffer) return 0;

    // Feature Extraction from high-speed pressure relaxation curve:
    // When the valve snaps shut, clean fluid experiences a steep negative pressure transient:
    // dP/dt = - (P_peak - P_base) / tau
    // If the 0.3 mm nozzle is partially clogged, relaxation time (tau) increases significantly.
    float p_initial = pressure_buffer[0];
    float p_final = pressure_buffer[63];
    float delta_p = p_initial - p_final;

    // Quantized classification heuristic:
    if (delta_p < 2.5f) {
        // Very shallow decay -> severe restriction / clogging
        s_ai_diag.clog_risk_score = 85;
        s_ai_diag.purge_recommended = true;
    } else if (delta_p < 5.0f) {
        // Moderate restriction
        s_ai_diag.clog_risk_score = 45;
        s_ai_diag.purge_recommended = false;
    } else {
        // Steep, clean relaxation -> nominal nozzle clearance
        s_ai_diag.clog_risk_score = 8;
        s_ai_diag.purge_recommended = false;
    }

    return s_ai_diag.clog_risk_score;
}

float edge_ai_compute_et0(float temp_c, float humidity_pct, float solar_lux) {
    // Hargreaves-Samani / Penman-Monteith empirical microclimate approximation:
    // Vapor Pressure Deficit (VPD):
    float e_sat = 0.6108f * expf((17.27f * temp_c) / (temp_c + 237.3f)); // kPa
    float e_act = e_sat * (humidity_pct / 100.0f);
    float vpd = e_sat - e_act; // kPa

    // Solar radiation proxy (Lux to MJ/m^2/day equivalent)
    float rad_proxy = (solar_lux / 100000.0f) * 25.0f; // Approx global solar MJ/m^2

    // Evapotranspiration Estimate (mm/day):
    float et0 = 0.0023f * (temp_c + 17.8f) * sqrtf(fmaxf(0.1f, vpd * 10.0f)) * (rad_proxy + 0.5f);

    // Clamp to realistic agricultural ranges (1.0 mm to 9.5 mm / day)
    if (et0 < 1.0f) et0 = 1.0f;
    if (et0 > 9.5f) et0 = 9.5f;

    s_ai_diag.estimated_et0_mm_day = et0;

    // Scale recommended pulse width proportionally to evapotranspiration
    s_ai_diag.recommended_pulse_ms = (uint16_t)(10.0f + (et0 * 2.2f));

    return et0;
}

void edge_ai_get_diagnostics(ai_diagnostics_t *out_diag) {
    if (out_diag) {
        *out_diag = s_ai_diag;
    }
}
