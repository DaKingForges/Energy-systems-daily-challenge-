"""
DAY 8: Mini-Grid Design Decision Analysis - TWO IMAGE VERSION
Energy System Management Portfolio - Week 2: System Design & Decision-Making

This code creates TWO SEPARATE IMAGES:
1. Image 1: Technical & Economic Charts Only
2. Image 2: Decision Analysis Summary

Run this complete script to generate both images.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime, timedelta

# ============================================================================
# 1. RURAL HOUSEHOLD LOAD PROFILE (NEW ASSUMPTIONS)
# ============================================================================

def define_rural_household_profile():
    """Define 24-hour load profile for rural Nigerian household"""
    
    # Rural households have different patterns:
    # - Lower overall consumption
    # - Evening lighting peaks
    # - Morning cooking peaks
    # - Productive uses during day (if available)
    
    hourly_load_w = [
        50, 50, 50, 50, 50, 75,    # 00:00-05:00: Minimal (security lighting)
        350, 600, 300, 200, 180, 180,  # 06:00-11:00: Morning activities
        200, 200, 200, 250, 300, 450,  # 12:00-17:00: Daytime with productive loads
        600, 750, 800, 450, 200, 100   # 18:00-23:00: Evening peak (lighting, TV)
    ]
    
    hours = list(range(24))
    time_labels = [f"{h:02d}:00" for h in hours]
    
    df = pd.DataFrame({
        'Hour': hours,
        'Time': time_labels,
        'Load_W': hourly_load_w,
        'Load_kW': [w/1000 for w in hourly_load_w]
    })
    
    daily_energy_kwh = df['Load_kW'].sum()
    
    return df, daily_energy_kwh

# ============================================================================
# 2. MINI-GRID SCALING & AGGREGATION
# ============================================================================

def scale_to_20_households(df_single_house):
    """Scale single household profile to 20 households with diversity factor"""
    
    # Apply diversity factor (not all households peak at same time)
    # Typical diversity factor for residential: 0.6-0.8
    diversity_factor = 0.75
    
    # Base scaling
    df_scaled = df_single_house.copy()
    df_scaled['Load_kW_20homes'] = df_single_house['Load_kW'] * 20 * diversity_factor
    
    # Add community loads (school, health center, water pumping)
    community_loads = [
        0, 0, 0, 0, 0, 0,      # 00:00-05:00
        1.5, 2.0, 1.5, 1.0, 1.0, 1.0,  # 06:00-11:00: School, water pumping
        1.0, 1.0, 1.0, 2.0, 1.5, 1.0,  # 12:00-17:00: Productive uses
        2.0, 1.5, 1.0, 0.5, 0, 0      # 18:00-23:00: Community center, security
    ]
    
    df_scaled['Community_kW'] = community_loads
    df_scaled['Total_MiniGrid_kW'] = df_scaled['Load_kW_20homes'] + df_scaled['Community_kW']
    
    # Calculate daily energy
    daily_energy_kwh = df_scaled['Total_MiniGrid_kW'].sum()
    
    return df_scaled, daily_energy_kwh

# ============================================================================
# 3. GENERATION OPTION 1: SOLAR + BATTERY (HIGH RENEWABLE)
# ============================================================================

def design_solar_battery_option(df_load, daily_energy_kwh):
    """Design solar + battery system for mini-grid"""
    
    # Location: Northern Nigeria (Kano region)
    solar_params = {
        'location': 'Northern Nigeria',
        'peak_sun_hours': 6.2,  # Higher in north
        'dry_season_psh': 6.8,
        'rainy_season_psh': 5.2,
        'tilt_angle': 15,
        'system_losses': 0.20  # 20% losses
    }
    
    # Size solar to meet 120% of daily load (allows for charging batteries)
    solar_capacity_factor = 1.2
    required_solar_kw = (daily_energy_kwh * solar_capacity_factor) / \
                       (solar_params['peak_sun_hours'] * (1 - solar_params['system_losses']))
    
    # Round up to nearest 5 kW (standard mini-grid sizes)
    solar_size_kw = np.ceil(required_solar_kw / 5) * 5
    
    # Create solar generation profile
    solar_profile = [0] * 24
    for hour in range(6, 19):  # 6 AM to 6 PM
        if hour <= 12:
            # Morning: ramp up
            normalized = np.sin((hour - 6) / 6 * np.pi/2)
        else:
            # Afternoon: ramp down
            normalized = np.sin((18 - hour) / 6 * np.pi/2)
        
        # Apply seasonal variation (use average for design)
        solar_profile[hour] = normalized * solar_size_kw * solar_params['peak_sun_hours'] / 6
    
    # Battery sizing for evening load (6 PM to 6 AM)
    evening_energy = df_load[df_load['Hour'].between(18, 23)]['Total_MiniGrid_kW'].sum()
    night_energy = df_load[df_load['Hour'].between(0, 5)]['Total_MiniGrid_kW'].sum()
    
    battery_energy_kwh = (evening_energy + night_energy) * 1.5  # 50% buffer
    
    # Battery power rating (peak evening load)
    peak_evening_load = df_load[df_load['Hour'].between(18, 23)]['Total_MiniGrid_kW'].max()
    battery_power_kw = peak_evening_load * 1.2  # 20% margin
    
    # Battery specifications
    battery_params = {
        'chemistry': 'LiFePO4',
        'capacity_kwh': battery_energy_kwh,
        'power_kw': battery_power_kw,
        'depth_of_discharge': 0.80,
        'round_trip_efficiency': 0.92,
        'usable_capacity_kwh': battery_energy_kwh * 0.80 * 0.92
    }
    
    # Simulate daily energy balance
    df_balance = df_load.copy()
    df_balance['Solar_Gen_kW'] = solar_profile
    df_balance['Solar_Energy_kWh'] = df_balance['Solar_Gen_kW']  # For 1-hour intervals
    
    # Calculate net load
    df_balance['Net_Load_kW'] = df_balance['Total_MiniGrid_kW'] - df_balance['Solar_Gen_kW']
    
    # Battery charge/discharge simulation (simple model)
    battery_soc = battery_params['usable_capacity_kwh']  # Start fully charged
    battery_flow = [0] * 24
    
    for i, row in df_balance.iterrows():
        net_load = row['Net_Load_kW']
        
        if net_load < 0:  # Excess solar
            # Charge battery (limited by available excess and charge rate)
            max_charge = min(-net_load, battery_power_kw, 
                           (battery_params['usable_capacity_kwh'] - battery_soc) / 0.92)
            battery_flow[i] = -max_charge  # Negative = charging
            battery_soc += max_charge * 0.92  # Account for charging efficiency
        
        else:  # Deficit
            # Discharge battery (limited by available energy and discharge rate)
            max_discharge = min(net_load, battery_power_kw, battery_soc)
            battery_flow[i] = max_discharge
            battery_soc -= max_discharge
    
    df_balance['Battery_Flow_kW'] = battery_flow
    df_balance['Final_Net_kW'] = df_balance['Net_Load_kW'] + df_balance['Battery_Flow_kW']
    
    # Calculate metrics
    total_solar_gen = df_balance['Solar_Energy_kWh'].sum()
    energy_deficit = df_balance[df_balance['Final_Net_kW'] > 0]['Final_Net_kW'].sum()
    energy_surplus = abs(df_balance[df_balance['Final_Net_kW'] < 0]['Final_Net_kW'].sum())
    
    reliability = 100 * (1 - energy_deficit / daily_energy_kwh) if daily_energy_kwh > 0 else 0
    
    option1 = {
        'name': 'Solar + Battery (High Renewable)',
        'solar_size_kw': solar_size_kw,
        'battery_capacity_kwh': battery_energy_kwh,
        'battery_power_kw': battery_power_kw,
        'total_solar_gen_kwh': total_solar_gen,
        'energy_deficit_kwh': energy_deficit,
        'energy_surplus_kwh': energy_surplus,
        'reliability_percent': reliability,
        'solar_penetration_percent': (total_solar_gen / daily_energy_kwh) * 100,
        'battery_utilization_percent': (sum(abs(np.array(battery_flow))) / (2 * battery_energy_kwh)) * 100,
        'df_balance': df_balance,
        'battery_params': battery_params,
        'solar_params': solar_params
    }
    
    return option1

# ============================================================================
# 4. GENERATION OPTION 2: SOLAR + GENERATOR (HYBRID)
# ============================================================================

def design_solar_generator_option(df_load, daily_energy_kwh):
    """Design solar + diesel generator hybrid system"""
    
    # Solar sizing: meet 60% of daily demand
    target_solar_fraction = 0.60
    
    solar_params = {
        'location': 'Northern Nigeria',
        'peak_sun_hours': 6.2,
        'system_losses': 0.20
    }
    
    solar_energy_needed = daily_energy_kwh * target_solar_fraction
    solar_size_kw = solar_energy_needed / (solar_params['peak_sun_hours'] * (1 - solar_params['system_losses']))
    solar_size_kw = np.ceil(solar_size_kw)  # Round up
    
    # Create solar generation profile
    solar_profile = [0] * 24
    for hour in range(6, 19):
        if hour <= 12:
            normalized = np.sin((hour - 6) / 6 * np.pi/2)
        else:
            normalized = np.sin((18 - hour) / 6 * np.pi/2)
        solar_profile[hour] = normalized * solar_size_kw * solar_params['peak_sun_hours'] / 6
    
    # Generator sizing: must cover peak load when solar is unavailable
    night_hours = list(range(19, 24)) + list(range(0, 7))
    peak_night_load = df_load[df_load['Hour'].isin(night_hours)]['Total_MiniGrid_kW'].max()
    generator_size_kw = peak_night_load * 1.3  # 30% margin
    
    # Typical mini-grid generator sizes: 20, 30, 50 kVA
    standard_sizes = [20, 30, 50, 75, 100]  # kVA
    
    # Generator selection
    required_kva = generator_size_kw / 0.8  # Assume 0.8 PF
    suitable_sizes = [s for s in standard_sizes if s >= required_kva]
    
    if suitable_sizes:
        generator_kva = min(suitable_sizes)
    else:
        generator_kva = standard_sizes[-1]
    
    generator_kw = generator_kva * 0.8
    
    # Generator fuel consumption
    fuel_consumption_lph = 0.28 * generator_kw  # Liters per hour at rated load
    
    # Simulate operation: generator runs when solar insufficient
    df_balance = df_load.copy()
    df_balance['Solar_Gen_kW'] = solar_profile
    df_balance['Solar_Energy_kWh'] = df_balance['Solar_Gen_kW']
    
    df_balance['Net_Load_kW'] = df_balance['Total_MiniGrid_kW'] - df_balance['Solar_Gen_kW']
    
    # Generator operation logic
    generator_on = [0] * 24
    generator_output = [0] * 24
    fuel_used = [0] * 24
    
    min_generator_load = 0.3 * generator_kw  # Minimum efficient load
    
    for i, row in df_balance.iterrows():
        net_load = row['Net_Load_kW']
        
        if net_load > min_generator_load:
            # Generator needed
            generator_on[i] = 1
            generator_output[i] = min(net_load, generator_kw)
            fuel_used[i] = (generator_output[i] / generator_kw) * fuel_consumption_lph
        elif net_load > 0:
            # Small deficit, run generator at minimum load
            generator_on[i] = 1
            generator_output[i] = min_generator_load
            fuel_used[i] = (min_generator_load / generator_kw) * fuel_consumption_lph
    
    df_balance['Generator_On'] = generator_on
    df_balance['Generator_Output_kW'] = generator_output
    df_balance['Fuel_Used_L'] = fuel_used
    df_balance['Final_Net_kW'] = df_balance['Net_Load_kW'] - df_balance['Generator_Output_kW']
    
    # Calculate metrics
    total_solar_gen = df_balance['Solar_Energy_kWh'].sum()
    total_generator_gen = sum(generator_output)
    total_fuel_used = sum(fuel_used)
    energy_deficit = df_balance[df_balance['Final_Net_kW'] > 0]['Final_Net_kW'].sum()
    
    reliability = 100 * (1 - energy_deficit / daily_energy_kwh) if daily_energy_kwh > 0 else 0
    
    # Generator runtime
    generator_hours = sum(generator_on)
    
    option2 = {
        'name': 'Solar + Generator (Hybrid)',
        'solar_size_kw': solar_size_kw,
        'generator_size_kw': generator_kw,
        'generator_kva': generator_kva,
        'total_solar_gen_kwh': total_solar_gen,
        'total_generator_gen_kwh': total_generator_gen,
        'total_fuel_used_l': total_fuel_used,
        'generator_runtime_hours': generator_hours,
        'energy_deficit_kwh': energy_deficit,
        'reliability_percent': reliability,
        'solar_penetration_percent': (total_solar_gen / daily_energy_kwh) * 100,
        'fuel_consumption_rate_lph': fuel_consumption_lph,
        'df_balance': df_balance
    }
    
    return option2

# ============================================================================
# 5. GENERATION OPTION 3: GENERATOR-ONLY (BASELINE)
# ============================================================================

def design_generator_only_option(df_load, daily_energy_kwh):
    """Design generator-only system as baseline"""
    
    # Size generator for peak load
    peak_load = df_load['Total_MiniGrid_kW'].max()
    generator_size_kw = peak_load * 1.3  # 30% margin
    
    # Standard sizes
    standard_sizes = [30, 50, 75, 100, 150]  # kVA
    required_kva = generator_size_kw / 0.8
    
    # Find appropriate generator size
    suitable_sizes = [s for s in standard_sizes if s >= required_kva]
    
    if suitable_sizes:
        generator_kva = min(suitable_sizes)
    else:
        generator_kva = standard_sizes[-1]
    
    generator_kw = generator_kva * 0.8
    
    # Fuel consumption
    avg_power_output = daily_energy_kwh / 24
    load_factor = avg_power_output / generator_kw
    
    base_fuel_rate = 0.25  # L/kWh at 50% load
    fuel_rate = base_fuel_rate * (1 + 0.2 * (load_factor - 0.5))
    
    total_fuel_used = daily_energy_kwh * fuel_rate
    
    # Operation: runs 24/7 for reliability
    generator_runtime = 24
    reliability = 100.0
    
    option3 = {
        'name': 'Generator-Only (Baseline)',
        'generator_size_kw': generator_kw,
        'generator_kva': generator_kva,
        'daily_fuel_consumption_l': total_fuel_used,
        'fuel_rate_l_per_kwh': fuel_rate,
        'generator_runtime_hours': generator_runtime,
        'reliability_percent': reliability,
        'operational_cost_per_kwh': fuel_rate * 900,
        'df_balance': df_load.copy()
    }
    
    return option3

# ============================================================================
# 6. ECONOMIC COMPARISON
# ============================================================================

def perform_economic_comparison(option1, option2, option3):
    """Compare economic viability of three options"""
    
    # Capital costs (approximate, for comparison)
    cost_params = {
        'solar_per_kw': 1200000,  # ₦/kW
        'battery_per_kwh': 450000,  # ₦/kWh
        'generator_per_kw': 300000,  # ₦/kW
        'balance_of_system_percent': 20,
        'diesel_price': 900,  # ₦/liter
        'generator_maintenance': 50,  # ₦/operating hour
        'project_lifetime_years': 15,
        'discount_rate': 0.12,
        'om_solar_percent': 1,
        'om_battery_percent': 2,
        'om_generator_percent': 5
    }
    
    # Option 1: Solar + Battery
    solar_cost = option1['solar_size_kw'] * cost_params['solar_per_kw']
    battery_cost = option1['battery_capacity_kwh'] * cost_params['battery_per_kwh']
    equipment_cost1 = solar_cost + battery_cost
    bos_cost1 = equipment_cost1 * (cost_params['balance_of_system_percent'] / 100)
    total_capital1 = equipment_cost1 + bos_cost1
    
    # Annual O&M
    om_solar1 = solar_cost * (cost_params['om_solar_percent'] / 100)
    om_battery1 = battery_cost * (cost_params['om_battery_percent'] / 100)
    annual_om1 = om_solar1 + om_battery1
    annual_fuel1 = 0
    total_annual_cost1 = annual_om1 + annual_fuel1
    
    # Option 2: Solar + Generator
    solar_cost2 = option2['solar_size_kw'] * cost_params['solar_per_kw']
    generator_cost2 = option2['generator_size_kw'] * cost_params['generator_per_kw']
    equipment_cost2 = solar_cost2 + generator_cost2
    bos_cost2 = equipment_cost2 * (cost_params['balance_of_system_percent'] / 100)
    total_capital2 = equipment_cost2 + bos_cost2
    
    # Annual O&M and fuel
    om_solar2 = solar_cost2 * (cost_params['om_solar_percent'] / 100)
    om_generator2 = generator_cost2 * (cost_params['om_generator_percent'] / 100)
    daily_fuel_cost2 = option2['total_fuel_used_l'] * cost_params['diesel_price']
    annual_fuel_cost2 = daily_fuel_cost2 * 365
    daily_maintenance2 = option2['generator_runtime_hours'] * cost_params['generator_maintenance']
    annual_maintenance2 = daily_maintenance2 * 365
    annual_om2 = om_solar2 + om_generator2 + annual_maintenance2
    total_annual_cost2 = annual_om2 + annual_fuel_cost2
    
    # Option 3: Generator-Only
    generator_cost3 = option3['generator_size_kw'] * cost_params['generator_per_kw']
    bos_cost3 = generator_cost3 * (cost_params['balance_of_system_percent'] / 100)
    total_capital3 = generator_cost3 + bos_cost3
    
    # Annual O&M and fuel
    om_generator3 = generator_cost3 * (cost_params['om_generator_percent'] / 100)
    daily_fuel_cost3 = option3['daily_fuel_consumption_l'] * cost_params['diesel_price']
    annual_fuel_cost3 = daily_fuel_cost3 * 365
    daily_maintenance3 = 24 * cost_params['generator_maintenance']
    annual_maintenance3 = daily_maintenance3 * 365
    annual_om3 = om_generator3 + annual_maintenance3
    total_annual_cost3 = annual_om3 + annual_fuel_cost3
    
    # Calculate Levelized Cost of Energy (LCOE)
    annual_energy = 365 * (option1.get('df_balance', pd.DataFrame())['Total_MiniGrid_kW'].sum() 
                          if 'df_balance' in option1 else 150)
    
    n = cost_params['project_lifetime_years']
    r = cost_params['discount_rate']
    crf = r * (1 + r)**n / ((1 + r)**n - 1)
    
    annualized_capital1 = total_capital1 * crf
    annualized_capital2 = total_capital2 * crf
    annualized_capital3 = total_capital3 * crf
    
    total_annualized_cost1 = annualized_capital1 + total_annual_cost1
    total_annualized_cost2 = annualized_capital2 + total_annual_cost2
    total_annualized_cost3 = annualized_capital3 + total_annual_cost3
    
    lcoe1 = total_annualized_cost1 / annual_energy if annual_energy > 0 else 0
    lcoe2 = total_annualized_cost2 / annual_energy
    lcoe3 = total_annualized_cost3 / annual_energy
    
    economic_comparison = {
        'option1': {
            'name': option1['name'],
            'total_capital_ngn': total_capital1,
            'annual_om_ngn': total_annual_cost1,
            'annualized_capital_ngn': annualized_capital1,
            'total_annualized_cost_ngn': total_annualized_cost1,
            'lcoe_ngn_per_kwh': lcoe1,
            'fuel_cost_annual_ngn': annual_fuel1,
            'components': {
                'solar_kw': option1['solar_size_kw'],
                'battery_kwh': option1['battery_capacity_kwh']
            }
        },
        'option2': {
            'name': option2['name'],
            'total_capital_ngn': total_capital2,
            'annual_om_ngn': total_annual_cost2,
            'annualized_capital_ngn': annualized_capital2,
            'total_annualized_cost_ngn': total_annualized_cost2,
            'lcoe_ngn_per_kwh': lcoe2,
            'fuel_cost_annual_ngn': annual_fuel_cost2,
            'components': {
                'solar_kw': option2['solar_size_kw'],
                'generator_kw': option2['generator_size_kw']
            }
        },
        'option3': {
            'name': option3['name'],
            'total_capital_ngn': total_capital3,
            'annual_om_ngn': total_annual_cost3,
            'annualized_capital_ngn': annualized_capital3,
            'total_annualized_cost_ngn': total_annualized_cost3,
            'lcoe_ngn_per_kwh': lcoe3,
            'fuel_cost_annual_ngn': annual_fuel_cost3,
            'components': {
                'generator_kw': option3['generator_size_kw']
            }
        },
        'annual_energy_kwh': annual_energy,
        'cost_params': cost_params
    }
    
    return economic_comparison

# ============================================================================
# 7. CREATE FIRST IMAGE: CHARTS ONLY
# ============================================================================

def create_charts_figure(df_scaled, option1, option2, option3, economic_comparison):
    """Create FIRST IMAGE with just charts"""
    
    plt.style.use('seaborn-v0_8-whitegrid')
    mpl.rcParams['font.size'] = 10
    mpl.rcParams['axes.titlesize'] = 12
    mpl.rcParams['figure.figsize'] = [16, 10]
    
    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    # 1. Mini-Grid Load Profile
    ax1 = fig.add_subplot(gs[0, 0])
    
    ax1.plot(df_scaled['Hour'], df_scaled['Total_MiniGrid_kW'], 
             'o-', color='#2C3E50', linewidth=2, markersize=4, label='Total Load')
    ax1.plot(df_scaled['Hour'], df_scaled['Load_kW_20homes'], 
             '--', color='#3498DB', linewidth=1.5, alpha=0.7, label='Households Only')
    ax1.fill_between(df_scaled['Hour'], 0, df_scaled['Community_kW'], 
                     alpha=0.3, color='#2ECC71', label='Community Loads')
    
    ax1.set_xlabel('Hour of Day', fontweight='bold')
    ax1.set_ylabel('Power Demand (kW)', fontweight='bold')
    ax1.set_title('20-Household Mini-Grid Load Profile', fontweight='bold', pad=10)
    ax1.set_xticks(range(0, 24, 3))
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=9)
    
    daily_energy = df_scaled['Total_MiniGrid_kW'].sum()
    ax1.annotate(f'Daily Energy: {daily_energy:.0f} kWh', 
                 xy=(12, df_scaled['Total_MiniGrid_kW'].max() * 0.8),
                 xytext=(8, df_scaled['Total_MiniGrid_kW'].max() * 0.9),
                 arrowprops=dict(arrowstyle='->', color='#E74C3C'),
                 fontweight='bold', fontsize=9,
                 bbox=dict(boxstyle='round', facecolor='#FEF9E7', alpha=0.9))
    
    # 2. Option 1: Solar + Battery Energy Balance
    ax2 = fig.add_subplot(gs[0, 1])
    
    df1 = option1['df_balance']
    
    ax2.fill_between(df1['Hour'], 0, df1['Total_MiniGrid_kW'], 
                     alpha=0.3, color='#2C3E50', label='Load')
    ax2.fill_between(df1['Hour'], 0, df1['Solar_Gen_kW'], 
                     alpha=0.5, color='#F39C12', label='Solar Generation')
    ax2.plot(df1['Hour'], df1['Battery_Flow_kW'], 
             '--', color='#9B59B6', linewidth=2, label='Battery Flow')
    
    ax2.axhline(y=0, color='black', linewidth=0.5)
    ax2.set_xlabel('Hour of Day', fontweight='bold')
    ax2.set_ylabel('Power (kW)', fontweight='bold')
    ax2.set_title(f"{option1['name']}\nReliability: {option1['reliability_percent']:.1f}%", 
                  fontweight='bold', pad=10)
    ax2.set_xticks(range(0, 24, 3))
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left', fontsize=8)
    
    ax2.annotate(f"Solar: {option1['solar_size_kw']:.0f} kW\nBattery: {option1['battery_capacity_kwh']:.0f} kWh", 
                 xy=(18, ax2.get_ylim()[1] * 0.8),
                 xytext=(14, ax2.get_ylim()[1] * 0.7),
                 arrowprops=dict(arrowstyle='->', color='#3498DB'),
                 fontsize=8, fontweight='bold',
                 bbox=dict(boxstyle='round', facecolor='#F8F9F9', alpha=0.9))
    
    # 3. Option 2: Solar + Generator Energy Balance
    ax3 = fig.add_subplot(gs[0, 2])
    
    df2 = option2['df_balance']
    
    ax3.fill_between(df2['Hour'], 0, df2['Total_MiniGrid_kW'], 
                     alpha=0.3, color='#2C3E50', label='Load')
    ax3.fill_between(df2['Hour'], 0, df2['Solar_Gen_kW'], 
                     alpha=0.5, color='#F39C12', label='Solar')
    ax3.fill_between(df2['Hour'], 0, df2['Generator_Output_kW'], 
                     alpha=0.5, color='#E74C3C', label='Generator')
    
    ax3.set_xlabel('Hour of Day', fontweight='bold')
    ax3.set_ylabel('Power (kW)', fontweight='bold')
    ax3.set_title(f"{option2['name']}\nReliability: {option2['reliability_percent']:.1f}%", 
                  fontweight='bold', pad=10)
    ax3.set_xticks(range(0, 24, 3))
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper left', fontsize=8)
    
    ax3.annotate(f"Solar: {option2['solar_size_kw']:.0f} kW\nGenerator: {option2['generator_size_kw']:.0f} kW", 
                 xy=(18, ax3.get_ylim()[1] * 0.8),
                 xytext=(14, ax3.get_ylim()[1] * 0.7),
                 arrowprops=dict(arrowstyle='->', color='#3498DB'),
                 fontsize=8, fontweight='bold',
                 bbox=dict(boxstyle='round', facecolor='#F8F9F9', alpha=0.9))
    
    # 4. Economic Comparison: LCOE
    ax4 = fig.add_subplot(gs[1, 0])
    
    options_names = ['Solar+Battery', 'Solar+Generator', 'Generator-Only']
    lcoe_values = [
        economic_comparison['option1']['lcoe_ngn_per_kwh'],
        economic_comparison['option2']['lcoe_ngn_per_kwh'],
        economic_comparison['option3']['lcoe_ngn_per_kwh']
    ]
    colors = ['#2ECC71', '#F39C12', '#E74C3C']
    
    bars4 = ax4.bar(options_names, lcoe_values, color=colors, alpha=0.8)
    ax4.set_ylabel('Levelized Cost (₦/kWh)', fontweight='bold')
    ax4.set_title('Economic Comparison: Levelized Cost of Energy', fontweight='bold', pad=10)
    ax4.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, lcoe) in enumerate(zip(bars4, lcoe_values)):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 10,
                f'₦{lcoe:.0f}', ha='center', va='bottom', fontweight='bold')
    
    ax4.axhline(y=110, color='#3498DB', linestyle='--', linewidth=1.5, 
                label='Grid Tariff (₦110/kWh)')
    ax4.legend(loc='upper right', fontsize=8)
    
    # 5. Capital Cost Breakdown
    ax5 = fig.add_subplot(gs[1, 1])
    
    capital_costs = [
        economic_comparison['option1']['total_capital_ngn'] / 1e6,
        economic_comparison['option2']['total_capital_ngn'] / 1e6,
        economic_comparison['option3']['total_capital_ngn'] / 1e6
    ]
    
    bars5 = ax5.bar(options_names, capital_costs, color=['#2ECC71', '#F39C12', '#E74C3C'])
    ax5.set_ylabel('Capital Cost (₦ Millions)', fontweight='bold')
    ax5.set_title('Initial Investment Comparison', fontweight='bold', pad=10)
    ax5.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, cost) in enumerate(zip(bars5, capital_costs)):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'₦{cost:.1f}M', ha='center', va='bottom', fontweight='bold')
    
    # 6. Reliability Comparison
    ax6 = fig.add_subplot(gs[1, 2])
    
    reliability_values = [
        option1['reliability_percent'],
        option2['reliability_percent'],
        option3['reliability_percent']
    ]
    
    bars6 = ax6.bar(options_names, reliability_values, color=['#2ECC71', '#F39C12', '#E74C3C'])
    ax6.set_ylabel('Reliability (%)', fontweight='bold')
    ax6.set_title('System Reliability Comparison', fontweight='bold', pad=10)
    ax6.set_ylim([90, 102])
    ax6.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, reliability) in enumerate(zip(bars6, reliability_values)):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{reliability:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    ax6.axhline(y=95, color='#E74C3C', linestyle='--', linewidth=1.5, 
                label='Minimum Target (95%)')
    ax6.legend(loc='upper right', fontsize=8)
    
    fig.suptitle('Mini-Grid Design Analysis: Technical & Economic Charts\n20 Household Rural Community - Northern Nigeria', 
                fontsize=14, fontweight='bold', y=1.02)
    
    plt.savefig('mini_grid_charts_only.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    return fig

# ============================================================================
# 8. CREATE SECOND IMAGE: DECISION ANALYSIS SUMMARY
# ============================================================================

def create_decision_summary_figure(df_scaled, option1, option2, option3, economic_comparison):
    """Create SECOND IMAGE with decision analysis summary"""
    
    plt.style.use('seaborn-v0_8-whitegrid')
    mpl.rcParams['font.size'] = 10
    
    fig = plt.figure(figsize=[14, 10])
    
    # Calculate scores for each option
    reliability_scores = [option1['reliability_percent'], 
                         option2['reliability_percent'], 
                         option3['reliability_percent']]
    
    lcoe_scores = [
        economic_comparison['option1']['lcoe_ngn_per_kwh'],
        economic_comparison['option2']['lcoe_ngn_per_kwh'],
        economic_comparison['option3']['lcoe_ngn_per_kwh']
    ]
    
    capital_costs = [
        economic_comparison['option1']['total_capital_ngn'] / 1e6,
        economic_comparison['option2']['total_capital_ngn'] / 1e6,
        economic_comparison['option3']['total_capital_ngn'] / 1e6
    ]
    
    # Normalize scores (higher is better, except for cost)
    reliability_norm = [s/100 for s in reliability_scores]
    lcoe_norm = [1 - (l/max(lcoe_scores)) for l in lcoe_scores]
    capital_norm = [1 - (c/max(capital_costs)) for c in capital_costs]
    
    # Weighted scoring
    weights = {'reliability': 0.4, 'cost': 0.4, 'capital': 0.2}
    
    total_scores = []
    for i in range(3):
        score = (reliability_norm[i] * weights['reliability'] +
                lcoe_norm[i] * weights['cost'] +
                capital_norm[i] * weights['capital'])
        total_scores.append(score)
    
    best_option_idx = np.argmax(total_scores)
    options_names = ['Solar + Battery', 'Solar + Generator', 'Generator-Only']
    best_option = options_names[best_option_idx]
    
    # Decision Summary Text
    decision_text = f"""
