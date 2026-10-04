"""
AGRI-WATT Physical Dataset Generator
Synthesizes physically grounded datasets based on hydraulic fluid dynamics
and FAO-56 Penman-Monteith solar microclimate equations for Edge-AI model training.
"""

import os
import numpy as np
import pandas as pd

def generate_datasets():
    datasets_dir = r"f:\HACKATHONS\vishwakarma\AGRI_WATT\datasets"
    os.makedirs(datasets_dir, exist_ok=True)
    np.random.seed(42)

    # -------------------------------------------------------------------------
    # 1. Hydraulic Pressure Relaxation & Orifice Clog Dataset
    # -------------------------------------------------------------------------
    print("[1/2] Generating Pressure Transient Clog Dataset (3,000 samples)...")
    n_clog = 3000
    classes = ['NORMAL', 'PARTIAL_CLOG', 'FULL_CLOG', 'CAVITATION_LEAK']
    class_probs = [0.45, 0.30, 0.15, 0.10]
    labels = np.random.choice(classes, size=n_clog, p=class_probs)

    p_initial = []
    p_peak = []
    tau_decay_ms = []
    dp_dt_max = []
    ripple_noise_psi = []
    orifice_diameter_mm = []

    for label in labels:
        if label == 'NORMAL':
            # Nominal 0.30 mm orifice, rapid pressure relaxation
            dia = np.random.normal(0.30, 0.02)
            p_init = np.random.normal(40.0, 1.2)
            p_pk = p_init + np.random.normal(4.5, 0.5)
            tau = np.random.normal(115.0, 12.0) # ms
            dp = (p_pk - p_init) / (tau * 1e-3)
            noise = np.random.uniform(0.1, 0.3)
        elif label == 'PARTIAL_CLOG':
            # Particulate restriction (0.15 - 0.22 mm)
            dia = np.random.uniform(0.14, 0.22)
            p_init = np.random.normal(43.5, 1.5)
            p_pk = p_init + np.random.normal(9.0, 1.0)
            tau = np.random.normal(275.0, 30.0) # prolonged decay
            dp = (p_pk - p_init) / (tau * 1e-3)
            noise = np.random.uniform(0.25, 0.55)
        elif label == 'FULL_CLOG':
            # Severe blockage (< 0.10 mm)
            dia = np.random.uniform(0.01, 0.09)
            p_init = np.random.normal(48.0, 2.0)
            p_pk = p_init + np.random.normal(15.5, 2.0)
            tau = np.random.normal(650.0, 80.0) # very sluggish decay
            dp = (p_pk - p_init) / (tau * 1e-3)
            noise = np.random.uniform(0.15, 0.40)
        else: # CAVITATION_LEAK
            # Line fracture or suction dry-run cavitation
            dia = np.random.uniform(0.35, 0.60)
            p_init = np.random.normal(26.0, 3.0)
            p_pk = p_init + np.random.normal(1.2, 0.4)
            tau = np.random.normal(45.0, 8.0) # instant collapse
            dp = (p_pk - p_init) / (tau * 1e-3)
            noise = np.random.uniform(0.85, 1.95) # severe acoustic pressure ripple

        orifice_diameter_mm.append(round(dia, 3))
        p_initial.append(round(p_init, 2))
        p_peak.append(round(p_pk, 2))
        tau_decay_ms.append(round(tau, 1))
        dp_dt_max.append(round(dp, 1))
        ripple_noise_psi.append(round(noise, 3))

    df_clog = pd.DataFrame({
        'p_initial_psi': p_initial,
        'p_peak_psi': p_peak,
        'tau_decay_ms': tau_decay_ms,
        'dp_dt_max': dp_dt_max,
        'ripple_noise_psi': ripple_noise_psi,
        'orifice_diameter_mm': orifice_diameter_mm,
        'diagnostic_label': labels
    })

    clog_csv = os.path.join(datasets_dir, "pressure_transient_clog_dataset.csv")
    df_clog.to_csv(clog_csv, index=False)
    print(f"[OK] Saved pressure transient dataset: {clog_csv} ({len(df_clog)} rows)")

    # -------------------------------------------------------------------------
    # 2. Solar Microclimate & FAO-56 Penman-Monteith Irrigation Dataset
    # -------------------------------------------------------------------------
    print("[2/2] Generating Solar Microclimate ET0 Dataset (5,000 samples)...")
    n_weather = 5000
    temp_c = np.random.uniform(18.0, 44.0, size=n_weather) # Semi-arid Indian climate
    humidity_pct = np.random.uniform(15.0, 85.0, size=n_weather)
    solar_rad_wm2 = np.random.uniform(200.0, 1050.0, size=n_weather)
    wind_speed_ms = np.random.uniform(0.5, 6.5, size=n_weather)
    soil_moisture_pct = np.random.uniform(12.0, 42.0, size=n_weather)
    kc_factor = np.random.uniform(0.65, 1.15, size=n_weather) # Crop coefficient (cotton/chilli)

    # Physical approximation of FAO-56 Penman-Monteith ET0 (mm/day)
    # ET0 = 0.408*Delta*(Rn - G) + gamma*(900/(T+273))*u2*(es - ea) / (Delta + gamma*(1 + 0.34*u2))
    # Empirical simplified form validated for semi-arid zones:
    rad_mj = solar_rad_wm2 * 0.0864 # Convert W/m2 to MJ/m2/day
    vpd_kpa = (1.0 - humidity_pct / 100.0) * 0.6108 * np.exp(17.27 * temp_c / (temp_c + 237.3))
    et0_mm = 0.0023 * (temp_c + 17.8) * np.sqrt(np.maximum(1.0, 45.0 - temp_c)) * (rad_mj * 0.408) + 0.35 * vpd_kpa * (1 + 0.54 * wind_speed_ms)
    et0_mm = np.clip(et0_mm, 1.5, 9.8) + np.random.normal(0, 0.15, size=n_weather)

    # Water dosing requirement per plant micro-zone (Liters/day)
    # Dose = Area * ET0 * Kc * (1 - SoilMoisture/FieldCapacity)
    field_capacity = 36.0
    moisture_deficit = np.clip((field_capacity - soil_moisture_pct) / field_capacity, 0.05, 1.0)
    dose_liters = np.clip(et0_mm * kc_factor * moisture_deficit * 2.8, 0.2, 12.0)

    df_weather = pd.DataFrame({
        'temp_c': np.round(temp_c, 1),
        'humidity_pct': np.round(humidity_pct, 1),
        'solar_rad_wm2': np.round(solar_rad_wm2, 1),
        'wind_speed_ms': np.round(wind_speed_ms, 2),
        'soil_moisture_pct': np.round(soil_moisture_pct, 1),
        'crop_kc': np.round(kc_factor, 2),
        'et0_penman_monteith_mm_day': np.round(et0_mm, 2),
        'recommended_water_dose_liters': np.round(dose_liters, 2)
    })

    weather_csv = os.path.join(datasets_dir, "solar_microclimate_irrigation_dataset.csv")
    df_weather.to_csv(weather_csv, index=False)
    print(f"[OK] Saved solar microclimate dataset: {weather_csv} ({len(df_weather)} rows)")

    return clog_csv, weather_csv

if __name__ == '__main__':
    generate_datasets()
