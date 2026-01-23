"""
DAY 3: Solar PV Sizing Analysis - Grid Offset Model (FIXED VERSION)
Energy System Management Portfolio Project
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime, timedelta

# ============================================================================
# 1. SOLAR ENERGY PARAMETERS (NIGERIA-SPECIFIC)
# ============================================================================

def define_solar_parameters():
    """Define Nigeria-specific solar energy parameters"""
    
    solar_parameters = {
        "location": "Nigeria (Average)",
        "peak_sun_hours": 5.5,
        "solar_irradiance": {
            "annual_average": 5.25,
            "dry_season": 6.2,
            "rainy_season": 4.3,
        },
        "tilt_angle": 15,
    }
    
    system_parameters = {
        "target_offset_percent": 60,
        "system_losses_percent": 20,
        "inverter_efficiency": 96,
        "module_efficiency": 20.5,
        "module_power": 550,
        "module_area": 2.72,
        "roof_space_available": 50,
        "panel_spacing_factor": 1.2,
    }
    
    return solar_parameters, system_parameters

# ============================================================================
# 2. HOUSEHOLD LOAD PROFILE (FROM DAY 1)
# ============================================================================

def get_household_load_profile():
    """24-hour load profile for typical Nigerian household"""
    
    hourly_load = [
        0.45, 0.45, 0.45, 0.45, 0.45, 0.45,
        2.20, 3.50, 1.80, 0.80, 0.65, 0.65,
        0.65, 1.80, 1.40, 0.90, 0.80, 1.60,
        1.40, 2.80, 3.20, 2.40, 2.10, 1.50
    ]
    
    hours = list(range(24))
    hour_labels = [f"{h:02d}:00" for h in hours]
    
    df = pd.DataFrame({
        'Hour': hours,
        'Time': hour_labels,
        'Load_kW': hourly_load,
        'Load_kWh': hourly_load  # For 1-hour intervals, kWh = kW
    })
    
    daily_energy = df['Load_kWh'].sum()
    
    return df, daily_energy

# ============================================================================
# 3. SOLAR GENERATION PROFILE MODELING
# ============================================================================

def create_solar_generation_profile(solar_params, system_params, pv_size_kw):
    """Create realistic solar generation profile for Nigeria"""
    
    hours = list(range(24))
    hour_labels = [f"{h:02d}:00" for h in hours]
    
    solar_generation = [0] * 24
    
    # Nigeria solar day: 6:00 AM to 6:00 PM
    sun_hours_start = 6
    sun_hours_end = 18
    sun_hours_center = 12
    
    for hour in range(sun_hours_start, sun_hours_end + 1):
        if hour <= sun_hours_center:
            morning_pos = (hour - sun_hours_start) / (sun_hours_center - sun_hours_start)
            normalized_gen = np.sin(morning_pos * (np.pi / 2))
        else:
            afternoon_pos = (sun_hours_end - hour) / (sun_hours_end - sun_hours_center)
            normalized_gen = np.sin(afternoon_pos * (np.pi / 2))
        
        net_normalized = normalized_gen * (1 - system_params['system_losses_percent']/100)
        hourly_gen = net_normalized * (pv_size_kw * solar_params['peak_sun_hours']) / 6
        solar_generation[hour] = max(0, hourly_gen)
    
    df_solar = pd.DataFrame({
        'Hour': hours,
        'Time': hour_labels,
        'Solar_Gen_kW': solar_generation,
        'Solar_Gen_kWh': solar_generation
    })
    
    daily_solar_energy = df_solar['Solar_Gen_kWh'].sum()
    
    return df_solar, daily_solar_energy

# ============================================================================
# 4. PV SYSTEM SIZING CALCULATIONS
# ============================================================================

def calculate_pv_sizing(daily_energy_kwh, solar_params, system_params):
    """Calculate required PV system size to meet offset target"""
    
    target_offset = system_params['target_offset_percent'] / 100
    system_losses = system_params['system_losses_percent'] / 100
    
    target_energy = daily_energy_kwh * target_offset
    required_solar_output = target_energy / (1 - system_losses)
    
    pv_size_kw = required_solar_output / solar_params['peak_sun_hours']
    
    panel_power_w = system_params['module_power']
    panel_count = int(np.ceil(pv_size_kw * 1000 / panel_power_w))
    
    actual_pv_size_kw = panel_count * panel_power_w / 1000
    
    panel_area = system_params['module_area']
    total_panel_area = panel_count * panel_area
    required_roof_space = total_panel_area * system_params['panel_spacing_factor']
    
    actual_solar_output = actual_pv_size_kw * solar_params['peak_sun_hours'] * (1 - system_losses)
    actual_offset_percent = (actual_solar_output / daily_energy_kwh) * 100
    
    sizing_results = {
        'target_offset_percent': system_params['target_offset_percent'],
        'daily_energy_kwh': daily_energy_kwh,
        'target_energy_kwh': target_energy,
        'calculated_pv_size_kw': pv_size_kw,
        'actual_pv_size_kw': actual_pv_size_kw,
        'panel_count': panel_count,
        'panel_power_w': panel_power_w,
        'panel_area_m2': panel_area,
        'total_panel_area_m2': total_panel_area,
        'required_roof_space_m2': required_roof_space,
        'actual_solar_output_kwh': actual_solar_output,
        'actual_offset_percent': actual_offset_percent,
        'roof_space_available_m2': system_params['roof_space_available'],
        'roof_space_utilization_percent': (required_roof_space / system_params['roof_space_available']) * 100,
    }
    
    return sizing_results

# ============================================================================
# 5. ENERGY BALANCE ANALYSIS
# ============================================================================

def analyze_energy_balance(df_load, df_solar, sizing_results):
    """Analyze energy balance between load and solar generation"""
    
    df_combined = pd.merge(df_load[['Hour', 'Time', 'Load_kW', 'Load_kWh']], 
                          df_solar[['Hour', 'Solar_Gen_kW', 'Solar_Gen_kWh']], 
                          on='Hour')
    
    # Calculate cumulative energy (FIX: Add this calculation)
    df_combined['Cumulative_Load_kWh'] = df_combined['Load_kWh'].cumsum()
    df_combined['Cumulative_Solar_kWh'] = df_combined['Solar_Gen_kWh'].cumsum()
    
    df_combined['Net_Load_kW'] = df_combined['Load_kW'] - df_combined['Solar_Gen_kW']
    df_combined['Net_Load_kWh'] = df_combined['Load_kWh'] - df_combined['Solar_Gen_kWh']
    
    total_load = df_combined['Load_kWh'].sum()
    total_solar = df_combined['Solar_Gen_kWh'].sum()
    
    self_consumed = min(total_solar, total_load)
    export_to_grid = max(0, total_solar - total_load)
    import_from_grid = max(0, total_load - total_solar)
    
    df_combined['Self_Consumed_kWh'] = df_combined.apply(
        lambda row: min(row['Solar_Gen_kWh'], row['Load_kWh']), axis=1)
    
    df_combined['Export_kWh'] = df_combined.apply(
        lambda row: max(0, row['Solar_Gen_kWh'] - row['Load_kWh']), axis=1)
    
    df_combined['Import_kWh'] = df_combined.apply(
        lambda row: max(0, row['Load_kWh'] - row['Solar_Gen_kWh']), axis=1)
    
    daytime_hours = list(range(6, 19))
    daytime_load = df_combined[df_combined['Hour'].isin(daytime_hours)]['Load_kWh'].sum()
    daytime_solar = df_combined[df_combined['Hour'].isin(daytime_hours)]['Solar_Gen_kWh'].sum()
    daytime_self_consumption = min(daytime_solar, daytime_load)
    
    balance_metrics = {
        'total_load_kwh': total_load,
        'total_solar_kwh': total_solar,
        'self_consumed_kwh': self_consumed,
        'export_to_grid_kwh': export_to_grid,
        'import_from_grid_kwh': import_from_grid,
        'self_consumption_rate_percent': (self_consumed / total_solar) * 100 if total_solar > 0 else 0,
        'solar_coverage_percent': (self_consumed / total_load) * 100 if total_load > 0 else 0,
        'daytime_load_kwh': daytime_load,
        'daytime_solar_kwh': daytime_solar,
        'daytime_self_consumption_kwh': daytime_self_consumption,
        'daytime_coverage_percent': (daytime_self_consumption / daytime_load) * 100 if daytime_load > 0 else 0,
    }
    
    return df_combined, balance_metrics

# ============================================================================
# 6. FINANCIAL AND ENVIRONMENTAL ANALYSIS
# ============================================================================

def calculate_benefits(df_combined, sizing_results):
    """Calculate financial and environmental benefits of solar PV"""
    
    financial_params = {
        'grid_tariff': 110,
        'solar_cost_per_kw': 1200000,
        'om_cost_per_year_percent': 1,
        'system_lifespan_years': 25,
    }
    
    environmental_params = {
        'grid_emission_factor': 0.6,
        'solar_emission_factor': 0.05,
    }
    
    system_cost = sizing_results['actual_pv_size_kw'] * financial_params['solar_cost_per_kw']
    annual_om_cost = system_cost * (financial_params['om_cost_per_year_percent'] / 100)
    
    annual_solar_gen = sizing_results['actual_solar_output_kwh'] * 365
    annual_grid_offset = min(annual_solar_gen, df_combined['Load_kWh'].sum() * 365)
    
    year1_energy_savings = annual_grid_offset * financial_params['grid_tariff']
    year1_net_savings = year1_energy_savings - annual_om_cost
    
    simple_payback_years = system_cost / year1_net_savings if year1_net_savings > 0 else float('inf')
    
    annual_co2_reduction = annual_grid_offset * (environmental_params['grid_emission_factor'] - environmental_params['solar_emission_factor'])
    
    benefits = {
        'system_size_kw': sizing_results['actual_pv_size_kw'],
        'system_cost_ngn': system_cost,
        'annual_om_cost_ngn': annual_om_cost,
        'annual_solar_generation_kwh': annual_solar_gen,
        'annual_grid_offset_kwh': annual_grid_offset,
        'annual_energy_savings_ngn': year1_energy_savings,
        'annual_net_savings_ngn': year1_net_savings,
        'simple_payback_years': simple_payback_years,
        'roi_percent': (year1_net_savings / system_cost) * 100,
        'lifetime_savings_ngn': year1_net_savings * financial_params['system_lifespan_years'],
        'annual_co2_reduction_kg': annual_co2_reduction,
        'equivalent_trees': annual_co2_reduction / 21.77,
        'equivalent_cars': annual_co2_reduction / 4600,
    }
    
    return benefits, financial_params, environmental_params

# ============================================================================
# 7. PROFESSIONAL VISUALIZATION DASHBOARD (FIXED)
# ============================================================================

def create_solar_analysis_dashboard(df_combined, sizing_results, balance_metrics, benefits):
    """Create comprehensive solar PV analysis dashboard"""
    
    plt.style.use('seaborn-v0_8-whitegrid')
    mpl.rcParams['font.size'] = 9
    mpl.rcParams['axes.titlesize'] = 11
    mpl.rcParams['figure.figsize'] = [16, 12]
    
    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(4, 3)
    
    # 1. Load vs Solar Generation Profile
    ax1 = fig.add_subplot(gs[0, :2])
    
    x = df_combined['Time']
    width = 0.35
    
    bars1 = ax1.bar(np.arange(len(x)) - width/2, df_combined['Load_kW'], 
                    width=width, color='#2980B9', alpha=0.8, label='Electrical Load')
    bars2 = ax1.bar(np.arange(len(x)) + width/2, df_combined['Solar_Gen_kW'], 
                    width=width, color='#F39C12', alpha=0.8, label='Solar Generation')
    
    ax1.set_xlabel('Hour of Day', fontweight='bold')
    ax1.set_ylabel('Power (kW)', fontweight='bold')
    ax1.set_title('Hourly Load vs Solar Generation Profile', fontweight='bold', pad=10)
    ax1.set_xticks(range(0, 24, 3))
    ax1.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 3)])
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.legend(loc='upper left', fontsize=9)
    
    # 2. Energy Balance Analysis
    ax2 = fig.add_subplot(gs[0, 2])
    
    balance_labels = ['Solar\nGeneration', 'Self-\nConsumed', 'Exported\n to Grid']
    balance_values = [
        balance_metrics['total_solar_kwh'],
        balance_metrics['self_consumed_kwh'],
        balance_metrics['export_to_grid_kwh']
    ]
    balance_colors = ['#F39C12', '#27AE60', '#3498DB']
    
    bars2_1 = ax2.bar(balance_labels, balance_values, color=balance_colors)
    ax2.set_ylabel('Daily Energy (kWh)', fontweight='bold')
    ax2.set_title('Daily Energy Balance', fontweight='bold', pad=10)
    ax2.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, val) in enumerate(zip(bars2_1, balance_values)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{val:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 3. Cumulative Energy Comparison (FIXED - using correct column names)
    ax3 = fig.add_subplot(gs[1, 0])
    
    ax3.plot(df_combined['Time'], df_combined['Cumulative_Load_kWh'],  # FIXED
             'o-', color='#2980B9', linewidth=2, markersize=4, label='Cumulative Load')
    ax3.plot(df_combined['Time'], df_combined['Cumulative_Solar_kWh'],  # FIXED
             's-', color='#F39C12', linewidth=2, markersize=4, label='Cumulative Solar')
    
    ax3.set_xlabel('Hour of Day', fontweight='bold')
    ax3.set_ylabel('Cumulative Energy (kWh)', fontweight='bold')
    ax3.set_title('Cumulative Energy Comparison', fontweight='bold', pad=10)
    ax3.set_xticks(df_combined['Time'][::3])
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper left', fontsize=9)
    
    target_energy = df_combined['Load_kWh'].sum() * 0.6
    ax3.axhline(y=target_energy, color='#E74C3C', linestyle='--', linewidth=1.5,
                label=f'Target Offset ({sizing_results["target_offset_percent"]}%)')
    ax3.legend(loc='upper left', fontsize=9)
    
    # 4. PV System Specifications
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis('off')
    
    specs_text = f"""