MINI-GRID DESIGN DECISION ANALYSIS SUMMARY
{'='*80}

DECISION QUESTION:
What is the optimal generation mix for a 20-household rural 
mini-grid in Northern Nigeria to meet energy demands reliably at lowest cost?

CONSTRAINTS:
• Must serve 20 rural households with limited grid access
• Must achieve >95% reliability target
• Must be economically viable for community ownership
• Must consider seasonal variations (dry vs rainy season)

{'='*80}

SYSTEM DESIGN SPECIFICATIONS:

1. LOAD PROFILE ANALYSIS:
• Daily Energy Demand: {df_scaled['Total_MiniGrid_kW'].sum():.0f} kWh
• Peak Demand: {df_scaled['Total_MiniGrid_kW'].max():.1f} kW
• Household Load: {df_scaled['Load_kW_20homes'].sum():.0f} kWh/day
• Community Load: {df_scaled['Community_kW'].sum():.0f} kWh/day

2. GENERATION OPTIONS EVALUATED:

OPTION 1: SOLAR + BATTERY (HIGH RENEWABLE)
• Solar PV: {option1['solar_size_kw']:.0f} kW
• Battery Storage: {option1['battery_capacity_kwh']:.0f} kWh
• Reliability: {option1['reliability_percent']:.1f}%
• Solar Penetration: {option1.get('solar_penetration_percent', 0):.1f}%
• LCOE: ₦{economic_comparison['option1']['lcoe_ngn_per_kwh']:.0f}/kWh
• Capital Cost: ₦{economic_comparison['option1']['total_capital_ngn']/1e6:.1f}M

