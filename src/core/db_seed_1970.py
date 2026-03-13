import sqlite3

DB_PATH = "everfall.db"

# ---------------------------------------------------------------------------
# NATION DATA
# ---------------------------------------------------------------------------

USA_DATA = {
    "name": "United States",
    "code": "USA",

    # Economy
    "base_gdp_billions": 1180.0,
    "population_millions": 210.0,
    "gdp_per_capita": 5619.0,
    "inflation_rate": 0.055,
    "unemployment_rate": 0.049,
    "government_revenue": 195.0,
    "government_spending": 220.0,
    "budget_deficit": -25.0,
    "national_debt": 380.0,
    "debt_to_gdp_ratio": 0.322,
    "nominal_interest_rate": 0.075,
    "real_interest_rate": 0.020,
    "money_supply": 600.0,
    "money_supply_growth": 0.055,
    "velocity_of_money": 4.2,
    "trade_balance": -2.5,
    "consumer_confidence": 0.68,
    "labor_force_millions": 82.8,
    "labor_participation_rate": 0.607,
    "marginal_propensity_to_consume": 0.68,

    # Sectors
    "consumer_goods_pct": 0.45,
    "heavy_industry_pct": 0.20,
    "military_production_pct": 0.22,
    "agriculture_pct": 0.08,
    "aerospace_pct": 0.03,
    "nuclear_program_pct": 0.02,

    # Institutional health
    "base_institutional_cohesion": 65.0,
    "political_stability": 60.0,
    "war_support_morale": 45.0,

    # Import elasticity
    "nru_basic_import_elasticity": 0.85,
    "nru_industrial_import_elasticity": 0.70,
    "nru_precision_import_elasticity": 0.60,
    "nru_strategic_import_elasticity": 0.20,
    "agu_import_elasticity": 0.90,

    "trade_policy_stance": "Balanced",
    "trade_policy_multiplier": 1.0,

    # Military
    "nuclear_stockpile": 15300,
    "total_active_units": 0,
    "total_military_personnel": 3460000,
    "defense_spending": 80.0,
    "defense_spending_pct_gdp": 0.068,

    # Space race
    "space_program_funding": 4.0,
    "rocket_production_capacity": 12,
    "lunar_payload_capacity": 50.0,
    "moon_base_personnel_capacity": 6,
    "moon_base_current_personnel": 0,
    "space_prestige_score": 75.0,

    # Conflicts
    "japan_insurgency_intensity": 65.0,
    "siberian_insurgency_intensity": 0.0,
    "total_casualties_this_tick": 0,
    "total_casualties_cumulative": 0,

    # Budget breakdown (billions)
    "defense_operations_spending": 35.0,
    "defense_procurement_spending": 25.0,
    "defense_rd_spending": 12.0,
    "intelligence_spending": 8.0,
    "infrastructure_spending": 15.0,
    "science_technology_spending": 8.0,
    "administrative_spending": 25.0,
    "social_programs_spending": 80.0,
    "debt_service_spending": 12.0,
}

GERMANY_DATA = {
    "name": "Greater Germanic Reich",
    "code": "GER",

    # Economy
    "base_gdp_billions": 980.0,
    "population_millions": 450.0,
    "gdp_per_capita": 2178.0,
    "inflation_rate": 0.035,
    "unemployment_rate": 0.030,
    "government_revenue": 320.0,
    "government_spending": 350.0,
    "budget_deficit": -30.0,
    "national_debt": 420.0,
    "debt_to_gdp_ratio": 0.429,
    "nominal_interest_rate": 0.055,
    "real_interest_rate": 0.020,
    "money_supply": 850.0,
    "money_supply_growth": 0.042,
    "velocity_of_money": 3.8,
    "trade_balance": 15.0,
    "consumer_confidence": 0.55,
    "labor_force_millions": 195.0,
    "labor_participation_rate": 0.65,
    "marginal_propensity_to_consume": 0.58,

    # Sectors
    "consumer_goods_pct": 0.30,
    "heavy_industry_pct": 0.35,
    "military_production_pct": 0.28,
    "agriculture_pct": 0.04,
    "aerospace_pct": 0.02,
    "nuclear_program_pct": 0.01,

    # Institutional health
    "base_institutional_cohesion": 55.0,
    "political_stability": 70.0,
    "war_support_morale": 65.0,

    # Import elasticity
    "nru_basic_import_elasticity": 0.60,
    "nru_industrial_import_elasticity": 0.50,
    "nru_precision_import_elasticity": 0.40,
    "nru_strategic_import_elasticity": 0.10,
    "agu_import_elasticity": 0.70,

    "trade_policy_stance": "Protectionist",
    "trade_policy_multiplier": 0.8,

    # Military
    "nuclear_stockpile": 12500,
    "total_active_units": 0,
    "total_military_personnel": 4200000,
    "defense_spending": 95.0,
    "defense_spending_pct_gdp": 0.097,

    # Space race
    "space_program_funding": 3.5,
    "rocket_production_capacity": 8,
    "lunar_payload_capacity": 35.0,
    "moon_base_personnel_capacity": 4,
    "moon_base_current_personnel": 0,
    "space_prestige_score": 60.0,

    # Conflicts
    "japan_insurgency_intensity": 0.0,
    "siberian_insurgency_intensity": 40.0,
    "total_casualties_this_tick": 0,
    "total_casualties_cumulative": 0,

    # Budget breakdown (billions)
    "defense_operations_spending": 45.0,
    "defense_procurement_spending": 30.0,
    "defense_rd_spending": 12.0,
    "intelligence_spending": 8.0,
    "infrastructure_spending": 25.0,
    "science_technology_spending": 6.0,
    "administrative_spending": 35.0,
    "social_programs_spending": 60.0,
    "debt_service_spending": 18.0,
}

