import sqlite3

from src.data.manufacturer_definitions import MANUFACTURERS
from src.data.unit_definitions import UNIT_TYPES


DB_PATH = "everfall.db"


def seed_reference_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    NATIONS = [
        {"name": "United States", "is_player": True},
        {"name": "Germany", "is_player": True}
    ]

    for n in NATIONS:
        cursor.execute("""
        INSERT OR IGNORE INTO nations (name, is_player)
        VALUES (?, ?)
        """, (n["name"], int(n["is_player"])))

    # Insert manufacturers
    for m in MANUFACTURERS:
        cursor.execute("""
        INSERT OR IGNORE INTO manufacturers (name, nation_id, industrial_capacity, specialization, is_active)
        VALUES (?, 
            (SELECT id FROM nations WHERE name = ?),
            ?, ?, 1)
        """, (m["name"], m["nation"], m["industrial_capacity"], m["specialization"]))

    # Insert unit types
    for u in UNIT_TYPES:
        cursor.execute("""
        INSERT OR IGNORE INTO unit_types
        (name, category, era, attack, defense, mobility, range_km,
         crew_required, fuel_consumption_per_turn, maintenance_difficulty,
         repair_threshold, manufacturer_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
            (SELECT id FROM manufacturers WHERE name = ?))
        """, (
            u["name"],
            u["category"],
            u["era"],
            u["attack"],
            u["defense"],
            u["mobility"],
            u["range_km"],
            u["crew_required"],
            u["fuel_consumption_per_turn"],
            u["maintenance_difficulty"],
            u["repair_threshold"],
            u["manufacturer"]
        ))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_reference_data()
    print("Reference data seeded successfully.")