OPTION 2: SOLAR + GENERATOR (HYBRID)
• Solar PV: {option2['solar_size_kw']:.0f} kW
• Generator: {option2['generator_size_kw']:.0f} kW
• Daily Fuel Use: {option2['total_fuel_used_l']:.1f} L
• Reliability: {option2['reliability_percent']:.1f}%
• Solar Penetration: {option2.get('solar_penetration_percent', 0):.1f}%
• LCOE: ₦{economic_comparison['option2']['lcoe_ngn_per_kwh']:.0f}/kWh
• Capital Cost: ₦{economic_comparison['option2']['total_capital_ngn']/1e6:.1f}M

OPTION 3: GENERATOR-ONLY (BASELINE)
• Generator: {option3['generator_size_kw']:.0f} kW
• Daily Fuel Use: {option3['daily_fuel_consumption_l']:.1f} L
• Reliability: {option3['reliability_percent']:.1f}%
• Fuel Rate: {option3['fuel_rate_l_per_kwh']:.3f} L/kWh
• LCOE: ₦{economic_comparison['option3']['lcoe_ngn_per_kwh']:.0f}/kWh
• Capital Cost: ₦{economic_comparison['option3']['total_capital_ngn']/1e6:.1f}M

{'='*80}

DECISION FRAMEWORK & SCORING:
CRITERIA                WEIGHT    SOLAR+BATTERY   SOLAR+GENERATOR   GENERATOR-ONLY
Reliability (>95%)      40%       {reliability_norm[0]:.2f}          {reliability_norm[1]:.2f}             {reliability_norm[2]:.2f}
Operating Cost (LCOE)   40%       {lcoe_norm[0]:.2f}          {lcoe_norm[1]:.2f}             {lcoe_norm[2]:.2f}
Capital Cost            20%       {capital_norm[0]:.2f}          {capital_norm[1]:.2f}             {capital_norm[2]:.2f}
TOTAL SCORE:           100%       {total_scores[0]:.2f}          {total_scores[1]:.2f}             {total_scores[2]:.2f}

