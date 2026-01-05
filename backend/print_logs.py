

def print_sensor_log(user_id, username, timestamp, ax, ay, az, gx, gy, gz, state, heartRate_stat, spo2_stat, stud_condition, avg_heartrate, max_heartrate,
                     min_heartrate, reading_count):
   
    print("===================================")
    print(f"Data received at: {timestamp}")
    print(f"User_id: {user_id}")
    print(f"Username: {username}")
    print(f"  ➤ Acceleration: X={ax:.2f}, Y={ay:.2f}, Z={az:.2f}")
    print(f"  ➤ Gyroscope:     X={gx:.2f}, Y={gy:.2f}, Z={gz:.2f}")
    print(f"  ➤ Activity:      {state}")
    print(f"  ➤ Heart Rate:    {heartRate_stat}")
    print(f"  ➤ SpO₂:          {spo2_stat}")
    print(f"  ➤ Student Condition:          {stud_condition}")
    print(f"  ➤ AVG Heart Rate:          {avg_heartrate}")
    print(f"  ➤ Max Heart Rate:          {max_heartrate}")
    print(f"  ➤ Min Heart Rate:          {reading_count}")
    print(f"  ➤ Number of HR Readings:          {min_heartrate}")
    print("===================================\n")    