PV SYSTEM SPECIFICATIONS
Target Offset: {sizing_results['target_offset_percent']}%
Actual Offset: {sizing_results['actual_offset_percent']:.1f}%

SYSTEM SIZE
PV Capacity: {sizing_results['actual_pv_size_kw']:.2f} kW
Number of Panels: {sizing_results['panel_count']} × {sizing_results['panel_power_w']}W
Panel Efficiency: 20.5%

ROOF SPACE
Panel Area: {sizing_results['total_panel_area_m2']:.1f} m²
Required Space: {sizing_results['required_roof_space_m2']:.1f} m²
Available Space: {sizing_results['roof_space_available_m2']} m²
Utilization: {sizing_results['roof_space_utilization_percent']:.1f}%

DAILY PERFORMANCE
Solar Generation: {sizing_results['actual_solar_output_kwh']:.1f} kWh
Peak Sun Hours: 5.5 hours
System Losses: 20%
"""
    
    ax4.text(0.05, 0.95, specs_text, fontfamily='monospace', fontsize=8,
             verticalalignment='top', linespacing=1.5,
             bbox=dict(boxstyle='round', facecolor='#F8F9F9', alpha=0.9))
    
    # 5. Financial Analysis
    ax5 = fig.add_subplot(gs[1, 2])
    
    financial_labels = ['System Cost', 'Annual Savings', 'Annual O&M']
    financial_values = [
        benefits['system_cost_ngn']/1000000,
        benefits['annual_energy_savings_ngn']/1000000,
        benefits['annual_om_cost_ngn']/1000,
    ]
    financial_colors = ['#E74C3C', '#27AE60', '#F39C12']
    
    bars5 = ax5.bar(financial_labels, financial_values, color=financial_colors)
    ax5.set_ylabel('Cost (₦ Millions/Thousands)', fontweight='bold')
    ax5.set_title('Financial Analysis - Year 1', fontweight='bold', pad=10)
    ax5.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, val) in enumerate(zip(bars5, financial_values)):
        height = bar.get_height()
        if i == 2:
            ax5.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'₦{val*1000:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
        else:
            ax5.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'₦{val:.1f}M', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 6. Environmental Benefits
    ax6 = fig.add_subplot(gs[2, 0])
    
    env_labels = ['CO2 Reduction', 'Equivalent Trees', 'Equivalent Cars']
    env_values = [
        benefits['annual_co2_reduction_kg']/1000,
        benefits['equivalent_trees'],
        benefits['equivalent_cars']
    ]
    env_colors = ['#2ECC71', '#27AE60', '#16A085']
    
    bars6 = ax6.bar(env_labels, env_values, color=env_colors)
    ax6.set_ylabel('Annual Environmental Impact', fontweight='bold')
    ax6.set_title('Environmental Benefits', fontweight='bold', pad=10)
    ax6.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, val) in enumerate(zip(bars6, env_values)):
        height = bar.get_height()
        if i == 0:
            ax6.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{val:.1f} tons', ha='center', va='bottom', fontweight='bold', fontsize=8)
        else:
            ax6.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{val:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 7. Net Load Profile
    ax7 = fig.add_subplot(gs[2, 1])
    
    net_load = df_combined['Net_Load_kW'].clip(lower=0)
    
    bars7 = ax7.bar(df_combined['Time'], net_load, color='#9B59B6', alpha=0.8)
    ax7.axhline(y=0, color='black', linewidth=0.8)
    
    ax7.set_xlabel('Hour of Day', fontweight='bold')
    ax7.set_ylabel('Net Load (kW) - Import from Grid', fontweight='bold')
    ax7.set_title('Net Load Profile After Solar Offset', fontweight='bold', pad=10)
    ax7.set_xticks(df_combined['Time'][::3])
    ax7.grid(True, alpha=0.3, axis='y')
    
    # 8. Payback and ROI Analysis
    ax8 = fig.add_subplot(gs[2, 2])
    ax8.axis('off')
    
    roi_text = f"""