# ---------------------------------------------------------------------------
# INITIAL RESOURCE STATE (Tick 0)
# Production capacities scale from GDP and sector percentages.
# Base formula: capacity = gdp * sector_pct * scaling_factor
# ---------------------------------------------------------------------------

def _calculate_initial_resources(nation_data):
    gdp = nation_data["base_gdp_billions"]
    heavy = nation_data["heavy_industry_pct"]
    mil = nation_data["military_production_pct"]
    agri = nation_data["agriculture_pct"]
    aero = nation_data["aerospace_pct"]
    nuke = nation_data["nuclear_program_pct"]
    consumer = nation_data["consumer_goods_pct"]

    # Scale GDP -> resource units (arbitrary scale: 1B GDP = ~10 NRU/tick)
    scale = 10.0

    basic_cap    = gdp * (heavy * 0.3 + consumer * 0.2) * scale
    industrial_cap = gdp * (heavy * 0.5 + mil * 0.3) * scale
    precision_cap  = gdp * (mil * 0.4 + aero * 0.6) * scale
    strategic_cap  = gdp * (nuke * 0.6 + aero * 0.2) * scale
    agu_cap        = gdp * agri * scale

    return {
        "nru_basic_capacity":      round(basic_cap, 2),
        "nru_industrial_capacity": round(industrial_cap, 2),
        "nru_precision_capacity":  round(precision_cap, 2),
        "nru_strategic_capacity":  round(strategic_cap, 2),
        "agu_capacity":            round(agu_cap, 2),

        # Actual production starts at 90% of capacity
        "nru_basic_production":      round(basic_cap * 0.9, 2),
        "nru_industrial_production": round(industrial_cap * 0.9, 2),
        "nru_precision_production":  round(precision_cap * 0.9, 2),
        "nru_strategic_production":  round(strategic_cap * 0.9, 2),
        "agu_production":            round(agu_cap * 0.9, 2),

        # Stockpiles = 2 ticks worth of production
        "nru_basic_stockpile":      round(basic_cap * 0.9 * 2, 2),
        "nru_industrial_stockpile": round(industrial_cap * 0.9 * 2, 2),
        "nru_precision_stockpile":  round(precision_cap * 0.9 * 2, 2),
        "nru_strategic_stockpile":  round(strategic_cap * 0.9 * 2, 2),
        "agu_stockpile":            round(agu_cap * 0.9 * 2, 2),
    }


# ---------------------------------------------------------------------------
# MINOR NATIONS (30 nations seeded at Tick 0)
# ---------------------------------------------------------------------------

