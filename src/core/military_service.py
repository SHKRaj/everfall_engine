import sqlite3

DB_PATH = "everfall.db"


def spawn_unit(nation_name, unit_type_name, display_name=None, location="home"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get Country ID
    cursor.execute("SELECT id FROM nations WHERE name = ?", (nation_name,))
    nation = cursor.fetchone()
    if not nation:
        raise ValueError(f"Nation '{nation_name}' not found.")
    nation_id = nation[0]

    # Get Unit Type ID
    cursor.execute("SELECT id FROM unit_types WHERE name = ?", (unit_type_name,))
    unit_type = cursor.fetchone()
    if not unit_type:
        raise ValueError(f"Unit type '{unit_type_name}' not found.")
    unit_type_id = unit_type[0]

    # Insert new unit
    cursor.execute("""
        INSERT INTO military_units
        (nation_id, unit_type_id, display_name, location)
        VALUES (?, ?, ?, ?)
    """, (nation_id, unit_type_id, display_name, location))

    unit_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return unit_id

def create_army_group(nation_name, group_name, location="home"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM nations WHERE name = ?", (nation_name,))
    nation = cursor.fetchone()
    if not nation:
        raise ValueError("Nation not found.")

    cursor.execute("""
        INSERT INTO army_groups (name, nation_id, location)
        VALUES (?, ?, ?)
    """, (group_name, nation[0], location))

    group_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return group_id

def get_units_in_group(group_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT mu.id, ut.name, mu.damage, mu.experience
    FROM military_units mu
    JOIN unit_types ut ON mu.unit_type_id = ut.id
    WHERE mu.army_group_id = ?
    AND mu.status = 'active'
    """, (group_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows

import random

def apply_group_damage(group_id, intensity):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, damage
        FROM military_units
        WHERE army_group_id = ?
        AND status = 'active'
    """, (group_id,))

    units = cursor.fetchall()

    for unit_id, current_damage in units:
        # Damage spread is randomized via uniform distribution
        spread = random.uniform(0.5, 1.5)
        damage_applied = intensity * spread * 0.2  # scaling factor

        new_damage = current_damage + damage_applied

        if new_damage >= 1.0:
            cursor.execute("""
                UPDATE military_units
                SET damage = 1.0,
                    status = 'destroyed'
                WHERE id = ?
            """, (unit_id,))
        else:
            # Survivors of the attack gain experience
            cursor.execute("""
                UPDATE military_units
                SET damage = ?,
                    experience = experience + ?
                WHERE id = ?
            """, (new_damage, intensity * 0.1, unit_id))

    conn.commit()
    conn.close()

def assign_unit_to_group(unit_id, group_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verify unit exists
    cursor.execute("SELECT id FROM military_units WHERE id = ?", (unit_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError(f"Unit {unit_id} does not exist.")

    # Verify group exists
    cursor.execute("SELECT id FROM army_groups WHERE id = ?", (group_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError(f"Army group {group_id} does not exist.")

    # Assign unit
    cursor.execute("""
        UPDATE military_units
        SET army_group_id = ?
        WHERE id = ?
    """, (group_id, unit_id))

    conn.commit()
    conn.close()
