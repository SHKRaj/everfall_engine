"""
EVERFALL ENGINE - Database Seeding (Refactored)
Seeds initial 1970 data for USA and Germany using the new schema.

Separates:
- Static config (nations table)
- Dynamic state (nation_state table, tick 0)
- Resources (nation_resources table, tick 0)
"""

import sqlite3

DB_PATH = "everfall.db"


def seed_nations():
    """Seed static nation configuration"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # USA Configuration
    cursor.execute("""
        INSERT OR REPLACE INTO nations (
            id, name, code,
            consumer_goods_pct, heavy_industry_pct, military_production_pct,
            agriculture_pct, aerospace_pct, nuclear_program_pct,
            nru_basic_import_elasticity, nru_industrial_import_elasticity,
            nru_precision_import_elasticity, nru_strategic_import_elasticity,
            agu_import_elasticity,
            trade_policy_stance, trade_policy_multiplier,
            nominal_interest_rate, target_money_growth, target_tax_rate
        ) VALUES (
            1, 'United States', 'USA',
            0.45, 0.20, 0.22, 0.08, 0.03, 0.02,
            0.85, 0.70, 0.60, 0.20, 0.90,
            'Balanced', 1.0,
            0.075, 0.055, 0.25
        )
    """)
    
    # Germany Configuration
    cursor.execute("""
        INSERT OR REPLACE INTO nations (
            id, name, code,
            consumer_goods_pct, heavy_industry_pct, military_production_pct,
            agriculture_pct, aerospace_pct, nuclear_program_pct,
            nru_basic_import_elasticity, nru_industrial_import_elasticity,
            nru_precision_import_elasticity, nru_strategic_import_elasticity,
            agu_import_elasticity,
            trade_policy_stance, trade_policy_multiplier,
            nominal_interest_rate, target_money_growth, target_tax_rate
        ) VALUES (
            2, 'Greater Germanic Reich', 'GER',
            0.30, 0.35, 0.28, 0.04, 0.02, 0.01,
            0.60, 0.50, 0.40, 0.10, 0.70,
            'Protectionist', 0.8,
            0.055, 0.042, 0.33
        )
    """)
    
    conn.commit()
    conn.close()
    print("✓ Nation configurations seeded")


def seed_initial_state():
    """Seed tick 0 state for both nations"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # USA Tick 0 State
    cursor.execute("""
        INSERT OR REPLACE INTO nation_state (
            nation_id, tick_number,
            population, working_age_population, labor_force, employed,
            labor_participation_rate,
            capital_stock, tfp,
            money_supply,
            national_debt, government_spending, government_revenue,
            consumer_confidence, institutional_cohesion, political_stability, war_support_morale,
            nuclear_stockpile, total_military_personnel,
            space_prestige_score, moon_base_personnel, lunar_payload_delivered_cumulative,
            japan_insurgency_intensity, siberian_insurgency_intensity,
            total_casualties_this_tick, total_casualties_cumulative
        ) VALUES (
            1, 0,
            210.0, 136.5, 82.8, 78.8,
            0.607,
            5000.0, 1.0,
            600.0,
            380.0, 220.0, 195.0,
            0.68, 65.0, 60.0, 45.0,
            15300, 2500000,
            75.0, 0, 0.0,
            65.0, 0.0,
            0, 0
        )
    """)
    
    # Germany Tick 0 State
    cursor.execute("""
        INSERT OR REPLACE INTO nation_state (
            nation_id, tick_number,
            population, working_age_population, labor_force, employed,
            labor_participation_rate,
            capital_stock, tfp,
            money_supply,
            national_debt, government_spending, government_revenue,
            consumer_confidence, institutional_cohesion, political_stability, war_support_morale,
            nuclear_stockpile, total_military_personnel,
            space_prestige_score, moon_base_personnel, lunar_payload_delivered_cumulative,
            japan_insurgency_intensity, siberian_insurgency_intensity,
            total_casualties_this_tick, total_casualties_cumulative
        ) VALUES (
            2, 0,
            450.0, 292.5, 195.0, 189.2,
            0.65,
            4200.0, 0.85,
            850.0,
            420.0, 350.0, 320.0,
            0.55, 55.0, 70.0, 65.0,
            12500, 4200000,
            60.0, 0, 0.0,
            0.0, 40.0,
            0, 0
        )
    """)
    
    conn.commit()
    conn.close()
    print("✓ Initial state (tick 0) seeded")