{'='*80}

RECOMMENDATION:
{best_option.upper()} is RECOMMENDED for this application.

RATIONALE:
{get_recommendation_rationale(best_option_idx)}

{'='*80}

RISK ASSESSMENT:
{get_risk_assessment(best_option_idx)}

MITIGATION STRATEGIES:
{get_mitigation_strategies(best_option_idx)}

{'='*80}

IMPLEMENTATION ROADMAP:

PHASE 1: PREPARATION (Months 1-3)
• Community engagement and ownership structure
• Detailed site assessment and design finalization
• Financing arrangement and tariff setting

PHASE 2: IMPLEMENTATION (Months 4-8)
• Procurement and logistics
• Installation and commissioning
• Training of local operators

PHASE 3: OPERATIONS (Months 9-12)
• System optimization and load growth monitoring
• Community capacity building
• Performance evaluation and reporting
"""
    
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    ax.text(0.02, 0.98, decision_text, fontfamily='monospace', fontsize=8,
            verticalalignment='top', linespacing=1.3,
            bbox=dict(boxstyle='round', facecolor='#F8F9F9', alpha=0.9))
    
    fig.suptitle('Mini-Grid Design Decision Analysis Summary\nEnergy System Management Portfolio - Day 8: System Design & Decision-Making', 
                fontsize=14, fontweight='bold', y=0.98)
    
    plt.savefig('mini_grid_decision_summary.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    return fig, best_option

def get_recommendation_rationale(best_idx):
    """Generate rationale for recommendation"""
    
    if best_idx == 0:  # Solar + Battery
        return """• HIGHEST RELIABILITY (>99%) with zero fuel dependency - exceeds the >95% target