FINANCIAL METRICS
System Cost: ₦{benefits['system_cost_ngn']:,.0f}
Annual Energy Savings: ₦{benefits['annual_energy_savings_ngn']:,.0f}
Annual O&M Cost: ₦{benefits['annual_om_cost_ngn']:,.0f}
Annual Net Savings: ₦{benefits['annual_net_savings_ngn']:,.0f}

RETURN ON INVESTMENT
Simple Payback: {benefits['simple_payback_years']:.1f} years
ROI (Year 1): {benefits['roi_percent']:.1f}%
Lifetime Savings: ₦{benefits['lifetime_savings_ngn']:,.0f}

GRID INTERACTION
Daily Import: {balance_metrics['import_from_grid_kwh']:.1f} kWh
Daily Export: {balance_metrics['export_to_grid_kwh']:.1f} kWh
Self-Consumption: {balance_metrics['self_consumption_rate_percent']:.1f}%
Solar Coverage: {balance_metrics['solar_coverage_percent']:.1f}%
"""
    
    ax8.text(0.05, 0.95, roi_text, fontfamily='monospace', fontsize=8,
             verticalalignment='top', linespacing=1.5,
             bbox=dict(boxstyle='round', facecolor='#F8F9F9', alpha=0.9))
    
    # 9. System Recommendations
    ax9 = fig.add_subplot(gs[3, :])
    ax9.axis('off')
    
    recommendations = f"""
