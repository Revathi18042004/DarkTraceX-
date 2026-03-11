import sqlite3

conn = sqlite3.connect("logs.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS attack_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attack_type TEXT,
    source_ip TEXT,
    darknet_origin TEXT,
    risk_level TEXT,
    timestamp TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database initialized")