• LOWEST OPERATING COST over project lifetime despite higher initial investment
• ENVIRONMENTAL SUSTAINABILITY: Zero emissions operation aligns with climate goals
• ENERGY SECURITY: Eliminates fuel supply chain risks in remote location
• LONG-TERM COST SAVINGS: Immune to fuel price volatility
• TECHNICAL MATURITY: Solar+battery systems proven in similar applications
• COMMUNITY OWNERSHIP: Predictable costs enable sustainable tariff structure"""
    
    elif best_idx == 1:  # Solar + Generator
        return """• BALANCED APPROACH: Good reliability with lower capital than full renewable
• FLEXIBLE OPERATION: Generator provides backup during extended cloudy periods
• PROVEN TECHNOLOGY: Both components have established local maintenance capacity
• GRADUAL TRANSITION: Can start with higher generator use, increase solar over time
• COST-EFFECTIVE: Lower upfront cost while maintaining good reliability
• RISK MITIGATION: Dual technology reduces single-point failure risk"""
    
    else:  # Generator-Only
        return """• LOWEST CAPITAL COST: Enables immediate implementation with limited funding
• SIMPLE TECHNOLOGY: Widely understood with abundant local expertise
• HIGH RELIABILITY: 100% when fuel is available
• QUICK DEPLOYMENT: Can be operational within weeks
• FLEXIBLE CAPACITY: Easy to adjust generator size as load grows
• INTERIM SOLUTION: Can serve while planning renewable transition
• SUBSIDY POTENTIAL: May qualify for government fuel subsidies"""

def get_risk_assessment(best_idx):
    """Generate risk assessment for recommended option"""
    
    if best_idx == 0:
        return """HIGH RISK:
