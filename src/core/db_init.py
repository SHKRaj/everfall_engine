import sqlite3


DB_PATH = "everfall.db"


def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Nations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        is_player BOOLEAN NOT NULL
    )
    """)

    # Manufacturers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS manufacturers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        nation_id INTEGER,
        industrial_capacity REAL,
        specialization TEXT,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        FOREIGN KEY (nation_id) REFERENCES nations(id)
    )
    """)

    # Unit Types (Reference Data)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS unit_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        era TEXT,
        attack REAL,
        defense REAL,
        mobility REAL,
        range_km REAL,
        crew_required INTEGER,
        fuel_consumption_per_turn REAL,
        maintenance_difficulty REAL,
        repair_threshold REAL,
        manufacturer_id INTEGER,
        FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id)
    )
    """)

    # Military Units (Individual Assets)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS military_units (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nation_id INTEGER NOT NULL,
        unit_type_id INTEGER NOT NULL,
        display_name TEXT,
        experience REAL DEFAULT 0.0,
        damage REAL DEFAULT 0.0,
        readiness REAL DEFAULT 1.0,
        fuel_level REAL DEFAULT 1.0,
        location TEXT,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (nation_id) REFERENCES nations(id),
        FOREIGN KEY (unit_type_id) REFERENCES unit_types(id)
        army_group_id INTEGER,
        FOREIGN KEY (army_group_id) REFERENCES army_groups(id)
    )
    """)

    # Army Groups / Formations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS army_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        nation_id INTEGER NOT NULL,
        location TEXT,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (nation_id) REFERENCES nations(id)
    )
    """)

    # Production Queue
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS production_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nation_id INTEGER NOT NULL,
        unit_type_id INTEGER NOT NULL,
        turns_remaining INTEGER NOT NULL,
        status TEXT DEFAULT 'building',
        FOREIGN KEY (nation_id) REFERENCES nations(id),
        FOREIGN KEY (unit_type_id) REFERENCES unit_types(id)
    )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
