from fastapi import FastAPI, Request, Form
from database import get_connection_cursor
from datetime import datetime, timedelta, timezone
import mysql.connector
from ml_models import rf_model, scaler, predict_activity, predict_condition
from sensors_data import load_sensor_data, validate_vital_signs
from compute_and_push import summary_compute, push_summary_db
from print_logs import print_sensor_log
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()


origins = [
    "http://localhost:5173",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

last_registered_user = {"user_id": None, "username": None}
latest_sensor_payload = None

def safe_int(value, default=0):
    if value is None:
        return default
    try:
        return int(float(value))  # converts decimal, string, float safely
    except (ValueError, TypeError):
        return default


    
def get_or_create_user(username: str):
  
    user_id = None
    is_new_user = False

    try:
        with get_connection_cursor(dictionary=False) as cursor:

            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
            row = cursor.fetchone()

            if row:
                user_id = row["id"]
                is_new_user = False  # Existing user
            else:
                # Create new user
                cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))

                user_id = cursor.lastrowid
                is_new_user = True  # New user

    except mysql.connector.Error as e:
        print("Database error in get_or_create_user:", e)

        user_id = None
        is_new_user = False

    return user_id, is_new_user


@app.get("/")
def home():
    return {"message": "IOT Dashboard Backend is running!"}

@app.post("/register_user")
async def register_user(username: str = Form(...)):
    username = username.strip()
    if not username:
        return {"status": "error", "message": "Username required!"}

    user_id, is_new_user = get_or_create_user(username)

    if is_new_user:
        message = f"Welcome, {username}! Your account has been created."
    else:
        message = f"Welcome back {username}!"

    if not user_id:
        return {"status": "error", "message": "Failed to create/get user. Check DB."}
    
    last_registered_user["user_id"] = user_id
    last_registered_user["username"] = username


    return {"status": "success", "user_id": user_id, "username": username, "message": message, "is_new_user": is_new_user}


@app.get("/current_user")
def current_user():
    if last_registered_user["user_id"] is None:
        return {"status": "error", "message": "No user registered yet"}
    return last_registered_user



