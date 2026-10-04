"""
AGRI-WATT Edge-AI Model Training Suite
Trains:
1. Hydraulic Transient Pressure Clog Diagnostic Classifier (ESP-NN target)
2. FAO-56 Penman-Monteith Evapotranspiration Regressor (Irrigation dosing)
Generates evaluation metrics, parity plots, confusion matrices, and saved model weights.
"""

import os
import joblib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    r2_score, mean_absolute_error, mean_squared_error
)

from dataset_loader import load_pressure_clog_data, load_microclimate_irrigation_data

def train_clog_classifier(output_dir, eval_dir):
    print("\n" + "="*60)
    print(" [1/2] TRAINING HYDRAULIC TRANSIENT CLOG CLASSIFIER")
    print("="*60)
    
    data = load_pressure_clog_data()
    X_train, X_test = data['X_train'], data['X_test']
    y_train, y_test = data['y_train'], data['y_test']
    classes = data['classes']
    
    # Random Forest Ensemble for robust feature splitting
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    clf.fit(X_train, y_train)
    
    # Train lightweight MLP for direct ESP32-S3 C weight extraction
    mlp = MLPClassifier(hidden_layer_sizes=(16, 8), max_iter=500, random_state=42, activation='relu')
    mlp.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    mlp_pred = mlp.predict(X_test)
    
    rf_acc = accuracy_score(y_test, y_pred)
    mlp_acc = accuracy_score(y_test, mlp_pred)
    
    print(f"[METRIC] Random Forest Test Accuracy: {rf_acc * 100:.2f}%")
    print(f"[METRIC] Edge MLP Test Accuracy:         {mlp_acc * 100:.2f}%")
    print("\nDetailed Classification Report (Random Forest):")
    print(classification_report(y_test, y_pred, target_names=classes))
    
    # Save models
    rf_path = os.path.join(output_dir, "pressure_clog_classifier.joblib")
    mlp_path = os.path.join(output_dir, "edge_mlp_clog_classifier.joblib")
    scaler_path = os.path.join(output_dir, "clog_feature_scaler.joblib")
    
    joblib.dump(clf, rf_path)
    joblib.dump(mlp, mlp_path)
    joblib.dump(data['scaler'], scaler_path)
    print(f"[SAVED] Saved model to: {rf_path}")
    
    # Generate Confusion Matrix Figure
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    cax = ax.matshow(cm, cmap='Blues', alpha=0.85)
    fig.colorbar(cax)
    
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(x=j, y=i, s=str(cm[i, j]), va='center', ha='center', 
                    size=12, weight='bold', color='black' if cm[i, j] < cm.max()/2 else 'white')
            
    ax.set_xticks(range(len(classes)))
    ax.set_yticks(range(len(classes)))
    ax.set_xticklabels(classes, rotation=25, ha='left', weight='bold')
    ax.set_yticklabels(classes, weight='bold')
    ax.set_xlabel('Predicted Diagnostic State', weight='bold')
    ax.set_ylabel('Ground Truth Physical State', weight='bold')
    ax.set_title(f'AGRI-WATT Clog Classifier Confusion Matrix\nAccuracy: {rf_acc*100:.1f}%', weight='bold', pad=15)
    
    plt.tight_layout()
    cm_path = os.path.join(eval_dir, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"[SAVED] Confusion matrix plot saved: {cm_path}")
    
    return mlp, data['scaler']

def train_et0_regressor(output_dir, eval_dir):
    print("\n" + "="*60)
    print(" [2/2] TRAINING SOLAR MICROCLIMATE ET0 REGRESSOR")
    print("="*60)
    
    data = load_microclimate_irrigation_data()
    X_train, X_test = data['X_train'], data['X_test']
    y_train, y_test = data['y_train'], data['y_test']
    
    reg = HistGradientBoostingRegressor(max_iter=150, max_depth=6, random_state=42)
    reg.fit(X_train, y_train)
    
    # Lightweight MLP Regressor for micro-controller deployment
    mlp_reg = MLPRegressor(hidden_layer_sizes=(16, 8), max_iter=500, random_state=42, activation='relu')
    mlp_reg.fit(X_train, y_train)
    
    y_pred = reg.predict(X_test)
    mlp_pred = mlp_reg.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    mlp_r2 = r2_score(y_test, mlp_pred)
    mlp_mae = mean_absolute_error(y_test, mlp_pred)
    
    print(f"[METRIC] Gradient Boosting R^2 Score: {r2:.4f}")
    print(f"[METRIC] Mean Absolute Error (MAE):    {mae:.3f} mm/day")
    print(f"[METRIC] Root Mean Squared Error (RMSE): {rmse:.3f} mm/day")
    print(f"[METRIC] Edge MLP R^2 Score:          {mlp_r2:.4f} (MAE: {mlp_mae:.3f} mm/day)")
    
    # Save models
    reg_path = os.path.join(output_dir, "et0_irrigation_regressor.joblib")
    mlp_reg_path = os.path.join(output_dir, "edge_mlp_et0_regressor.joblib")
    scaler_path = os.path.join(output_dir, "et0_feature_scaler.joblib")
    
    joblib.dump(reg, reg_path)
    joblib.dump(mlp_reg, mlp_reg_path)
    joblib.dump(data['scaler'], scaler_path)
    print(f"[SAVED] Saved model to: {reg_path}")
    
    # Parity Plot
    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    ax.scatter(y_test, y_pred, alpha=0.4, color='#0072BD', edgecolors='none', s=25, label='Test Observations')
    min_val, max_val = min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], '--', color='#D95319', linewidth=2, label='Ideal Parity (1:1)')
    
    ax.set_xlabel('FAO-56 Penman-Monteith Ground Truth ET0 [mm/day]', weight='bold')
    ax.set_ylabel('Model Predicted ET0 [mm/day]', weight='bold')
    ax.set_title(f'AGRI-WATT ET0 Regressor Parity Plot\n$R^2 = {r2:.4f}$ | MAE = {mae:.3f} mm/day', weight='bold')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper left')
    
    plt.tight_layout()
    parity_path = os.path.join(eval_dir, "et0_regression_parity.png")
    plt.savefig(parity_path, dpi=300)
    plt.close()
    print(f"[SAVED] Parity plot saved: {parity_path}")
    
    return mlp_reg, data['scaler']

def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    output_dir = os.path.join(base_dir, "models", "trained")
    eval_dir = os.path.join(base_dir, "models", "evaluation")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(eval_dir, exist_ok=True)
    
    mlp_clog, scaler_clog = train_clog_classifier(output_dir, eval_dir)
    mlp_et0, scaler_et0 = train_et0_regressor(output_dir, eval_dir)
    
    print("\n" + "="*60)
    print(" ALL MODELS TRAINED AND VALIDATED SUCCESSFULLY!")
    print("="*60)

if __name__ == '__main__':
    main()
