from datetime import datetime

def load_sensor_data(form_data):
    """
    Extracts sensor data from the form data.
    Uses server timestamp if no timestamp is provided.
    Converts all values to proper numeric types.
    """
    return {
        "user_id": int(form_data.get("user_id", 0)),
        "username": form_data.get("username", 0),
        "ax": float(form_data.get("ax", 0)),
        "ay": float(form_data.get("ay", 0)),
        "az": float(form_data.get("az", 0)),
        "gx": float(form_data.get("gx", 0)),
        "gy": float(form_data.get("gy", 0)),
        "gz": float(form_data.get("gz", 0)),
        "heartRate": int(form_data.get("heartRate", 0)),
        "spo2": int(form_data.get("spo2", 0)),
        "timestamp": form_data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def validate_vital_signs(heartRate, spo2):
    """
    Validates vital signs.
    Returns None if the reading is invalid (0, 999, -999).
    """
    heartRate_stat = heartRate if heartRate not in [0, 999, -999] else None
    spo2_stat = spo2 if spo2 not in [0, 999, -999] else None
    return heartRate_stat, spo2_stat