SYSTEM DESIGN RECOMMENDATIONS

1. PV SYSTEM SPECIFICATION:
   • Size: {sizing_results['actual_pv_size_kw']:.2f} kW system ({sizing_results['panel_count']} panels)
   • Panels: {sizing_results['panel_count']} × {sizing_results['panel_power_w']}W monocrystalline
   • Inverter: {sizing_results['actual_pv_size_kw']:.2f} kW grid-tied inverter (96% efficiency)

2. EXPECTED PERFORMANCE:
   • Daily Generation: {sizing_results['actual_solar_output_kwh']:.1f} kWh
   • Annual Generation: {benefits['annual_solar_generation_kwh']:,.0f} kWh
   • Grid Offset: {sizing_results['actual_offset_percent']:.1f}% of total consumption

3. FINANCIAL IMPLICATIONS:
   • Initial Investment: ₦{benefits['system_cost_ngn']:,.0f}
   • Annual Savings: ₦{benefits['annual_net_savings_ngn']:,.0f}
   • Payback Period: {benefits['simple_payback_years']:.1f} years
   • 25-Year Savings: ₦{benefits['lifetime_savings_ngn']:,.0f}

4. ENVIRONMENTAL BENEFITS:
   • Annual CO2 Reduction: {benefits['annual_co2_reduction_kg']/1000:.1f} tons
   • Equivalent to planting {int(benefits['equivalent_trees'])} trees annually
