"""
DAY 9: PV vs Generator Break-Even Analysis
Energy System Management Portfolio - Week 2: System Design & Decision-Making

Decision Question: For a household currently relying on a generator for backup power,
at what point does investing in a solar PV system become cheaper than continuing
generator use, and what is the optimal investment decision?

Constraints:
- Household currently uses generator during outages (4 outages/week, 4 hours each)
- Generator efficiency: 0.3 L/kWh (petrol at ₦900/L)
- Solar system: 5 kW with battery storage
- Time horizon: 10-year analysis
- Discount rate: 12% for NPV calculation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime, timedelta

plt.style.use('seaborn-v0_8-whitegrid')
mpl.rcParams['font.size'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['figure.figsize'] = [15, 10]

# ============================================================================
# 1. SCENARIO DEFINITION & ASSUMPTIONS
# ============================================================================

def define_scenario():
    """
    Define the decision scenario for PV vs Generator break-even analysis
    NEW assumptions for this decision problem
    """
    
    print("=" * 80)
    print("PV vs GENERATOR BREAK-EVEN ANALYSIS")
    print("=" * 80)
    print("\nDECISION SCENARIO:")
    print("Household currently relies on generator during grid outages.")
    print("Should they continue using generator or invest in solar PV system?")
    
    # Scenario parameters (NEW assumptions)
    scenario = {
        'household_profile': {
            'daily_energy_kwh': 20,  # Average daily consumption
            'outage_pattern': {
                'frequency_per_week': 4,  # 4 outages per week
                'duration_hours': 4,  # 4 hours per outage
                'outage_timing': 'Evening (6-10 PM)'  # Most critical hours
            },
            'generator_usage': {
                'coverage_percent': 100,  # Generator runs during all outages
                'efficiency_l_per_kwh': 0.3,  # 0.3 liters per kWh
                'fuel_type': 'Petrol',
                'fuel_price_ngn_per_l': 900,  # Current petrol price
                'generator_capacity_kw': 5,  # 5 kVA generator
                'maintenance_cost_per_hour': 50,  # ₦50 per operating hour
                'generator_lifespan_years': 8,  # Typical lifespan
                'current_generator_age_years': 2  # Already 2 years old
            }
        },
        
        'solar_option': {
            'system_size_kw': 5,  # 5 kW system
            'battery_storage_kwh': 10,  # 10 kWh battery
            'solar_productivity': {
                'peak_sun_hours': 5.5,  # Nigeria average
                'system_efficiency': 0.75,  # 75% overall efficiency
                'daily_generation_kwh': 5 * 5.5 * 0.75  # ~20.6 kWh/day
            },
            'capital_cost': {
                'solar_per_kw': 1200000,  # ₦1.2M per kW
                'battery_per_kwh': 450000,  # ₦450k per kWh
                'balance_of_system': 500000,  # Inverter, installation, etc.
                'total_capex': (5 * 1200000) + (10 * 450000) + 500000
            },
            'operational_costs': {
                'annual_maintenance_percent': 1,  # 1% of CAPEX per year
                'battery_replacement_year': 8,  # Replace battery in year 8
                'battery_replacement_cost': 10 * 450000 * 0.7,  # 70% of initial cost
                'inverter_replacement_year': 10,  # Replace inverter in year 10
                'inverter_replacement_cost': 400000
            },
            'system_lifespan_years': 25,
            'warranty_years': 5
        },
        
        'financial_parameters': {
            'analysis_period_years': 10,
            'discount_rate': 0.12,  # 12% discount rate
            'inflation_rate': 0.15,  # 15% inflation (Nigeria)
            'fuel_price_escalation': 0.10,  # 10% annual increase
            'grid_tariff_ngn_per_kwh': 110,  # For comparison only
            'financing_option': {
                'loan_available': True,
                'loan_interest_rate': 0.18,  # 18% interest
                'loan_term_years': 5
            }
        },
        
        'grid_parameters': {
            'availability_percent': 65,  # Grid available 65% of the time
            'tariff_ngn_per_kwh': 110,
            'reliability_improvement': 0.02  # 2% annual improvement in grid reliability
        }
    }
    
    # Calculate current generator usage
    weekly_outage_hours = scenario['household_profile']['outage_pattern']['frequency_per_week'] * \
                         scenario['household_profile']['outage_pattern']['duration_hours']
    weekly_generator_hours = weekly_outage_hours
    
    # Energy provided by generator during outages
    # Assume generator runs at 50% load during outages
    generator_load_kw = scenario['household_profile']['generator_usage']['generator_capacity_kw'] * 0.5
    weekly_generator_energy_kwh = weekly_generator_hours * generator_load_kw
    
    # Convert to annual
    annual_generator_hours = weekly_generator_hours * 52
    annual_generator_energy_kwh = weekly_generator_energy_kwh * 52
    
    scenario['current_usage'] = {
        'weekly_generator_hours': weekly_generator_hours,
        'weekly_generator_energy_kwh': weekly_generator_energy_kwh,
        'annual_generator_hours': annual_generator_hours,
        'annual_generator_energy_kwh': annual_generator_energy_kwh
    }
    
    # Display scenario summary
    print("\nSCENARIO PARAMETERS:")
    print("-" * 60)
    print(f"HOUSEHOLD:")
    print(f"  • Daily Energy Consumption: {scenario['household_profile']['daily_energy_kwh']} kWh")
    print(f"  • Outage Pattern: {scenario['household_profile']['outage_pattern']['frequency_per_week']}×/week, {scenario['household_profile']['outage_pattern']['duration_hours']} hours each")
    print(f"  • Annual Generator Usage: {annual_generator_hours:.0f} hours, {annual_generator_energy_kwh:.0f} kWh")
    
    print(f"\nGENERATOR OPTION:")
    print(f"  • Efficiency: {scenario['household_profile']['generator_usage']['efficiency_l_per_kwh']} L/kWh")
    print(f"  • Fuel Price: ₦{scenario['household_profile']['generator_usage']['fuel_price_ngn_per_l']:,.0f}/L")
    print(f"  • Maintenance: ₦{scenario['household_profile']['generator_usage']['maintenance_cost_per_hour']}/hour")
    
    print(f"\nSOLAR OPTION:")
    print(f"  • System Size: {scenario['solar_option']['system_size_kw']} kW")
    print(f"  • Battery Storage: {scenario['solar_option']['battery_storage_kwh']} kWh")
    print(f"  • CAPEX: ₦{scenario['solar_option']['capital_cost']['total_capex']:,.0f}")
    print(f"  • Daily Generation: {scenario['solar_option']['solar_productivity']['daily_generation_kwh']:.1f} kWh")
    
    print(f"\nFINANCIAL:")
    print(f"  • Analysis Period: {scenario['financial_parameters']['analysis_period_years']} years")
    print(f"  • Discount Rate: {scenario['financial_parameters']['discount_rate']*100:.0f}%")
    print(f"  • Fuel Price Escalation: {scenario['financial_parameters']['fuel_price_escalation']*100:.0f}%/year")
    
    return scenario

# ============================================================================
# 2. GENERATOR COST MODEL
# ============================================================================

def model_generator_costs(scenario):
    """
    Model cumulative costs of continuing generator use
    NEW: Includes generator replacement, fuel escalation, maintenance
    """
    
    print("\n" + "=" * 80)
    print("GENERATOR COST MODEL")
    print("=" * 80)
    
    years = scenario['financial_parameters']['analysis_period_years']
    fuel_price = scenario['household_profile']['generator_usage']['fuel_price_ngn_per_l']
    fuel_escalation = scenario['financial_parameters']['fuel_price_escalation']
    efficiency = scenario['household_profile']['generator_usage']['efficiency_l_per_kwh']
    maintenance_rate = scenario['household_profile']['generator_usage']['maintenance_cost_per_hour']
    annual_energy = scenario['current_usage']['annual_generator_energy_kwh']
    annual_hours = scenario['current_usage']['annual_generator_hours']
    current_generator_age = scenario['household_profile']['generator_usage']['current_generator_age_years']
    generator_lifespan = scenario['household_profile']['generator_usage']['generator_lifespan_years']
    generator_capacity = scenario['household_profile']['generator_usage']['generator_capacity_kw']
    
    # Generator replacement cost (if needed during analysis period)
    generator_replacement_cost = generator_capacity * 250000  # ₦250k per kW
    
    # Initialize arrays
    generator_costs = pd.DataFrame(index=range(years+1), 
                                   columns=['Year', 'Fuel_Cost', 'Maintenance_Cost', 
                                            'Replacement_Cost', 'Total_Annual_Cost', 
                                            'Cumulative_Cost', 'Cumulative_Discounted'])
    
    # Year 0 (baseline)
    generator_costs.loc[0] = [0, 0, 0, 0, 0, 0, 0]
    
    # Calculate costs for each year
    for year in range(1, years+1):
        # Calculate fuel cost with escalation
        current_fuel_price = fuel_price * ((1 + fuel_escalation) ** (year-1))
        fuel_cost = annual_energy * efficiency * current_fuel_price
        
        # Maintenance cost (with inflation)
        maintenance_cost = annual_hours * maintenance_rate * ((1 + scenario['financial_parameters']['inflation_rate']) ** (year-1))
        
        # Replacement cost (if generator reaches end of life)
        replacement_cost = 0
        generator_age_at_year_start = current_generator_age + year - 1
        
        if generator_age_at_year_start >= generator_lifespan:
            # Need to replace generator
            replacement_cost = generator_replacement_cost
            # Reset generator age after replacement
            current_generator_age = 0
        
        # Total annual cost
        total_annual = fuel_cost + maintenance_cost + replacement_cost
        
        # Cumulative cost (undiscounted)
        cumulative = generator_costs.loc[year-1, 'Cumulative_Cost'] + total_annual
        
        # Discounted cost
        discount_rate = scenario['financial_parameters']['discount_rate']
        discounted_annual = total_annual / ((1 + discount_rate) ** year)
        cumulative_discounted = generator_costs.loc[year-1, 'Cumulative_Discounted'] + discounted_annual
        
        generator_costs.loc[year] = [year, fuel_cost, maintenance_cost, replacement_cost,
                                     total_annual, cumulative, cumulative_discounted]
    
    # Calculate key metrics
    total_generator_cost = generator_costs['Total_Annual_Cost'].sum()
    final_cumulative = generator_costs.loc[years, 'Cumulative_Cost']
    final_cumulative_discounted = generator_costs.loc[years, 'Cumulative_Discounted']
    
    print(f"\nGENERATOR COST SUMMARY ({years} years):")
    print("-" * 60)
    print(f"Total Fuel Cost:      ₦{generator_costs['Fuel_Cost'].sum():,.0f}")
    print(f"Total Maintenance:    ₦{generator_costs['Maintenance_Cost'].sum():,.0f}")
    print(f"Replacement Cost:     ₦{generator_costs['Replacement_Cost'].sum():,.0f}")
    print(f"Total Cost:           ₦{total_generator_cost:,.0f}")
    print(f"Final Cumulative:     ₦{final_cumulative:,.0f}")
    print(f"Discounted Cumulative:₦{final_cumulative_discounted:,.0f}")
    
    # Cost per kWh
    total_energy_kwh = annual_energy * years
    cost_per_kwh = total_generator_cost / total_energy_kwh if total_energy_kwh > 0 else 0
    
    print(f"Cost per kWh:         ₦{cost_per_kwh:.0f}")
    print(f"Grid Tariff:          ₦{scenario['financial_parameters']['grid_tariff_ngn_per_kwh']}/kWh")
    print(f"Premium over grid:    {((cost_per_kwh/scenario['financial_parameters']['grid_tariff_ngn_per_kwh'])-1)*100:.0f}%")
    
    return generator_costs

# ============================================================================
# 3. SOLAR PV COST MODEL
# ============================================================================

def model_solar_costs(scenario):
    """
    Model cumulative costs of investing in solar PV system
    NEW: Includes financing, battery replacement, degradation, maintenance
    """
    
    print("\n" + "=" * 80)
    print("SOLAR PV COST MODEL")
    print("=" * 80)
    
    years = scenario['financial_parameters']['analysis_period_years']
    solar_capex = scenario['solar_option']['capital_cost']['total_capex']
    maintenance_rate = scenario['solar_option']['operational_costs']['annual_maintenance_percent']
    battery_replacement_year = scenario['solar_option']['operational_costs']['battery_replacement_year']
    battery_replacement_cost = scenario['solar_option']['operational_costs']['battery_replacement_cost']
    inverter_replacement_year = scenario['solar_option']['operational_costs']['inverter_replacement_year']
    inverter_replacement_cost = scenario['solar_option']['operational_costs']['inverter_replacement_cost']
    discount_rate = scenario['financial_parameters']['discount_rate']
    
    # Energy generation model
    daily_generation = scenario['solar_option']['solar_productivity']['daily_generation_kwh']
    annual_generation = daily_generation * 365
    
    # Solar panel degradation: 0.5% per year
    degradation_rate = 0.005
    
    # Financing options
    financing = scenario['financial_parameters']['financing_option']
    
    # Initialize arrays
    solar_costs = pd.DataFrame(index=range(years+1),
                               columns=['Year', 'CAPEX', 'Maintenance_Cost', 
                                        'Battery_Replacement', 'Inverter_Replacement',
                                        'Total_Annual_Cost', 'Cumulative_Cost', 
                                        'Cumulative_Discounted', 'Energy_Generated_kWh',
                                        'Grid_Energy_Displaced_kWh', 'Generator_Energy_Displaced_kWh',
                                        'Total_Energy_Value'])
    
    # Year 0 (initial investment)
    solar_costs.loc[0] = [0, solar_capex, 0, 0, 0, solar_capex, solar_capex, solar_capex,
                         0, 0, 0, 0]
    
    # Calculate if financing with loan
    if financing['loan_available'] and years >= financing['loan_term_years']:
        # Calculate loan payments
        loan_amount = solar_capex
        interest_rate = financing['loan_interest_rate']
        loan_term = financing['loan_term_years']
        
        # Monthly payment calculation
        monthly_rate = interest_rate / 12
        num_payments = loan_term * 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                         ((1 + monthly_rate) ** num_payments - 1)
        annual_loan_payment = monthly_payment * 12
    else:
        annual_loan_payment = 0
    
    # Calculate costs for each year
    for year in range(1, years+1):
        # Maintenance cost (escalated with inflation)
        maintenance_cost = solar_capex * (maintenance_rate/100) * \
                          ((1 + scenario['financial_parameters']['inflation_rate']) ** (year-1))
        
        # Replacement costs
        battery_cost = battery_replacement_cost if year == battery_replacement_year else 0
        inverter_cost = inverter_replacement_cost if year == inverter_replacement_year else 0
        
        # Energy generation with degradation
        current_efficiency = (1 - degradation_rate) ** (year-1)
        energy_generated = annual_generation * current_efficiency
        
        # Energy displacement
        # Solar displaces generator usage first, then grid usage
        generator_energy_displaced = min(energy_generated, 
                                        scenario['current_usage']['annual_generator_energy_kwh'])
        grid_energy_displaced = max(0, energy_generated - generator_energy_displaced)
        
        # Value of displaced energy
        generator_value = generator_energy_displaced * scenario['household_profile']['generator_usage']['fuel_price_ngn_per_l'] * \
                         scenario['household_profile']['generator_usage']['efficiency_l_per_kwh']
        grid_value = grid_energy_displaced * scenario['financial_parameters']['grid_tariff_ngn_per_kwh']
        total_energy_value = generator_value + grid_value
        
        # Total annual cost (net of energy savings if we want to show net cost)
        # For cumulative cost comparison, we show gross cost
        total_annual_cost = maintenance_cost + battery_cost + inverter_cost
        
        # If using loan, add loan payments for first loan_term years
        if year <= financing['loan_term_years']:
            total_annual_cost += annual_loan_payment
        
        # Cumulative costs
        cumulative = solar_costs.loc[year-1, 'Cumulative_Cost'] + total_annual_cost
        cumulative_discounted = solar_costs.loc[year-1, 'Cumulative_Discounted'] + \
                               (total_annual_cost / ((1 + discount_rate) ** year))
        
        solar_costs.loc[year] = [year, 0, maintenance_cost, battery_cost, inverter_cost,
                                 total_annual_cost, cumulative, cumulative_discounted,
                                 energy_generated, grid_energy_displaced, 
                                 generator_energy_displaced, total_energy_value]
    
    # Calculate key metrics
    total_solar_cost = solar_costs['Total_Annual_Cost'].sum() + solar_capex
    final_cumulative = solar_costs.loc[years, 'Cumulative_Cost']
    final_cumulative_discounted = solar_costs.loc[years, 'Cumulative_Discounted']
    
    # Total energy generated and value
    total_energy_generated = solar_costs['Energy_Generated_kWh'].sum()
    total_energy_value = solar_costs['Total_Energy_Value'].sum()
    
    # Net cost (considering energy savings)
    net_solar_cost = total_solar_cost - total_energy_value
    net_cumulative_discounted = final_cumulative_discounted - \
                               (total_energy_value / ((1 + discount_rate) ** (years/2)))  # Rough discounting
    
    print(f"\nSOLAR PV COST SUMMARY ({years} years):")
    print("-" * 60)
    print(f"Initial CAPEX:        ₦{solar_capex:,.0f}")
    print(f"Total Maintenance:    ₦{solar_costs['Maintenance_Cost'].sum():,.0f}")
    print(f"Battery Replacement:  ₦{solar_costs['Battery_Replacement'].sum():,.0f}")
    print(f"Inverter Replacement: ₦{solar_costs['Inverter_Replacement'].sum():,.0f}")
    
    if financing['loan_available']:
        total_loan_payments = annual_loan_payment * min(years, financing['loan_term_years'])
        print(f"Loan Payments:        ₦{total_loan_payments:,.0f}")
    
    print(f"Total Gross Cost:     ₦{total_solar_cost:,.0f}")
    print(f"Total Energy Value:   ₦{total_energy_value:,.0f}")
    print(f"Net Cost:             ₦{net_solar_cost:,.0f}")
    print(f"Final Cumulative:     ₦{final_cumulative:,.0f}")
    print(f"Discounted Cumulative:₦{final_cumulative_discounted:,.0f}")
    
    # Cost per kWh (net)
    if total_energy_generated > 0:
        net_cost_per_kwh = net_solar_cost / total_energy_generated
        gross_cost_per_kwh = total_solar_cost / total_energy_generated
        print(f"Gross Cost per kWh:   ₦{gross_cost_per_kwh:.0f}")
        print(f"Net Cost per kWh:     ₦{net_cost_per_kwh:.0f}")
    
    # Compare with generator
    generator_energy_displaced_total = solar_costs['Generator_Energy_Displaced_kWh'].sum()
    print(f"Generator Energy Displaced: {generator_energy_displaced_total:,.0f} kWh")
    print(f"Grid Energy Displaced:     {solar_costs['Grid_Energy_Displaced_kWh'].sum():,.0f} kWh")
    
    return solar_costs

# ============================================================================
# 4. BREAK-EVEN ANALYSIS
# ============================================================================

def calculate_break_even(generator_costs, solar_costs, scenario):
    """
    Calculate break-even point between generator and solar options
    """
    
    print("\n" + "=" * 80)
    print("BREAK-EVEN ANALYSIS")
    print("=" * 80)
    
    years = scenario['financial_parameters']['analysis_period_years']
    
    # Calculate cumulative costs for each option
    gen_cumulative = generator_costs['Cumulative_Cost']
    sol_cumulative = solar_costs['Cumulative_Cost']
    
    gen_cumulative_discounted = generator_costs['Cumulative_Discounted']
    sol_cumulative_discounted = solar_costs['Cumulative_Discounted']
    
    # Find break-even year (undiscounted)
    break_even_year = None
    for year in range(1, years+1):
        if sol_cumulative[year] <= gen_cumulative[year]:
            break_even_year = year
            break
    
    # Find break-even year (discounted)
    break_even_year_discounted = None
    for year in range(1, years+1):
        if sol_cumulative_discounted[year] <= gen_cumulative_discounted[year]:
            break_even_year_discounted = year
            break
    
    # Calculate savings at end of analysis period
    total_savings_undiscounted = gen_cumulative[years] - sol_cumulative[years]
    total_savings_discounted = gen_cumulative_discounted[years] - sol_cumulative_discounted[years]
    
    # Payback period (simple)
    solar_capex = scenario['solar_option']['capital_cost']['total_capex']
    annual_generator_cost = generator_costs.loc[1, 'Total_Annual_Cost']
    annual_solar_maintenance = solar_costs.loc[1, 'Total_Annual_Cost']
    
    # Annual savings (first year approximation)
    annual_savings = annual_generator_cost - annual_solar_maintenance
    
    # Simple payback (ignoring time value of money and escalation)
    simple_payback = solar_capex / annual_savings if annual_savings > 0 else float('inf')
    
    print(f"\nBREAK-EVEN RESULTS:")
    print("-" * 60)
    
    if break_even_year:
        print(f"Break-even Year (undiscounted): Year {break_even_year}")
        print(f"  • Generator cumulative: ₦{gen_cumulative[break_even_year]:,.0f}")
        print(f"  • Solar cumulative:     ₦{sol_cumulative[break_even_year]:,.0f}")
    else:
        print(f"No break-even within {years} years (undiscounted)")
    
    if break_even_year_discounted:
        print(f"\nBreak-even Year (discounted @{scenario['financial_parameters']['discount_rate']*100:.0f}%): Year {break_even_year_discounted}")
        print(f"  • Generator cumulative: ₦{gen_cumulative_discounted[break_even_year_discounted]:,.0f}")
        print(f"  • Solar cumulative:     ₦{sol_cumulative_discounted[break_even_year_discounted]:,.0f}")
    else:
        print(f"\nNo break-even within {years} years (discounted)")
    
    print(f"\nSimple Payback Period: {simple_payback:.1f} years")
    print(f"Annual Savings (Year 1): ₦{annual_savings:,.0f}")
    
    print(f"\n{scenario['financial_parameters']['analysis_period_years']}-YEAR SAVINGS:")
    print(f"Total Savings (undiscounted): ₦{total_savings_undiscounted:,.0f}")
    print(f"Total Savings (discounted):   ₦{total_savings_discounted:,.0f}")
    
    if total_savings_discounted > 0:
        print(f"Net Present Value (NPV):      ₦{total_savings_discounted:,.0f}")
        print(f"Return on Investment (ROI):   {(total_savings_undiscounted/solar_capex)*100:.1f}%")
    
    # Sensitivity to key parameters
    print(f"\nSENSITIVITY ANALYSIS:")
    print("-" * 60)
    
    # Sensitivity to fuel price
    base_fuel_price = scenario['household_profile']['generator_usage']['fuel_price_ngn_per_l']
    for change in [-0.2, -0.1, 0.1, 0.2]:  # ±10%, ±20%
        new_fuel_price = base_fuel_price * (1 + change)
        # Recalculate simple payback with new fuel price
        new_annual_generator_cost = annual_generator_cost * (1 + change)
        new_annual_savings = new_annual_generator_cost - annual_solar_maintenance
        new_payback = solar_capex / new_annual_savings if new_annual_savings > 0 else float('inf')
        print(f"Fuel price {change*100:+.0f}%: Payback = {new_payback:.1f} years")
    
    # Sensitivity to solar cost
    base_solar_capex = solar_capex
    for change in [-0.2, -0.1, 0.1, 0.2]:
        new_solar_capex = base_solar_capex * (1 + change)
        new_payback = new_solar_capex / annual_savings if annual_savings > 0 else float('inf')
        print(f"Solar cost {change*100:+.0f}%: Payback = {new_payback:.1f} years")
    
    return {
        'break_even_year': break_even_year,
        'break_even_year_discounted': break_even_year_discounted,
        'simple_payback': simple_payback,
        'total_savings_undiscounted': total_savings_undiscounted,
        'total_savings_discounted': total_savings_discounted,
        'annual_savings': annual_savings
    }

# ============================================================================
# 5. DECISION DASHBOARD VISUALIZATION (Corrected Version)
# ============================================================================

def create_decision_dashboard(scenario, generator_costs, solar_costs, break_even_results):
    """
    Create comprehensive decision dashboard for break-even analysis
    """
    
    fig = plt.figure(constrained_layout=True, figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.25)
    
    # 1. Cumulative Cost Comparison (Undiscounted)
    ax1 = fig.add_subplot(gs[0, 0])
    
    years = list(range(scenario['financial_parameters']['analysis_period_years'] + 1))
    
    ax1.plot(years, generator_costs['Cumulative_Cost']/1e6, 
             'o-', color='#E74C3C', linewidth=2.5, markersize=6, label='Generator Option')
    ax1.plot(years, solar_costs['Cumulative_Cost']/1e6,
             's-', color='#2ECC71', linewidth=2.5, markersize=6, label='Solar PV Option')
    
    # Highlight break-even point
    if break_even_results['break_even_year']:
        be_year = break_even_results['break_even_year']
        be_cost = generator_costs.loc[be_year, 'Cumulative_Cost']/1e6
        ax1.plot(be_year, be_cost, 'o', color='#F39C12', markersize=12, 
                label=f'Break-even: Year {be_year}')
        ax1.axvline(x=be_year, color='#F39C12', linestyle='--', alpha=0.7)
    
    ax1.set_xlabel('Year', fontweight='bold')
    ax1.set_ylabel('Cumulative Cost (₦ Millions)', fontweight='bold')
    ax1.set_title('Cumulative Cost Comparison (Undiscounted)', 
                  fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best')
    
    # Add savings annotation
    final_year = scenario['financial_parameters']['analysis_period_years']
    savings = (generator_costs.loc[final_year, 'Cumulative_Cost'] - 
               solar_costs.loc[final_year, 'Cumulative_Cost'])/1e6
    ax1.annotate(f'10-year savings:\n₦{savings:.1f}M',
                 xy=(final_year, min(generator_costs.loc[final_year, 'Cumulative_Cost'],
                                    solar_costs.loc[final_year, 'Cumulative_Cost'])/1e6),
                 xytext=(final_year-3, max(generator_costs['Cumulative_Cost'])/1e6 * 0.7),
                 arrowprops=dict(arrowstyle='->', color='#3498DB'),
                 fontweight='bold', fontsize=9,
                 bbox=dict(boxstyle='round', facecolor='#FEF9E7', alpha=0.9))
    
    # 2. Cumulative Cost Comparison (Discounted)
    ax2 = fig.add_subplot(gs[0, 1])
    
    ax2.plot(years, generator_costs['Cumulative_Discounted']/1e6,
             'o-', color='#E74C3C', linewidth=2.5, markersize=6, label='Generator')
    ax2.plot(years, solar_costs['Cumulative_Discounted']/1e6,
             's-', color='#2ECC71', linewidth=2.5, markersize=6, label='Solar')
    
    # Highlight break-even point
    if break_even_results['break_even_year_discounted']:
        be_year_d = break_even_results['break_even_year_discounted']
        be_cost_d = generator_costs.loc[be_year_d, 'Cumulative_Discounted']/1e6
        ax2.plot(be_year_d, be_cost_d, 'o', color='#F39C12', markersize=12,
                label=f'Break-even: Year {be_year_d}')
        ax2.axvline(x=be_year_d, color='#F39C12', linestyle='--', alpha=0.7)
    
    ax2.set_xlabel('Year', fontweight='bold')
    ax2.set_ylabel('Discounted Cost (₦ Millions)', fontweight='bold')
    ax2.set_title(f"Cumulative Cost Comparison (Discounted @{scenario['financial_parameters']['discount_rate']*100:.0f}%)", 
                  fontweight='bold', pad=10)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best')
    
    # 3. Annual Cost Breakdown
    ax3 = fig.add_subplot(gs[0, 2])
    
    # Generator annual costs
    gen_fuel = generator_costs.loc[1:final_year, 'Fuel_Cost'].values
    gen_maint = generator_costs.loc[1:final_year, 'Maintenance_Cost'].values
    gen_replacement = generator_costs.loc[1:final_year, 'Replacement_Cost'].values
    
    # Solar annual costs
    sol_maint = solar_costs.loc[1:final_year, 'Maintenance_Cost'].values
    sol_battery = solar_costs.loc[1:final_year, 'Battery_Replacement'].values
    sol_inverter = solar_costs.loc[1:final_year, 'Inverter_Replacement'].values
    
    x = np.arange(1, final_year+1)
    width = 0.35
    
    bars_gen = ax3.bar(x - width/2, gen_fuel + gen_maint + gen_replacement, width,
                      label='Generator Total', color='#E74C3C', alpha=0.8)
    bars_sol = ax3.bar(x + width/2, sol_maint + sol_battery + sol_inverter, width,
                      label='Solar O&M', color='#2ECC71', alpha=0.8)
    
    ax3.set_xlabel('Year', fontweight='bold')
    ax3.set_ylabel('Annual Operating Cost (₦)', fontweight='bold')
    ax3.set_title('Annual Operating Cost Comparison', fontweight='bold', pad=10)
    ax3.set_xticks(x)
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.legend(loc='upper left')
    
    # 4. Cost Component Breakdown
    ax4 = fig.add_subplot(gs[1, 0])
    
    # Total costs over analysis period
    gen_total_fuel = generator_costs['Fuel_Cost'].sum()
    gen_total_maint = generator_costs['Maintenance_Cost'].sum()
    gen_total_replace = generator_costs['Replacement_Cost'].sum()
    
    sol_total_capex = scenario['solar_option']['capital_cost']['total_capex']
    sol_total_maint = solar_costs['Maintenance_Cost'].sum()
    sol_total_battery = solar_costs['Battery_Replacement'].sum()
    sol_total_inverter = solar_costs['Inverter_Replacement'].sum()
    
    gen_components = [gen_total_fuel, gen_total_maint, gen_total_replace]
    gen_labels = ['Fuel', 'Maintenance', 'Generator Replacement']
    gen_colors = ['#E74C3C', '#F1948A', '#F5B7B1']
    
    sol_components = [sol_total_capex, sol_total_maint, sol_total_battery, sol_total_inverter]
    sol_labels = ['Initial CAPEX', 'Maintenance', 'Battery Replacement', 'Inverter Replacement']
    sol_colors = ['#2ECC71', '#82E0AA', '#A9DFBF', '#D4EFDF']
    
    # Plot generator components
    bars_gen4 = ax4.bar(['Generator'] + ['']*(len(gen_components)-1), gen_components, 
                       color=gen_colors, label='Fuel')
    
    # Add stacked bars for other components
    bottom = np.zeros(1)
    for i in range(1, len(gen_components)):
        bars = ax4.bar([''], [gen_components[i]], bottom=[bottom[0]], 
                      color=gen_colors[i])
        bottom += gen_components[i]
    
    # Plot solar components
    bottom = np.zeros(1)
    for i in range(len(sol_components)):
        bars = ax4.bar(['Solar'], [sol_components[i]], bottom=[bottom[0]], 
                      color=sol_colors[i])
        bottom += sol_components[i]
    
    ax4.set_ylabel('Total Cost (₦)', fontweight='bold')
    ax4.set_title('Total Cost Breakdown (10 Years)', fontweight='bold', pad=10)
    ax4.set_ylim(0, max(sum(gen_components), sum(sol_components)) * 1.1)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Create custom legend
    from matplotlib.patches import Patch
    legend_elements = []
    for label, color in zip(gen_labels, gen_colors):
        legend_elements.append(Patch(facecolor=color, label=label))
    for label, color in zip(sol_labels, sol_colors):
        legend_elements.append(Patch(facecolor=color, label=label))
    
    ax4.legend(handles=legend_elements, loc='upper right', fontsize=8)
    
    # 5. Payback Period Sensitivity
    ax5 = fig.add_subplot(gs[1, 1])
    
    # Sensitivity analysis
    base_fuel = scenario['household_profile']['generator_usage']['fuel_price_ngn_per_l']
    base_solar = scenario['solar_option']['capital_cost']['total_capex']
    base_annual_savings = break_even_results['annual_savings']
    
    fuel_changes = np.array([-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3])
    payback_fuel = []
    
    for change in fuel_changes:
        new_fuel_price = base_fuel * (1 + change)
        # Recalculate annual savings
        annual_energy = scenario['current_usage']['annual_generator_energy_kwh']
        new_annual_generator_cost = annual_energy * scenario['household_profile']['generator_usage']['efficiency_l_per_kwh'] * new_fuel_price
        new_annual_generator_cost += scenario['current_usage']['annual_generator_hours'] * \
                                     scenario['household_profile']['generator_usage']['maintenance_cost_per_hour']
        new_annual_savings = new_annual_generator_cost - solar_costs.loc[1, 'Total_Annual_Cost']
        new_payback = base_solar / new_annual_savings if new_annual_savings > 0 else 20  # Cap at 20 years
        payback_fuel.append(new_payback)
    
    ax5.plot(fuel_changes*100, payback_fuel, 'o-', color='#3498DB', 
             linewidth=2, markersize=8)
    ax5.axhline(y=break_even_results['simple_payback'], color='#2ECC71', 
                linestyle='--', label=f'Base: {break_even_results["simple_payback"]:.1f} years')
    ax5.axhline(y=5, color='#E74C3C', linestyle='--', alpha=0.7, label='5-year target')
    ax5.axhline(y=10, color='#F39C12', linestyle='--', alpha=0.7, label='10-year limit')
    
    ax5.set_xlabel('Fuel Price Change (%)', fontweight='bold')
    ax5.set_ylabel('Payback Period (Years)', fontweight='bold')
    ax5.set_title('Sensitivity to Fuel Price Changes', fontweight='bold', pad=10)
    ax5.grid(True, alpha=0.3)
    ax5.legend(loc='best')
    
    # 6. Energy & Environmental Impact
    ax6 = fig.add_subplot(gs[1, 2])
    
    # Energy metrics
    total_generator_energy = scenario['current_usage']['annual_generator_energy_kwh'] * \
                            scenario['financial_parameters']['analysis_period_years']
    total_solar_energy = solar_costs['Energy_Generated_kWh'].sum()
    solar_displaces_generator = solar_costs['Generator_Energy_Displaced_kWh'].sum()
    solar_displaces_grid = solar_costs['Grid_Energy_Displaced_kWh'].sum()
    
    # Fuel savings
    total_fuel_saved_liters = solar_displaces_generator * \
                             scenario['household_profile']['generator_usage']['efficiency_l_per_kwh']
    
    # Environmental impact (CO2 savings)
    # Generator: 2.3 kg CO2 per liter of petrol
    # Grid: 0.85 kg CO2 per kWh (Nigeria grid average)
    co2_generator = total_fuel_saved_liters * 2.3
    co2_grid = solar_displaces_grid * 0.85
    total_co2_savings = co2_generator + co2_grid
    
    categories = ['Energy Generated\nby Solar', 'Generator Energy\nDisplaced', 
                  'Grid Energy\nDisplaced', 'Fuel Saved', 'CO₂ Reduction']
    values = [total_solar_energy/1000, solar_displaces_generator/1000, 
              solar_displaces_grid/1000, total_fuel_saved_liters, total_co2_savings/1000]
    units = ['MWh', 'MWh', 'MWh', 'Liters', 'Tonnes']
    
    bars6 = ax6.bar(categories, values, color=['#2ECC71', '#3498DB', '#9B59B6', 
                                               '#E74C3C', '#F39C12'], alpha=0.8)
    ax6.set_ylabel('Value', fontweight='bold')
    ax6.set_title('Energy & Environmental Impact (10 Years)', fontweight='bold', pad=10)
    ax6.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, value, unit in zip(bars6, values, units):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2, height * 1.05,
                f'{value:,.0f} {unit}', ha='center', va='bottom', fontsize=8)
    
    # 7. Monthly Cash Flow Comparison (Corrected Section)
    ax7 = fig.add_subplot(gs[2, 0])
    
    # Calculate monthly costs
    months = list(range(1, 121))  # 10 years = 120 months
    
    # Generator monthly cost (simplified)
    monthly_generator_fuel = scenario['current_usage']['annual_generator_energy_kwh'] * \
                            scenario['household_profile']['generator_usage']['efficiency_l_per_kwh'] * \
                            scenario['household_profile']['generator_usage']['fuel_price_ngn_per_l'] / 12
    monthly_generator_maint = scenario['current_usage']['annual_generator_hours'] * \
                             scenario['household_profile']['generator_usage']['maintenance_cost_per_hour'] / 12
    monthly_generator = monthly_generator_fuel + monthly_generator_maint
    
    # Solar monthly cost (with loan)
    financing = scenario['financial_parameters']['financing_option']
    if financing['loan_available']:
        loan_amount = scenario['solar_option']['capital_cost']['total_capex']
        interest_rate = financing['loan_interest_rate']
        loan_term = financing['loan_term_years']
        
        monthly_rate = interest_rate / 12
        num_payments = loan_term * 12
        monthly_loan_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                              ((1 + monthly_rate) ** num_payments - 1)
    else:
        monthly_loan_payment = 0
        loan_term = 0  # Added default value
    
    monthly_solar_maintenance = (scenario['solar_option']['capital_cost']['total_capex'] * 
                                (scenario['solar_option']['operational_costs']['annual_maintenance_percent']/100)) / 12
    
    # Monthly savings from solar
    monthly_energy_value = solar_costs.loc[1, 'Total_Energy_Value'] / 12
    
    # Plot
    x_months = np.array(months)
    
    # Generator cost remains relatively constant (with escalation)
    gen_monthly = monthly_generator * ((1 + scenario['financial_parameters']['fuel_price_escalation']/12) ** (x_months-1))
    
    # Solar cost: loan payments for first loan_term years, then just maintenance
    # FIX: Using list comprehension
    sol_monthly = []
    for month in months:
        if month <= loan_term * 12:
            sol_monthly.append(monthly_loan_payment + monthly_solar_maintenance - monthly_energy_value)
        else:
            sol_monthly.append(monthly_solar_maintenance - monthly_energy_value)
    
    # Convert to numpy array to allow division
    sol_monthly_np = np.array(sol_monthly)
    
    ax7.plot(x_months, gen_monthly/1000, color='#E74C3C', linewidth=1.5, 
             label='Generator Net Cost')
    ax7.plot(x_months, sol_monthly_np/1000, color='#2ECC71', linewidth=1.5,  # Using numpy array
             label='Solar Net Cost')
    
    # Highlight when solar becomes cheaper
    for month in range(1, 121):
        if sol_monthly_np[month-1] < gen_monthly[month-1]:
            ax7.axvline(x=month, color='#F39C12', linestyle='--', alpha=0.3, linewidth=0.5)
            break
    
    ax7.set_xlabel('Month', fontweight='bold')
    ax7.set_ylabel('Net Monthly Cost (₦ Thousands)', fontweight='bold')
    ax7.set_title('Monthly Cash Flow Comparison', fontweight='bold', pad=10)
    ax7.grid(True, alpha=0.3)
    ax7.legend(loc='best')
    ax7.set_xlim(1, 120)
    
    # 8. Decision Matrix
    ax8 = fig.add_subplot(gs[2, 1])
    ax8.axis('off')
    
    # Decision criteria
    criteria = [
        ('Financial Payback', 30),
        ('Fuel Price Risk', 25),
        ('Environmental Impact', 20),
        ('Operational Simplicity', 15),
        ('Grid Independence', 10)
    ]
    
    # Score each option
    solar_scores = []
    generator_scores = []
    
    for criterion, weight in criteria:
        if criterion == 'Financial Payback':
            if break_even_results['simple_payback'] <= 5:
                solar_scores.append(weight * 0.9)
                generator_scores.append(weight * 0.3)
            elif break_even_results['simple_payback'] <= 10:
                solar_scores.append(weight * 0.7)
                generator_scores.append(weight * 0.5)
            else:
                solar_scores.append(weight * 0.4)
                generator_scores.append(weight * 0.8)
        
        elif criterion == 'Fuel Price Risk':
            solar_scores.append(weight * 0.9)  # Solar avoids fuel price risk
            generator_scores.append(weight * 0.2)  # Generator exposed to fuel price risk
        
        elif criterion == 'Environmental Impact':
            solar_scores.append(weight * 1.0)  # Solar is clean
            generator_scores.append(weight * 0.1)  # Generator pollutes
        
        elif criterion == 'Operational Simplicity':
            solar_scores.append(weight * 0.7)  # Solar requires less daily operation
            generator_scores.append(weight * 0.6)  # Generator requires refueling, maintenance
        
        elif criterion == 'Grid Independence':
            solar_scores.append(weight * 0.8)  # Solar provides more independence
            generator_scores.append(weight * 0.7)  # Generator also provides independence
    
    total_solar_score = sum(solar_scores)
    total_generator_score = sum(generator_scores)
    
    # Plot radar chart
    ax9 = fig.add_subplot(gs[2, 2], projection='polar')
    
    angles = np.linspace(0, 2*np.pi, len(criteria), endpoint=False).tolist()
    angles += angles[:1]  # Close the polygon
    
    solar_plot = solar_scores + [solar_scores[0]]
    generator_plot = generator_scores + [generator_scores[0]]
    
    ax9.plot(angles, solar_plot, 'o-', linewidth=2, color='#2ECC71', 
             label=f'Solar ({total_solar_score:.0f})')
    ax9.fill(angles, solar_plot, alpha=0.25, color='#2ECC71')
    
    ax9.plot(angles, generator_plot, 'o-', linewidth=2, color='#E74C3C',
             label=f'Generator ({total_generator_score:.0f})')
    ax9.fill(angles, generator_plot, alpha=0.25, color='#E74C3C')
    
    ax9.set_xticks(angles[:-1])
    ax9.set_xticklabels([c[0] for c in criteria], fontsize=8)
    ax9.set_ylim(0, 30)
    ax9.set_title('Multi-Criteria Decision Analysis', fontweight='bold', pad=20)
    ax9.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax9.grid(True)
    
    fig.suptitle('PV vs Generator Break-Even Analysis: Investment Decision Dashboard\nDay 9: Energy System Management Portfolio', 
                fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig('pv_vs_generator_break_even.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    return fig
    
# ============================================================================
# 6. FINAL DECISION & RECOMMENDATION
# ============================================================================

def generate_final_recommendation(scenario, break_even_results, generator_costs, solar_costs):
    """
    Generate final investment recommendation
    """
    
    print("\n" + "=" * 100)
    print("FINAL INVESTMENT RECOMMENDATION")
    print("=" * 100)
    
    years = scenario['financial_parameters']['analysis_period_years']
    solar_capex = scenario['solar_option']['capital_cost']['total_capex']
    final_year = years
    
    # Calculate key metrics
    total_generator_cost = generator_costs.loc[final_year, 'Cumulative_Cost']
    total_solar_cost = solar_costs.loc[final_year, 'Cumulative_Cost']
    savings = total_generator_cost - total_solar_cost
    
    discounted_savings = (generator_costs.loc[final_year, 'Cumulative_Discounted'] - 
                         solar_costs.loc[final_year, 'Cumulative_Discounted'])
    
    roi = (savings / solar_capex) * 100
    
    # Determine recommendation
    if break_even_results['break_even_year_discounted'] and break_even_results['break_even_year_discounted'] <= 5:
        recommendation = "STRONGLY RECOMMEND SOLAR PV INVESTMENT"
        confidence = "High"
        color = "GREEN"
    elif break_even_results['break_even_year_discounted'] and break_even_results['break_even_year_discounted'] <= 10:
        recommendation = "RECOMMEND SOLAR PV INVESTMENT"
        confidence = "Medium"
        color = "YELLOW"
    else:
        recommendation = "CONTINUE WITH GENERATOR FOR NOW"
        confidence = "Low"
        color = "RED"
    
    print(f"\nDECISION: {recommendation}")
    print(f"CONFIDENCE LEVEL: {confidence}")
    
    print(f"\nKEY FINANCIAL METRICS:")
    print("-" * 60)
    print(f"Solar System CAPEX:          ₦{solar_capex:,.0f}")
    print(f"10-year Generator Cost:      ₦{total_generator_cost:,.0f}")
    print(f"10-year Solar Cost:          ₦{total_solar_cost:,.0f}")
    print(f"10-year Savings:             ₦{savings:,.0f}")
    print(f"Discounted Savings (NPV):    ₦{discounted_savings:,.0f}")
    print(f"Return on Investment:        {roi:.1f}%")
    print(f"Simple Payback Period:       {break_even_results['simple_payback']:.1f} years")
    
    if break_even_results['break_even_year_discounted']:
        print(f"Discounted Break-even:       Year {break_even_results['break_even_year_discounted']}")
    
    # Energy and environmental impact
    total_solar_energy = solar_costs['Energy_Generated_kWh'].sum()
    fuel_displaced = solar_costs['Generator_Energy_Displaced_kWh'].sum() * \
                    scenario['household_profile']['generator_usage']['efficiency_l_per_kwh']
    co2_savings = fuel_displaced * 2.3  # kg CO2 per liter
    
    print(f"\nENERGY & ENVIRONMENTAL IMPACT:")
    print("-" * 60)
    print(f"Total Solar Energy Generated: {total_solar_energy:,.0f} kWh")
    print(f"Generator Fuel Displaced:     {fuel_displaced:,.0f} liters")
    print(f"CO₂ Emissions Avoided:        {co2_savings/1000:,.1f} tonnes")
    
    print(f"\nRISK ASSESSMENT:")
    print("-" * 60)
    print(f"Generator Risks:")
    print("  • Fuel price volatility (10% annual escalation assumed)")
    print("  • Maintenance costs increasing with generator age")
    print("  • Noise and air pollution")
    print("  • Fuel availability during shortages")
    
    print(f"\nSolar PV Risks:")
    print("  • High upfront capital requirement")
    print("  • Battery replacement cost in year 8")
    print("  • Performance degradation over time (0.5%/year)")
    print("  • Limited generation during prolonged cloudy periods")
    
    print(f"\nMITIGATION STRATEGIES:")
    print("-" * 60)
    print(f"1. Financing: Consider solar loan or lease to reduce upfront cost")
    print(f"2. Phased Implementation: Start with smaller system, expand later")
    print(f"3. Hybrid Approach: Keep generator as backup for critical loads")
    print(f"4. Government Incentives: Explore available subsidies or tax breaks")
    
    print(f"\nIMPLEMENTATION ROADMAP:")
    print("-" * 60)
    if recommendation.startswith("RECOMMEND SOLAR"):
        print(f"Month 1-2: Energy audit and system design")
        print(f"Month 2-3: Financing arrangement and vendor selection")
        print(f"Month 3-4: Procurement and installation")
        print(f"Month 4-5: Commissioning and staff training")
        print(f"Month 5-6: Performance monitoring and optimization")
    else:
        print(f"Month 1-3: Implement generator efficiency measures")
        print(f"Month 4-6: Explore smaller solar pilot (e.g., solar lighting)")
        print(f"Month 7-12: Re-evaluate when fuel prices increase or solar costs decrease")
    
    print(f"\nMONITORING METRICS:")
    print("-" * 60)
    print(f"• Monthly fuel consumption and cost")
    print(f"• Generator operating hours and maintenance costs")
    print(f"• Grid reliability improvements")
    print(f"• Solar system cost trends (wait for price reductions)")
    
    print(f"\nDECISION REVIEW TRIGGERS:")
    print("-" * 60)
    print(f"1. Fuel price increase >20% from current level")
    print(f"2. Solar system costs decrease >15%")
    print(f"3. Grid reliability deteriorates significantly")
    print(f"4. Government introduces new solar incentives")
    print(f"5. Generator requires major repair or replacement")
    
    return {
        'recommendation': recommendation,
        'confidence': confidence,
        'savings': savings,
        'roi': roi,
        'payback': break_even_results['simple_payback']
    }

# ============================================================================
# 7. MAIN DECISION EXECUTION
# ============================================================================

def main():
    """Execute PV vs Generator break-even analysis"""
    
    print("=" * 100)
    print("DAY 9: PV vs GENERATOR BREAK-EVEN ANALYSIS")
    print("Energy System Management Portfolio - Week 2: System Design & Decision-Making")
    print("=" * 100)
    
    print("\nDECISION QUESTION:")
    print("For a household currently using generator during outages,")
    print("at what point does investing in solar PV become cheaper than")
    print("continuing generator use, and what is the optimal investment decision?")
    
    # Step 1: Define scenario
    print("\n" + "=" * 80)
    print("STEP 1: SCENARIO DEFINITION")
    print("=" * 80)
    scenario = define_scenario()
    
    # Step 2: Model generator costs
    print("\n" + "=" * 80)
    print("STEP 2: GENERATOR COST MODELING")
    print("=" * 80)
    generator_costs = model_generator_costs(scenario)
    
    # Step 3: Model solar PV costs
    print("\n" + "=" * 80)
    print("STEP 3: SOLAR PV COST MODELING")
    print("=" * 80)
    solar_costs = model_solar_costs(scenario)
    
    # Step 4: Break-even analysis
    print("\n" + "=" * 80)
    print("STEP 4: BREAK-EVEN CALCULATION")
    print("=" * 80)
    break_even_results = calculate_break_even(generator_costs, solar_costs, scenario)
    
    # Step 5: Create decision dashboard
    print("\n" + "=" * 80)
    print("STEP 5: CREATING DECISION DASHBOARD")
    print("=" * 80)
    fig = create_decision_dashboard(scenario, generator_costs, solar_costs, break_even_results)
    
    # Step 6: Generate final recommendation
    print("\n" + "=" * 80)
    print("STEP 6: FINAL RECOMMENDATION")
    print("=" * 80)
    recommendation = generate_final_recommendation(scenario, break_even_results, generator_costs, solar_costs)
    
    # Step 7: Decision summary
    print("\n" + "=" * 100)
    print("DECISION-MAKING PROCESS SUMMARY")
    print("=" * 100)
    print("\n1. Problem Framing:")
    print("   • Investment decision: Solar PV vs continuing generator use")
    print("   • Time horizon: 10-year analysis")
    print("   • Key constraint: High upfront cost of solar")
    
    print("\n2. Data & Assumptions:")
    print("   • Current generator usage: 832 hours/year, 2,080 kWh/year")
    print("   • Fuel price: ₦900/L with 10% annual escalation")
    print("   • Solar system: 5 kW with 10 kWh battery, ₦10.7M CAPEX")
    print("   • Financial: 12% discount rate, 15% inflation")
    
    print("\n3. Analysis Methodology:")
    print("   • Time-series cost modeling for both options")
    print("   • Discounted cash flow analysis (NPV calculation)")
    print("   • Break-even point identification")
    print("   • Sensitivity analysis on key parameters")
    
    print("\n4. Decision Criteria:")
    print("   • Financial: Payback period, NPV, ROI")
    print("   • Risk: Fuel price volatility, maintenance costs")
    print("   • Environmental: CO₂ emissions reduction")
    print("   • Operational: Reliability, maintenance requirements")
    
    print("\n5. Key Findings:")
    print(f"   • Break-even point: Year {break_even_results.get('break_even_year_discounted', 'N/A')} (discounted)")
    print(f"   • Simple payback: {break_even_results['simple_payback']:.1f} years")
    print(f"   • 10-year savings: ₦{break_even_results['total_savings_undiscounted']:,.0f}")
    print(f"   • NPV: ₦{break_even_results['total_savings_discounted']:,.0f}")
    
    print("\n" + "=" * 100)
    print("PORTFOLIO DELIVERABLES:")
    print("=" * 100)
    print("✓ pv_vs_generator_break_even.png - Main decision dashboard")
    print("✓ Complete financial models for both options")
    print("✓ Break-even analysis with sensitivity testing")
    print("✓ Investment recommendation with implementation roadmap")
    
    print("\n" + "=" * 100)
    print("PORTFOLIO VALUE STATEMENT:")
    print("=" * 100)
    print("'Conducted comprehensive break-even analysis comparing solar PV investment")
    print("vs continuing generator use, identifying break-even at Year X with")
    print("10-year savings of ₦Y and providing data-driven investment recommendation.'")
    
    print("\n" + "=" * 100)
    print("DAY 9 COMPLETE - READY FOR DAY 10: EV CHARGING INFRASTRUCTURE")
    print("=" * 100)
    
    return {
        'scenario': scenario,
        'generator_costs': generator_costs,
        'solar_costs': solar_costs,
        'break_even_results': break_even_results,
        'recommendation': recommendation
    }

# ============================================================================
# EXECUTE ANALYSIS
# ============================================================================

if __name__ == "__main__":
    results = main()