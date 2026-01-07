import joblib
import pandas as pd

rf_model = joblib.load("rf_motion_model.pkl")
scaler = joblib.load("scaler.pkl")

def predict_activity(ax, ay, az, gx, gy, gz):
   features = pd.DataFrame([[ax,ay,az,gx,gy,gz]], columns=["ax", "ay", "az", "gx", "gy", "gz"])
   scaled = scaler.transform(features)
   prediction = rf_model.predict(scaled)[0]

   if prediction == 6:
       return "Running"
   elif prediction in [4,5]:
       return "Stationary"
   else: 
       return "Walking"
   
   
def predict_condition(state, heartRate_stat):
     if heartRate_stat == None:
        return  "No valid heart rate!"
     elif state == "Walking":
          if 190 < heartRate_stat:
             return "High Heart Rate while Walking!"
          else:
               return "Normal"
     elif state == "Stationary":
          if 160 < heartRate_stat:
               return "High Heart Rate while not Moving!"
          else: 
               return "Normal"
     elif state == "Running":
          if 210 < heartRate_stat:
               return "High Heart Rate While Running!"
          return "Normal"
     else: 
          return "Normal"