"""
    
    ax9.text(0.02, 0.98, recommendations, fontfamily='monospace', fontsize=7,
             verticalalignment='top', linespacing=1.4,
             bbox=dict(boxstyle='round', facecolor='#FEF9E7', alpha=0.9))
    
    fig.suptitle('Solar PV Sizing Analysis: Grid Offset Model for Nigerian Household\nEnergy System Management Portfolio - Day 3', 
                fontsize=14, fontweight='bold', y=1.02)
    
    plt.savefig('solar_pv_sizing_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    return fig

# ============================================================================
# 8. DATA EXPORT FUNCTIONS
# ============================================================================

def export_analysis_results(df_combined, sizing_results, benefits):
    """Export analysis results to CSV files"""
    
    df_combined.to_csv('solar_hourly_analysis.csv', index=False)
    
    sizing_summary = {
        'Parameter': [
            'Target Offset Percentage',
            'Actual Offset Percentage',
            'PV System Size (kW)',
            'Number of Panels',
            'Panel Power (W)',
            'Total Panel Area (m²)',
            'Required Roof Space (m²)',
            'Available Roof Space (m²)',
            'Roof Space Utilization (%)',
            'Daily Solar Generation (kWh)',
        ],
        'Value': [
            f"{sizing_results['target_offset_percent']}%",
            f"{sizing_results['actual_offset_percent']:.1f}%",
            f"{sizing_results['actual_pv_size_kw']:.2f}",
            f"{sizing_results['panel_count']}",
            f"{sizing_results['panel_power_w']}",
            f"{sizing_results['total_panel_area_m2']:.1f}",
            f"{sizing_results['required_roof_space_m2']:.1f}",
            f"{sizing_results['roof_space_available_m2']}",
            f"{sizing_results['roof_space_utilization_percent']:.1f}%",
            f"{sizing_results['actual_solar_output_kwh']:.1f}",
        ]
    }
    
    df_sizing = pd.DataFrame(sizing_summary)
    df_sizing.to_csv('solar_system_sizing_summary.csv', index=False)
    
    financial_summary = {
        'Metric': [
            'System Cost (₦)',
            'Annual Energy Savings (₦)',
            'Annual O&M Cost (₦)',
            'Annual Net Savings (₦)',
            'Simple Payback Period (years)',
            'ROI (Year 1, %)',
            'Lifetime Savings (₦)',
            'Annual CO2 Reduction (kg)',
        ],
        'Value': [
            f"₦{benefits['system_cost_ngn']:,.0f}",
            f"₦{benefits['annual_energy_savings_ngn']:,.0f}",
            f"₦{benefits['annual_om_cost_ngn']:,.0f}",
            f"₦{benefits['annual_net_savings_ngn']:,.0f}",
            f"{benefits['simple_payback_years']:.1f}",
            f"{benefits['roi_percent']:.1f}%",
            f"₦{benefits['lifetime_savings_ngn']:,.0f}",
            f"{benefits['annual_co2_reduction_kg']:,.0f}",
        ]
    }
    
    df_financial = pd.DataFrame(financial_summary)
    df_financial.to_csv('solar_financial_summary.csv', index=False)
    
    return df_sizing, df_financial

# ============================================================================
# 9. MAIN EXECUTION FUNCTION
# ============================================================================

def main():
    """Execute solar PV sizing analysis"""
    
    print("=" * 80)
    print("DAY 3: SOLAR PV SIZING ANALYSIS - GRID OFFSET MODEL")
    print("=" * 80)
    
    # Step 1: Define solar parameters
    print("\n1. DEFINING SOLAR ENERGY PARAMETERS...")
    solar_params, system_params = define_solar_parameters()
    print(f"   • Peak Sun Hours: {solar_params['peak_sun_hours']} hours/day")
    print(f"   • Target Offset: {system_params['target_offset_percent']}%")
    
    # Step 2: Load household profile
    print("\n2. LOADING HOUSEHOLD DEMAND PROFILE...")
    df_load, daily_energy = get_household_load_profile()
    print(f"   • Daily Energy Consumption: {daily_energy:.1f} kWh")
    
    # Step 3: Calculate PV system sizing
    print("\n3. CALCULATING PV SYSTEM SIZING...")
    sizing_results = calculate_pv_sizing(daily_energy, solar_params, system_params)
    print(f"   • Required PV Size: {sizing_results['calculated_pv_size_kw']:.2f} kW")
    print(f"   • Actual PV Size: {sizing_results['actual_pv_size_kw']:.2f} kW")
    
    # Step 4: Create solar generation profile
    print("\n4. MODELING SOLAR GENERATION PROFILE...")
    df_solar, daily_solar = create_solar_generation_profile(
        solar_params, system_params, sizing_results['actual_pv_size_kw']
    )
    print(f"   • Daily Solar Generation: {daily_solar:.1f} kWh")
    
    # Step 5: Analyze energy balance
    print("\n5. ANALYZING ENERGY BALANCE...")
    df_combined, balance_metrics = analyze_energy_balance(df_load, df_solar, sizing_results)
    print(f"   • Self-Consumption: {balance_metrics['self_consumption_rate_percent']:.1f}%")
    
    # Step 6: Calculate benefits
    print("\n6. CALCULATING FINANCIAL & ENVIRONMENTAL BENEFITS...")
    benefits, _, _ = calculate_benefits(df_combined, sizing_results)
    print(f"   • System Cost: ₦{benefits['system_cost_ngn']:,.0f}")
    print(f"   • Annual Savings: ₦{benefits['annual_net_savings_ngn']:,.0f}")
    
    # Step 7: Create visualizations
    print("\n7. CREATING PROFESSIONAL VISUALIZATIONS...")
    create_solar_analysis_dashboard(df_combined, sizing_results, balance_metrics, benefits)
    
    # Step 8: Export data
    print("\n8. EXPORTING ANALYSIS DATA...")
    export_analysis_results(df_combined, sizing_results, benefits)
    
    # Step 9: Print findings
    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)
    
    findings = f"""
