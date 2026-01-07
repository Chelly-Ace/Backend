# ml_predict.py
import os
import joblib
import pandas as pd

# -------------------- Paths --------------------
BASE_DIR = os.path.dirname(__file__)
RF_MODEL_PATH = os.path.join(BASE_DIR, "rf_motion_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")

# -------------------- Load Models --------------------
rf_model = joblib.load(RF_MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# -------------------- Prediction Functions --------------------
def predict_activity(ax, ay, az, gx, gy, gz):
    """
    Predicts activity based on sensor readings.
    Returns: 'Running', 'Stationary', or 'Walking'
    """
    features = pd.DataFrame(
        [[ax, ay, az, gx, gy, gz]],
        columns=["ax", "ay", "az", "gx", "gy", "gz"]
    )
    scaled = scaler.transform(features)
    prediction = rf_model.predict(scaled)[0]

    if prediction == 6:
        return "Running"
    elif prediction in [4, 5]:
        return "Stationary"
    else:
        return "Walking"

def predict_condition(state, heart_rate):
    """
    Predicts condition based on activity state and heart rate.
    Handles None values safely.
    Returns a string description.
    """
    if heart_rate is None:
        return "No valid heart rate!"

    if state == "Walking":
        return "High Heart Rate while Walking!" if heart_rate > 190 else "Normal"
    elif state == "Stationary":
        return "High Heart Rate while not Moving!" if heart_rate > 160 else "Normal"
    elif state == "Running":
        return "High Heart Rate While Running!" if heart_rate > 210 else "Normal"
    else:
        return "Normal"
