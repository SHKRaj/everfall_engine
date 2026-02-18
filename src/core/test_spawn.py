import sqlite3

conn = sqlite3.connect("everfall.db")
cursor = conn.cursor()

cursor.execute("""
SELECT 
    mu.id,
    n.name as nation,
    ut.name as unit_type,
    mu.display_name,
    mu.experience,
    mu.damage,
    mu.readiness,
    mu.fuel_level,
    mu.location,
    mu.status
FROM military_units mu
JOIN nations n ON mu.nation_id = n.id
JOIN unit_types ut ON mu.unit_type_id = ut.id
""")
rows = cursor.fetchall()

for row in rows:
    print(f"""
Unit ID: {row[0]}
Nation: {row[1]}
Type: {row[2]}
Damage: {row[5]}
Status: {row[9]}
------------------------
""")

conn.close()