SYSTEM DESIGN SUMMARY:

1. OPTIMAL SYSTEM CONFIGURATION:
   • PV System Size: {sizing_results['actual_pv_size_kw']:.2f} kW
   • Panel Configuration: {sizing_results['panel_count']} × {sizing_results['panel_power_w']}W panels
   • Expected Daily Generation: {sizing_results['actual_solar_output_kwh']:.1f} kWh

2. ENERGY OFFSET PERFORMANCE:
   • Target Offset: {sizing_results['target_offset_percent']}%
   • Actual Offset Achieved: {sizing_results['actual_offset_percent']:.1f}%
   • Daily Self-Consumption: {balance_metrics['self_consumption_rate_percent']:.1f}%

3. FINANCIAL ANALYSIS:
   • Total System Cost: ₦{benefits['system_cost_ngn']:,.0f}
   • Annual Net Savings: ₦{benefits['annual_net_savings_ngn']:,.0f}
   • Simple Payback Period: {benefits['simple_payback_years']:.1f} years

4. ENVIRONMENTAL IMPACT:
   • Annual CO2 Reduction: {benefits['annual_co2_reduction_kg']/1000:.1f} metric tons
   • Equivalent to planting {int(benefits['equivalent_trees'])} trees annually
"""
    
    print(findings)
    
    print("\n" + "=" * 80)
    print("PROJECT DELIVERABLES:")
    print("=" * 80)
    print("✓ solar_pv_sizing_analysis.png - Main analysis dashboard")
    print("✓ solar_hourly_analysis.csv - Detailed hourly data")
    print("✓ solar_system_sizing_summary.csv - System specifications")
    print("✓ solar_financial_summary.csv - Financial analysis")
    
    print("\n" + "=" * 80)
    print("PROJECT COMPLETE")
    print("=" * 80)

# ============================================================================
# EXECUTE ANALYSIS
# ============================================================================

if __name__ == "__main__":
    main()