• Capital financing availability and cost
• Battery lifespan and replacement planning
• Seasonal solar variation affecting dry vs rainy season performance

MEDIUM RISK:
• Local technical capacity for system maintenance
• Theft or vandalism of solar equipment
• Community willingness to pay for higher reliability

LOW RISK:
• Fuel price volatility (no fuel needed)
• Environmental regulatory changes
• Generator maintenance complexity"""
    
    elif best_idx == 1:
        return """HIGH RISK:
• Fuel price volatility affecting operating costs
• Fuel supply chain reliability in remote location
• Generator maintenance and spare parts availability

MEDIUM RISK:
• Seasonal solar variation
• Optimal dispatch strategy implementation
• Balance between fuel use and battery cycling

LOW RISK:
• Technology familiarity
• Environmental compliance
• Community acceptance"""
    
    else:
        return """HIGH RISK:
• Fuel price and availability volatility
• Environmental pollution and community health impacts
• Operating cost sensitivity to fuel price increases
• Noise pollution affecting community acceptance

MEDIUM RISK:
• Generator maintenance requirements
• Fuel theft or diversion
• Carbon tax or environmental regulation changes

LOW RISK:
• Technology complexity
• Initial capital requirements
• Implementation timeline"""

def get_mitigation_strategies(best_idx):
    """Generate mitigation strategies for recommended option"""
    
    if best_idx == 0:
        return """• FINANCING: Seek blended finance with grants, concessional loans, and community equity