MINOR_NATIONS = [
    # Middle East
    {"name": "Iran",          "region": "Middle East", "alignment_tendency": "Swing",
     "base_gdp_billions": 22.0,  "population_millions": 28.0,  "industrial_capacity": 40, "military_strength": 45,
     "primary_export_type": "Oil"},
    {"name": "Saudi Arabia",  "region": "Middle East", "alignment_tendency": "Western",
     "base_gdp_billions": 18.0,  "population_millions": 7.5,   "industrial_capacity": 25, "military_strength": 30,
     "primary_export_type": "Oil"},
    {"name": "Iraq",          "region": "Middle East", "alignment_tendency": "Swing",
     "base_gdp_billions": 5.0,   "population_millions": 9.0,   "industrial_capacity": 30, "military_strength": 35,
     "primary_export_type": "Oil"},
    {"name": "Turkey",        "region": "Middle East", "alignment_tendency": "Western",
     "base_gdp_billions": 15.0,  "population_millions": 35.0,  "industrial_capacity": 45, "military_strength": 50,
     "primary_export_type": "Industrial"},
    {"name": "Egypt",         "region": "Middle East", "alignment_tendency": "Swing",
     "base_gdp_billions": 7.0,   "population_millions": 33.0,  "industrial_capacity": 30, "military_strength": 40,
     "primary_export_type": "Agriculture"},

    # Asia
    {"name": "Japan",         "region": "Asia", "alignment_tendency": "Western",
     "base_gdp_billions": 200.0, "population_millions": 104.0, "industrial_capacity": 80, "military_strength": 20,
     "primary_export_type": "Industrial"},
    {"name": "China",         "region": "Asia", "alignment_tendency": "Neutral",
     "base_gdp_billions": 100.0, "population_millions": 800.0, "industrial_capacity": 50, "military_strength": 70,
     "primary_export_type": "Industrial",
     "nuclear_capable": True, "nuclear_stockpile": 75},
    {"name": "India",         "region": "Asia", "alignment_tendency": "Neutral",
     "base_gdp_billions": 55.0,  "population_millions": 550.0, "industrial_capacity": 40, "military_strength": 45,
     "primary_export_type": "Agriculture",
     "nuclear_capable": True, "nuclear_stockpile": 0},
    {"name": "South Korea",   "region": "Asia", "alignment_tendency": "Western",
     "base_gdp_billions": 8.0,   "population_millions": 31.0,  "industrial_capacity": 35, "military_strength": 40,
     "primary_export_type": "Industrial"},
    {"name": "Pakistan",      "region": "Asia", "alignment_tendency": "Western",
     "base_gdp_billions": 10.0,  "population_millions": 60.0,  "industrial_capacity": 25, "military_strength": 35,
     "primary_export_type": "Agriculture"},
    {"name": "Vietnam",       "region": "Asia", "alignment_tendency": "Swing",
     "base_gdp_billions": 3.0,   "population_millions": 40.0,  "industrial_capacity": 15, "military_strength": 50,
     "primary_export_type": "Agriculture"},

    # Europe
    {"name": "France",        "region": "Europe", "alignment_tendency": "Western",
     "base_gdp_billions": 140.0, "population_millions": 50.0,  "industrial_capacity": 70, "military_strength": 55,
     "primary_export_type": "Industrial",
     "nuclear_capable": True, "nuclear_stockpile": 36},
    {"name": "United Kingdom","region": "Europe", "alignment_tendency": "Western",
     "base_gdp_billions": 125.0, "population_millions": 55.0,  "industrial_capacity": 65, "military_strength": 50,
     "primary_export_type": "Industrial",
     "nuclear_capable": True, "nuclear_stockpile": 280},
    {"name": "Sweden",        "region": "Europe", "alignment_tendency": "Neutral",
     "base_gdp_billions": 32.0,  "population_millions": 8.0,   "industrial_capacity": 60, "military_strength": 35,
     "primary_export_type": "Strategic_Metals"},
    {"name": "Switzerland",   "region": "Europe", "alignment_tendency": "Neutral",
     "base_gdp_billions": 18.0,  "population_millions": 6.3,   "industrial_capacity": 55, "military_strength": 25,
     "primary_export_type": "Precision"},
    {"name": "Spain",         "region": "Europe", "alignment_tendency": "Axis",
     "base_gdp_billions": 35.0,  "population_millions": 33.0,  "industrial_capacity": 40, "military_strength": 35,
     "primary_export_type": "Agriculture"},

    # Africa
    {"name": "South Africa",  "region": "Africa", "alignment_tendency": "Western",
     "base_gdp_billions": 18.0,  "population_millions": 22.0,  "industrial_capacity": 45, "military_strength": 40,
     "primary_export_type": "Strategic_Metals",
     "nuclear_capable": True, "nuclear_stockpile": 0},
    {"name": "Nigeria",       "region": "Africa", "alignment_tendency": "Swing",
     "base_gdp_billions": 7.0,   "population_millions": 55.0,  "industrial_capacity": 20, "military_strength": 25,
     "primary_export_type": "Oil"},
    {"name": "Congo",         "region": "Africa", "alignment_tendency": "Swing",
     "base_gdp_billions": 3.5,   "population_millions": 18.0,  "industrial_capacity": 15, "military_strength": 20,
     "primary_export_type": "Strategic_Metals"},
    {"name": "Ethiopia",      "region": "Africa", "alignment_tendency": "Neutral",
     "base_gdp_billions": 2.0,   "population_millions": 25.0,  "industrial_capacity": 10, "military_strength": 25,
     "primary_export_type": "Agriculture"},

    # Americas
    {"name": "Brazil",        "region": "Americas", "alignment_tendency": "Western",
     "base_gdp_billions": 40.0,  "population_millions": 95.0,  "industrial_capacity": 45, "military_strength": 40,
     "primary_export_type": "Agriculture"},
    {"name": "Mexico",        "region": "Americas", "alignment_tendency": "Western",
     "base_gdp_billions": 35.0,  "population_millions": 50.0,  "industrial_capacity": 40, "military_strength": 35,
     "primary_export_type": "Oil"},
    {"name": "Argentina",     "region": "Americas", "alignment_tendency": "Swing",
     "base_gdp_billions": 30.0,  "population_millions": 24.0,  "industrial_capacity": 42, "military_strength": 35,
     "primary_export_type": "Agriculture"},
    {"name": "Canada",        "region": "Americas", "alignment_tendency": "Western",
     "base_gdp_billions": 90.0,  "population_millions": 21.0,  "industrial_capacity": 65, "military_strength": 35,
     "primary_export_type": "Strategic_Metals"},
    {"name": "Cuba",          "region": "Americas", "alignment_tendency": "Swing",
     "base_gdp_billions": 4.0,   "population_millions": 8.5,   "industrial_capacity": 20, "military_strength": 30,
     "primary_export_type": "Agriculture"},

    # Extra swing states
    {"name": "Libya",         "region": "Middle East", "alignment_tendency": "Swing",
     "base_gdp_billions": 5.0,   "population_millions": 2.0,   "industrial_capacity": 20, "military_strength": 25,
     "primary_export_type": "Oil"},
    {"name": "Indonesia",     "region": "Asia", "alignment_tendency": "Swing",
     "base_gdp_billions": 12.0,  "population_millions": 120.0, "industrial_capacity": 25, "military_strength": 35,
     "primary_export_type": "Oil"},
    {"name": "Venezuela",     "region": "Americas", "alignment_tendency": "Swing",
     "base_gdp_billions": 13.0,  "population_millions": 10.0,  "industrial_capacity": 30, "military_strength": 30,
     "primary_export_type": "Oil"},
    {"name": "Morocco",       "region": "Africa", "alignment_tendency": "Western",
     "base_gdp_billions": 3.5,   "population_millions": 15.0,  "industrial_capacity": 20, "military_strength": 25,
     "primary_export_type": "Strategic_Metals"},
    {"name": "Australia",     "region": "Asia", "alignment_tendency": "Western",
     "base_gdp_billions": 45.0,  "population_millions": 12.5,  "industrial_capacity": 55, "military_strength": 30,
     "primary_export_type": "Strategic_Metals"},
]