@app.post("/data")
async def receive_data(request: Request, user_id: int = Form(...)):
    if not user_id:
           return {"status": "error", "message": "User ID required before storing readings"}
  
    form_data = await request.form()
    data = load_sensor_data(form_data)

    
    try: 

        with get_connection_cursor() as cursor:

            state = predict_activity(
                data["ax"], data["ay"], data["az"],
                data["gx"], data["gy"], data["gz"]
            )

            heartRate_stat, spo2_stat = validate_vital_signs(data["heartRate"], data["spo2"])

            avg_heartrate, max_heartrate, min_heartrate, reading_count= summary_compute(cursor, user_id)

            stud_condition = predict_condition(state, heartRate_stat)
            username = data["username"]

            print_sensor_log(
                user_id, username, data["timestamp"], data["ax"], data["ay"], data["az"],
                data["gx"], data["gy"], data["gz"],
                state, heartRate_stat, spo2_stat, stud_condition, avg_heartrate,
                max_heartrate, min_heartrate, reading_count
            )
            global latest_sensor_payload
            latest_sensor_payload = {
                "user_id": user_id,
                "username": username,
                "timestamp": data["timestamp"],
                "ax": data["ax"],
                "ay": data["ay"],
                "az": data["az"],
                "gx": data["gx"],
                "gy": data["gy"],
                "gz": data["gz"],
                "predicted_activity": state,
                "heart_rate": heartRate_stat,
                "spo2": spo2_stat,
                "stud_condition": stud_condition,
                "avg_heartrate": avg_heartrate,
                "max_heartrate": max_heartrate,
                "min_heartrate": min_heartrate,
                "reading_count": reading_count
            }

            sql = """ 
                INSERT INTO heart_rate_motion_readings (user_id, recorded_at, ax, ay, az, gx, gy, gz, heart_rate, spo2, predicted_activity, stud_condition)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                user_id, data["timestamp"], data["ax"],
                data["ay"], data["az"], data["gx"],
                data["gy"], data["gz"], heartRate_stat, spo2_stat, state, stud_condition
                
            )
            cursor.execute(sql, values)

            push_summary_db(cursor,user_id, data, avg_heartrate, max_heartrate, min_heartrate, reading_count)

            print("✅ Data successfully saved to heart_rate_motion_readings.")

    except mysql.connector.Error as e:
            print("Database error:", e)


    return {
        "status": "Data received successfully ✅",
        "user": user_id,
        "username": username,
        "timestamp": data["timestamp"],
        "acceleration": {"x": data["ax"], "y": data["ay"], "z": data["az"]},
        "gyroscope": {"x": data["gx"], "y": data["gy"], "z": data["gz"]},
        "heartrate": heartRate_stat,
        "oxygen_saturation": spo2_stat,
        "stud_condition": stud_condition,
        "AVG Heart Rate": avg_heartrate,
        "Max Heart Rate": max_heartrate,
        "Min Heart Rate": min_heartrate,
        "Number of HR Readings": reading_count
    }  

@app.get("/latest")
def get_latest_sensor_data():
    if latest_sensor_payload is None:
        return {
            "status": "No live data available",
            "device_status": "Disconnected"
        }
    return{
        "status": "success",
        "device_status": "Connected",
        **latest_sensor_payload
    }

@app.get("/daily")       
def get_daily_readings(username: str):
    
    try: 
         with get_connection_cursor(dictionary=True) as cursor:

            cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()
            if not user:
                return {"status": "error", "message": "User not found"}
            user_id = user["id"]

            cursor.execute("""
                SELECT * FROM heart_rate_motion_readings WHERE user_id=%s ORDER BY recorded_at ASC
            """, (user_id,))
            
            daily_data = cursor.fetchall()

            if not daily_data:
                return {"status": "No readings for today"}
            return {
                "status": "Success",
                "count": len(daily_data),
                "data": daily_data

            }
         
    except mysql.connector.Error as e:
         print("Database error: ", e) 
         
@app.get("/user_list")
def get_user_list():
    try:
        with get_connection_cursor(dictionary=True) as cursor:

            cursor.execute("SELECT username FROM users ORDER BY username ASC")
            users = cursor.fetchall()
            return {"users": [r["username"] for r in users]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.get("/history")
def get_history():
    try: 
        with get_connection_cursor(dictionary=True) as cursor: 
            # Fetch all users
            cursor.execute("SELECT id, username FROM users ORDER BY username ASC")
            users = cursor.fetchall()
            
                
            all_users_history = []

            for user in users:
                user_id = user.get("id")
                username = user.get("username")

                if not user_id:
                    continue  # skip invalid users

                # Fetch latest reading
                cursor.execute(
                    """
                    SELECT id, recorded_at, heart_rate, predicted_activity, stud_condition
                    FROM heart_rate_motion_readings 
                    WHERE user_id=%s
                    ORDER BY recorded_at DESC
                    LIMIT 1  
                    """,
                    (user_id,)
                )
                latest_reading = cursor.fetchone()
                

                # Fetch latest summary
                cursor.execute("""
                    SELECT avg_heart_rate, min_heart_rate, max_heart_rate, total_readings
                    FROM heart_rate_summary
                    WHERE user_id=%s
                    ORDER BY summary_date DESC
                    LIMIT 1
                """, (user_id,))
                summary = cursor.fetchone()
                

                merged_latest = None
                if latest_reading:
                    merged_latest = {
                        "heartRate": safe_int(latest_reading.get("heart_rate")),
                        "activity": latest_reading.get("predicted_activity") or "Unknown",
                        "anomaly": latest_reading.get("stud_condition") or "Normal",
                        "avgBpm": safe_int(summary.get("avg_heart_rate")) if summary else 0,
                        "minBpm": safe_int(summary.get("min_heart_rate")) if summary else 0,
                        "maxBpm": safe_int(summary.get("max_heart_rate")) if summary else 0,
                        "totalReadings": safe_int(summary.get("total_readings")) if summary else 0
                    }

                    # Fetch last 10 readings
                    cursor.execute("""
                        SELECT id, recorded_at, heart_rate, predicted_activity, stud_condition
                        FROM heart_rate_motion_readings
                        WHERE user_id=%s
                        ORDER BY recorded_at DESC
                        LIMIT 10
                    """, (user_id,))
                    history = cursor.fetchall() or []
                    

                    history_list = [
                        {
                            "id": row.get("id"),
                            "timestamp": row.get("recorded_at"),
                            "heartRate": safe_int(row.get("heart_rate")),
                            "activity": row.get("predicted_activity", "Unknown"),
                            "anomaly": row.get("stud_condition", "Normal")
                        }
                        for row in history
                    ]

                    all_users_history.append({
                        "username": username,
                        "latest": merged_latest,
                        "history": history_list
                    })

        return {
            "status": "success",
            "data": all_users_history
        }

    except Exception as e:  
     return {"status": "error", "message": str(e)}