• BATTERY WARRANTY: Secure 8-10 year performance warranties from reputable manufacturers
• SEASONAL DESIGN: Oversize solar by 20% to account for rainy season reduction
• CAPACITY BUILDING: Invest in training local youth as system operators
• COMMUNITY ENGAGEMENT: Establish mini-grid cooperative for ownership and governance
• TARIFF DESIGN: Implement increasing block tariff to ensure affordability and sustainability"""
    
    elif best_idx == 1:
        return """• FUEL HEDGING: Establish bulk fuel purchasing agreements or consider biofuel blends
• PREVENTIVE MAINTENANCE: Implement rigorous maintenance schedule with local technicians
• HYBRID OPTIMIZATION: Use smart controller to minimize fuel use while maintaining reliability
• SOLAR EXPANSION: Design for future solar addition as costs decrease
• FUEL SECURITY: Maintain minimum 2-week fuel reserve at site
• COMMUNITY INVOLVEMENT: Train community members in basic generator maintenance"""
    
    else:
        return """• FUEL MANAGEMENT: Establish transparent fuel procurement and monitoring system
• MAINTENANCE FUND: Create sinking fund for generator overhaul and replacement
• TRANSITION PLAN: Develop 3-5 year plan to integrate renewable components
• EFFICIENCY MEASURES: Implement demand-side management and efficient appliances
• ENVIRONMENTAL OFFSETS: Explore carbon credit opportunities
• COMMUNITY EDUCATION: Raise awareness about fuel costs and energy conservation"""

# ============================================================================
# 9. TECHNICAL SPECIFICATIONS (BONUS THIRD IMAGE)
# ============================================================================

def create_technical_specifications(option1, option2, option3, economic, best_idx):
    """Create detailed technical specification sheet (third image)"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    options_list = ['Solar + Battery', 'Solar + Generator', 'Generator-Only']
    
    if best_idx == 0:
        best_option = option1
        specs = economic['option1']
    elif best_idx == 1:
        best_option = option2
        specs = economic['option2']
    else:
        best_option = option3
        specs = economic['option3']
    
    spec_text = f"""
RECOMMENDED SYSTEM SPECIFICATIONS
{best_option['name']}

SYSTEM OVERVIEW:
• Designed for: 20 rural households + community loads
• Location: Northern Nigeria
• Daily Energy Demand: {option1['df_balance']['Total_MiniGrid_kW'].sum():.0f} kWh
• Design Reliability: {best_option['reliability_percent']:.1f}%

COMPONENT SPECIFICATIONS:
"""
    
    if 'solar_size_kw' in best_option:
        spec_text += f"""• Solar PV: {best_option['solar_size_kw']:.1f} kW
  - Type: Monocrystalline, 20% efficiency
  - Mounting: Fixed tilt at 15°, south-facing
  - Expected Generation: {best_option.get('total_solar_gen_kwh', 0):.0f} kWh/day
"""
    
    if 'battery_capacity_kwh' in best_option:
        spec_text += f"""• Battery Storage: {best_option['battery_capacity_kwh']:.1f} kWh
  - Chemistry: LiFePO4
  - Usable Capacity: {best_option['battery_params']['usable_capacity_kwh']:.1f} kWh
  - Power Rating: {best_option['battery_power_kw']:.1f} kW
  - Depth of Discharge: {best_option['battery_params']['depth_of_discharge']*100:.0f}%
  - Round-trip Efficiency: {best_option['battery_params']['round_trip_efficiency']*100:.0f}%
"""
    
    if 'generator_size_kw' in best_option:
        spec_text += f"""• Generator: {best_option['generator_size_kw']:.1f} kW ({best_option.get('generator_kva', 0):.1f} kVA)
  - Type: Diesel, silent canopy
  - Expected Runtime: {best_option.get('generator_runtime_hours', 0):.0f} hours/day
  - Fuel Consumption: {best_option.get('total_fuel_used_l', best_option.get('daily_fuel_consumption_l', 0)):.1f} L/day
  - Fuel Rate: {best_option.get('fuel_consumption_rate_lph', best_option.get('fuel_rate_l_per_kwh', 0)):.2f} L/kWh
"""

    spec_text += f"""
ELECTRICAL SYSTEM:
• Distribution: 230V AC, single-phase
• Protection: Circuit breakers, surge protection
• Metering: Prepaid smart meters for each household
• Control: Automatic load management system

FINANCIAL SPECIFICATIONS:
• Total Capital Cost: ₦{specs['total_capital_ngn']:,.0f}
• Annual Operating Cost: ₦{specs['annual_om_ngn'] + specs.get('fuel_cost_annual_ngn', 0):,.0f}
• Levelized Cost of Energy: ₦{specs['lcoe_ngn_per_kwh']:.0f}/kWh
• Project Lifetime: {economic['cost_params']['project_lifetime_years']} years

PERFORMANCE METRICS:
• Solar Penetration: {best_option.get('solar_penetration_percent', 0):.1f}%
• Battery Utilization: {best_option.get('battery_utilization_percent', 0):.1f}%
• Generator Capacity Factor: {best_option.get('total_generator_gen_kwh', 0)/(best_option.get('generator_size_kw', 1)*24)*100 if best_option.get('generator_size_kw', 0) > 0 else 0:.1f}%
• System Availability: >95% target

TARIFF DESIGN (Example):
• Fixed charge: ₦500/month per household
• Energy charge: ₦{min(150, specs['lcoe_ngn_per_kwh']*1.2):.0f}/kWh
• Expected revenue: ₦{(min(150, specs['lcoe_ngn_per_kwh']*1.2)*option1['df_balance']['Total_MiniGrid_kW'].sum()*30 + 500*20):,.0f}/month
• Operating margin: {((min(150, specs['lcoe_ngn_per_kwh']*1.2)*option1['df_balance']['Total_MiniGrid_kW'].sum()*30 + 500*20) - (specs['annual_om_ngn'] + specs.get('fuel_cost_annual_ngn', 0))/12)/(specs['annual_om_ngn'] + specs.get('fuel_cost_annual_ngn', 0))*12*100:.1f}%

IMPLEMENTATION TIMELINE:
• Month 1-2: Community engagement and site assessment
• Month 3-4: Detailed design and financing
• Month 5-6: Procurement and logistics
• Month 7-8: Installation and commissioning
• Month 9-12: Operation and optimization
"""
    
    ax.text(0.05, 0.95, spec_text, fontfamily='monospace', fontsize=9,
            verticalalignment='top', linespacing=1.4,
            bbox=dict(boxstyle='round', facecolor='#F8F9F9', alpha=0.9))
    
    ax.set_title('Recommended Mini-Grid System: Technical Specifications', 
                 fontsize=12, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('mini_grid_technical_specifications.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()

# ============================================================================
# 10. MAIN FUNCTION FOR TWO IMAGES
# ============================================================================

def main():
    """Main function to run the complete analysis and generate two images"""
    
    print("=" * 80)
    print("DAY 8: MINI-GRID DESIGN DECISION ANALYSIS - TWO IMAGE VERSION")
    print("=" * 80)
    
    # Step 1: Define rural household profile
    print("\n1. DEFINING RURAL HOUSEHOLD LOAD PROFILE...")
    df_household, household_energy = define_rural_household_profile()
    print(f"   • Single household daily energy: {household_energy:.1f} kWh")
    
    # Step 2: Scale to mini-grid
    print("\n2. SCALING TO 20-HOUSEHOLD MINI-GRID...")
    df_minigrid, minigrid_energy = scale_to_20_households(df_household)
    print(f"   • Mini-grid daily energy: {minigrid_energy:.1f} kWh")
    print(f"   • Peak demand: {df_minigrid['Total_MiniGrid_kW'].max():.2f} kW")
    
    # Step 3: Design three options
    print("\n3. DESIGNING GENERATION OPTIONS...")
    option1 = design_solar_battery_option(df_minigrid, minigrid_energy)
    option2 = design_solar_generator_option(df_minigrid, minigrid_energy)
    option3 = design_generator_only_option(df_minigrid, minigrid_energy)
    
    print(f"   • Option 1: Solar + Battery: {option1['solar_size_kw']:.1f} kW PV, {option1['battery_capacity_kwh']:.1f} kWh battery")
    print(f"   • Option 2: Solar + Generator: {option2['solar_size_kw']:.1f} kW PV, {option2['generator_size_kw']:.1f} kW generator")
    print(f"   • Option 3: Generator-Only: {option3['generator_size_kw']:.1f} kW generator")
    
    # Step 4: Economic comparison
    print("\n4. PERFORMING ECONOMIC COMPARISON...")
    economic = perform_economic_comparison(option1, option2, option3)
    
    print(f"   • Option 1 LCOE: ₦{economic['option1']['lcoe_ngn_per_kwh']:.0f}/kWh")
    print(f"   • Option 2 LCOE: ₦{economic['option2']['lcoe_ngn_per_kwh']:.0f}/kWh")
    print(f"   • Option 3 LCOE: ₦{economic['option3']['lcoe_ngn_per_kwh']:.0f}/kWh")
    
    # Step 5: Create Image 1: Charts Only
    print("\n5. CREATING IMAGE 1: TECHNICAL & ECONOMIC CHARTS...")
    create_charts_figure(df_minigrid, option1, option2, option3, economic)
    
    # Step 6: Create Image 2: Decision Analysis Summary
    print("\n6. CREATING IMAGE 2: DECISION ANALYSIS SUMMARY...")
    fig2, recommendation = create_decision_summary_figure(df_minigrid, option1, option2, option3, economic)
    
    # Step 7: Create Image 3: Technical Specifications
    print("\n7. CREATING IMAGE 3: TECHNICAL SPECIFICATIONS...")
    create_technical_specifications(option1, option2, option3, economic, 
                                   ['Solar + Battery', 'Solar + Generator', 'Generator-Only'].index(recommendation))
    
    # Final output
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE - THREE IMAGES GENERATED:")
    print("=" * 80)
    print("1. mini_grid_charts_only.png - Technical & economic charts (6 charts)")
    print("2. mini_grid_decision_summary.png - Decision analysis summary")
    print("3. mini_grid_technical_specifications.png - Technical specifications")
    print("\nRECOMMENDATION: " + recommendation.upper())
    print("=" * 80)

# ============================================================================
# RUN THE ANALYSIS
# ============================================================================

if __name__ == "__main__":
    main()