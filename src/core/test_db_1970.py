"""
Verification script for the 1970 Cold War database.
Run from the project root: python -m src.core.test_db_1970
"""

import sqlite3
import os
import sys

# Allow running from project root without package install
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.db_init_1970 import initialize_database_1970, verify_tables, EXPECTED_TABLES
from src.core.db_seed_1970 import seed_all

DB_PATH = "everfall.db"


def _fmt_b(val):
    """Format billions value."""
    if val is None:
        return "N/A"
    return f"${val:,.0f}B"


def _fmt_m(val):
    """Format millions value."""
    if val is None:
        return "N/A"
    return f"{val:,.1f}M"


def run_tests():
    # -----------------------------------------------------------------------
    # 1. Wipe and reinitialise from scratch
    # -----------------------------------------------------------------------
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing {DB_PATH}")

    print("Initializing schema...")
    initialize_database_1970()

    print("Seeding 1970 data...")
    seed_all()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print()
    print("=" * 60)
    print("  1970 COLD WAR DATABASE INITIALIZED")
    print("=" * 60)

    # -----------------------------------------------------------------------
    # 2. Nations side-by-side
    # -----------------------------------------------------------------------
    cursor.execute("SELECT * FROM nations ORDER BY code")
    nations = cursor.fetchall()

    print()
    print("NATIONS:")
    for n in nations:
        print(
            f"  {n['code']}: {_fmt_b(n['base_gdp_billions'])} GDP"
            f" | Pop: {_fmt_m(n['population_millions'])}"
            f" | Nukes: {n['nuclear_stockpile']:,}"
            f" | Cohesion: {n['base_institutional_cohesion']:.0f}/100"
            f" | Stability: {n['political_stability']:.0f}/100"
        )
    assert len(nations) == 2, f"Expected 2 nations, got {len(nations)}"

    # -----------------------------------------------------------------------
    # 3. Resource capacities
    # -----------------------------------------------------------------------
    print()
    print("RESOURCE PRODUCTION CAPACITIES (Tick 0):")
    cursor.execute("""
        SELECT n.code,
               nr.nru_basic_capacity, nr.nru_industrial_capacity,
               nr.nru_precision_capacity, nr.nru_strategic_capacity,
               nr.agu_capacity
        FROM nation_resources nr
        JOIN nations n ON n.id = nr.nation_id
        WHERE nr.tick_number = 0
        ORDER BY n.code
    """)
    for row in cursor.fetchall():
        print(
            f"  {row['code']}: Basic={row['nru_basic_capacity']:.0f}"
            f"  Industrial={row['nru_industrial_capacity']:.0f}"
            f"  Precision={row['nru_precision_capacity']:.0f}"
            f"  Strategic={row['nru_strategic_capacity']:.0f}"
            f"  AGU={row['agu_capacity']:.0f}"
        )

    print()
    print("RESOURCE STOCKPILES (Tick 0):")
    cursor.execute("""
        SELECT n.code,
               nr.nru_basic_stockpile, nr.nru_industrial_stockpile,
               nr.nru_precision_stockpile, nr.nru_strategic_stockpile,
               nr.agu_stockpile
        FROM nation_resources nr
        JOIN nations n ON n.id = nr.nation_id
        WHERE nr.tick_number = 0
        ORDER BY n.code
    """)
    for row in cursor.fetchall():
        print(
            f"  {row['code']}: Basic={row['nru_basic_stockpile']:.0f}"
            f"  Industrial={row['nru_industrial_stockpile']:.0f}"
            f"  Precision={row['nru_precision_stockpile']:.0f}"
            f"  Strategic={row['nru_strategic_stockpile']:.0f}"
            f"  AGU={row['agu_stockpile']:.0f}"
        )

    # -----------------------------------------------------------------------
    # 4. Nuclear stockpiles
    # -----------------------------------------------------------------------
    print()
    print("NUCLEAR ARSENALS:")
    for n in nations:
        print(f"  {n['code']}: {n['nuclear_stockpile']:,} warheads")

    # -----------------------------------------------------------------------
    # 5. Space race
    # -----------------------------------------------------------------------
    print()
    print("SPACE RACE:")
    for n in nations:
        print(
            f"  {n['code']}: {n['rocket_production_capacity']} launches/yr"
            f" | {n['lunar_payload_capacity']:.0f}t lunar payload"
            f" | Prestige: {n['space_prestige_score']:.0f}"
            f" | Moon base capacity: {n['moon_base_personnel_capacity']}"
        )

    # -----------------------------------------------------------------------
    # 6. Active conflicts
    # -----------------------------------------------------------------------
    print()
    print("ACTIVE CONFLICTS:")
    for n in nations:
        if n["japan_insurgency_intensity"] > 0:
            print(f"  Japan Insurgency ({n['code']}): {n['japan_insurgency_intensity']:.0f}/100 intensity")
        if n["siberian_insurgency_intensity"] > 0:
            print(f"  Siberian Insurgency ({n['code']}): {n['siberian_insurgency_intensity']:.0f}/100 intensity")

    # -----------------------------------------------------------------------
    # 7. Economic quick-view
    # -----------------------------------------------------------------------
    print()
    print("ECONOMIC OVERVIEW:")
    for n in nations:
        print(
            f"  {n['code']}: Inflation={n['inflation_rate']*100:.1f}%"
            f" | Unemployment={n['unemployment_rate']*100:.1f}%"
            f" | Trade balance={_fmt_b(n['trade_balance'])}"
            f" | Debt/GDP={n['debt_to_gdp_ratio']*100:.1f}%"
        )

    # -----------------------------------------------------------------------
    # 8. Budget breakdown
    # -----------------------------------------------------------------------
    print()
    print("DEFENSE BUDGET:")
    for n in nations:
        print(
            f"  {n['code']}: Total={_fmt_b(n['defense_spending'])}"
            f" ({n['defense_spending_pct_gdp']*100:.1f}% GDP)"
            f" | Ops={_fmt_b(n['defense_operations_spending'])}"
            f" | Procurement={_fmt_b(n['defense_procurement_spending'])}"
            f" | R&D={_fmt_b(n['defense_rd_spending'])}"
        )

    # -----------------------------------------------------------------------
    # 9. Minor nations summary
    # -----------------------------------------------------------------------
    cursor.execute("SELECT COUNT(*) FROM minor_nations")
    mn_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT region, COUNT(*) as cnt
        FROM minor_nations
        GROUP BY region
        ORDER BY region
    """)
    regions = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*) FROM minor_nations WHERE nuclear_capable = 1
    """)
    nuke_capable = cursor.fetchone()[0]

    print()
    print(f"MINOR NATIONS: {mn_count} total, {nuke_capable} nuclear-capable")
    for r in regions:
        print(f"  {r['region']}: {r['cnt']}")

    # -----------------------------------------------------------------------
    # 10. Diplomacy snapshot
    # -----------------------------------------------------------------------
    cursor.execute("""
        SELECT alignment_tendency, COUNT(*) as cnt,
               AVG(md.approval_of_usa) as avg_usa,
               AVG(md.approval_of_germany) as avg_ger
        FROM minor_nations mn
        JOIN minor_nation_diplomacy md ON md.minor_nation_id = mn.id
        WHERE md.tick_number = 0
        GROUP BY alignment_tendency
        ORDER BY alignment_tendency
    """)
    print()
    print("DIPLOMACY BY ALIGNMENT (Tick 0 approvals):")
    for row in cursor.fetchall():
        print(
            f"  {row['alignment_tendency']:10s}: {row['cnt']} nations"
            f" | USA approval={row['avg_usa']:.0f}"
            f" | GER approval={row['avg_ger']:.0f}"
        )

    # -----------------------------------------------------------------------
    # 11. Table verification
    # -----------------------------------------------------------------------
    print()
    print("TABLE VERIFICATION:")
    existing, missing = verify_tables()
    for table in EXPECTED_TABLES:
        status = "OK" if table in existing else "MISSING"
        print(f"  {table:<30} {status}")

    conn.close()

    # -----------------------------------------------------------------------
    # Final status
    # -----------------------------------------------------------------------
    print()
    if missing:
        print(f"WARNING: {len(missing)} missing table(s): {missing}")
        sys.exit(1)
    else:
        print(f"All {len(EXPECTED_TABLES)} tables created successfully.")
        print("Database ready for simulation.")


if __name__ == "__main__":
    run_tests()
