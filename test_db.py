import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 1️⃣ Load the .env file
load_dotenv()

# 2️⃣ Read DATABASE_URL from environment
DATABASE_URL = os.getenv("MYSQL_PUBLIC_URL")

# 3️⃣ Add the sanity check here
if DATABASE_URL is None:
    raise ValueError("❌ MYSQL_URL is not set! Check your .env file.")

# 4️⃣ Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 5️⃣ Test the connection
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT NOW();"))  # SQLAlchemy 2.x requires text()
        current_time = result.fetchone()[0]
        print("✅ Successfully connected to Railway MySQL!")
        print("Database current time:", current_time)
except Exception as e:
    print("❌ Database connection failed:", e)
