"""
EVERFALL ENGINE - Test Suite for Refactored Architecture
Tests the separation of config vs state, and derived metrics calculation.
"""

import sqlite3
import sys

# Add current directory to path for imports
sys.path.insert(0, '/home/claude')

from db_schema_refactored import initialize_database
from db_seed_refactored import seed_all
from metrics import get_all_metrics, calculate_gdp, calculate_inflation_rate

DB_PATH = "everfall.db"


def test_database_structure():
    """Test that all tables exist"""
    print("\n" + "="*60)
    print("TEST 1: Database Structure")
    print("="*60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = [
        'nations', 'nation_state', 'nation_resources',
        'characters', 'buffs',
        'minor_nations', 'minor_nation_diplomacy',
        'manufacturers', 'unit_types', 'unit_type_costs',
        'military_units', 'army_groups', 'production_queue',
        'tick_history', 'pending_decisions', 'events'
    ]
    
    print("\nRequired tables:")
    for table in required_tables:
        status = "✓" if table in tables else "✗"
        print(f"  {status} {table}")
    
    missing = set(required_tables) - set(tables)
    if missing:
        print(f"\n✗ FAILED: Missing tables: {missing}")
        return False
    else:
        print("\n✓ PASSED: All required tables exist")
        return True
    
    conn.close()


def test_seeded_data():
    """Test that initial data was seeded correctly"""
    print("\n" + "="*60)
    print("TEST 2: Seeded Data")
    print("="*60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check nations
    cursor.execute("SELECT COUNT(*) FROM nations")
    nation_count = cursor.fetchone()[0]
    
    if nation_count != 2:
        print(f"✗ FAILED: Expected 2 nations, got {nation_count}")
        return False
    
    print(f"✓ Nations: {nation_count}")
    
    # Check tick 0 state
    cursor.execute("SELECT COUNT(*) FROM nation_state WHERE tick_number = 0")
    state_count = cursor.fetchone()[0]
    
    if state_count != 2:
        print(f"✗ FAILED: Expected 2 state records for tick 0, got {state_count}")
        return False
    
    print(f"✓ Tick 0 state: {state_count}")
    
    # Check tick 0 resources
    cursor.execute("SELECT COUNT(*) FROM nation_resources WHERE tick_number = 0")
    resource_count = cursor.fetchone()[0]
    
    if resource_count != 2:
        print(f"✗ FAILED: Expected 2 resource records for tick 0, got {resource_count}")
        return False
    
    print(f"✓ Tick 0 resources: {resource_count}")
    
    # Verify USA data
    cursor.execute("""
        SELECT population, nuclear_stockpile, institutional_cohesion
        FROM nation_state WHERE nation_id = 1 AND tick_number = 0
    """)
    usa_data = cursor.fetchone()
    
    if usa_data:
        pop, nukes, cohesion = usa_data
        print(f"\nUSA (Tick 0):")
        print(f"  Population: {pop}M")
        print(f"  Nuclear stockpile: {nukes}")
        print(f"  Institutional cohesion: {cohesion}/100")
        
        if pop != 210.0 or nukes != 15300:
            print("✗ FAILED: USA data mismatch")
            return False
    else:
        print("✗ FAILED: No USA data found")
        return False
    
    # Verify Germany data
    cursor.execute("""
        SELECT population, nuclear_stockpile, institutional_cohesion
        FROM nation_state WHERE nation_id = 2 AND tick_number = 0
    """)
    ger_data = cursor.fetchone()
    
    if ger_data:
        pop, nukes, cohesion = ger_data
        print(f"\nGermany (Tick 0):")
        print(f"  Population: {pop}M")
        print(f"  Nuclear stockpile: {nukes}")
        print(f"  Institutional cohesion: {cohesion}/100")
        
        if pop != 450.0 or nukes != 12500:
            print("✗ FAILED: Germany data mismatch")
            return False
    else:
        print("✗ FAILED: No Germany data found")
        return False
    
    print("\n✓ PASSED: All seeded data verified")
    conn.close()
    return True


def test_derived_metrics():
    """Test that derived metrics calculate correctly"""
    print("\n" + "="*60)
    print("TEST 3: Derived Metrics Calculation")
    print("="*60)
    
    # Test USA metrics
    print("\nUSA Metrics (Tick 0):")
    try:
        gdp = calculate_gdp(1, 0)
        print(f"  GDP: ${gdp:.2f}B")
        
        if gdp <= 0:
            print("✗ FAILED: GDP should be positive")
            return False
        
        metrics = get_all_metrics(1, 0)
        
        print(f"  GDP per capita: ${metrics['gdp_per_capita']:.2f}")
        print(f"  Inflation: {metrics['inflation_rate']*100:.2f}%")
        print(f"  Unemployment: {metrics['unemployment_rate']*100:.2f}%")
        print(f"  Debt/GDP: {metrics['debt_to_gdp_ratio']*100:.1f}%")
        print(f"  MPC: {metrics['mpc']:.3f}")
        
        # Sanity checks
        if metrics['gdp_per_capita'] <= 0:
            print("✗ FAILED: GDP per capita should be positive")
            return False
        
        if not (0 <= metrics['unemployment_rate'] <= 1):
            print("✗ FAILED: Unemployment rate out of bounds")
            return False
        
    except Exception as e:
        print(f"✗ FAILED: Error calculating metrics: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test Germany metrics
    print("\nGermany Metrics (Tick 0):")
    try:
        gdp = calculate_gdp(2, 0)
        print(f"  GDP: ${gdp:.2f}B")
        
        metrics = get_all_metrics(2, 0)
        
        print(f"  GDP per capita: ${metrics['gdp_per_capita']:.2f}")
        print(f"  Inflation: {metrics['inflation_rate']*100:.2f}%")
        print(f"  Unemployment: {metrics['unemployment_rate']*100:.2f}%")
        print(f"  Debt/GDP: {metrics['debt_to_gdp_ratio']*100:.1f}%")
        print(f"  MPC: {metrics['mpc']:.3f}")
        
    except Exception as e:
        print(f"✗ FAILED: Error calculating metrics: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✓ PASSED: All metrics calculated successfully")
    return True


def test_config_vs_state_separation():
    """Test that config and state are properly separated"""
    print("\n" + "="*60)
    print("TEST 4: Config vs State Separation")
    print("="*60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Config should NOT have population
    cursor.execute("PRAGMA table_info(nations)")
    nation_columns = [row[1] for row in cursor.fetchall()]
    
    if 'population' in nation_columns:
        print("✗ FAILED: 'population' should not be in nations table")
        return False
    
    print("✓ nations table: No dynamic state variables")
    
    # State should have population
    cursor.execute("PRAGMA table_info(nation_state)")
    state_columns = [row[1] for row in cursor.fetchall()]
    
    if 'population' not in state_columns:
        print("✗ FAILED: 'population' should be in nation_state table")
        return False
    
    print("✓ nation_state table: Has dynamic state variables")
    
    # Config should have sector allocations
    if 'consumer_goods_pct' not in nation_columns:
        print("✗ FAILED: 'consumer_goods_pct' should be in nations table")
        return False
    
    print("✓ nations table: Has policy configuration")
    
    print("\n✓ PASSED: Config and state properly separated")
    conn.close()
    return True


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*60)
    print("EVERFALL ENGINE - REFACTORED ARCHITECTURE TEST SUITE")
    print("="*60)
    
    # Initialize fresh database
    print("\nInitializing database...")
    initialize_database()
    
    print("\nSeeding initial data...")
    seed_all()
    
    # Run tests
    tests = [
        test_database_structure,
        test_seeded_data,
        test_config_vs_state_separation,
        test_derived_metrics
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n✗ {total - passed} TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
