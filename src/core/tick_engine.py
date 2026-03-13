"""
EVERFALL ENGINE - Main Tick Engine
Orchestrates all simulation subsystems and updates game state.

TICK FLOW:
1. Read pending decisions from database
2. Update population & demographics
3. Update labor market
4. Update capital stock & TFP
5. Update resources (NRU/AGU production, imports, consumption)
6. Update economy (money supply, revenue, spending, debt)
7. Update institutional health (cohesion, confidence, stability)
8. Process production queue
9. Resolve combat
10. Update space race
11. Process events
12. Write results to database
13. Generate reports

Each tick = 3 months in-game time
Start date: January 1, 1970
"""

import sqlite3
import datetime
from typing import Dict, List

DB_PATH = "everfall.db"

# Import subsystem modules (to be created)
# from population_engine import update_population
# from labor_engine import update_labor_market
# from capital_engine import update_capital_stock
# from resource_engine import update_resources
# from economy_engine import update_economy
# from cohesion_engine import update_institutional_health
# from production_engine import process_production_queue
# from combat_engine import resolve_combat
# from space_engine import update_space_race


class TickEngine:
    """Main simulation engine"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.current_tick = 0
        self.game_start_date = datetime.date(1970, 1, 1)
    
    def get_game_date(self, tick_number):
        """Convert tick number to in-game date"""
        months_elapsed = tick_number * 3
        years = months_elapsed // 12
        months = months_elapsed % 12
        
        year = self.game_start_date.year + years
        month = self.game_start_date.month + months
        
        # Handle month overflow
        while month > 12:
            month -= 12
            year += 1
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        return f"{month_names[month-1]} {year}"
    
    def get_current_tick(self):
        """Get the latest tick number from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT MAX(tick_number) FROM tick_history")
        result = cursor.fetchone()[0]
        
        conn.close()
        
        return result if result is not None else -1
    
    def initialize_tick_0(self):
        """
        Initialize tick 0 with starting conditions.
        Should be called after seeding the database.
        """
        print("Initializing Tick 0...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tick 0 history entry
        cursor.execute("""
            INSERT INTO tick_history (tick_number, game_date)
            VALUES (0, ?)
        """, (self.get_game_date(0),))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Tick 0 initialized: {self.get_game_date(0)}")
    
    def run_tick(self, tick_number):
        """
        Execute one full simulation tick.
        """
        print(f"\n{'='*60}")
        print(f"RUNNING TICK {tick_number}: {self.get_game_date(tick_number)}")
        print(f"{'='*60}\n")
        
        # Get both nations (USA = 1, Germany = 2)
        nations = [1, 2]
        
        # 1. READ PENDING DECISIONS
        print("1. Reading pending decisions...")
        decisions = self._read_decisions(tick_number)
        print(f"   → {len(decisions)} decisions to process")
        
        # 2. UPDATE POPULATION & DEMOGRAPHICS
        print("\n2. Updating population & demographics...")
        for nation_id in nations:
            self._update_population(nation_id, tick_number)
        
        # 3. UPDATE LABOR MARKET
        print("\n3. Updating labor market...")
        for nation_id in nations:
            self._update_labor_market(nation_id, tick_number)
        
        # 4. UPDATE CAPITAL STOCK & TFP
        print("\n4. Updating capital stock & productivity...")
        for nation_id in nations:
            self._update_capital_stock(nation_id, tick_number)
            self._update_tfp(nation_id, tick_number)
        
        # 5. UPDATE RESOURCES
        print("\n5. Updating resources (NRU/AGU)...")
        for nation_id in nations:
            self._update_resources(nation_id, tick_number)
        
        # 6. UPDATE ECONOMY
        print("\n6. Updating economy...")
        for nation_id in nations:
            self._update_economy(nation_id, tick_number)
        
        # 7. UPDATE INSTITUTIONAL HEALTH
        print("\n7. Updating institutional health...")
        for nation_id in nations:
            self._update_institutional_health(nation_id, tick_number)
        
        # 8. PROCESS PRODUCTION QUEUE
        print("\n8. Processing production queue...")
        for nation_id in nations:
            self._process_production(nation_id, tick_number)
        
        # 9. RESOLVE COMBAT
        print("\n9. Resolving combat...")
        combat_results = self._resolve_combat(tick_number)
        
        # 10. UPDATE SPACE RACE
        print("\n10. Updating space race...")
        for nation_id in nations:
            self._update_space_race(nation_id, tick_number)
        
        # 11. PROCESS EVENTS
        print("\n11. Processing events...")
        events = self._process_events(tick_number)
        
        # 12. RECORD TICK HISTORY
        print("\n12. Recording tick history...")
        self._record_tick_history(tick_number, combat_results, events)
        
        # 13. GENERATE REPORT
        print("\n13. Generating report...")
        self._generate_report(tick_number)
        
        print(f"\n✓ Tick {tick_number} completed successfully")
        print(f"{'='*60}\n")
    
    # ========================================
    # DECISION PROCESSING
    # ========================================
    
    def _read_decisions(self, tick_number):
        """Read and approve pending decisions for this tick"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM pending_decisions
            WHERE tick_number = ? AND status = 'pending'
        """, (tick_number,))
        
        decisions = cursor.fetchall()
        
        # Mark as approved (GM has pre-approved them)
        cursor.execute("""
            UPDATE pending_decisions
            SET status = 'approved'
            WHERE tick_number = ? AND status = 'pending'
        """, (tick_number,))
        
        conn.commit()
        conn.close()
        
        return decisions
    
    # ========================================
    # STATE UPDATE FUNCTIONS (Stubs - to be implemented)
    # ========================================
    
    def _update_population(self, nation_id, tick_number):
        """
        Update population from births, deaths, migration, and war casualties.
        STUB - Full implementation in population_engine.py
        """
        print(f"   → Nation {nation_id}: Population update (STUB)")
        # TODO: Implement full population model
        pass
    
    def _update_labor_market(self, nation_id, tick_number):
        """
        Update labor force, employment, participation rate.
        STUB - Full implementation in labor_engine.py
        """
        print(f"   → Nation {nation_id}: Labor market update (STUB)")
        # TODO: Implement labor market model
        pass
    
    def _update_capital_stock(self, nation_id, tick_number):
        """
        Update capital stock from investment and depreciation.
        STUB - Full implementation in capital_engine.py
        """
        print(f"   → Nation {nation_id}: Capital stock update (STUB)")
        # TODO: Implement capital accumulation model
        pass
    
    def _update_tfp(self, nation_id, tick_number):
        """
        Update Total Factor Productivity from R&D spending and innovation.
        STUB - Full implementation in capital_engine.py
        """
        print(f"   → Nation {nation_id}: TFP update (STUB)")
        # TODO: Implement TFP growth model
        pass
    
    def _update_resources(self, nation_id, tick_number):
        """
        Update NRU/AGU production, consumption, imports, exports.
        STUB - Full implementation in resource_engine.py
        """
        print(f"   → Nation {nation_id}: Resource update (STUB)")
        # TODO: Implement resource model with Leontief I-O
        pass
    
    def _update_economy(self, nation_id, tick_number):
        """
        Update money supply, revenue, spending, debt.
        STUB - Full implementation in economy_engine.py
        """
        print(f"   → Nation {nation_id}: Economic update (STUB)")
        # TODO: Implement fiscal/monetary model
        pass
    
    def _update_institutional_health(self, nation_id, tick_number):
        """
        Update cohesion, stability, morale, confidence.
        STUB - Full implementation in cohesion_engine.py
        """
        print(f"   → Nation {nation_id}: Institutional health update (STUB)")
        # TODO: Implement cohesion decay model
        pass
    
    def _process_production(self, nation_id, tick_number):
        """
        Process production queue, complete units.
        STUB - Full implementation in production_engine.py
        """
        print(f"   → Nation {nation_id}: Production processing (STUB)")
        # TODO: Implement production system
        pass
    
    def _resolve_combat(self, tick_number):
        """
        Resolve all combat (battles, insurgencies).
        STUB - Full implementation in combat_engine.py
        """
        print(f"   → Combat resolution (STUB)")
        # TODO: Implement Lanchester + Monte Carlo combat
        return {}
    
    def _update_space_race(self, nation_id, tick_number):
        """
        Update space race progress, launches, moon base.
        STUB - Full implementation in space_engine.py
        """
        print(f"   → Nation {nation_id}: Space race update (STUB)")
        # TODO: Implement space race mechanics
        pass
    
    def _process_events(self, tick_number):
        """
        Generate and process random/scripted events.
        STUB - Full implementation in events_engine.py
        """
        print(f"   → Event processing (STUB)")
        # TODO: Implement event system
        return []
    
    # ========================================
    # HISTORY & REPORTING
    # ========================================
    
    def _record_tick_history(self, tick_number, combat_results, events):
        """Record this tick in history table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tick_history 
            (tick_number, game_date, total_battles, total_units_destroyed)
            VALUES (?, ?, ?, ?)
        """, (
            tick_number,
            self.get_game_date(tick_number),
            combat_results.get('total_battles', 0),
            combat_results.get('total_destroyed', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def _generate_report(self, tick_number):
        """Generate summary report for GM"""
        from metrics import get_all_metrics
        
        print("\n" + "="*60)
        print(f"TICK {tick_number} SUMMARY REPORT")
        print("="*60)
        
        for nation_id, nation_name in [(1, "USA"), (2, "Germany")]:
            print(f"\n{nation_name}:")
            
            # Get metrics
            metrics = get_all_metrics(nation_id, tick_number)
            
            print(f"  GDP: ${metrics['gdp']:.1f}B")
            print(f"  GDP per capita: ${metrics['gdp_per_capita']:.0f}")
            print(f"  GDP Growth: {metrics['real_gdp_growth']*100:.2f}%")
            print(f"  Inflation: {metrics['inflation_rate']*100:.2f}%")
            print(f"  Unemployment: {metrics['unemployment_rate']*100:.2f}%")
            print(f"  Debt/GDP: {metrics['debt_to_gdp_ratio']*100:.1f}%")
            print(f"  Trade Balance: ${metrics['trade_balance']:.1f}B")
        
        print("\n" + "="*60 + "\n")


# ========================================
# CLI INTERFACE
# ========================================

def main():
    """Main entry point for manual tick execution"""
    import sys
    
    engine = TickEngine()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            # Initialize tick 0
            engine.initialize_tick_0()
        
        elif command == "run":
            # Run next tick
            current_tick = engine.get_current_tick()
            next_tick = current_tick + 1
            engine.run_tick(next_tick)
        
        elif command == "run-multiple":
            # Run multiple ticks
            num_ticks = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            current_tick = engine.get_current_tick()
            
            for i in range(num_ticks):
                next_tick = current_tick + i + 1
                engine.run_tick(next_tick)
        
        else:
            print(f"Unknown command: {command}")
    
    else:
        print("Everfall Engine - Tick Runner")
        print("\nUsage:")
        print("  python tick_engine.py init              - Initialize tick 0")
        print("  python tick_engine.py run               - Run next tick")
        print("  python tick_engine.py run-multiple N    - Run N ticks")


if __name__ == "__main__":
    main()