# ---------------------------------------------------------------------------
# UNIT TYPE COSTS
# ---------------------------------------------------------------------------

UNIT_TYPE_COSTS = [
    {
        "unit_type_name": "M48 Patton",
        "nru_basic_cost": 2.5,
        "nru_industrial_cost": 3.0,
        "nru_precision_cost": 1.5,
        "nru_strategic_cost": 0.2,
        "agu_cost": 0.0,
        "nru_basic_maintenance": 0.3,
        "nru_industrial_maintenance": 0.15,
        "nru_precision_maintenance": 0.06,
        "nru_strategic_maintenance": 0.01,
        "agu_maintenance": 0.0,
    },
]


# ---------------------------------------------------------------------------
# SEED FUNCTIONS
# ---------------------------------------------------------------------------

def seed_nations(cursor):
    cols = list(USA_DATA.keys())
    for data in [USA_DATA, GERMANY_DATA]:
        placeholders = ", ".join(["?"] * len(cols))
        col_names = ", ".join(cols)
        values = [data[c] for c in cols]
        cursor.execute(
            f"INSERT OR IGNORE INTO nations ({col_names}) VALUES ({placeholders})",
            values
        )


def seed_initial_resources(cursor):
    for data in [USA_DATA, GERMANY_DATA]:
        cursor.execute("SELECT id FROM nations WHERE code = ?", (data["code"],))
        row = cursor.fetchone()
        if not row:
            continue
        nation_id = row[0]

        res = _calculate_initial_resources(data)
        cursor.execute("""
            INSERT OR IGNORE INTO nation_resources
            (nation_id, tick_number,
             nru_basic_capacity, nru_industrial_capacity, nru_precision_capacity,
             nru_strategic_capacity, agu_capacity,
             nru_basic_production, nru_industrial_production, nru_precision_production,
             nru_strategic_production, agu_production,
             nru_basic_stockpile, nru_industrial_stockpile, nru_precision_stockpile,
             nru_strategic_stockpile, agu_stockpile)
            VALUES (?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nation_id,
            res["nru_basic_capacity"],    res["nru_industrial_capacity"],
            res["nru_precision_capacity"],res["nru_strategic_capacity"],
            res["agu_capacity"],
            res["nru_basic_production"],   res["nru_industrial_production"],
            res["nru_precision_production"],res["nru_strategic_production"],
            res["agu_production"],
            res["nru_basic_stockpile"],    res["nru_industrial_stockpile"],
            res["nru_precision_stockpile"],res["nru_strategic_stockpile"],
            res["agu_stockpile"],
        ))


def seed_minor_nations(cursor):
    for mn in MINOR_NATIONS:
        cursor.execute("""
            INSERT OR IGNORE INTO minor_nations
            (name, region, alignment_tendency, base_gdp_billions, population_millions,
             industrial_capacity, military_strength, primary_export_type,
             nuclear_capable, nuclear_stockpile)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mn["name"],
            mn.get("region"),
            mn.get("alignment_tendency"),
            mn.get("base_gdp_billions"),
            mn.get("population_millions"),
            mn.get("industrial_capacity", 50),
            mn.get("military_strength", 30),
            mn.get("primary_export_type"),
            int(mn.get("nuclear_capable", False)),
            mn.get("nuclear_stockpile", 0),
        ))


