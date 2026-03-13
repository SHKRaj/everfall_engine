"""
EVERFALL ENGINE - 1970 Cold War Simulation
Refactored Database Schema

ARCHITECTURE:
- nations: Static configuration (policy settings)
- nation_state: Dynamic state (updated each tick)
- Derived metrics calculated on-demand via metrics.py
"""

import sqlite3

DB_PATH = "everfall.db"


def initialize_database():
    """
    Create all database tables for the 1970 simulation.
    Separates static config from dynamic state.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ========================================
    # NATIONS (STATIC CONFIGURATION)
    # ========================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        code TEXT NOT NULL UNIQUE,
        
        -- POLICY SETTINGS (player-controlled, change via decisions)
        -- Economic sector allocations (must sum to 1.0)
        consumer_goods_pct REAL DEFAULT 0.40,
        heavy_industry_pct REAL DEFAULT 0.20,
        military_production_pct REAL DEFAULT 0.20,
        agriculture_pct REAL DEFAULT 0.10,
        aerospace_pct REAL DEFAULT 0.05,
        nuclear_program_pct REAL DEFAULT 0.05,
        
        -- Trade policy
        nru_basic_import_elasticity REAL DEFAULT 0.8,
        nru_industrial_import_elasticity REAL DEFAULT 0.7,
        nru_precision_import_elasticity REAL DEFAULT 0.6,
        nru_strategic_import_elasticity REAL DEFAULT 0.3,
        agu_import_elasticity REAL DEFAULT 0.9,
        
        trade_policy_stance TEXT DEFAULT 'Balanced',
        trade_policy_multiplier REAL DEFAULT 1.0,
        
        -- Monetary policy
        nominal_interest_rate REAL DEFAULT 0.05
    )
    """)

    # ========================================
    # NATION_STATE (DYNAMIC - UPDATED EACH TICK)
    # ========================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nation_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nation_id INTEGER NOT NULL,
        tick_number INTEGER NOT NULL,
        
        -- POPULATION & DEMOGRAPHICS
        population REAL NOT NULL,
        working_age_population REAL NOT NULL,
        labor_force REAL NOT NULL,
        employed REAL NOT NULL,
        labor_participation_rate REAL DEFAULT 0.60,
        
        -- PRODUCTION FACTORS
        capital_stock REAL NOT NULL,
        tfp REAL DEFAULT 1.0,  -- Total Factor Productivity
        
        -- MONETARY
        money_supply REAL NOT NULL,
        
        -- FISCAL
        national_debt REAL DEFAULT 0,
        government_spending REAL NOT NULL,
        government_revenue REAL NOT NULL,
        
        -- INSTITUTIONAL HEALTH (0-100 scale)
        consumer_confidence REAL DEFAULT 0.7,
        institutional_cohesion REAL DEFAULT 70.0,
        political_stability REAL DEFAULT 70.0,
        war_support_morale REAL DEFAULT 60.0,
        
        -- MILITARY
        nuclear_stockpile INTEGER DEFAULT 0,
        total_military_personnel INTEGER DEFAULT 0,
        
        -- SPACE RACE
        space_prestige_score REAL DEFAULT 0,
        moon_base_personnel INTEGER DEFAULT 0,
        lunar_payload_delivered_cumulative REAL DEFAULT 0,
        rocket_launches_this_tick INTEGER DEFAULT 0,
        
        -- CONFLICTS
        japan_insurgency_intensity REAL DEFAULT 0,
        siberian_insurgency_intensity REAL DEFAULT 0,
        total_casualties_this_tick INTEGER DEFAULT 0,
        total_casualties_cumulative INTEGER DEFAULT 0,
        
        FOREIGN KEY (nation_id) REFERENCES nations(id),
        UNIQUE(nation_id, tick_number)
    )
    """)

    # ========================================
    # NATION_RESOURCES (NRU & AGU per tick)
    # ========================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nation_resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nation_id INTEGER NOT NULL,
        tick_number INTEGER NOT NULL,
        
        -- PRODUCTION CAPACITY (max theoretical output)
        nru_basic_capacity REAL DEFAULT 0,
        nru_industrial_capacity REAL DEFAULT 0,
        nru_precision_capacity REAL DEFAULT 0,
        nru_strategic_capacity REAL DEFAULT 0,
        agu_capacity REAL DEFAULT 0,
        
        -- ACTUAL PRODUCTION (after capacity utilization, buffs, damage)
        nru_basic_production REAL DEFAULT 0,
        nru_industrial_production REAL DEFAULT 0,
        nru_precision_production REAL DEFAULT 0,
        nru_strategic_production REAL DEFAULT 0,
        agu_production REAL DEFAULT 0,
        
        -- DEMAND (military + economy + consumption)
        nru_basic_demand REAL DEFAULT 0,
        nru_industrial_demand REAL DEFAULT 0,
        nru_precision_demand REAL DEFAULT 0,
        nru_strategic_demand REAL DEFAULT 0,
        agu_demand REAL DEFAULT 0,
        
        -- TRADE (calculated via import elasticity)
        nru_basic_imports REAL DEFAULT 0,
        nru_industrial_imports REAL DEFAULT 0,
        nru_precision_imports REAL DEFAULT 0,
        nru_strategic_imports REAL DEFAULT 0,
        agu_imports REAL DEFAULT 0,
        
        nru_basic_exports REAL DEFAULT 0,
        nru_industrial_exports REAL DEFAULT 0,
        nru_precision_exports REAL DEFAULT 0,
        nru_strategic_exports REAL DEFAULT 0,
        agu_exports REAL DEFAULT 0,
        
        -- TOTAL SUPPLY (production + imports)
        nru_basic_supply REAL DEFAULT 0,
        nru_industrial_supply REAL DEFAULT 0,
        nru_precision_supply REAL DEFAULT 0,
        nru_strategic_supply REAL DEFAULT 0,
        agu_supply REAL DEFAULT 0,
        
        -- SHORTFALLS (unmet demand)
        nru_basic_shortfall REAL DEFAULT 0,
        nru_industrial_shortfall REAL DEFAULT 0,
        nru_precision_shortfall REAL DEFAULT 0,
        nru_strategic_shortfall REAL DEFAULT 0,
        agu_shortfall REAL DEFAULT 0,
        
        -- STOCKPILES (strategic reserves)
        nru_basic_stockpile REAL DEFAULT 0,
        nru_industrial_stockpile REAL DEFAULT 0,
        nru_precision_stockpile REAL DEFAULT 0,
        nru_strategic_stockpile REAL DEFAULT 0,
        agu_stockpile REAL DEFAULT 0,
        
        FOREIGN KEY (nation_id) REFERENCES nations(id),
        UNIQUE(nation_id, tick_number)
    )
    """)

    # ========================================
    # CHARACTERS (Players on each team)
    # ========================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        nation_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        
        -- Activity focus (multiple can be active)
        focus_economy BOOLEAN DEFAULT 0,
        focus_aerospace BOOLEAN DEFAULT 0,
        focus_stability BOOLEAN DEFAULT 0,
        focus_military BOOLEAN DEFAULT 0,
        focus_diplomacy BOOLEAN DEFAULT 0,
        focus_intelligence BOOLEAN DEFAULT 0,
        focus_nuclear_program BOOLEAN DEFAULT 0,
        
        -- Derived competencies (0-100)
        economic_competence REAL DEFAULT 50,
        military_competence REAL DEFAULT 50,
        diplomatic_influence REAL DEFAULT 50,
        intelligence_effectiveness REAL DEFAULT 50,
        
        -- Authority level (affects buff strength)
        authority_level INTEGER DEFAULT 5,
        
        FOREIGN KEY (nation_id) REFERENCES nations(id)
    )
    """)

    # ========================================
    # BUFFS (Universal modifier system)
    # ========================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buffs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        source_type TEXT NOT NULL,
        source_id INTEGER,
        
        target_type TEXT NOT NULL,
        target_id INTEGER,
        
        stat_name TEXT NOT NULL,
        modifier_type TEXT NOT NULL,
        value REAL NOT NULL,
        
        created_tick INTEGER NOT NULL,
        expires_tick INTEGER,
        
        description TEXT,
        is_active BOOLEAN DEFAULT 1
    )
    """)

    # ========================================
    # MINOR NATIONS
    # ========================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS minor_nations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        region TEXT,
        alignment_tendency TEXT,
        
        base_gdp_billions REAL,
        population_millions REAL,
        industrial_capacity REAL DEFAULT 50,
        military_strength REAL DEFAULT 30,
        
        primary_export_type TEXT,
        
        nuclear_capable BOOLEAN DEFAULT 0,
        nuclear_stockpile INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS minor_nation_diplomacy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        minor_nation_id INTEGER NOT NULL,
        tick_number INTEGER NOT NULL,
        
        approval_of_usa REAL DEFAULT 50,
        approval_of_germany REAL DEFAULT 50,
        
        usa_approval_of_them REAL DEFAULT 50,
        germany_approval_of_them REAL DEFAULT 50,
        
        trade_policy_usa TEXT DEFAULT 'Open',
        trade_policy_germany TEXT DEFAULT 'Open',
        
        trade_volume_usa REAL DEFAULT 0,
        trade_volume_germany REAL DEFAULT 0,
        
        nru_basic_to_usa REAL DEFAULT 0,
        nru_industrial_to_usa REAL DEFAULT 0,
        nru_precision_to_usa REAL DEFAULT 0,
        nru_strategic_to_usa REAL DEFAULT 0,
        agu_to_usa REAL DEFAULT 0,
        
        nru_basic_to_germany REAL DEFAULT 0,
        nru_industrial_to_germany REAL DEFAULT 0,
        nru_precision_to_germany REAL DEFAULT 0,
        nru_strategic_to_germany REAL DEFAULT 0,
        agu_to_germany REAL DEFAULT 0,
        
        alignment_shift_risk REAL DEFAULT 10,
        influence_battle_score REAL DEFAULT 0,
        
        FOREIGN KEY (minor_nation_id) REFERENCES minor_nations(id),
        UNIQUE(minor_nation_id, tick_number)
    )
    """)

    # ========================================
    # MILITARY TABLES (Keep existing)
    # ========================================
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS unit_type_costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_type_id INTEGER NOT NULL,
        
        nru_basic_cost REAL DEFAULT 0,
        nru_industrial_cost REAL DEFAULT 0,
        nru_precision_cost REAL DEFAULT 0,
        nru_strategic_cost REAL DEFAULT 0,
        agu_cost REAL DEFAULT 0,
        
        nru_basic_maintenance REAL DEFAULT 0,
        nru_industrial_maintenance REAL DEFAULT 0,
        nru_precision_maintenance REAL DEFAULT 0,
        nru_strategic_maintenance REAL DEFAULT 0,
        agu_maintenance REAL DEFAULT 0,
        
        FOREIGN KEY (unit_type_id) REFERENCES unit_types(id)
    )
    """)

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
        army_group_id INTEGER,
        FOREIGN KEY (nation_id) REFERENCES nations(id),
        FOREIGN KEY (unit_type_id) REFERENCES unit_types(id),
        FOREIGN KEY (army_group_id) REFERENCES army_groups(id)
    )
    """)

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS production_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nation_id INTEGER NOT NULL,
        unit_type_id INTEGER NOT NULL,
        quantity INTEGER DEFAULT 1,
        months_remaining REAL NOT NULL,
        priority INTEGER DEFAULT 5,
        status TEXT DEFAULT 'building',
        resources_locked BOOLEAN DEFAULT 0,
        FOREIGN KEY (nation_id) REFERENCES nations(id),
        FOREIGN KEY (unit_type_id) REFERENCES unit_types(id)
    )
    """)

    # ========================================
    # GAME MANAGEMENT
    # ========================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tick_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tick_number INTEGER NOT NULL UNIQUE,
        game_date TEXT NOT NULL,
        real_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        
        total_battles INTEGER DEFAULT 0,
        total_units_destroyed INTEGER DEFAULT 0,
        usa_gdp_growth REAL,
        germany_gdp_growth REAL,
        
        events_summary TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pending_decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tick_number INTEGER NOT NULL,
        nation_id INTEGER NOT NULL,
        character_id INTEGER,
        
        decision_type TEXT NOT NULL,
        decision_data TEXT NOT NULL,
        
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (nation_id) REFERENCES nations(id),
        FOREIGN KEY (character_id) REFERENCES characters(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tick_number INTEGER NOT NULL,
        nation_id INTEGER,
        
        event_type TEXT NOT NULL,
        severity TEXT,
        
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        outcome TEXT,
        
        FOREIGN KEY (nation_id) REFERENCES nations(id)
    )
    """)

    conn.commit()
    conn.close()
    print("✓ Refactored database schema created successfully.")


if __name__ == "__main__":
    initialize_database()