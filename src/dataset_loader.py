"""
AGRI-WATT Dataset Loader Module
Handles preprocessing, validation, normalization, and train/test splitting
for hydraulic pressure transient and microclimate solar datasets.
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

def load_pressure_clog_data(data_dir=None, test_size=0.2, random_state=42):
    """
    Loads pressure transient clog diagnostic dataset.
    Features: [p_initial_psi, p_peak_psi, tau_decay_ms, dp_dt_max, ripple_noise_psi]
    Target: diagnostic_label in {NORMAL, PARTIAL_CLOG, FULL_CLOG, CAVITATION_LEAK}
    """
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(__file__), "..", "datasets")
        
    csv_path = os.path.join(data_dir, "pressure_transient_clog_dataset.csv")
    df = pd.read_csv(csv_path)
    
    feature_cols = ['p_initial_psi', 'p_peak_psi', 'tau_decay_ms', 'dp_dt_max', 'ripple_noise_psi']
    X = df[feature_cols].values
    y_raw = df['diagnostic_label'].values
    
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    return {
        'X_train': X_train_scaled,
        'X_test': X_test_scaled,
        'y_train': y_train,
        'y_test': y_test,
        'scaler': scaler,
        'label_encoder': label_encoder,
        'feature_names': feature_cols,
        'classes': list(label_encoder.classes_)
    }

def load_microclimate_irrigation_data(data_dir=None, test_size=0.2, random_state=42):
    """
    Loads solar microclimate dataset for FAO-56 Penman-Monteith ET0 regression.
    Features: [temp_c, humidity_pct, solar_rad_wm2, wind_speed_ms, soil_moisture_pct, crop_kc]
    Target: et0_penman_monteith_mm_day
    """
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(__file__), "..", "datasets")
        
    csv_path = os.path.join(data_dir, "solar_microclimate_irrigation_dataset.csv")
    df = pd.read_csv(csv_path)
    
    feature_cols = ['temp_c', 'humidity_pct', 'solar_rad_wm2', 'wind_speed_ms', 'soil_moisture_pct', 'crop_kc']
    target_col = 'et0_penman_monteith_mm_day'
    
    X = df[feature_cols].values
    y = df[target_col].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    return {
        'X_train': X_train_scaled,
        'X_test': X_test_scaled,
        'y_train': y_train,
        'y_test': y_test,
        'scaler': scaler,
        'feature_names': feature_cols
    }
