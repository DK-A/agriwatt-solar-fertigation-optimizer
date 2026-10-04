/**
 * @file main.c
 * @brief AGRI-WATT System Main Orchestrator for ESP32-S3 Dual-Core FreeRTOS
 * @company Team TECHTONICS | Schneider Electric Yuva Yodha Tech Hackathon
 */

#include <stdio.h>
#include "power_mppt.h"
#include "hydraulic_control.h"
#include "solenoid_driver.h"
#include "edge_ai_diagnostics.h"
#include "modbus_telemetry.h"

// FreeRTOS task handles
static void task_core0_power_hydraulics(void *pvParameters);
static void task_core1_analytics_comm(void *pvParameters);

void app_main(void) {
    printf("=================================================================\n");
    printf("  AGRI-WATT: Solar-Direct Closed-Loop Fertigation & Energy Manager\n");
    printf("  Target: ESP32-S3 (Xtensa Dual-Core 240 MHz) | FreeRTOS Pinned Cores\n");
    printf("=================================================================\n");

    // Initialize Subsystems
    power_mppt_init();
    hydraulic_control_init(40.0f); // 40.0 PSI default target
    solenoid_driver_init();
    edge_ai_init();
    modbus_telemetry_init(1, 19200);

    // Run clean-water reverse purge cycle on startup
    printf("[SYS] Performing startup 5-second clean-water reverse purge...\n");
    solenoid_driver_reverse_purge(5);

    // Spawn Core 0 Task: Hard Real-Time Power Conversion & Hydraulic PI (Pinned to Core 0)
    // xTaskCreatePinnedToCore(task_core0_power_hydraulics, "PowerHydraulics", 4096, NULL, 5, NULL, 0);

    // Spawn Core 1 Task: Edge-AI Inference & Modbus Telemetry (Pinned to Core 1)
    // xTaskCreatePinnedToCore(task_core1_analytics_comm, "AnalyticsComm", 4096, NULL, 1, NULL, 1);

    printf("[SYS] Subsystems active. Entering closed-loop operational state.\n");
}

static void task_core0_power_hydraulics(void *pvParameters) {
    while (1) {
        // Simulated 1 kHz execution loop
        // 1. Sample transducers (V_pv, I_pv, Line Pressure) via ADC DMA
        float simulated_v_pv = 32.4f;
        float simulated_i_pv = 8.6f;
        float simulated_pressure = 40.1f;
        float simulated_motor_curr = 2.1f;

        // 2. Update Incremental Conductance MPPT loop
        power_mppt_update(simulated_v_pv, simulated_i_pv);

        // 3. Update Hydraulic PI control loop (38-42 PSI)
        hydraulic_control_update(simulated_pressure, simulated_motor_curr);

        // 4. Trigger high-speed micro-injection pulses at configured intervals
        // solenoid_driver_fire_pulse(15); // 15 ms pulse

        // vTaskDelay(pdMS_TO_TICKS(1)); // 1 ms tick
    }
}

static void task_core1_analytics_comm(void *pvParameters) {
    while (1) {
        // 1. Process Modbus-RTU over RS-485 requests
        modbus_telemetry_poll();

        // 2. Run Edge-AI microclimate evapotranspiration calculation (every 10 seconds)
        edge_ai_compute_et0(34.5f, 45.0f, 85000.0f);

        // vTaskDelay(pdMS_TO_TICKS(100)); // 100 ms tick
    }
}
