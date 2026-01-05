
"""
summary_compute(): Compute for the avg_heartrate, max_heartrate, min_heartrate, reading_count

  
push_summary_compute(): Push the summary_date, avg_heart_rate, min_heart_rate, max_heart_rate, total_readings

"""
def summary_compute(cursor, user_id: int):
       cursor.execute("""
    SELECT AVG(heart_rate), MIN(heart_rate), MAX(heart_rate), COUNT(heart_rate) FROM heart_rate_motion_readings 
    WHERE      user_id=%s
    """, (user_id,)) 
       
       avg_heartrate, min_heartrate, max_heartrate, reading_count = cursor.fetchone()
       
       return avg_heartrate, min_heartrate, max_heartrate, reading_count

def push_summary_db(cursor, user_id: int, data, avg_heartrate, min_heartrate, max_heartrate,reading_count):
     sql2 = """
INSERT INTO heart_rate_summary (user_id, summary_date, avg_heart_rate, min_heart_rate, max_heart_rate, total_readings) VALUES(%s, %s, %s , %s , %s , %s)
"""
     values2 = (user_id, data["timestamp"],
                avg_heartrate, min_heartrate,  max_heartrate, reading_count)
     cursor.execute(sql2, values2)
