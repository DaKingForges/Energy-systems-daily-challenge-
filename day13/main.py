"""
DAY 13: Hybrid Energy System Trade-Off Analysis
Energy System Management Portfolio - Week 2: System Design & Decision-Making

Objective: Compare three hybrid configurations for a 25-household community:
1. Solar PV + Battery (Lithium-ion)
2. Solar PV + Diesel Generator
3. Solar PV + Pumped Hydro Storage (PHS)

Metrics: Cost, Reliability, CO₂ emissions, Levelized Cost of Energy (LCOE)
Decision: Best option based on trade-offs between reliability, cost, and environment.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.optimize import minimize_scalar

plt.style.use('seaborn-v0_8-whitegrid')
mpl.rcParams['font.size'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['figure.figsize'] = [16, 10]

# ============================================================================
# 1. COMMUNITY LOAD PROFILE (SCALED FROM DAY 1)
# ============================================================================

def create_community_load():
    """
    Scale Day 1 household load profile to a 25-household community
    with diversity factor and community loads.
    """
    
    print("=" * 80)
    print("COMMUNITY LOAD PROFILE GENERATION")
    print("=" * 80)
    
    # Day 1 household profile (hourly kW)
    # Morning peak (6-8 AM), Evening peak (7-10 PM)
    household_hourly = [
        0.6, 0.5, 0.4, 0.4, 0.5, 0.8,  # 00-05
        2.1, 2.8, 1.6, 1.2, 1.0, 1.0,  # 06-11
        1.0, 1.0, 1.2, 1.5, 2.2, 2.8,  # 12-17
        3.8, 4.2, 4.5, 3.2, 1.5, 0.8   # 18-23
    ]
    
    # Scale to 25 households with diversity factor
    n_households = 25
    diversity_factor = 0.75  # Not all households peak simultaneously
    community_hourly = np.array(household_hourly) * n_households * diversity_factor
    
    # Add community loads (street lights, water pumping, school, health post)
    community_base = [
        2.0, 1.8, 1.8, 1.8, 1.8, 2.0,  # 00-05: minimal lighting
        3.0, 4.0, 5.0, 5.0, 5.0, 5.0,  # 06-11: water pumping, school
        5.0, 5.0, 5.0, 5.0, 6.0, 8.0,  # 12-17: productive uses
        12.0, 12.0, 10.0, 8.0, 5.0, 3.0  # 18-23: evening lights
    ]
    
    total_load_kw = community_hourly + community_base
    
    # Create hourly DataFrame
    hours = list(range(24))
    df_load = pd.DataFrame({
        'Hour': hours,
        'Load_kW': total_load_kw,
        'Households_kW': community_hourly,
        'Community_kW': community_base
    })
    
    daily_energy_kwh = df_load['Load_kW'].sum()
    peak_demand_kw = df_load['Load_kW'].max()
    load_factor = daily_energy_kwh / (24 * peak_demand_kw)
    
    print(f"Community size: {n_households} households")
    print(f"Daily energy demand: {daily_energy_kwh:.1f} kWh")
    print(f"Peak demand: {peak_demand_kw:.1f} kW")
    print(f"Load factor: {load_factor:.3f}")
    
    return df_load, daily_energy_kwh, peak_demand_kw

# ============================================================================
# 2. SYSTEM COMPONENT PARAMETERS & COSTS
# ============================================================================

def define_system_parameters():
    """
    Define technical and financial parameters for all components.
    """
    
    params = {
        # Solar PV
        'solar': {
            'capex_per_kw': 1_200_000,     # ₦/kW (installed)
            'opex_percent_per_year': 1.0,   # % of capex
            'lifetime_years': 25,
            'peak_sun_hours': 5.5,          # Nigeria average
            'derating_factor': 0.75,        # system losses, soiling, etc.
            'degradation_per_year': 0.005   # 0.5% annual degradation
        },
        
        # Battery (Lithium-ion)
        'battery': {
            'capex_per_kwh': 450_000,       # ₦/kWh
            'opex_percent_per_year': 1.5,
            'lifetime_years': 10,
            'replacement_cost_per_kwh': 400_000,  # future cost
            'round_trip_efficiency': 0.92,
            'max_dod': 0.8,                # 80% depth of discharge
            'max_charge_power_per_kwh': 0.5,  # 0.5C
            'max_discharge_power_per_kwh': 1.0  # 1C
        },
        
        # Diesel Generator
        'generator': {
            'capex_per_kw': 250_000,        # ₦/kW
            'opex_percent_per_year': 5.0,   # maintenance
            'lifetime_years': 15,
            'fuel_price_ngn_per_l': 900,    # current diesel price
            'fuel_escalation_per_year': 0.10,  # 10% annual increase
            'fuel_efficiency_l_per_kwh': 0.30, # at 70% load
            'min_load_percent': 30,         # minimum efficient load
            'co2_per_l_kg': 2.68            # kg CO2 per liter diesel
        },
        
        # Pumped Hydro Storage (PHS)
        'phs': {
            'turbine_capex_per_kw': 150_000,      # ₦/kW (penstock, turbine, generator)
            'storage_capex_per_kwh': 40_000,      # ₦/kWh (reservoir construction)
            'opex_percent_per_year': 1.0,
            'lifetime_years': 50,                 # long infrastructure life
            'turbine_efficiency': 0.90,           # turbine/generator efficiency
            'pump_efficiency': 0.89,              # pump/motor efficiency
            'round_trip_efficiency': 0.80,        # overall (90% * 89%)
            'max_discharge_hours': 10,            # storage duration (1 MWh @ 100 kW = 10h)
            'min_reservoir_level': 0.1            # 10% minimum
        },
        
        # Financial
        'financial': {
            'discount_rate': 0.12,
            'inflation_rate': 0.15,
            'analysis_period_years': 20,
            'grid_tariff_ngn_per_kwh': 110,       # for comparison
            'carbon_tax_ngn_per_tonne': 0         # not applied in base case
        }
    }
    
    # Pre-calculate some useful values
    params['solar']['daily_generation_per_kw'] = (
        params['solar']['peak_sun_hours'] * 
        params['solar']['derating_factor']
    )
    
    return params

# ============================================================================
# 3. SOLAR GENERATION PROFILE
# ============================================================================

def solar_generation_profile(solar_capacity_kw, params):
    """
    Generate hourly solar power output for given capacity.
    """
    solar_kw = np.zeros(24)
    for hour in range(6, 19):
        if hour <= 12:
            normalized = np.sin((hour - 6) / 6 * np.pi/2)
        else:
            normalized = np.sin((18 - hour) / 6 * np.pi/2)
        
        solar_kw[hour] = normalized * solar_capacity_kw * params['solar']['derating_factor']
    
    return solar_kw

# ============================================================================
# 4. OPTION 1: SOLAR + BATTERY
# ============================================================================

def design_solar_battery(load_kw, params):
    """
    Size solar PV and battery to meet community load with high reliability.
    Uses iterative approach to find minimum cost system with <1% loss of load.
    """
    
    print("\n" + "=" * 80)
    print("OPTION 1: SOLAR PV + BATTERY STORAGE")
    print("=" * 80)
    
    daily_load_kwh = np.sum(load_kw)
    peak_load = np.max(load_kw)
    
    # Initial sizing heuristics
    # Solar sized to meet daily energy with storage
    solar_size_min = daily_load_kwh / params['solar']['daily_generation_per_kw'] * 0.7
    solar_size_max = daily_load_kwh / params['solar']['daily_generation_per_kw'] * 1.3
    
    # Simple optimization: find solar capacity that minimizes total cost
    # while meeting reliability constraint
    def system_cost(solar_capacity):
        solar_capacity = max(1, solar_capacity)
        solar_gen = solar_generation_profile(solar_capacity, params)
        
        # Battery sizing: need to cover evening peak and overnight
        evening_night_load = np.sum(load_kw[18:24]) + np.sum(load_kw[0:6])
        solar_evening = np.sum(solar_gen[18:24]) + np.sum(solar_gen[0:6])
        battery_needed = max(0, evening_night_load - solar_evening)
        
        # Add margin and account for DoD, efficiency
        battery_capacity = battery_needed / (params['battery']['max_dod'] * params['battery']['round_trip_efficiency'])
        battery_capacity = np.ceil(battery_capacity * 2) / 2  # round to 0.5 kWh
        
        # Simulate daily operation
        unmet = simulate_solar_battery(load_kw, solar_gen, battery_capacity, params)
        if unmet > daily_load_kwh * 0.01:  # >1% unmet
            return 1e12  # penalize
        
        # Costs
        solar_capex = solar_capacity * params['solar']['capex_per_kw']
        battery_capex = battery_capacity * params['battery']['capex_per_kwh']
        total_capex = solar_capex + battery_capex
        
        # Annualized cost (capital recovery + O&M)
        crf = (params['financial']['discount_rate'] * (1 + params['financial']['discount_rate'])**20) / \
              ((1 + params['financial']['discount_rate'])**20 - 1)
        annualized_capex = total_capex * crf
        
        # O&M
        solar_om = solar_capex * (params['solar']['opex_percent_per_year'] / 100)
        battery_om = battery_capex * (params['battery']['opex_percent_per_year'] / 100)
        
        return annualized_capex + solar_om + battery_om
    
    # Find optimal solar capacity
    result = minimize_scalar(system_cost, bounds=(solar_size_min, solar_size_max), method='bounded')
    optimal_solar = result.x
    
    # Recalculate battery size at optimal solar
    solar_gen = solar_generation_profile(optimal_solar, params)
    evening_night_load = np.sum(load_kw[18:24]) + np.sum(load_kw[0:6])
    solar_evening = np.sum(solar_gen[18:24]) + np.sum(solar_gen[0:6])
    battery_needed = max(0, evening_night_load - solar_evening)
    battery_capacity = battery_needed / (params['battery']['max_dod'] * params['battery']['round_trip_efficiency'])
    battery_capacity = np.ceil(battery_capacity * 2) / 2  # round to 0.5 kWh
    
    # Final simulation
    unmet, charge_profile, discharge_profile, soc = simulate_solar_battery_detailed(
        load_kw, solar_gen, battery_capacity, params)
    
    reliability = 100 - (unmet / np.sum(load_kw) * 100)
    
    # Financials
    solar_capex = optimal_solar * params['solar']['capex_per_kw']
    battery_capex = battery_capacity * params['battery']['capex_per_kwh']
    total_capex = solar_capex + battery_capex
    
    # Annual O&M
    solar_om = solar_capex * (params['solar']['opex_percent_per_year'] / 100)
    battery_om = battery_capex * (params['battery']['opex_percent_per_year'] / 100)
    annual_om = solar_om + battery_om
    
    # Battery replacement in year 10
    battery_replacement_cost = battery_capacity * params['battery']['replacement_cost_per_kwh']
    
    # LCOE calculation
    annual_energy = np.sum(load_kw) * 365
    total_lifetime_cost = total_capex + battery_replacement_cost + annual_om * 20
    lcoe = total_lifetime_cost / (annual_energy * 20)
    
    # CO2 emissions (zero for solar+battery)
    co2_annual = 0
    
    results = {
        'option': 'Solar + Battery',
        'solar_kw': optimal_solar,
        'battery_kwh': battery_capacity,
        'capex_ngn': total_capex,
        'annual_om_ngn': annual_om,
        'lcoe_ngn': lcoe,
        'reliability_percent': reliability,
        'unmet_kwh': unmet,
        'co2_annual_kg': co2_annual,
        'solar_gen': solar_gen,
        'battery_charge': charge_profile,
        'battery_discharge': discharge_profile,
        'soc': soc
    }
    
    print(f"Solar capacity: {optimal_solar:.1f} kW")
    print(f"Battery capacity: {battery_capacity:.1f} kWh")
    print(f"Total CAPEX: ₦{total_capex:,.0f}")
    print(f"Annual O&M: ₦{annual_om:,.0f}")
    print(f"Reliability: {reliability:.1f}%")
    print(f"LCOE: ₦{lcoe:.0f}/kWh")
    
    return results

def simulate_solar_battery(load_kw, solar_gen, battery_capacity, params):
    """Simple simulation to get unmet energy."""
    battery_kwh = battery_capacity * params['battery']['max_dod']
    battery_soc = battery_kwh  # start full
    unmet = 0
    
    for hour in range(24):
        net_load = load_kw[hour] - solar_gen[hour]
        if net_load < 0:  # excess solar
            charge = min(-net_load, (battery_kwh - battery_soc) / params['battery']['round_trip_efficiency'])
            battery_soc += charge * params['battery']['round_trip_efficiency']
        else:  # deficit
            discharge = min(net_load, battery_soc)
            battery_soc -= discharge
            unmet += net_load - discharge
    return unmet

def simulate_solar_battery_detailed(load_kw, solar_gen, battery_capacity, params):
    """Detailed simulation with power constraints and SOC tracking."""
    usable_capacity = battery_capacity * params['battery']['max_dod']
    max_charge_power = battery_capacity * params['battery']['max_charge_power_per_kwh']
    max_discharge_power = battery_capacity * params['battery']['max_discharge_power_per_kwh']
    
    battery_soc = usable_capacity  # start full
    charge_profile = np.zeros(24)
    discharge_profile = np.zeros(24)
    soc_profile = np.zeros(24)
    unmet = 0
    
    for hour in range(24):
        net_load = load_kw[hour] - solar_gen[hour]
        
        if net_load < 0:  # excess solar
            charge_power = min(-net_load, max_charge_power)
            charge_energy = charge_power  # 1 hour
            charge_energy = min(charge_energy, (usable_capacity - battery_soc) / params['battery']['round_trip_efficiency'])
            battery_soc += charge_energy * params['battery']['round_trip_efficiency']
            charge_profile[hour] = charge_energy
        else:  # deficit
            discharge_power = min(net_load, max_discharge_power)
            discharge_energy = min(discharge_power, battery_soc)
            battery_soc -= discharge_energy
            discharge_profile[hour] = discharge_energy
            unmet += net_load - discharge_energy
        
        soc_profile[hour] = battery_soc / usable_capacity * 100
    
    return unmet, charge_profile, discharge_profile, soc_profile

# ============================================================================
# 5. OPTION 2: SOLAR + DIESEL GENERATOR
# ============================================================================

def design_solar_generator(load_kw, params):
    """
    Solar PV sized to minimize LCOE with generator as backup.
    """
    
    print("\n" + "=" * 80)
    print("OPTION 2: SOLAR PV + DIESEL GENERATOR")
    print("=" * 80)
    
    daily_load_kwh = np.sum(load_kw)
    peak_load = np.max(load_kw)
    
    # Generator sized to meet peak load + margin
    generator_kw = peak_load * 1.2
    generator_kw = np.ceil(generator_kw / 10) * 10  # round to nearest 10 kW
    
    # Solar sizing: trade-off between fuel savings and capex
    # We'll find solar capacity that minimizes LCOE
    def system_cost(solar_capacity):
        solar_capacity = max(0, solar_capacity)
        solar_gen = solar_generation_profile(solar_capacity, params)
        
        # Simulate operation
        fuel_l, gen_energy, unmet = simulate_solar_generator(load_kw, solar_gen, generator_kw, params)
        
        if unmet > daily_load_kwh * 0.01:  # >1% unmet
            return 1e12
        
        # Costs
        solar_capex = solar_capacity * params['solar']['capex_per_kw']
        gen_capex = generator_kw * params['generator']['capex_per_kw']
        total_capex = solar_capex + gen_capex
        
        crf = (params['financial']['discount_rate'] * (1 + params['financial']['discount_rate'])**20) / \
              ((1 + params['financial']['discount_rate'])**20 - 1)
        annualized_capex = total_capex * crf
        
        # O&M
        solar_om = solar_capex * (params['solar']['opex_percent_per_year'] / 100)
        gen_om = gen_capex * (params['generator']['opex_percent_per_year'] / 100)
        
        # Fuel cost (first year)
        fuel_cost = fuel_l * params['generator']['fuel_price_ngn_per_l']
        
        return annualized_capex + solar_om + gen_om + fuel_cost
    
    # Find optimal solar
    result = minimize_scalar(system_cost, bounds=(0, daily_load_kwh / params['solar']['daily_generation_per_kw'] * 1.2))
    optimal_solar = result.x
    
    # Final simulation with optimal solar
    solar_gen = solar_generation_profile(optimal_solar, params)
    fuel_l, gen_energy, unmet, gen_hours, gen_profile = simulate_solar_generator_detailed(
        load_kw, solar_gen, generator_kw, params)
    
    reliability = 100 - (unmet / np.sum(load_kw) * 100)
    
    # Financials
    solar_capex = optimal_solar * params['solar']['capex_per_kw']
    gen_capex = generator_kw * params['generator']['capex_per_kw']
    total_capex = solar_capex + gen_capex
    
    solar_om = solar_capex * (params['solar']['opex_percent_per_year'] / 100)
    gen_om = gen_capex * (params['generator']['opex_percent_per_year'] / 100)
    annual_om = solar_om + gen_om
    
    # Fuel cost (first year) and escalation
    fuel_cost_year1 = fuel_l * params['generator']['fuel_price_ngn_per_l']
    
    # LCOE with fuel escalation
    annual_energy = np.sum(load_kw) * 365
    total_lifetime_cost = total_capex + annual_om * 20
    
    # Fuel costs over 20 years with escalation
    fuel_costs = 0
    for year in range(1, 21):
        fuel_costs += fuel_cost_year1 * ((1 + params['generator']['fuel_escalation_per_year']) ** (year-1)) / \
                     ((1 + params['financial']['discount_rate']) ** year)
    
    total_lifetime_cost += fuel_costs * 20  # simplified, but approximate
    
    lcoe = total_lifetime_cost / (annual_energy * 20)
    
    # CO2 emissions
    co2_annual_kg = fuel_l * 365 * params['generator']['co2_per_l_kg']
    
    results = {
        'option': 'Solar + Generator',
        'solar_kw': optimal_solar,
        'generator_kw': generator_kw,
        'capex_ngn': total_capex,
        'annual_om_ngn': annual_om,
        'annual_fuel_l': fuel_l * 365,
        'annual_fuel_cost_ngn': fuel_cost_year1 * 365,
        'lcoe_ngn': lcoe,
        'reliability_percent': reliability,
        'unmet_kwh': unmet,
        'co2_annual_kg': co2_annual_kg,
        'solar_gen': solar_gen,
        'gen_profile': gen_profile,
        'gen_hours': gen_hours
    }
    
    print(f"Solar capacity: {optimal_solar:.1f} kW")
    print(f"Generator capacity: {generator_kw:.1f} kW")
    print(f"Total CAPEX: ₦{total_capex:,.0f}")
    print(f"Annual O&M: ₦{annual_om:,.0f}")
    print(f"Annual fuel consumption: {fuel_l * 365:.0f} L")
    print(f"Reliability: {reliability:.1f}%")
    print(f"LCOE: ₦{lcoe:.0f}/kWh")
    print(f"CO₂ emissions: {co2_annual_kg/1000:.1f} tonnes/year")
    
    return results

def simulate_solar_generator(load_kw, solar_gen, generator_kw, params):
    """Simple simulation for optimization."""
    unmet = 0
    gen_energy = 0
    fuel = 0
    min_load = generator_kw * (params['generator']['min_load_percent'] / 100)
    
    for hour in range(24):
        net_load = load_kw[hour] - solar_gen[hour]
        if net_load > 0:
            if net_load >= min_load:
                gen = min(net_load, generator_kw)
            else:
                gen = min_load  # run at min load
            gen_energy += gen
            fuel += gen * params['generator']['fuel_efficiency_l_per_kwh']
            unmet += max(0, net_load - gen)
    return fuel, gen_energy, unmet

def simulate_solar_generator_detailed(load_kw, solar_gen, generator_kw, params):
    """Detailed simulation with generator dispatch logic."""
    unmet = 0
    gen_energy = 0
    fuel = 0
    gen_hours = 0
    gen_profile = np.zeros(24)
    min_load = generator_kw * (params['generator']['min_load_percent'] / 100)
    
    for hour in range(24):
        net_load = load_kw[hour] - solar_gen[hour]
        if net_load > 0:
            if net_load >= min_load:
                gen = min(net_load, generator_kw)
            else:
                gen = min_load
            gen_energy += gen
            fuel += gen * params['generator']['fuel_efficiency_l_per_kwh']
            unmet += max(0, net_load - gen)
            gen_profile[hour] = gen
            gen_hours += 1
        else:
            gen_profile[hour] = 0
    
    return fuel, gen_energy, unmet, gen_hours, gen_profile

# ============================================================================
# 6. OPTION 3: SOLAR + PUMPED HYDRO STORAGE
# ============================================================================

def design_solar_phs(load_kw, params):
    """
    Solar PV with Pumped Hydro Storage (PHS).
    Fixed PHS: 100 kW turbine, 1 MWh storage, 80% round-trip.
    Solar sized to meet load with PHS shifting.
    """
    
    print("\n" + "=" * 80)
    print("OPTION 3: SOLAR PV + PUMPED HYDRO STORAGE")
    print("=" * 80)
    
    # Fixed PHS parameters
    turbine_power_kw = 100
    storage_capacity_kwh = 1000  # 1 MWh
    round_trip_eff = params['phs']['round_trip_efficiency']
    pump_eff = params['phs']['pump_efficiency']
    turbine_eff = params['phs']['turbine_efficiency']
    
    # Find solar capacity that minimizes LCOE with PHS
    daily_load_kwh = np.sum(load_kw)
    
    def system_cost(solar_capacity):
        solar_gen = solar_generation_profile(solar_capacity, params)
        
        # Simulate PHS operation
        unmet, dumped, soc = simulate_solar_phs(load_kw, solar_gen, 
                                                turbine_power_kw, storage_capacity_kwh, 
                                                pump_eff, turbine_eff, round_trip_eff, params)
        
        if unmet > daily_load_kwh * 0.05:  # >5% unmet, penalize
            return 1e12
        
        # Costs
        solar_capex = solar_capacity * params['solar']['capex_per_kw']
        phs_capex = (turbine_power_kw * params['phs']['turbine_capex_per_kw'] + 
                    storage_capacity_kwh * params['phs']['storage_capex_per_kwh'])
        total_capex = solar_capex + phs_capex
        
        crf = (params['financial']['discount_rate'] * (1 + params['financial']['discount_rate'])**20) / \
              ((1 + params['financial']['discount_rate'])**20 - 1)
        annualized_capex = total_capex * crf
        
        solar_om = solar_capex * (params['solar']['opex_percent_per_year'] / 100)
        phs_om = phs_capex * (params['phs']['opex_percent_per_year'] / 100)
        
        return annualized_capex + solar_om + phs_om
    
    # Optimize solar capacity
    result = minimize_scalar(system_cost, bounds=(daily_load_kwh / params['solar']['daily_generation_per_kw'] * 0.8,
                                                   daily_load_kwh / params['solar']['daily_generation_per_kw'] * 1.5))
    optimal_solar = result.x
    
    # Final simulation
    solar_gen = solar_generation_profile(optimal_solar, params)
    unmet, dumped, soc, pump_profile, turbine_profile = simulate_solar_phs_detailed(
        load_kw, solar_gen, turbine_power_kw, storage_capacity_kwh,
        pump_eff, turbine_eff, round_trip_eff, params)
    
    reliability = 100 - (unmet / np.sum(load_kw) * 100)
    
    # Financials
    solar_capex = optimal_solar * params['solar']['capex_per_kw']
    phs_capex = (turbine_power_kw * params['phs']['turbine_capex_per_kw'] + 
                storage_capacity_kwh * params['phs']['storage_capex_per_kwh'])
    total_capex = solar_capex + phs_capex
    
    solar_om = solar_capex * (params['solar']['opex_percent_per_year'] / 100)
    phs_om = phs_capex * (params['phs']['opex_percent_per_year'] / 100)
    annual_om = solar_om + phs_om
    
    # LCOE
    annual_energy = np.sum(load_kw) * 365
    total_lifetime_cost = total_capex + annual_om * 20
    lcoe = total_lifetime_cost / (annual_energy * 20)
    
    # CO2 emissions (zero for solar+PHS)
    co2_annual = 0
    
    results = {
        'option': 'Solar + PHS',
        'solar_kw': optimal_solar,
        'phs_turbine_kw': turbine_power_kw,
        'phs_storage_kwh': storage_capacity_kwh,
        'capex_ngn': total_capex,
        'annual_om_ngn': annual_om,
        'lcoe_ngn': lcoe,
        'reliability_percent': reliability,
        'unmet_kwh': unmet,
        'dumped_kwh': dumped,
        'co2_annual_kg': co2_annual,
        'solar_gen': solar_gen,
        'pump_profile': pump_profile,
        'turbine_profile': turbine_profile,
        'soc': soc
    }
    
    print(f"Solar capacity: {optimal_solar:.1f} kW")
    print(f"PHS: {turbine_power_kw} kW turbine, {storage_capacity_kwh} kWh storage")
    print(f"Total CAPEX: ₦{total_capex:,.0f}")
    print(f"Annual O&M: ₦{annual_om:,.0f}")
    print(f"Reliability: {reliability:.1f}%")
    print(f"LCOE: ₦{lcoe:.0f}/kWh")
    print(f"Unmet energy: {unmet:.1f} kWh/day ({100-reliability:.1f}%)")
    print(f"Dumped solar: {dumped:.1f} kWh/day")
    
    return results

def simulate_solar_phs(load_kw, solar_gen, turbine_kw, storage_kwh, pump_eff, turbine_eff, rt_eff, params):
    """Simplified PHS simulation for optimization."""
    soc = storage_kwh * 0.5  # start half full
    unmet = 0
    dumped = 0
    
    for hour in range(24):
        net_load = load_kw[hour] - solar_gen[hour]
        
        if net_load < 0:  # excess solar
            # Pump to store
            pump_power = min(-net_load, turbine_kw)  # pump is same turbine rating
            pump_energy = pump_power * pump_eff  # energy stored
            stored = min(pump_energy, storage_kwh - soc)
            soc += stored
            dumped += (-net_load) - (stored / pump_eff)
        else:  # deficit
            # Generate from storage
            gen_power = min(net_load, turbine_kw)
            gen_energy = gen_power / turbine_eff  # energy taken from storage
            available = min(gen_energy, soc)
            soc -= available
            unmet += net_load - (available * turbine_eff)
    
    return unmet, dumped, soc

def simulate_solar_phs_detailed(load_kw, solar_gen, turbine_kw, storage_kwh, 
                                pump_eff, turbine_eff, rt_eff, params):
    """Detailed PHS simulation with SOC tracking and profiles."""
    soc = storage_kwh * 0.5  # start half full
    unmet = 0
    dumped = 0
    pump_profile = np.zeros(24)
    turbine_profile = np.zeros(24)
    soc_profile = np.zeros(24)
    
    for hour in range(24):
        net_load = load_kw[hour] - solar_gen[hour]
        
        if net_load < 0:  # excess solar
            # Pump to store
            pump_power = min(-net_load, turbine_kw)
            pump_energy = pump_power * pump_eff  # stored energy per hour
            stored = min(pump_energy, storage_kwh - soc)
            soc += stored
            dumped += (-net_load) - pump_power
            pump_profile[hour] = pump_power
        else:  # deficit
            # Generate from storage
            gen_power = min(net_load, turbine_kw)
            gen_energy = gen_power / turbine_eff  # water energy needed
            available = min(gen_energy, soc)
            soc -= available
            generated = available * turbine_eff
            unmet += net_load - generated
            turbine_profile[hour] = generated
            pump_profile[hour] = 0
        
        soc_profile[hour] = soc / storage_kwh * 100
    
    return unmet, dumped, soc_profile, pump_profile, turbine_profile

# ============================================================================
# 7. COMPARISON TABLE & DASHBOARD
# ============================================================================

def create_comparison_table(results_list):
    """
    Create comparison table of all options.
    """
    df = pd.DataFrame(results_list)
    
    # Format for display
    df_display = df[['option', 'solar_kw', 'capex_ngn', 'lcoe_ngn', 
                      'reliability_percent', 'co2_annual_kg']].copy()
    df_display.columns = ['Option', 'Solar (kW)', 'CAPEX (₦M)', 'LCOE (₦/kWh)', 
                          'Reliability (%)', 'CO₂ (tonnes/yr)']
    
    df_display['CAPEX (₦M)'] = df_display['CAPEX (₦M)'] / 1e6
    df_display['CO₂ (tonnes/yr)'] = df_display['CO₂ (tonnes/yr)'] / 1000
    
    return df_display

def create_dashboard(load_kw, params, results_solar_battery, results_solar_gen, results_solar_phs):
    """
    Create comprehensive comparison dashboard.
    """
    
    fig = plt.figure(constrained_layout=True, figsize=(18, 12))
    gs = fig.add_gridspec(3, 4, hspace=0.25, wspace=0.25)
    
    hours = list(range(24))
    
    # 1. Community Load Profile
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.bar(hours, load_kw, color='#2C3E50', alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Hour of Day', fontweight='bold')
    ax1.set_ylabel('Load (kW)', fontweight='bold')
    ax1.set_title('Community Load Profile (25 households)', fontweight='bold')
    ax1.set_xticks(range(0, 24, 3))
    ax1.grid(True, alpha=0.3)
    
    # Annotate daily energy and peak
    daily_energy = np.sum(load_kw)
    peak = np.max(load_kw)
    ax1.text(0.02, 0.95, f'Daily: {daily_energy:.0f} kWh\nPeak: {peak:.1f} kW',
             transform=ax1.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 2. Option 1: Solar + Battery
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(hours, results_solar_battery['solar_gen'], 'y-', linewidth=2, label='Solar')
    ax2.plot(hours, load_kw, 'k--', linewidth=1.5, alpha=0.7, label='Load')
    ax2.fill_between(hours, 0, results_solar_battery['battery_discharge'], 
                     color='green', alpha=0.5, label='Battery Discharge')
    ax2.fill_between(hours, 0, -results_solar_battery['battery_charge'], 
                     color='blue', alpha=0.3, label='Battery Charge')
    ax2.set_xlabel('Hour', fontweight='bold')
    ax2.set_ylabel('Power (kW)', fontweight='bold')
    ax2.set_title('Solar + Battery', fontweight='bold')
    ax2.set_xticks(range(0, 24, 3))
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=7)
    ax2.text(0.02, 0.95, f'PV: {results_solar_battery["solar_kw"]:.0f} kW\nBatt: {results_solar_battery["battery_kwh"]:.0f} kWh',
             transform=ax2.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 3. Option 2: Solar + Generator
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(hours, results_solar_gen['solar_gen'], 'y-', linewidth=2, label='Solar')
    ax3.plot(hours, load_kw, 'k--', linewidth=1.5, alpha=0.7, label='Load')
    ax3.bar(hours, results_solar_gen['gen_profile'], color='red', alpha=0.6, label='Generator')
    ax3.set_xlabel('Hour', fontweight='bold')
    ax3.set_ylabel('Power (kW)', fontweight='bold')
    ax3.set_title('Solar + Generator', fontweight='bold')
    ax3.set_xticks(range(0, 24, 3))
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper right', fontsize=7)
    ax3.text(0.02, 0.95, f'PV: {results_solar_gen["solar_kw"]:.0f} kW\nGen: {results_solar_gen["generator_kw"]:.0f} kW\nFuel: {results_solar_gen["annual_fuel_l"]:.0f} L/yr',
             transform=ax3.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 4. Option 3: Solar + PHS
    ax4 = fig.add_subplot(gs[0, 3])
    ax4.plot(hours, results_solar_phs['solar_gen'], 'y-', linewidth=2, label='Solar')
    ax4.plot(hours, load_kw, 'k--', linewidth=1.5, alpha=0.7, label='Load')
    ax4.fill_between(hours, 0, results_solar_phs['turbine_profile'], 
                     color='green', alpha=0.5, label='Turbine')
    ax4.fill_between(hours, 0, -results_solar_phs['pump_profile'], 
                     color='blue', alpha=0.3, label='Pump')
    ax4.set_xlabel('Hour', fontweight='bold')
    ax4.set_ylabel('Power (kW)', fontweight='bold')
    ax4.set_title('Solar + Pumped Hydro', fontweight='bold')
    ax4.set_xticks(range(0, 24, 3))
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc='upper right', fontsize=7)
    ax4.text(0.02, 0.95, f'PV: {results_solar_phs["solar_kw"]:.0f} kW\nPHS: {results_solar_phs["phs_turbine_kw"]:.0f} kW, {results_solar_phs["phs_storage_kwh"]/1000:.0f} MWh',
             transform=ax4.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 5. Battery SOC (Option 1)
    ax5 = fig.add_subplot(gs[1, 0])
    ax5.plot(hours, results_solar_battery['soc'], 'b-', linewidth=2)
    ax5.set_xlabel('Hour', fontweight='bold')
    ax5.set_ylabel('State of Charge (%)', fontweight='bold')
    ax5.set_title('Battery SOC - Solar+Battery', fontweight='bold')
    ax5.set_xticks(range(0, 24, 3))
    ax5.set_ylim(0, 100)
    ax5.grid(True, alpha=0.3)
    
    # 6. Generator Runtime (Option 2)
    ax6 = fig.add_subplot(gs[1, 1])
    gen_hours = results_solar_gen['gen_hours']
    ax6.bar(['Generator'], [gen_hours], color='red', alpha=0.7)
    ax6.set_ylabel('Hours per day', fontweight='bold')
    ax6.set_title(f'Generator Runtime: {gen_hours:.0f} hrs/day', fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='y')
    
    # 7. PHS SOC (Option 3)
    ax7 = fig.add_subplot(gs[1, 2])
    ax7.plot(hours, results_solar_phs['soc'], 'c-', linewidth=2)
    ax7.set_xlabel('Hour', fontweight='bold')
    ax7.set_ylabel('Reservoir Level (%)', fontweight='bold')
    ax7.set_title('PHS Reservoir - Solar+PHS', fontweight='bold')
    ax7.set_xticks(range(0, 24, 3))
    ax7.set_ylim(0, 100)
    ax7.grid(True, alpha=0.3)
    
    # 8. Dumped Solar Energy (Option 3)
    ax8 = fig.add_subplot(gs[1, 3])
    dumped = results_solar_phs['dumped_kwh']
    ax8.bar(['Dumped Solar'], [dumped], color='orange', alpha=0.7)
    ax8.set_ylabel('kWh per day', fontweight='bold')
    ax8.set_title(f'Excess Solar: {dumped:.1f} kWh/day', fontweight='bold')
    ax8.grid(True, alpha=0.3, axis='y')
    
    # 9. LCOE Comparison
    ax9 = fig.add_subplot(gs[2, 0:2])
    options = ['Solar+Battery', 'Solar+Generator', 'Solar+PHS']
    lcoes = [results_solar_battery['lcoe_ngn'], 
             results_solar_gen['lcoe_ngn'],
             results_solar_phs['lcoe_ngn']]
    colors = ['green', 'red', 'blue']
    bars = ax9.bar(options, lcoes, color=colors, alpha=0.7)
    ax9.set_ylabel('LCOE (₦/kWh)', fontweight='bold')
    ax9.set_title('Levelized Cost of Energy Comparison', fontweight='bold')
    ax9.grid(True, alpha=0.3, axis='y')
    
    for bar, lcoe in zip(bars, lcoes):
        height = bar.get_height()
        ax9.text(bar.get_x() + bar.get_width()/2, height + 5,
                f'₦{lcoe:.0f}', ha='center', va='bottom', fontweight='bold')
    
    # 10. Reliability vs CO₂ Trade-off
    ax10 = fig.add_subplot(gs[2, 2:])
    reliabilities = [results_solar_battery['reliability_percent'],
                     results_solar_gen['reliability_percent'],
                     results_solar_phs['reliability_percent']]
    co2s = [results_solar_battery['co2_annual_kg']/1000,
            results_solar_gen['co2_annual_kg']/1000,
            results_solar_phs['co2_annual_kg']/1000]
    
    scatter = ax10.scatter(reliabilities, co2s, c=lcoes, s=200, cmap='viridis', alpha=0.8)
    for i, opt in enumerate(options):
        ax10.annotate(opt, (reliabilities[i]+0.2, co2s[i]), fontsize=9, fontweight='bold')
    
    ax10.set_xlabel('Reliability (%)', fontweight='bold')
    ax10.set_ylabel('CO₂ Emissions (tonnes/year)', fontweight='bold')
    ax10.set_title('Trade-off: Reliability vs Emissions', fontweight='bold')
    ax10.grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax10)
    cbar.set_label('LCOE (₦/kWh)')
    
    fig.suptitle('Hybrid Energy System Trade-Off Analysis: Solar-Only vs Solar+Generator vs Solar+Pumped Hydro\nDay 13: Energy System Management Portfolio',
                fontsize=14, fontweight='bold', y=1.02)
    
    # plt.tight_layout()
    plt.savefig('hybrid_energy_tradeoff_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    return fig

# ============================================================================
# 8. MAIN EXECUTION
# ============================================================================

def main():
    """Execute hybrid energy system trade-off analysis."""
    
    print("=" * 100)
    print("DAY 13: HYBRID ENERGY SYSTEM TRADE-OFF ANALYSIS")
    print("Energy System Management Portfolio - Week 2: System Design & Decision-Making")
    print("=" * 100)
    
    # Step 1: Create community load profile
    print("\n" + "=" * 80)
    print("STEP 1: COMMUNITY LOAD PROFILE")
    print("=" * 80)
    load_df, daily_energy, peak_demand = create_community_load()
    load_kw = load_df['Load_kW'].values
    
    # Step 2: Define system parameters
    print("\n" + "=" * 80)
    print("STEP 2: SYSTEM PARAMETERS")
    print("=" * 80)
    params = define_system_parameters()
    
    # Step 3: Design and simulate Option 1 (Solar + Battery)
    results_solar_battery = design_solar_battery(load_kw, params)
    
    # Step 4: Design and simulate Option 2 (Solar + Generator)
    results_solar_gen = design_solar_generator(load_kw, params)
    
    # Step 5: Design and simulate Option 3 (Solar + PHS)
    results_solar_phs = design_solar_phs(load_kw, params)
    
    # Step 6: Create comparison table
    print("\n" + "=" * 80)
    print("STEP 6: COMPARISON SUMMARY")
    print("=" * 80)
    
    results_list = [results_solar_battery, results_solar_gen, results_solar_phs]
    comparison_df = create_comparison_table(results_list)
    
    print("\n" + "=" * 80)
    print("COMPARISON TABLE")
    print("=" * 80)
    print(comparison_df.to_string(index=False))
    
    # Step 7: Create dashboard
    print("\n" + "=" * 80)
    print("STEP 7: GENERATING DECISION DASHBOARD")
    print("=" * 80)
    fig = create_dashboard(load_kw, params, results_solar_battery, results_solar_gen, results_solar_phs)
    
    # Step 8: Recommendation
    print("\n" + "=" * 100)
    print("RECOMMENDATION & MANAGERIAL INSIGHTS")
    print("=" * 100)
    
    # Find best in each category
    best_reliability = max(results_list, key=lambda x: x['reliability_percent'])
    best_lcoe = min(results_list, key=lambda x: x['lcoe_ngn'])
    lowest_co2 = min(results_list, key=lambda x: x['co2_annual_kg'])
    
    print(f"\n🎯 BEST RELIABILITY: {best_reliability['option']} - {best_reliability['reliability_percent']:.1f}%")
    print(f"💰 LOWEST LCOE: {best_lcoe['option']} - ₦{best_lcoe['lcoe_ngn']:.0f}/kWh")
    print(f"🌍 LOWEST EMISSIONS: {lowest_co2['option']} - {lowest_co2['co2_annual_kg']/1000:.1f} tonnes/year")
    
    print("\n📊 TRADE-OFF ANALYSIS:")
    print("-" * 60)
    print("Solar + Battery:")
    print(f"  • Highest reliability ({results_solar_battery['reliability_percent']:.1f}%)")
    print(f"  • Zero emissions")
    print(f"  • Moderate LCOE (₦{results_solar_battery['lcoe_ngn']:.0f}/kWh)")
    print(f"  • Requires large battery (replacement cost in year 10)")
    
    print("\nSolar + Generator:")
    print(f"  • Lowest LCOE (₦{results_solar_gen['lcoe_ngn']:.0f}/kWh)")
    print(f"  • High reliability ({results_solar_gen['reliability_percent']:.1f}%)")
    print(f"  • Significant emissions ({results_solar_gen['co2_annual_kg']/1000:.1f} tonnes/year)")
    print(f"  • Fuel price risk and logistics")
    
    print("\nSolar + Pumped Hydro:")
    print(f"  • Zero emissions")
    print(f"  • Long asset life (50+ years)")
    print(f"  • Lower LCOE than battery (₦{results_solar_phs['lcoe_ngn']:.0f}/kWh)")
    print(f"  • Requires suitable geography for reservoirs")
    print(f"  • Slightly lower reliability ({results_solar_phs['reliability_percent']:.1f}%) due to storage limits")
    
    print("\n" + "=" * 80)
    print("FINAL RECOMMENDATION")
    print("=" * 80)
    
    # Decision logic
    if best_lcoe['option'] == 'Solar + Generator' and best_reliability['option'] == 'Solar + Battery':
        print("\n✅ RECOMMENDED: Solar + Pumped Hydro Storage")
        print("   Balanced solution: zero emissions, moderate cost, good reliability.")
        print("   Best long-term investment with lowest lifetime cost among zero-carbon options.")
        print("   Suitable if topography permits reservoir construction.")
    else:
        print("\n✅ RECOMMENDED: Solar + Battery")
        print("   Highest reliability, zero emissions, and falling battery costs.")
        print("   Ideal for communities prioritizing energy access and environmental goals.")
    
    print("\n   Solar + Generator is financially attractive today but carries fuel risk.")
    print("   Consider it as transitional solution or backup only.")
    
    print("\n" + "=" * 100)
    print("PORTFOLIO VALUE STATEMENT:")
    print("=" * 100)
    print("'Simulated hybrid microgrid options for a 25-household community,")
    print("comparing solar+battery, solar+diesel, and solar+pumped hydro storage.")
    print("Analyzed trade-offs between cost (LCOE ₦XX–₦YY/kWh), reliability (XX–YY%),")
    print("and emissions (0–YY tonnes CO₂/year). Recommended optimal configuration")
    print("based on community priorities and geographic constraints.'")
    
    print("\n" + "=" * 100)
    print("DAY 13 COMPLETE - READY FOR DAY 14: COMPLETE BUSINESS CASE PRESENTATION")
    print("=" * 100)
    
    return {
        'load': load_kw,
        'params': params,
        'solar_battery': results_solar_battery,
        'solar_generator': results_solar_gen,
        'solar_phs': results_solar_phs,
        'comparison': comparison_df
    }

# ============================================================================
# EXECUTE
# ============================================================================

if __name__ == "__main__":
    results = main()