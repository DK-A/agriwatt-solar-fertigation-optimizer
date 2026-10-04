"""
AGRI-WATT Python Inference Engine & Benchmark Suite
Provides unified inference APIs for both Edge-AI models:
- Clog diagnostic classifier
- Microclimate ET0 regressor
Benchmarks single-sample and batch prediction latencies.
"""

import os
import time
import joblib
import numpy as np

class AgriWattInferenceEngine:
    def __init__(self, models_dir=None):
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(__file__), "..", "models", "trained")
            
        self.clog_model = joblib.load(os.path.join(models_dir, "pressure_clog_classifier.joblib"))
        self.clog_scaler = joblib.load(os.path.join(models_dir, "clog_feature_scaler.joblib"))
        
        self.et0_model = joblib.load(os.path.join(models_dir, "et0_irrigation_regressor.joblib"))
        self.et0_scaler = joblib.load(os.path.join(models_dir, "et0_feature_scaler.joblib"))
        
        # Matches LabelEncoder alphabetical ordering:
        self.classes = ['CAVITATION_LEAK', 'FULL_CLOG', 'NORMAL', 'PARTIAL_CLOG']

    def diagnose_pressure_transient(self, p_initial, p_peak, tau_decay_ms, dp_dt_max, ripple_noise):
        """
        Diagnoses hydraulic condition from single pressure transient.
        Returns: diagnostic_state, confidence, probabilities
        """
        features = np.array([[p_initial, p_peak, tau_decay_ms, dp_dt_max, ripple_noise]])
        scaled = self.clog_scaler.transform(features)
        
        probs = self.clog_model.predict_proba(scaled)[0]
        pred_idx = np.argmax(probs)
        state = self.classes[pred_idx]
        confidence = probs[pred_idx]
        
        return {
            'state': state,
            'confidence': float(confidence),
            'probabilities': {cls: float(p) for cls, p in zip(self.classes, probs)}
        }

    def predict_et0_dosing(self, temp_c, humidity_pct, solar_rad_wm2, wind_speed_ms, soil_moisture_pct, crop_kc):
        """
        Predicts reference evapotranspiration (ET0) and recommended water dose.
        """
        features = np.array([[temp_c, humidity_pct, solar_rad_wm2, wind_speed_ms, soil_moisture_pct, crop_kc]])
        scaled = self.et0_scaler.transform(features)
        
        et0_pred = float(self.et0_model.predict(scaled)[0])
        
        # Calculate precision irrigation dose (Liters/day per plant zone)
        field_capacity = 36.0
        deficit = max(0.05, min(1.0, (field_capacity - soil_moisture_pct) / field_capacity))
        dose_liters = max(0.2, et0_pred * crop_kc * deficit * 2.8)
        
        return {
            'et0_mm_day': round(et0_pred, 2),
            'recommended_dose_liters': round(dose_liters, 2)
        }

def benchmark_latency():
    print("[*] Initializing AGRI-WATT Inference Engine Benchmark...")
    engine = AgriWattInferenceEngine()
    
    # Benchmark Clog Diagnostic
    n_iters = 1000
    t0 = time.perf_counter()
    for _ in range(n_iters):
        _ = engine.diagnose_pressure_transient(40.2, 44.5, 120.0, 35.8, 0.18)
    t_clog_ms = (time.perf_counter() - t0) / n_iters * 1000.0
    
    # Benchmark ET0 Regressor
    t0 = time.perf_counter()
    for _ in range(n_iters):
        _ = engine.predict_et0_dosing(32.5, 45.0, 850.0, 2.4, 22.0, 0.95)
    t_et0_ms = (time.perf_counter() - t0) / n_iters * 1000.0
    
    print(f"[BENCHMARK] Clog Diagnostic Inference Latency: {t_clog_ms:.3f} ms / prediction")
    print(f"[BENCHMARK] ET0 Dosing Inference Latency:       {t_et0_ms:.3f} ms / prediction")
    
    # Verification Sample
    res_normal = engine.diagnose_pressure_transient(40.0, 44.2, 115.0, 36.5, 0.20)
    print("\nSample Normal Prediction:", res_normal)
    
    res_clog = engine.diagnose_pressure_transient(47.5, 62.0, 680.0, 21.3, 0.28)
    print("Sample Clog Prediction:  ", res_clog)
    
    res_et0 = engine.predict_et0_dosing(36.0, 32.0, 920.0, 3.1, 18.0, 1.05)
    print("Sample ET0 Dosing:       ", res_et0)

if __name__ == '__main__':
    benchmark_latency()
