"""
EVERFALL ENGINE - Derived Metrics Module
All calculated metrics that are never stored in the database.

These functions compute values on-demand from stored state.
"""

import sqlite3
import math

DB_PATH = "everfall.db"

# ========================================
# HELPER FUNCTIONS
# ========================================

def get_nation_state(nation_id, tick_number):
    """Get stored state for a nation at a specific tick"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM nation_state
        WHERE nation_id = ? AND tick_number = ?
    """, (nation_id, tick_number))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    # Convert to dict
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


def get_nation_config(nation_id):
    """Get static configuration for a nation"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM nations WHERE id = ?", (nation_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


def get_nation_resources(nation_id, tick_number):
    """Get resource state for a nation at a specific tick"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM nation_resources
        WHERE nation_id = ? AND tick_number = ?
    """, (nation_id, tick_number))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


def get_buffs(target_type, target_id, stat_name, tick_number):
    """Get all active buffs for a specific stat"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM buffs
        WHERE target_type = ?
        AND target_id = ?
        AND stat_name = ?
        AND is_active = 1
        AND (expires_tick IS NULL OR expires_tick >= ?)
    """, (target_type, target_id, stat_name, tick_number))
    
    rows = cursor.fetchall()
    conn.close()
    
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def apply_buffs(base_value, buffs):
    """
    Apply buffs to a base value.
    Additive buffs applied first, then multiplicative.
    """
    value = base_value
    
    # Apply additive buffs first
    for buff in buffs:
        if buff['modifier_type'] == 'additive':
            value += buff['value']
    
    # Then multiplicative
    for buff in buffs:
        if buff['modifier_type'] == 'multiplicative':
            value *= buff['value']
    
    return value


# ========================================
# PRODUCTION FUNCTION
# ========================================

def calculate_gdp(nation_id, tick_number):
    """
    Calculate GDP using Cobb-Douglas production function.
    Y = A * L^α * K^(1-α)
    
    Where:
    - Y = GDP
    - A = Total Factor Productivity (TFP)
    - L = Employed labor
    - K = Capital stock
    - α = Labor share of output (typically 0.65)
    """
    state = get_nation_state(nation_id, tick_number)
    if not state:
        return 0.0
    
    A = state['tfp']
    L = state['employed']
    K = state['capital_stock']
    
    alpha = 0.65  # Labor share (standard for developed economies)
    
    # Apply buffs to TFP
    tfp_buffs = get_buffs('nation', nation_id, 'tfp', tick_number)
    A = apply_buffs(A, tfp_buffs)
    
    gdp = A * (L ** alpha) * (K ** (1 - alpha))
    
    # Apply GDP buffs (from policies, events, etc.)
    gdp_buffs = get_buffs('nation', nation_id, 'gdp', tick_number)
    gdp = apply_buffs(gdp, gdp_buffs)
    
    return gdp


def calculate_real_gdp_growth(nation_id, tick_number):
    """
    Calculate real GDP growth rate from previous tick.
    """
    if tick_number == 0:
        return 0.0
    
    current_gdp = calculate_gdp(nation_id, tick_number)
    previous_gdp = calculate_gdp(nation_id, tick_number - 1)
    
    if previous_gdp == 0:
        return 0.0
    
    growth_rate = (current_gdp / previous_gdp) - 1.0
    
    return growth_rate


# ========================================
# DERIVED ECONOMIC METRICS
# ========================================

def calculate_gdp_per_capita(nation_id, tick_number):
    """GDP per person"""
    state = get_nation_state(nation_id, tick_number)
    if not state or state['population'] == 0:
        return 0.0
    
    gdp = calculate_gdp(nation_id, tick_number)
    return gdp / state['population']


def calculate_inflation_rate(nation_id, tick_number):
    """
    Calculate inflation using Quantity Theory of Money.
    MV = PY  =>  %ΔP = %ΔM + %ΔV - %ΔY
    
    Inflation ≈ Money Supply Growth - Real GDP Growth + Velocity Change
    """
    if tick_number == 0:
        return 0.02  # Default 2%
    
    current_state = get_nation_state(nation_id, tick_number)
    previous_state = get_nation_state(nation_id, tick_number - 1)
    
    if not current_state or not previous_state:
        return 0.02
    
    # Money supply growth
    m_growth = (current_state['money_supply'] / previous_state['money_supply']) - 1.0
    
    # Real GDP growth
    real_gdp_growth = calculate_real_gdp_growth(nation_id, tick_number)
    
    # Velocity change (assume relatively stable for now)
    current_velocity = calculate_velocity_of_money(nation_id, tick_number)
    previous_velocity = calculate_velocity_of_money(nation_id, tick_number - 1)
    v_change = (current_velocity / previous_velocity) - 1.0 if previous_velocity > 0 else 0.0
    
    # Inflation = Money growth - Real growth + Velocity change
    inflation = m_growth - real_gdp_growth + v_change
    
    # Floor at -10% (severe deflation cap), ceiling at 50% (hyperinflation)
    inflation = max(-0.10, min(0.50, inflation))
    
    return inflation


def calculate_unemployment_rate(nation_id, tick_number):
    """
    Unemployment rate = (Labor Force - Employed) / Labor Force
    """
    state = get_nation_state(nation_id, tick_number)
    if not state or state['labor_force'] == 0:
        return 0.05  # Default 5%
    
    unemployed = state['labor_force'] - state['employed']
    unemployment_rate = unemployed / state['labor_force']
    
    return max(0.0, min(1.0, unemployment_rate))


def calculate_mpc(nation_id, tick_number):
    """
    Marginal Propensity to Consume.
    Varies with:
    - Income level (wealth effect)
    - Consumer confidence
    - Inflation expectations
    """
    state = get_nation_state(nation_id, tick_number)
    if not state:
        return 0.65
    
    gdp_per_capita = calculate_gdp_per_capita(nation_id, tick_number)
    
    # Base MPC decreases with wealth (rich people save more)
    # Assume $50k GDP/capita = 90% MPC, linear decrease
    base_mpc = 0.90 - (gdp_per_capita / 50000.0) * 0.30
    base_mpc = max(0.40, min(0.95, base_mpc))
    
    # Consumer confidence effect
    confidence = state['consumer_confidence']
    confidence_modifier = (confidence - 0.5) * 0.2  # ±10% effect
    
    # Inflation expectation effect (high inflation = spend now)
    inflation = calculate_inflation_rate(nation_id, tick_number)
    inflation_modifier = min(inflation * 2.0, 0.1)  # Up to +10% from inflation
    
    mpc = base_mpc + confidence_modifier + inflation_modifier
    
    return max(0.40, min(0.95, mpc))


def calculate_velocity_of_money(nation_id, tick_number):
    """
    Velocity of Money = GDP / Money Supply
    """
    state = get_nation_state(nation_id, tick_number)
    if not state or state['money_supply'] == 0:
        return 4.0  # Typical value
    
    gdp = calculate_gdp(nation_id, tick_number)
    velocity = gdp / state['money_supply']
    
    return velocity


def calculate_real_interest_rate(nation_id, tick_number):
    """
    Real Interest Rate = Nominal Rate - Inflation Rate
    Fisher Equation
    """
    config = get_nation_config(nation_id)
    if not config:
        return 0.02
    
    nominal_rate = config['nominal_interest_rate']
    inflation = calculate_inflation_rate(nation_id, tick_number)
    
    real_rate = nominal_rate - inflation
    
    return real_rate


def calculate_debt_to_gdp_ratio(nation_id, tick_number):
    """
    National Debt / GDP
    """
    state = get_nation_state(nation_id, tick_number)
    if not state:
        return 0.0
    
    gdp = calculate_gdp(nation_id, tick_number)
    if gdp == 0:
        return 0.0
    
    ratio = state['national_debt'] / gdp
    
    return ratio


def calculate_budget_deficit(nation_id, tick_number):
    """
    Budget Deficit = Government Spending - Government Revenue
    Positive = deficit, Negative = surplus
    """
    state = get_nation_state(nation_id, tick_number)
    if not state:
        return 0.0
    
    deficit = state['government_spending'] - state['government_revenue']
    
    return deficit


# ========================================
# TRADE METRICS
# ========================================

def calculate_trade_balance(nation_id, tick_number):
    """
    Trade Balance = Total Exports - Total Imports (in USD)
    
    Calculated from NRU/AGU flows with pricing.
    """
    resources = get_nation_resources(nation_id, tick_number)
    if not resources:
        return 0.0
    
    # Calculate total physical exports
    total_exports_nru = (
        resources['nru_basic_exports'] +
        resources['nru_industrial_exports'] +
        resources['nru_precision_exports'] +
        resources['nru_strategic_exports']
    )
    total_exports_agu = resources['agu_exports']
    
    # Calculate total physical imports
    total_imports_nru = (
        resources['nru_basic_imports'] +
        resources['nru_industrial_imports'] +
        resources['nru_precision_imports'] +
        resources['nru_strategic_imports']
    )
    total_imports_agu = resources['agu_imports']
    
    # Convert to USD (simplified pricing - can be refined)
    # Assume average NRU price = $10B per unit, AGU = $2B per unit
    avg_nru_price = 10.0  # billions
    avg_agu_price = 2.0   # billions
    
    export_value = (total_exports_nru * avg_nru_price) + (total_exports_agu * avg_agu_price)
    import_value = (total_imports_nru * avg_nru_price) + (total_imports_agu * avg_agu_price)
    
    trade_balance = export_value - import_value
    
    return trade_balance


def calculate_export_to_gdp_ratio(nation_id, tick_number):
    """Exports as % of GDP"""
    gdp = calculate_gdp(nation_id, tick_number)
    if gdp == 0:
        return 0.0
    
    # Calculate export value
    resources = get_nation_resources(nation_id, tick_number)
    if not resources:
        return 0.0
    
    total_exports_nru = (
        resources['nru_basic_exports'] +
        resources['nru_industrial_exports'] +
        resources['nru_precision_exports'] +
        resources['nru_strategic_exports']
    )
    total_exports_agu = resources['agu_exports']
    
    avg_nru_price = 10.0
    avg_agu_price = 2.0
    
    export_value = (total_exports_nru * avg_nru_price) + (total_exports_agu * avg_agu_price)
    
    return export_value / gdp


def calculate_import_to_gdp_ratio(nation_id, tick_number):
    """Imports as % of GDP"""
    gdp = calculate_gdp(nation_id, tick_number)
    if gdp == 0:
        return 0.0
    
    resources = get_nation_resources(nation_id, tick_number)
    if not resources:
        return 0.0
    
    total_imports_nru = (
        resources['nru_basic_imports'] +
        resources['nru_industrial_imports'] +
        resources['nru_precision_imports'] +
        resources['nru_strategic_imports']
    )
    total_imports_agu = resources['agu_imports']
    
    avg_nru_price = 10.0
    avg_agu_price = 2.0
    
    import_value = (total_imports_nru * avg_nru_price) + (total_imports_agu * avg_agu_price)
    
    return import_value / gdp


# ========================================
# RESOURCE SELF-SUFFICIENCY
# ========================================

def calculate_nru_self_sufficiency(nation_id, tick_number, nru_type):
    """
    Self-sufficiency = Production / Demand
    1.0 = fully self-sufficient
    <1.0 = needs imports
    >1.0 = can export
    """
    resources = get_nation_resources(nation_id, tick_number)
    if not resources:
        return 1.0
    
    production = resources[f'nru_{nru_type}_production']
    demand = resources[f'nru_{nru_type}_demand']
    
    if demand == 0:
        return 1.0
    
    return production / demand


def calculate_food_security_index(nation_id, tick_number):
    """
    Food Security = (AGU Supply + AGU Stockpile/4) / AGU Demand
    
    Stockpile divided by 4 because it represents ~3 months reserve
    """
    resources = get_nation_resources(nation_id, tick_number)
    if not resources:
        return 1.0
    
    supply = resources['agu_supply']
    stockpile = resources['agu_stockpile']
    demand = resources['agu_demand']
    
    if demand == 0:
        return 1.0
    
    # Available food = current supply + quarter of reserves
    available = supply + (stockpile / 4.0)
    
    food_security = available / demand
    
    return food_security


# ========================================
# MILITARY METRICS
# ========================================

def calculate_defense_spending_pct_gdp(nation_id, tick_number):
    """Defense spending as % of GDP"""
    state = get_nation_state(nation_id, tick_number)
    if not state:
        return 0.0
    
    gdp = calculate_gdp(nation_id, tick_number)
    if gdp == 0:
        return 0.0
    
    config = get_nation_config(nation_id)
    if not config:
        return 0.0
    
    # Defense spending = GDP × military_production_pct (simplified)
    defense_spending = gdp * config['military_production_pct']
    
    return defense_spending / gdp


def calculate_recruitable_population(nation_id, tick_number):
    """
    Recruitable = Working Age Population × (1 - Current Recruitment Rate)
    """
    state = get_nation_state(nation_id, tick_number)
    if not state:
        return 0.0
    
    working_age = state['working_age_population']
    already_recruited = state['total_military_personnel']
    
    # Assume max 10% of working age can be recruited without economic collapse
    max_recruitable = working_age * 0.10
    
    available = max_recruitable - already_recruited
    
    return max(0.0, available)


# ========================================
# QUICK ACCESS FUNCTIONS
# ========================================

def get_all_metrics(nation_id, tick_number):
    """
    Get all derived metrics for a nation at once.
    Returns a dict of calculated values.
    """
    metrics = {}
    
    # Economic
    metrics['gdp'] = calculate_gdp(nation_id, tick_number)
    metrics['gdp_per_capita'] = calculate_gdp_per_capita(nation_id, tick_number)
    metrics['real_gdp_growth'] = calculate_real_gdp_growth(nation_id, tick_number)
    metrics['inflation_rate'] = calculate_inflation_rate(nation_id, tick_number)
    metrics['unemployment_rate'] = calculate_unemployment_rate(nation_id, tick_number)
    metrics['mpc'] = calculate_mpc(nation_id, tick_number)
    metrics['velocity_of_money'] = calculate_velocity_of_money(nation_id, tick_number)
    metrics['real_interest_rate'] = calculate_real_interest_rate(nation_id, tick_number)
    metrics['debt_to_gdp_ratio'] = calculate_debt_to_gdp_ratio(nation_id, tick_number)
    metrics['budget_deficit'] = calculate_budget_deficit(nation_id, tick_number)
    
    # Trade
    metrics['trade_balance'] = calculate_trade_balance(nation_id, tick_number)
    metrics['export_to_gdp'] = calculate_export_to_gdp_ratio(nation_id, tick_number)
    metrics['import_to_gdp'] = calculate_import_to_gdp_ratio(nation_id, tick_number)
    
    # Resources
    metrics['nru_basic_self_sufficiency'] = calculate_nru_self_sufficiency(nation_id, tick_number, 'basic')
    metrics['nru_industrial_self_sufficiency'] = calculate_nru_self_sufficiency(nation_id, tick_number, 'industrial')
    metrics['nru_precision_self_sufficiency'] = calculate_nru_self_sufficiency(nation_id, tick_number, 'precision')
    metrics['nru_strategic_self_sufficiency'] = calculate_nru_self_sufficiency(nation_id, tick_number, 'strategic')
    metrics['food_security_index'] = calculate_food_security_index(nation_id, tick_number)
    
    # Military
    metrics['defense_spending_pct_gdp'] = calculate_defense_spending_pct_gdp(nation_id, tick_number)
    metrics['recruitable_population'] = calculate_recruitable_population(nation_id, tick_number)
    
    return metrics


if __name__ == "__main__":
    # Test with mock data
    print("Metrics module loaded successfully.")
    print("Available functions:")
    print("- calculate_gdp(nation_id, tick_number)")
    print("- calculate_inflation_rate(nation_id, tick_number)")
    print("- calculate_unemployment_rate(nation_id, tick_number)")
    print("- get_all_metrics(nation_id, tick_number)")
