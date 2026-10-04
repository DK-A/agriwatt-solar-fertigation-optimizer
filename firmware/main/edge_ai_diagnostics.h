/**
 * @file edge_ai_diagnostics.h
 * @brief Embedded Edge-AI Engine for Hydraulic Anomaly Detection & Microclimate ET
 * @target ESP32-S3 Core 1 (Xtensa PIE Vector Unit / ESP-NN)
 */

#ifndef EDGE_AI_DIAGNOSTICS_H
#define EDGE_AI_DIAGNOSTICS_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint8_t clog_risk_score;        // 0 (Clean) to 100 (Critical Clog)
    float estimated_et0_mm_day;     // Localized crop Evapotranspiration estimate
    uint16_t recommended_pulse_ms;  // AI-recommended pulse duration (ms)
    bool leak_detected;             // Flagged if line pressure decays without pulse
    bool purge_recommended;         // True if reverse purge cycle should be triggered
} ai_diagnostics_t;

/**
 * @brief Initialize Edge-AI model buffers and vector structures
 */
void edge_ai_init(void);

/**
 * @brief Run inference on high-frequency pressure decay curve
 * @param pressure_buffer Array of 64 consecutive 10 kHz pressure samples post-valve closure
 * @return uint8_t Clog risk score (0-100)
 */
uint8_t edge_ai_analyze_pressure_decay(const float *pressure_buffer);

/**
 * @brief Calculate microclimate crop evapotranspiration deficit
 * @param temp_c Ambient temperature (Celsius)
 * @param humidity_pct Relative humidity (%)
 * @param solar_lux Ambient solar illuminance (Lux)
 * @return float Calculated ET0 in mm/day
 */
float edge_ai_compute_et0(float temp_c, float humidity_pct, float solar_lux);

/**
 * @brief Get latest AI diagnostic outputs
 */
void edge_ai_get_diagnostics(ai_diagnostics_t *out_diag);

#ifdef __cplusplus
}
#endif

#endif // EDGE_AI_DIAGNOSTICS_H
