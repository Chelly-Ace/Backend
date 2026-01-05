-- 1. Create database
CREATE DATABASE IF NOT EXISTS health_monitoring;
USE health_monitoring;
-- 2. Users table
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
-- 3. Heart rate & motion readings table
CREATE TABLE heart_rate_motion_readings(
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ax FLOAT,
  ay FLOAT,
  az FLOAT,
  gx FLOAT,
  gy FLOAT,
  gz FLOAT,
  heart_rate INT NOT NULL,
  spo2 FLOAT NOT NULL,
  predicted_activity VARCHAR(50) DEFAULT NULL,
  stud_condition VARCHAR(20) DEFAULT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
-- 4. Heart rate summary table
CREATE TABLE heart_rate_summary (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  summary_date DATE DEFAULT (CURRENT_DATE),
  avg_heart_rate INT,
  min_heart_rate INT,
  max_heart_rate INT,
  total_readings INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
-- 5. Indexes for fast queries
CREATE INDEX idx_summary_date ON heart_rate_summary (summary_date);
CREATE INDEX idx_recorded_at ON heart_rate_motion_readings (recorded_at);
CREATE INDEX idx_predicted_activity ON heart_rate_motion_readings(predicted_activity);
CREATE INDEX idx_stud_condition ON heart_rate_motion_readings(stud_condition);