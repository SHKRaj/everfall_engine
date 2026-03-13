import sqlite3
import os

DB_PATH = "everfall.db"


def initialize_database_1970():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    # -------------------------------------------------------------------------
    # EXISTING TABLES (from db_init.py) - kept for compatibility
    # -------------------------------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nations_legacy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        is_player BOOLEAN NOT NULL
    )
    """)

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

    # -------------------------------------------------------------------------
    # 1. NATIONS TABLE (full 1970 simulation data)
    # -------------------------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        code TEXT NOT NULL UNIQUE,

        -- A. Economic fundamentals
        base_gdp_billions REAL NOT NULL,
        population_millions REAL NOT NULL,
        gdp_per_capita REAL,
        inflation_rate REAL DEFAULT 0.02,
        unemployment_rate REAL DEFAULT 0.05,
        government_revenue REAL,
        government_spending REAL,
        budget_deficit REAL,
        national_debt REAL,
        debt_to_gdp_ratio REAL,
        nominal_interest_rate REAL DEFAULT 0.05,
        real_interest_rate REAL,
        money_supply REAL,
        money_supply_growth REAL DEFAULT 0.03,
        velocity_of_money REAL DEFAULT 4.0,
        trade_balance REAL,
        consumer_confidence REAL DEFAULT 0.7,
        labor_force_millions REAL,
        labor_participation_rate REAL DEFAULT 0.60,
        marginal_propensity_to_consume REAL DEFAULT 0.65,

        -- B. Economic sectors (must sum to 1.0)
        consumer_goods_pct REAL DEFAULT 0.40,
        heavy_industry_pct REAL DEFAULT 0.20,
        military_production_pct REAL DEFAULT 0.20,
        agriculture_pct REAL DEFAULT 0.10,
        aerospace_pct REAL DEFAULT 0.05,
        nuclear_program_pct REAL DEFAULT 0.05,

        -- C. Institutional health (0-100 scale)
        base_institutional_cohesion REAL DEFAULT 70.0,
        political_stability REAL DEFAULT 70.0,
        war_support_morale REAL DEFAULT 60.0,

        -- G. Trade policy & import elasticity (0-1 scale)
        nru_basic_import_elasticity REAL DEFAULT 0.8,
        nru_industrial_import_elasticity REAL DEFAULT 0.7,
        nru_precision_import_elasticity REAL DEFAULT 0.6,
        nru_strategic_import_elasticity REAL DEFAULT 0.3,
        agu_import_elasticity REAL DEFAULT 0.9,

        trade_policy_stance TEXT DEFAULT 'Balanced',
        trade_policy_multiplier REAL DEFAULT 1.0,

        -- H. Military
        nuclear_stockpile INTEGER DEFAULT 0,
        total_active_units INTEGER DEFAULT 0,
        total_military_personnel INTEGER DEFAULT 0,
        defense_spending REAL,
        defense_spending_pct_gdp REAL,

        -- I. Space race
        space_program_funding REAL DEFAULT 0,
        rocket_production_capacity INTEGER DEFAULT 0,
        lunar_payload_capacity REAL DEFAULT 0,
        moon_base_personnel_capacity INTEGER DEFAULT 0,
        moon_base_current_personnel INTEGER DEFAULT 0,
        space_prestige_score REAL DEFAULT 0,

        -- J. Active conflicts
        japan_insurgency_intensity REAL DEFAULT 0,
        siberian_insurgency_intensity REAL DEFAULT 0,
        total_casualties_this_tick INTEGER DEFAULT 0,
        total_casualties_cumulative INTEGER DEFAULT 0,

        -- K. Budget breakdown
        defense_operations_spending REAL,
        defense_procurement_spending REAL,
        defense_rd_spending REAL,
        intelligence_spending REAL,
        infrastructure_spending REAL,
        science_technology_spending REAL,
        administrative_spending REAL,
        social_programs_spending REAL,
        debt_service_spending REAL
    )
    """)

    # -------------------------------------------------------------------------
    # 2. NATION_RESOURCES TABLE (NRU & AGU per-tick snapshot)
    # -------------------------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nation_resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nation_id INTEGER NOT NULL,
        tick_number INTEGER NOT NULL,

        -- Production capacity (theoretical max)
        nru_basic_capacity REAL DEFAULT 0,
        nru_industrial_capacity REAL DEFAULT 0,
        nru_precision_capacity REAL DEFAULT 0,
        nru_strategic_capacity REAL DEFAULT 0,
        agu_capacity REAL DEFAULT 0,

        -- Actual production (after buffs, insurgency damage, etc.)
        nru_basic_production REAL DEFAULT 0,
        nru_industrial_production REAL DEFAULT 0,
        nru_precision_production REAL DEFAULT 0,
        nru_strategic_production REAL DEFAULT 0,
        agu_production REAL DEFAULT 0,

        -- Demand (what nation needs this tick)
        nru_basic_demand REAL DEFAULT 0,
        nru_industrial_demand REAL DEFAULT 0,
        nru_precision_demand REAL DEFAULT 0,
        nru_strategic_demand REAL DEFAULT 0,
        agu_demand REAL DEFAULT 0,

        -- Trade (calculated via import elasticity formula)
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

        -- Total supply (production + imports)
        nru_basic_supply REAL DEFAULT 0,
        nru_industrial_supply REAL DEFAULT 0,
        nru_precision_supply REAL DEFAULT 0,
        nru_strategic_supply REAL DEFAULT 0,
        agu_supply REAL DEFAULT 0,

        -- Unmet demand (shortfalls when supply < demand)
        nru_basic_shortfall REAL DEFAULT 0,
        nru_industrial_shortfall REAL DEFAULT 0,
        nru_precision_shortfall REAL DEFAULT 0,
        nru_strategic_shortfall REAL DEFAULT 0,
        agu_shortfall REAL DEFAULT 0,

        -- Stockpiles (strategic reserves)
        nru_basic_stockpile REAL DEFAULT 0,
        nru_industrial_stockpile REAL DEFAULT 0,
        nru_precision_stockpile REAL DEFAULT 0,
        nru_strategic_stockpile REAL DEFAULT 0,
        agu_stockpile REAL DEFAULT 0,

        FOREIGN KEY (nation_id) REFERENCES nations(id),
        UNIQUE(nation_id, tick_number)
    )
    """)

    # -------------------------------------------------------------------------
    # 3. CHARACTERS TABLE (Players on each team)
    # -------------------------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        nation_id INTEGER NOT NULL,
        role TEXT NOT NULL,

        -- Activity focus booleans (can have multiple active)
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

        -- Authority level (1-10, affects buff strength)
        authority_level INTEGER DEFAULT 5,

        FOREIGN KEY (nation_id) REFERENCES nations(id)
    )
    """)

    # -------------------------------------------------------------------------
    # 4. BUFFS TABLE (Universal buff system)
    # -------------------------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buffs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        -- Source (what created this buff?)
        source_type TEXT NOT NULL,
        source_id INTEGER,

        -- Target (what does this buff affect?)
        target_type TEXT NOT NULL,
        target_id INTEGER,

        -- Effect
        stat_name TEXT NOT NULL,
        modifier_type TEXT NOT NULL,
        value REAL NOT NULL,

        -- Duration
        created_tick INTEGER NOT NULL,
        expires_tick INTEGER,

        -- Metadata
        description TEXT,
        is_active BOOLEAN DEFAULT 1
    )
    """)

    # -------------------------------------------------------------------------
    # 5. MINOR_NATIONS TABLE (NPC nations)
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # 6. MINOR_NATION_DIPLOMACY TABLE (Per-tick diplomatic state)
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # 7. UNIT_TYPE_COSTS TABLE (Resource costs for units)
    # -------------------------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS unit_type_costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_type_id INTEGER NOT NULL,

        -- One-time construction costs
        nru_basic_cost REAL DEFAULT 0,
        nru_industrial_cost REAL DEFAULT 0,
        nru_precision_cost REAL DEFAULT 0,
        nru_strategic_cost REAL DEFAULT 0,
        agu_cost REAL DEFAULT 0,

        -- Monthly maintenance costs (tick = 3 months)
        nru_basic_maintenance REAL DEFAULT 0,
        nru_industrial_maintenance REAL DEFAULT 0,
        nru_precision_maintenance REAL DEFAULT 0,
        nru_strategic_maintenance REAL DEFAULT 0,
        agu_maintenance REAL DEFAULT 0,

        FOREIGN KEY (unit_type_id) REFERENCES unit_types(id)
    )
    """)

    # -------------------------------------------------------------------------
    # 8. TICK_HISTORY TABLE (Log of each simulation run)
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # 9. PENDING_DECISIONS TABLE (Player inputs awaiting execution)
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # 10. EVENTS TABLE (Generated events and outcomes)
    # -------------------------------------------------------------------------
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


EXPECTED_TABLES = [
    "manufacturers",
    "unit_types",
    "army_groups",
    "military_units",
    "production_queue",
    "nations",
    "nation_resources",
    "characters",
    "buffs",
    "minor_nations",
    "minor_nation_diplomacy",
    "unit_type_costs",
    "tick_history",
    "pending_decisions",
    "events",
]


def verify_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing = {row[0] for row in cursor.fetchall()}
    conn.close()
    missing = [t for t in EXPECTED_TABLES if t not in existing]
    return existing, missing


if __name__ == "__main__":
    initialize_database_1970()
    existing, missing = verify_tables()
    if missing:
        print(f"WARNING: Missing tables: {missing}")
    else:
        print(f"All {len(EXPECTED_TABLES)} tables created successfully.")
