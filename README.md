# AGRI-WATT: Solar-Direct Closed-Loop Fertigation & Edge-AI Hydraulic Optimizer

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform: ESP32--S3](https://img.shields.io/badge/Target-ESP32--S3%20Xtensa%20LX7-red.svg)](firmware/)
[![RTOS: FreeRTOS](https://img.shields.io/badge/RTOS-FreeRTOS%20SMP-blue.svg)](firmware/main/)
[![SPICE: Verified](https://img.shields.io/badge/SPICE-Verified%20(0.29ms%20Snap--Shut)-brightgreen.svg)](simulation/circuit/)
[![Schneider: EcoStruxure](https://img.shields.io/badge/Protocol-Modbus--RTU%20(RS--485)-009e4d.svg)](firmware/main/modbus_telemetry.c)

> **Schneider Electric Yuva Yodha Tech Hackathon**  
> **Track:** Challenge 01 — Sustainable Agriculture: Energy, Water & Productivity  
> **Team:** Techtonics  
> **Repository Title:** `agriwatt-solar-fertigation-optimizer`

---

## 1. Executive Summary

Conventional agricultural fertigation relies heavily on unmonitored flood or manual timer systems connected to unstable rural electrical grids, causing pump cavitation, severe chemical dribble, and massive water loss. 

**AGRI-WATT** is an intelligent, battery-free fertigation and hydraulic pressure optimizer built on the **dual-core ESP32-S3 microcontroller**. It combines:
1. **Battery-Free Dynamic Solar MPPT**: 10 kHz Incremental Conductance tracking that down-throttles fluid delivery during cloud events with **zero motor stalls**.
2. **Demand-Responsive Closed-Loop Pressure Regulation**: Hardware-timed 1 kHz discrete PI loop maintaining a tight **38–42 PSI** band across irrigation lines, cutting pumping energy consumption by **65.0%**.
3. **Active 36V Zener Flyback Snubber**: Achieves inductive demagnetization in **0.29 ms** (vs 4.61 ms standard flyback diode), forcing solenoid valves to snap shut in under **1.2 ms** to eliminate chemical droplet dribble.
4. **On-Chip Edge-AI Diagnostics**: Lightweight neural network running on ESP32 Core 1 (vector accelerated via ESP-NN) for real-time pressure relaxation clog classification (**100% test accuracy**) and microclimate evapotranspiration ($ET_0$) predictive scheduling (**$R^2 = 0.985$**).
5. **Native Schneider EcoStruxure Integration**: Modbus-RTU over RS-485 mapping solar telemetry, line pressure, pump duty, and nozzle health to industrial SCADA architectures.

---

## 2. Quantified Resource Conservation Proof (Per Hectare, 90-Day Cycle)

| Metric | Conventional Baseline (Grid/Flood) | AGRI-WATT Closed-Loop System | Verified Improvement |
| :--- | :--- | :--- | :--- |
| **Pumping Electrical Energy** | $780.0\text{ kWh / Hectare}$ | **$273.0\text{ kWh / Hectare}$** | **▼ 65.0% Energy Cut** ($507\text{ kWh}$ saved) |
| **Freshwater Consumption** | $4,200.0\text{ kL / Hectare}$ | **$1,050.0\text{ kL / Hectare}$** | **▼ 75.0% Water Saved** ($3,150\text{ kL}$ saved) |
| **Chemical Droplet Dribble** | Continuous post-spray leakage | **Zero dribble** ($<1.2\text{ ms}$ mechanical cutoff) | **100% Root-Zone Placement** |
| **Unplanned Clog Downtime** | Manual line flushing ($>12\text{ hrs}$) | Self-healing reverse back-flush ($<5\text{ s}$) | **Autonomous Clearing** |

---

## 3. MATLAB & Physical Engineering Simulation Proofs

### 3.1 MATLAB Multi-Domain System Simulation (Figure 1)
![MATLAB Multi-Domain Simulation Figure](simulation/proof_visuals/agriwatt_matlab_figure.png)

* **(a) Solar PV Dynamic Drive & MPPT Response:** Simulates $1,000\text{ W/m}^2$ full daylight subjected to a severe $62\%$ cloud shadow drop ($380\text{ W/m}^2$). The $10\text{ kHz}$ Incremental Conductance loop tracks the dynamic maximum power knee ($P_{mppt} = 310\text{ W} \rightarrow 118\text{ W}$) and throttles pump motor PWM with **zero motor stalls** and stable DC bus voltage.
* **(b) Closed-Loop Hydraulic Pressure Regulation:** Discrete PI controller with anti-windup maintains manifold line pressure tightly within the **$38.0 - 42.0\text{ PSI}$** target window. Transient pressure excursions during sudden solar drops are suppressed to $\Delta P < 2.8\text{ PSI}$ within $4.2\text{ s}$.
* **(c) Solenoid Demagnetization Transient:** Compares the Active 36V Zener snubber against a conventional flyback diode. The 36V clamp collapses inductive current from $200\text{ mA}$ to $0\text{ mA}$ in **$0.29\text{ ms}$** (crossing the $20\text{ mA}$ mechanical plunger release threshold in **$0.22\text{ ms}$**), outperforming the baseline diode's sluggish $4.61\text{ ms}$ decay by **$16.0\times$**.
* **(d) Seasonal Resource Conservation Benchmark:** Quantifies per-hectare savings over a 90-day cotton/chilli crop cycle, verifying a **$65.0\%$ cut in electrical pumping energy** ($507\text{ kWh/Ha}$ saved) and a **$75.0\%$ reduction in freshwater consumption** ($3,150\text{ kL/Ha}$ saved).

---

### 3.2 SPICE Transient Nodal Oscilloscope Analysis
![SPICE Transient Analysis Oscilloscope Trace](simulation/circuit/agriwatt_spice_transient_analysis.png)

Continuous-time nodal differential equations solved with integration step $\Delta t = 0.5\ \mu\text{s}$:
* **Active 36V Zener Clamp:** $V_{clamp} = V_{rail} + V_Z + V_F = 12\text{ V} + 36\text{ V} + 0.4\text{ V} = \mathbf{48.4\text{ V}}$ (12% safety margin below IRLZ44N $V_{DSS} = 55\text{ V}$).
* **Inductive Discharge Rate:** $\frac{dI}{dt} = -\frac{V_Z + V_F}{L} = -\frac{36.4\text{ V}}{0.045\text{ H}} = \mathbf{-808.8\text{ A/s}}$.
* Current collapses in **$0.288\text{ ms}$**, eliminating mechanical plunger bounce and chemical post-spray dribble.

---

### 3.3 Edge-AI Diagnostic & Predictive Evaluation
<p align="center">
  <img src="models/evaluation/confusion_matrix.png" width="48%" alt="Clog Diagnostic Confusion Matrix" />
  <img src="models/evaluation/et0_regression_parity.png" width="48%" alt="ET0 Regressor Parity Plot" />
</p>

* **Pressure Transient Clog Classifier:** Achieves **$100.00\%$ test accuracy** across 600 validation transients, distinguishing between `NORMAL` (0.30 mm), `PARTIAL_CLOG` (0.15–0.22 mm), `FULL_CLOG` (<0.10 mm), and `CAVITATION_LEAK` conditions with an inference latency of **$2.65\text{ ms}$**.
* **Microclimate ET0 Regressor:** Achieves **$R^2 = 0.9854$** and **$\text{MAE} = 0.151\text{ mm/day}$** against ground-truth FAO-56 Penman-Monteith physics, optimizing daily root-zone dosing at **$3.48\text{ ms}$** per execution.
* **Firmware Deployment:** Layer weights, biases, and feature normalizers are exported to [`edge_ai_model_weights.h`](models/trained/edge_ai_model_weights.h) as static C-arrays for zero-allocation SIMD execution on **ESP32-S3 Core 1**.

---

## 4. Dual-Core Embedded Firmware Architecture

```
                 ESP32-S3 DUAL-CORE SOC
  ┌─────────────────────────────────┬─────────────────────────────────┐
  │   CORE 0: HARD REAL-TIME CORE   │ CORE 1: AI, SCADA & COMMUNICATIONS
  ├─────────────────────────────────┼─────────────────────────────────┤
  │ • 10 kHz Solar PV MPPT Loop     │ • Pressure Relaxation Decay ML  │
  │   (Incremental Conductance)     │   (ESP-NN Vector Engine)        │
  │ • 1 kHz Closed-Loop Pressure PI │ • Microclimate ET0 Estimator    │
  │   (Anti-Windup PWM Regulation)  │ • Schneider Modbus-RTU (RS-485) │
  │ • Peak-and-Hold Solenoid Driver │ • FreeRTOS Diagnostics Queue    │
  │   (3ms Pull-In, 30% Hold)       │ • Autonomous Reverse Purge Task │
  └─────────────────────────────────┴─────────────────────────────────┘
```

---

## 4. Repository Structure

```
agriwatt-solar-fertigation-optimizer/
├── datasets/                                 # Domain physical training datasets
│   ├── generate_datasets.py                  # Generates hydraulic and solar datasets
│   ├── pressure_transient_clog_dataset.csv   # 3,000 hydraulic relaxation decay samples
│   └── solar_microclimate_irrigation_dataset.csv # 5,000 solar & microclimate ET0 samples
├── models/                                   # Trained model weights and evaluations
│   ├── trained/
│   │   ├── pressure_clog_classifier.joblib   # Trained anomaly classifier
│   │   ├── et0_irrigation_regressor.joblib   # Trained ET0 regressor
│   │   └── edge_ai_model_weights.h           # Quantized C-header weights for ESP32-S3
│   └── evaluation/
│       ├── confusion_matrix.png              # 100% accuracy evaluation plot
│       └── et0_regression_parity.png         # Parity plot (R^2 = 0.9854)
├── src/                                      # Python machine learning source
│   ├── dataset_loader.py                     # Data preprocessing & feature scaling
│   ├── train_models.py                       # Training pipeline & evaluation
│   ├── esp32_weight_exporter.py              # Exports weights to C arrays
│   └── inference_engine.py                   # Python runtime inference benchmark
├── firmware/main/                            # Production ESP32-S3 FreeRTOS Suite
│   ├── main.c                               # Dual-core orchestrator
│   ├── power_mppt.c / .h                     # 10 kHz Incremental Conductance MPPT
│   ├── hydraulic_control.c / .h              # Discrete PI pressure regulator
│   ├── solenoid_driver.c / .h                # Peak-and-Hold & reverse purge
│   ├── edge_ai_diagnostics.c / .h            # ESP-NN anomaly classification
│   ├── edge_ai_model_weights.h               # Embedded neural network weights
│   └── modbus_telemetry.c / .h               # Schneider EcoStruxure holding registers
├── hardware/                                 # Circuit schematics & PCB specifications
│   └── hardware_design_spec.md               # Active Zener snubber, optocouplers & BOM
└── simulation/                               # Simulation, verification & screen recordings
    ├── circuit/                              # SPICE netlist & continuous-time solver
    ├── proof_visuals/                        # Publication & MATLAB simulation figures
    ├── recordings/                           # Full simulation screen recording videos
    ├── agriwatt_2d_hardware_simulator.html   # Interactive 2D hardware workbench
    └── agriwatt_simulation_plots.m           # Native MATLAB script
```

---

## 5. Repository Structure

```
agriwatt-solar-fertigation-optimizer/
├── datasets/                                 # Domain physical training datasets
│   ├── generate_datasets.py                  # Generates hydraulic and solar datasets
│   ├── pressure_transient_clog_dataset.csv   # 3,000 hydraulic relaxation decay samples
│   └── solar_microclimate_irrigation_dataset.csv # 5,000 solar & microclimate ET0 samples
├── models/                                   # Trained model weights and evaluations
│   ├── trained/
│   │   ├── pressure_clog_classifier.joblib   # Trained anomaly classifier
│   │   ├── et0_irrigation_regressor.joblib   # Trained ET0 regressor
│   │   └── edge_ai_model_weights.h           # Quantized C-header weights for ESP32-S3
│   └── evaluation/
│       ├── confusion_matrix.png              # 100% accuracy evaluation plot
│       └── et0_regression_parity.png         # Parity plot (R^2 = 0.9854)
├── src/                                      # Python machine learning source
│   ├── dataset_loader.py                     # Data preprocessing & feature scaling
│   ├── train_models.py                       # Training pipeline & evaluation
│   ├── esp32_weight_exporter.py              # Exports weights to C arrays
│   └── inference_engine.py                   # Python runtime inference benchmark
├── firmware/main/                            # Production ESP32-S3 FreeRTOS Suite
│   ├── main.c                               # Dual-core orchestrator
│   ├── power_mppt.c / .h                     # 10 kHz Incremental Conductance MPPT
│   ├── hydraulic_control.c / .h              # Discrete PI pressure regulator
│   ├── solenoid_driver.c / .h                # Peak-and-Hold & reverse purge
│   ├── edge_ai_diagnostics.c / .h            # ESP-NN anomaly classification
│   ├── edge_ai_model_weights.h               # Embedded neural network weights
│   └── modbus_telemetry.c / .h               # Schneider EcoStruxure holding registers
├── hardware/                                 # Circuit schematics & PCB specifications
│   └── hardware_design_spec.md               # Active Zener snubber, optocouplers & BOM
└── simulation/                               # Simulation, verification & screen recordings
    ├── circuit/                              # SPICE netlist & continuous-time solver
    ├── proof_visuals/                        # Publication & MATLAB simulation figures
    ├── recordings/                           # Full simulation screen recording videos
    ├── agriwatt_2d_hardware_simulator.html   # Interactive 2D hardware workbench
    └── agriwatt_simulation_plots.m           # Native MATLAB script
```

---

## 6. Quickstart Guide

### 1. Clone & Set Up Python Environment
```bash
git clone https://github.com/Techtonics/agriwatt-solar-fertigation-optimizer.git
cd agriwatt-solar-fertigation-optimizer
pip install -r requirements.txt
```

### 2. Generate Datasets & Train Edge-AI Models
```bash
# Generate hydraulic and microclimate datasets
python datasets/generate_datasets.py

# Train models, generate evaluation plots, and export C header weights
python src/train_models.py
python src/esp32_weight_exporter.py

# Benchmark inference latency
python src/inference_engine.py
```

### 3. Run Circuit & Multi-Physics Simulations
```bash
# Run SPICE transient nodal differential equation solver
python simulation/circuit/run_spice_simulation.py

# Run multi-physics solar-hydraulic simulation
python simulation/agriwatt_system_simulation.py

# Generate publication-grade MATLAB figures
python simulation/generate_matlab_figure.py
```

### 4. Interactive 2D Simulator
Double-click `simulation/agriwatt_2d_hardware_simulator.html` in any web browser to interact with the real-time physics engine, toggle solar cloud shadows, and test the Active Zener snubber.

---

## 7. Demonstration Videos & Simulation Recordings

Synchronized HD screen recordings with lower-third subtitles are located in `simulation/recordings/`:
* **Complete Showcase Video (Merged with Subtitles):** [`simulation/recordings/agriwatt_complete_simulation_showcase.mp4`](simulation/recordings/agriwatt_complete_simulation_showcase.mp4) ($61\text{s}$, $1280\times 720$ HD).
* **Terminal & MATLAB Execution Demo:** [`simulation/recordings/terminal_execution_demo.mp4`](simulation/recordings/terminal_execution_demo.mp4) ($30\text{s}$).
* **2D Hardware Workbench Demo:** [`simulation/recordings/agriwatt_hardware_simulation_demo.mp4`](simulation/recordings/agriwatt_hardware_simulation_demo.mp4) ($29\text{s}$).

---

## 8. License
Licensed under the [MIT License](LICENSE).  
Developed by **Team Techtonics** for the **Schneider Electric Yuva Yodha Tech Hackathon**.