def seed_minor_nation_diplomacy(cursor):
    """Seed tick-0 diplomatic state for all minor nations."""
    cursor.execute("SELECT id, alignment_tendency FROM minor_nations")
    nations = cursor.fetchall()

    for mn_id, tendency in nations:
        if tendency == "Western":
            approval_usa, approval_ger = 65.0, 35.0
            usa_app, ger_app = 60.0, 40.0
        elif tendency == "Axis":
            approval_usa, approval_ger = 35.0, 65.0
            usa_app, ger_app = 40.0, 60.0
        elif tendency == "Neutral":
            approval_usa, approval_ger = 50.0, 50.0
            usa_app, ger_app = 50.0, 50.0
        else:  # Swing
            approval_usa, approval_ger = 50.0, 50.0
            usa_app, ger_app = 48.0, 48.0

        cursor.execute("""
            INSERT OR IGNORE INTO minor_nation_diplomacy
            (minor_nation_id, tick_number,
             approval_of_usa, approval_of_germany,
             usa_approval_of_them, germany_approval_of_them,
             alignment_shift_risk, influence_battle_score)
            VALUES (?, 0, ?, ?, ?, ?, ?, 0)
        """, (mn_id, approval_usa, approval_ger, usa_app, ger_app,
              15.0 if tendency == "Swing" else 5.0))


def seed_unit_type_costs(cursor):
    for cost in UNIT_TYPE_COSTS:
        cursor.execute(
            "SELECT id FROM unit_types WHERE name = ?",
            (cost["unit_type_name"],)
        )
        row = cursor.fetchone()
        if not row:
            continue
        unit_type_id = row[0]
        cursor.execute("""
            INSERT OR IGNORE INTO unit_type_costs
            (unit_type_id, nru_basic_cost, nru_industrial_cost, nru_precision_cost,
             nru_strategic_cost, agu_cost,
             nru_basic_maintenance, nru_industrial_maintenance, nru_precision_maintenance,
             nru_strategic_maintenance, agu_maintenance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            unit_type_id,
            cost["nru_basic_cost"],       cost["nru_industrial_cost"],
            cost["nru_precision_cost"],   cost["nru_strategic_cost"],
            cost["agu_cost"],
            cost["nru_basic_maintenance"],cost["nru_industrial_maintenance"],
            cost["nru_precision_maintenance"],cost["nru_strategic_maintenance"],
            cost["agu_maintenance"],
        ))


def seed_tick_history(cursor):
    cursor.execute("""
        INSERT OR IGNORE INTO tick_history
        (tick_number, game_date, total_battles, total_units_destroyed, events_summary)
        VALUES (0, 'Jan 1970', 0, 0, '{"note": "Game start"}')
    """)


def seed_all():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    seed_nations(cursor)
    seed_initial_resources(cursor)
    seed_minor_nations(cursor)
    seed_minor_nation_diplomacy(cursor)
    seed_unit_type_costs(cursor)
    seed_tick_history(cursor)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_all()
    print("1970 seed data inserted successfully.")