def seed_initial_resources():
    """Seed tick 0 resource capacities and stockpiles"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # USA Resources (Tick 0)
    # Capacities roughly based on GDP × sector allocation × 10 scaling
    # $1180B GDP × 0.20 heavy industry × 10 = ~2360 NRU-Industrial capacity
    cursor.execute("""
        INSERT OR REPLACE INTO nation_resources (
            nation_id, tick_number,
            nru_basic_capacity, nru_industrial_capacity, nru_precision_capacity, nru_strategic_capacity,
            agu_capacity,
            nru_basic_production, nru_industrial_production, nru_precision_production, nru_strategic_production,
            agu_production,
            nru_basic_stockpile, nru_industrial_stockpile, nru_precision_stockpile, nru_strategic_stockpile,
            agu_stockpile
        ) VALUES (
            1, 0,
            1800.0, 2360.0, 1400.0, 600.0,
            950.0,
            1800.0, 2360.0, 1400.0, 600.0,
            950.0,
            3600.0, 4720.0, 2800.0, 1200.0,
            1900.0
        )
    """)
    
    # Germany Resources (Tick 0)
    # $980B GDP × 0.35 heavy industry × 10 = ~3430 NRU-Industrial capacity
    cursor.execute("""
        INSERT OR REPLACE INTO nation_resources (
            nation_id, tick_number,
            nru_basic_capacity, nru_industrial_capacity, nru_precision_capacity, nru_strategic_capacity,
            agu_capacity,
            nru_basic_production, nru_industrial_production, nru_precision_production, nru_strategic_production,
            agu_production,
            nru_basic_stockpile, nru_industrial_stockpile, nru_precision_stockpile, nru_strategic_stockpile,
            agu_stockpile
        ) VALUES (
            2, 0,
            2100.0, 3430.0, 1100.0, 400.0,
            400.0,
            2100.0, 3430.0, 1100.0, 400.0,
            400.0,
            4200.0, 6860.0, 2200.0, 800.0,
            800.0
        )
    """)
    
    conn.commit()
    conn.close()
    print("✓ Initial resources (tick 0) seeded")


def seed_unit_type_costs():
    """Add resource costs for existing unit types"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get M48 Patton unit type ID
    cursor.execute("SELECT id FROM unit_types WHERE name = 'M48 Patton'")
    result = cursor.fetchone()
    
    if result:
        m48_id = result[0]
        
        cursor.execute("""
            INSERT OR REPLACE INTO unit_type_costs (
                unit_type_id,
                nru_basic_cost, nru_industrial_cost, nru_precision_cost, nru_strategic_cost,
                nru_basic_maintenance, nru_industrial_maintenance, nru_precision_maintenance
            ) VALUES (?, 2.5, 3.0, 1.5, 0.2, 0.3, 0.15, 0.06)
        """, (m48_id,))
        
        print(f"✓ Unit costs seeded for M48 Patton (ID: {m48_id})")
    else:
        print("⚠ M48 Patton not found, skipping unit costs")
    
    conn.commit()
    conn.close()


def seed_all():
    """Run all seeding functions"""
    print("\n" + "="*60)
    print("SEEDING DATABASE WITH 1970 INITIAL CONDITIONS")
    print("="*60 + "\n")
    
    seed_nations()
    seed_initial_state()
    seed_initial_resources()
    seed_unit_type_costs()
    
    print("\n" + "="*60)
    print("SEEDING COMPLETE")
    print("="*60 + "\n")
    
    # Verify
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, code FROM nations")
    nations = cursor.fetchall()
    
    print("Nations seeded:")
    for name, code in nations:
        print(f"  - {name} ({code})")
    
    cursor.execute("SELECT COUNT(*) FROM nation_state WHERE tick_number = 0")
    state_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM nation_resources WHERE tick_number = 0")
    resource_count = cursor.fetchone()[0]
    
    print(f"\nTick 0 state records: {state_count}")
    print(f"Tick 0 resource records: {resource_count}")
    
    conn.close()


if __name__ == "__main__":
    seed_all()
