import sqlite3
from src.core.military_service import (
    spawn_unit,
    create_army_group,
    assign_unit_to_group,
    apply_group_damage,
)

DB_PATH = "everfall.db"


def clear_units():
    """Removes all military units and army groups for clean testing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM military_units")
    cursor.execute("DELETE FROM army_groups")
    conn.commit()
    conn.close()


def print_group_state(group_id, title):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "=" * 40)
    print(title)
    print("=" * 40)

    cursor.execute("""
        SELECT mu.id, ut.name, mu.damage, mu.experience, mu.status
        FROM military_units mu
        JOIN unit_types ut ON mu.unit_type_id = ut.id
        WHERE mu.army_group_id = ?
        ORDER BY mu.id
    """, (group_id,))

    rows = cursor.fetchall()

    for row in rows:
        print(
            f"Unit {row[0]} | {row[1]} | "
            f"Damage: {round(row[2], 3)} | "
            f"XP: {round(row[3], 3)} | "
            f"Status: {row[4]}"
        )

    conn.close()


def main():
    clear_units()

    # Spawn 10 tanks for the United States
    unit_ids = []
    for _ in range(10):
        uid = spawn_unit("United States", "M48 Patton")
        unit_ids.append(uid)

    # Create Army Group and assign units
    group_id = create_army_group("United States", "1st Armored Group")

    # Assign units to the group
    for uid in unit_ids:
        assign_unit_to_group(uid, group_id)

    # Show initial state before damage
    print_group_state(group_id, "BEFORE DAMAGE")

    # Apply damage (intensity = 0.4 example) 
    apply_group_damage(group_id, intensity=0.4)

    # Show after damage state
    print_group_state(group_id, "AFTER DAMAGE")


if __name__ == "__main__":
    main()
