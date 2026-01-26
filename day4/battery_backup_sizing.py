"""
DAY 4: Battery Backup Survival Model
Energy System Management Portfolio Project

Objective: Size a battery system for 8-hour blackout survival
for a typical Nigerian household, considering critical loads and system losses.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime, timedelta

# ============================================================================
# 1. SYSTEM PARAMETERS AND ASSUMPTIONS
# ============================================================================

def define_battery_parameters():
    """Define battery system parameters and assumptions"""
    
    battery_params = {
        "scenario": "8-hour blackout survival",
        "blackout_period_hours": 8,
        "blackout_start_hour": 19,  # 7 PM (typical evening outage start)
        "critical_load_selection": "Essential loads only",
        
        # Battery technology parameters (LiFePO4 - modern choice)
        "battery_chemistry": "Lithium Iron Phosphate (LiFePO4)",
        "nominal_voltage": 48,  # V (standard for residential systems)
        "depth_of_discharge": 90,  # % (LiFePO4 can safely discharge to 10% SOC)
        "round_trip_efficiency": 95,  # % (modern LiFePO4 systems)
        "cycle_life": 6000,  # cycles @ 90% DoD
        "calendar_life_years": 10,
        "temperature_range": "0°C to 45°C",
        
        # Inverter/charger parameters
        "inverter_efficiency": 96,  # %
        "charger_efficiency": 98,  # %
        "inverter_standby_loss": 10,  # W (continuous when on)
        "system_losses": 3,  # % (wiring, connections)
        
        # Safety margins
        "safety_factor": 1.15,  # 15% safety margin
        "aging_factor": 1.10,  # 10% for capacity degradation over time
    }
    
    return battery_params

# ============================================================================
# 2. CRITICAL LOAD SELECTION AND PROFILING
# ============================================================================

def identify_critical_loads():
    """Identify and profile critical loads for backup power"""
    
    critical_loads = {
        "category": "Essential loads for 8-hour blackout survival",
        
        # Individual critical appliances with typical usage patterns
        "appliances": [
            {
                "name": "Refrigerator",
                "power_w": 150,
                "duty_cycle": 40,  # % time running during blackout
                "priority": "Critical",
                "notes": "Food preservation essential"
            },
            {
                "name": "LED Lighting (Essential areas)",
                "power_w": 40,
                "usage_hours": 6,
                "priority": "Critical",
                "notes": "Living room + 2 bedrooms"
            },
            {
                "name": "Ceiling Fans (2 units)",
                "power_w": 120,
                "usage_hours": 8,
                "priority": "Critical",
                "notes": "Bedroom fans for sleep comfort"
            },
            {
                "name": "WiFi Router + Modem",
                "power_w": 15,
                "usage_hours": 8,
                "priority": "Critical",
                "notes": "Communication essential"
            },
            {
                "name": "Smartphone Charging",
                "power_w": 30,
                "usage_hours": 2,
                "priority": "Critical",
                "notes": "Emergency communication"
            },
            {
                "name": "Laptop (Work/Study)",
                "power_w": 60,
                "usage_hours": 3,
                "priority": "Important",
                "notes": "Work continuity"
            },
            {
                "name": "TV (Small LED)",
                "power_w": 50,
                "usage_hours": 2,
                "priority": "Optional",
                "notes": "Entertainment/news"
            },
        ],
        
        # Load scheduling during blackout
        "load_schedule": {
            "hour_19_20": ["Refrigerator", "Lighting", "Fans", "Router", "TV"],
            "hour_20_21": ["Refrigerator", "Lighting", "Fans", "Router", "Laptop"],
            "hour_21_22": ["Refrigerator", "Lighting", "Fans", "Router"],
            "hour_22_23": ["Refrigerator", "Fans", "Router"],
            "hour_23_00": ["Refrigerator", "Fans"],
            "hour_00_01": ["Refrigerator", "Fans"],
            "hour_01_02": ["Refrigerator"],
            "hour_02_03": ["Refrigerator"],
        }
    }
    
    return critical_loads

def create_critical_load_profile(battery_params, critical_loads):
    """Create hourly critical load profile for 8-hour blackout"""
    
    # Extract blackout period
    start_hour = battery_params["blackout_start_hour"]
    duration = battery_params["blackout_period_hours"]
    
    # Create time array for blackout period
    blackout_hours = list(range(start_hour, start_hour + duration))
    time_labels = [f"{h%24:02d}:00" for h in blackout_hours]
    
    # Initialize load profile
    hourly_load_w = [0] * duration
    
    # Define appliance power dictionary for easy lookup
    appliance_power = {item["name"]: item["power_w"] for item in critical_loads["appliances"]}
    
    # Apply load schedule
    for hour_idx, hour_range in enumerate(critical_loads["load_schedule"].keys()):
        appliances = critical_loads["load_schedule"][hour_range]
        
        # Calculate total load for this hour
        total_load_w = 0
        for appliance in appliances:
            if appliance in appliance_power:
                total_load_w += appliance_power[appliance]
        
        # Add refrigerator duty cycle (runs ~40% of time)
        if "Refrigerator" in appliances:
            fridge_power = appliance_power["Refrigerator"]
            total_load_w = total_load_w - fridge_power + (fridge_power * 0.4)
        
        hourly_load_w[hour_idx] = total_load_w
    
    # Add inverter standby loss
    hourly_load_w = [load + battery_params["inverter_standby_loss"] for load in hourly_load_w]
    
    # Convert to kW
    hourly_load_kw = [w / 1000 for w in hourly_load_w]
    
    # Create DataFrame
    df_profile = pd.DataFrame({
        'Hour_Global': blackout_hours,
        'Hour_Local': list(range(1, duration + 1)),
        'Time': time_labels,
        'Load_W': hourly_load_w,
        'Load_kW': hourly_load_kw,
    })
    
    # Calculate cumulative energy
    df_profile['Cumulative_Energy_Wh'] = df_profile['Load_W'].cumsum()
    df_profile['Cumulative_Energy_kWh'] = df_profile['Load_kW'].cumsum()
    
    total_energy_wh = df_profile['Load_W'].sum()
    total_energy_kwh = total_energy_wh / 1000
    
    return df_profile, total_energy_kwh

# ============================================================================
# 3. BATTERY SYSTEM SIZING CALCULATIONS
# ============================================================================

def calculate_battery_sizing(total_energy_kwh, battery_params):
    """Calculate required battery capacity considering all losses"""
    
    # Extract parameters
    inverter_eff = battery_params["inverter_efficiency"] / 100
    round_trip_eff = battery_params["round_trip_efficiency"] / 100
    dod = battery_params["depth_of_discharge"] / 100
    system_losses = battery_params["system_losses"] / 100
    safety_factor = battery_params["safety_factor"]
    aging_factor = battery_params["aging_factor"]
    
    # Step 1: Energy required at battery terminals (DC side)
    # Account for inverter losses (DC to AC conversion)
    dc_energy_required = total_energy_kwh / inverter_eff
    
    # Step 2: Account for round-trip efficiency (charging and discharging losses)
    battery_energy_required = dc_energy_required / round_trip_eff
    
    # Step 3: Account for system losses (wiring, connections)
    battery_energy_with_losses = battery_energy_required / (1 - system_losses)
    
    # Step 4: Account for depth of discharge
    battery_capacity_required = battery_energy_with_losses / dod
    
    # Step 5: Apply safety and aging factors
    final_battery_capacity = battery_capacity_required * safety_factor * aging_factor
    
    # Calculate usable capacity
    usable_capacity = final_battery_capacity * dod
    
    # For 48V system, calculate Ah rating
    nominal_voltage = battery_params["nominal_voltage"]
    battery_capacity_ah = (final_battery_capacity * 1000) / nominal_voltage
    
    # Typical battery module sizes (common LiFePO4 modules)
    common_module_sizes = [2.5, 5.0, 7.5, 10.0]  # kWh
    recommended_modules = []
    
    remaining_capacity = final_battery_capacity
    for module in sorted(common_module_sizes, reverse=True):
        if remaining_capacity >= module:
            count = int(remaining_capacity // module)
            if count > 0:
                recommended_modules.append({"size_kwh": module, "count": count})
                remaining_capacity -= count * module
    
    if remaining_capacity > 0:
        # Add smallest module that covers remainder
        for module in sorted(common_module_sizes):
            if module >= remaining_capacity:
                recommended_modules.append({"size_kwh": module, "count": 1})
                remaining_capacity = 0
                break
    
    sizing_results = {
        'total_energy_required_kwh': total_energy_kwh,
        'dc_energy_required_kwh': dc_energy_required,
        'battery_energy_required_kwh': battery_energy_required,
        'battery_capacity_required_kwh': battery_capacity_required,
        'final_battery_capacity_kwh': final_battery_capacity,
        'usable_capacity_kwh': usable_capacity,
        'depth_of_discharge_percent': battery_params["depth_of_discharge"],
        'round_trip_efficiency_percent': battery_params["round_trip_efficiency"],
        'inverter_efficiency_percent': battery_params["inverter_efficiency"],
        'battery_capacity_ah': battery_capacity_ah,
        'nominal_voltage': nominal_voltage,
        'recommended_modules': recommended_modules,
        'total_module_capacity_kwh': sum([m["size_kwh"] * m["count"] for m in recommended_modules]),
    }
    
    return sizing_results

# ============================================================================
# 4. STATE OF CHARGE SIMULATION
# ============================================================================

def simulate_state_of_charge(df_profile, sizing_results, battery_params):
    """Simulate battery state of charge during 8-hour blackout"""
    
    # Extract parameters
    initial_soc = 100  # Start at 100%
    dod = battery_params["depth_of_discharge"] / 100
    min_soc = 100 - battery_params["depth_of_discharge"]
    battery_capacity_kwh = sizing_results['final_battery_capacity_kwh']
    
    # Calculate energy draw each hour (considering inverter efficiency)
    inverter_eff = battery_params["inverter_efficiency"] / 100
    hourly_energy_kwh = df_profile['Load_kW'].values  # AC energy
    
    # DC energy drawn from battery each hour
    hourly_dc_energy_kwh = hourly_energy_kwh / inverter_eff
    
    # Initialize SOC arrays
    soc_percent = [initial_soc]
    remaining_energy_kwh = [battery_capacity_kwh]
    
    # Simulate hour by hour
    for hour_idx in range(len(hourly_dc_energy_kwh)):
        # Calculate new remaining energy
        new_remaining = remaining_energy_kwh[-1] - hourly_dc_energy_kwh[hour_idx]
        new_remaining = max(new_remaining, 0)  # Cannot go below 0
        
        # Calculate SOC
        new_soc = (new_remaining / battery_capacity_kwh) * 100
        
        soc_percent.append(new_soc)
        remaining_energy_kwh.append(new_remaining)
    
    # Add to DataFrame
    df_soc = df_profile.copy()
    df_soc['SOC_Percent'] = soc_percent[1:]  # Exclude initial 100%
    df_soc['Remaining_Energy_kWh'] = remaining_energy_kwh[1:]
    df_soc['Cumulative_Drawn_kWh'] = df_soc['Load_kW'].cumsum()
    
    # Calculate metrics
    final_soc = soc_percent[-1]
    energy_drawn_kwh = battery_capacity_kwh * (initial_soc - final_soc) / 100
    depth_of_discharge_actual = initial_soc - final_soc
    
    soc_metrics = {
        'initial_soc_percent': initial_soc,
        'final_soc_percent': final_soc,
        'min_soc_percent': min_soc,
        'depth_of_discharge_actual_percent': depth_of_discharge_actual,
        'energy_drawn_kwh': energy_drawn_kwh,
        'battery_capacity_utilization_percent': (energy_drawn_kwh / battery_capacity_kwh) * 100,
        'autonomy_hours': len(df_soc),
        'reserve_hours': 0 if final_soc <= min_soc else (final_soc - min_soc) * len(df_soc) / depth_of_discharge_actual,
    }
    
    return df_soc, soc_metrics

# ============================================================================
# 5. INVERTER SIZING AND SYSTEM DESIGN
# ============================================================================

def design_inverter_system(df_profile, battery_params):
    """Size inverter and design complete battery system"""
    
    # Inverter sizing based on peak load
    peak_load_w = df_profile['Load_W'].max()
    peak_load_kw = peak_load_w / 1000
    
    # Add 20% margin for startup surges (motors, compressors)
    inverter_size_w = peak_load_w * 1.2
    inverter_size_kw = inverter_size_w / 1000
    
    # Typical inverter sizes (common in market)
    common_inverter_sizes = [1.0, 1.5, 2.0, 3.0, 4.0, 5.0]  # kW
    
    # Select appropriate inverter size
    recommended_inverter_kw = None
    for size in common_inverter_sizes:
        if size >= inverter_size_kw:
            recommended_inverter_kw = size
            break
    
    if recommended_inverter_kw is None:
        recommended_inverter_kw = common_inverter_sizes[-1]
    
    # Calculate system costs (approximate Nigerian market 2025)
    inverter_cost_per_kw = 350000  # ₦ per kW
    battery_cost_per_kwh = 450000  # ₦ per kWh (LiFePO4)
    installation_cost_percent = 20  # % of equipment cost
    
    inverter_cost = recommended_inverter_kw * inverter_cost_per_kw
    
    system_design = {
        'peak_load_w': peak_load_w,
        'peak_load_kw': peak_load_kw,
        'calculated_inverter_kw': inverter_size_kw,
        'recommended_inverter_kw': recommended_inverter_kw,
        'inverter_efficiency_percent': battery_params['inverter_efficiency'],
        'inverter_standby_loss_w': battery_params['inverter_standby_loss'],
        'inverter_cost_ngn': inverter_cost,
        'battery_cost_per_kwh': battery_cost_per_kwh,
        'installation_cost_percent': installation_cost_percent,
    }
    
    return system_design

# ============================================================================
# 6. PROFESSIONAL VISUALIZATION DASHBOARD (IMPROVED)
# ============================================================================

def create_battery_analysis_dashboard(df_soc, sizing_results, soc_metrics, system_design, critical_loads):
    """Create comprehensive battery backup analysis dashboard"""
    
    # ========== PART 1: MAIN VISUALIZATION DASHBOARD ==========
    
    plt.style.use('seaborn-v0_8-whitegrid')
    mpl.rcParams['font.size'] = 9
    mpl.rcParams['axes.titlesize'] = 11
    mpl.rcParams['figure.figsize'] = [16, 10]  # Reduced from 12
    
    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. State of Charge vs Time Plot (Primary Deliverable)
    ax1 = fig.add_subplot(gs[0, :2])
    
    hours = df_soc['Hour_Local'].values
    soc = df_soc['SOC_Percent'].values
    
    # Plot SOC line
    line1 = ax1.plot(hours, soc, 'o-', color='#27AE60', linewidth=3, 
                     markersize=8, markeredgecolor='white', markeredgewidth=1.5,
                     label='State of Charge (SOC)')
    
    # Fill area under curve
    ax1.fill_between(hours, soc, alpha=0.2, color='#27AE60')
    
    # Add minimum SOC line
    min_soc = 100 - sizing_results['depth_of_discharge_percent']
    ax1.axhline(y=min_soc, color='#E74C3C', linestyle='--', linewidth=2,
                label=f'Minimum SOC ({min_soc}%)')
    
    # Add critical SOC zone (below 30%)
    ax1.axhspan(0, 30, alpha=0.1, color='red', label='Critical Zone')
    
    ax1.set_xlabel('Blackout Duration (Hours)', fontweight='bold')
    ax1.set_ylabel('State of Charge (%)', fontweight='bold')
    ax1.set_title('Battery State of Charge During 8-Hour Blackout', fontweight='bold', pad=10)
    ax1.set_xticks(range(1, 9))
    ax1.set_xlim(0.5, 8.5)
    ax1.set_ylim(0, 105)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=9)
    
    # Annotate key points
    ax1.annotate(f'Start: {soc[0]:.1f}%', xy=(1, soc[0]), xytext=(1.5, soc[0]+10),
                 arrowprops=dict(arrowstyle='->', color='#2C3E50'),
                 fontweight='bold', fontsize=9)
    ax1.annotate(f'End: {soc[-1]:.1f}%', xy=(8, soc[-1]), xytext=(6.5, soc[-1]-15),
                 arrowprops=dict(arrowstyle='->', color='#2C3E50'),
                 fontweight='bold', fontsize=9)
    
    # 2. Critical Load Profile
    ax2 = fig.add_subplot(gs[0, 2])
    
    load_values = df_soc['Load_kW'].values
    
    bars2 = ax2.bar(range(1, 9), load_values, color='#2980B9', alpha=0.8)
    ax2.set_xlabel('Hour of Blackout', fontweight='bold')
    ax2.set_ylabel('Critical Load (kW)', fontweight='bold')
    ax2.set_title('Critical Load Profile', fontweight='bold', pad=10)
    ax2.set_xticks(range(1, 9))
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars2, load_values)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 3. Battery System Specifications
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.axis('off')
    
    specs_text = f"""
BATTERY SYSTEM SPECIFICATIONS
Technology: {sizing_results.get('battery_chemistry', 'LiFePO4')}
Blackout Duration: 8 hours (7 PM - 3 AM)

BATTERY CAPACITY
Total: {sizing_results['final_battery_capacity_kwh']:.2f} kWh
Usable: {sizing_results['usable_capacity_kwh']:.2f} kWh
DoD: {sizing_results['depth_of_discharge_percent']}%
Voltage: {sizing_results['nominal_voltage']}V DC
Ah Rating: {sizing_results['battery_capacity_ah']:.0f} Ah

PERFORMANCE
Efficiency: {sizing_results['round_trip_efficiency_percent']}%
Inverter Eff: {sizing_results['inverter_efficiency_percent']}%
System Losses: 3%
Safety Margin: 15%
"""
    
    ax3.text(0.05, 0.95, specs_text, fontfamily='monospace', fontsize=8,
             verticalalignment='top', linespacing=1.5,
             bbox=dict(boxstyle='round', facecolor='#F8F9F9', alpha=0.9))
    
    # 4. Energy Balance Analysis
    ax4 = fig.add_subplot(gs[1, 1])
    
    energy_labels = ['Required\n(AC Load)', 'DC Input\nNeeded', 'Battery\nStorage', 'Usable\nCapacity']
    energy_values = [
        sizing_results['total_energy_required_kwh'],
        sizing_results['dc_energy_required_kwh'],
        sizing_results['final_battery_capacity_kwh'],
        sizing_results['usable_capacity_kwh']
    ]
    energy_colors = ['#3498DB', '#2980B9', '#2C3E50', '#27AE60']
    
    bars4 = ax4.bar(energy_labels, energy_values, color=energy_colors)
    ax4.set_ylabel('Energy Capacity (kWh)', fontweight='bold')
    ax4.set_title('Energy Flow Analysis', fontweight='bold', pad=10)
    ax4.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, val) in enumerate(zip(bars4, energy_values)):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 5. Cost Analysis
    ax5 = fig.add_subplot(gs[1, 2])
    
    battery_cost = sizing_results['final_battery_capacity_kwh'] * system_design['battery_cost_per_kwh']
    total_equipment_cost = battery_cost + system_design['inverter_cost_ngn']
    installation_cost = total_equipment_cost * (system_design['installation_cost_percent'] / 100)
    total_system_cost = total_equipment_cost + installation_cost
    
    cost_labels = ['Battery\nSystem', 'Inverter', 'Installation', 'Total\nSystem']
    cost_values = [
        battery_cost / 1000000,  # Convert to millions
        system_design['inverter_cost_ngn'] / 1000000,
        installation_cost / 1000000,
        total_system_cost / 1000000
    ]
    cost_colors = ['#27AE60', '#3498DB', '#F39C12', '#2C3E50']
    
    bars5 = ax5.bar(cost_labels, cost_values, color=cost_colors)
    ax5.set_ylabel('Cost (₦ Millions)', fontweight='bold')
    ax5.set_title('System Cost Breakdown', fontweight='bold', pad=10)
    ax5.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, val) in enumerate(zip(bars5, cost_values)):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'₦{val:.1f}M', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 6. Performance Metrics
    ax6 = fig.add_subplot(gs[2, 0])
    
    perf_labels = ['Final SOC', 'DoD Used', 'Capacity\nUtilized', 'Reserve\nMargin']
    perf_values = [
        soc_metrics['final_soc_percent'],
        soc_metrics['depth_of_discharge_actual_percent'],
        soc_metrics['battery_capacity_utilization_percent'],
        max(0, soc_metrics['final_soc_percent'] - soc_metrics['min_soc_percent'])
    ]
    perf_colors = ['#2ECC71', '#E74C3C', '#3498DB', '#F39C12']
    
    bars6 = ax6.bar(perf_labels, perf_values, color=perf_colors)
    ax6.set_ylabel('Performance Metric (%)', fontweight='bold')
    ax6.set_title('System Performance', fontweight='bold', pad=10)
    ax6.grid(True, alpha=0.3, axis='y')
    ax6.set_ylim(0, 105)
    
    for i, (bar, val) in enumerate(zip(bars6, perf_values)):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 7. SOC Timeline Visualization
    ax7 = fig.add_subplot(gs[2, 1])
    
    # Create SOC timeline with color coding
    soc_colors = []
    for soc_value in soc:
        if soc_value >= 70:
            soc_colors.append('#2ECC71')  # Green (good)
        elif soc_value >= 40:
            soc_colors.append('#F39C12')  # Orange (warning)
        elif soc_value >= 20:
            soc_colors.append('#E74C3C')  # Red (critical)
        else:
            soc_colors.append('#7B241C')  # Dark red (empty)
    
    bars7 = ax7.bar(range(1, 9), [1]*8, color=soc_colors, edgecolor='black', linewidth=1)
    
    # Add SOC values on bars
    for i, (bar, soc_val) in enumerate(zip(bars7, soc)):
        ax7.text(bar.get_x() + bar.get_width()/2., 0.5,
                f'{soc_val:.0f}%', ha='center', va='center',
                fontweight='bold', fontsize=9, color='white')
    
    ax7.set_xlabel('Hour of Blackout', fontweight='bold')
    ax7.set_title('SOC Timeline (Color-Coded)', fontweight='bold', pad=10)
    ax7.set_xticks(range(1, 9))
    ax7.set_yticks([])
    
    # 8. Critical Load Breakdown
    ax8 = fig.add_subplot(gs[2, 2])
    
    critical_appliances = []
    critical_powers = []
    for appliance in critical_loads['appliances']:
        if appliance['priority'] == 'Critical':
            critical_appliances.append(appliance['name'])
            critical_powers.append(appliance['power_w'])
    
    bars8 = ax8.barh(critical_appliances, critical_powers, color='#9B59B6', alpha=0.8)
    ax8.set_xlabel('Power (W)', fontweight='bold')
    ax8.set_title('Critical Appliance Power', fontweight='bold', pad=10)
    ax8.grid(True, alpha=0.3, axis='x')
    
    for i, (bar, val) in enumerate(zip(bars8, critical_powers)):
        width = bar.get_width()
        ax8.text(width + 5, bar.get_y() + bar.get_height()/2.,
                f'{val}W', ha='left', va='center', fontweight='bold', fontsize=8)
    
    fig.suptitle('Battery Backup Survival Model: 8-Hour Blackout Resilience\nEnergy System Management Portfolio - Day 4', 
                fontsize=14, fontweight='bold', y=1.02)
    
    plt.savefig('battery_backup_survival_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    # ========== PART 2: SEPARATE TEXT REPORT IMAGE ==========
    create_text_report_image(sizing_results, soc_metrics, system_design, total_system_cost, critical_loads)
    
    # ========== PART 3: PERFORMANCE ANALYSIS CHARTS ==========
    create_performance_analysis_charts(df_soc, sizing_results)
    
    return fig, total_system_cost

def create_text_report_image(sizing_results, soc_metrics, system_design, total_system_cost, critical_loads):
    """Create a separate image for the detailed text report"""
    
    plt.figure(figsize=(14, 18))
    plt.axis('off')
    
    battery_cost = sizing_results['final_battery_capacity_kwh'] * system_design['battery_cost_per_kwh']
    installation_cost = total_system_cost - battery_cost - system_design['inverter_cost_ngn']
    
    report_text = f"""
{'='*80}
BATTERY BACKUP SURVIVAL ANALYSIS - DETAILED REPORT
{'='*80}

SYSTEM DESIGN RECOMMENDATIONS

1. BATTERY SYSTEM SPECIFICATION:
   • Battery Capacity: {sizing_results['final_battery_capacity_kwh']:.2f} kWh LiFePO4
   • Configuration: {sizing_results['nominal_voltage']}V system, {sizing_results['battery_capacity_ah']:.0f} Ah
   • Inverter: {system_design['recommended_inverter_kw']:.0f} kW pure sine wave inverter
   • Charger: {system_design['recommended_inverter_kw']:.0f} kW MPPT solar charger (for future solar integration)

2. PERFORMANCE EXPECTATIONS:
   • Blackout Survival: 8 hours at specified critical load
   • Final SOC: {soc_metrics['final_soc_percent']:.1f}% (above minimum {soc_metrics['min_soc_percent']}%)
   • Reserve Margin: {max(0, soc_metrics['final_soc_percent'] - soc_metrics['min_soc_percent']):.1f}% ({soc_metrics.get('reserve_hours', 0):.1f} extra hours)
   • Cycle Life: {sizing_results.get('cycle_life', 6000)} cycles @ {sizing_results['depth_of_discharge_percent']}% DoD

3. FINANCIAL IMPLICATIONS:
   • Total System Cost: ₦{total_system_cost:,.0f}
   • Battery Cost: ₦{battery_cost:,.0f} ({sizing_results['final_battery_capacity_kwh']:.2f} kWh @ ₦{system_design['battery_cost_per_kwh']:,.0f}/kWh)
   • Inverter Cost: ₦{system_design['inverter_cost_ngn']:,.0f}
   • Installation: ₦{installation_cost:,.0f} (20% of equipment)

4. INTEGRATION WITH PREVIOUS ANALYSES:
   • Solar PV (Day 3): This battery can be charged by the {sizing_results.get('pv_size_reference', '4.95')} kW solar system
   • Generator (Day 2): Battery can reduce generator runtime by {min(8, 24):.0f} hours during blackouts
   • Load Profile (Day 1): Sized for critical loads from the original {sizing_results.get('daily_energy_reference', '33.2')} kWh/day profile

5. OPTIMIZATION RECOMMENDATIONS:
   • Load Management: Stagger high-power appliances to reduce peak load
   • Efficiency Improvements: Use DC appliances where possible to avoid inverter losses
   • Monitoring: Install battery management system (BMS) for safety and performance tracking
   • Maintenance: Regular capacity testing every 6 months

6. RISK MITIGATION:
   • Temperature Control: Install in temperature-controlled environment (20-25°C optimal)
   • Ventilation: Ensure adequate ventilation for heat dissipation
   • Surge Protection: Install surge protectors for grid connection
   • Warranty: Ensure minimum 5-year battery warranty, 2-year inverter warranty

7. SCALABILITY AND FUTURE EXPANSION:
   • Design for 20-30% future expansion capacity
   • Plan for EV charger integration (if considering electric vehicle)
   • Consider grid-tie capability for net metering when available
   • Design for potential integration with community microgrid

CRITICAL LOAD COMPOSITION:
"""
    
    # Add critical appliances
    for appliance in critical_loads['appliances']:
        if appliance['priority'] == 'Critical':
            report_text += f"   • {appliance['name']}: {appliance['power_w']}W"
            if 'duty_cycle' in appliance:
                report_text += f" (duty cycle: {appliance['duty_cycle']}%)"
            if 'usage_hours' in appliance:
                report_text += f" (usage: {appliance['usage_hours']} hours)"
            report_text += f" - {appliance['notes']}\n"
    
    report_text += f"""
{'='*80}
BUSINESS CASE JUSTIFICATION
{'='*80}

The {sizing_results['final_battery_capacity_kwh']:.2f} kWh battery backup system provides:
• 8 hours of essential power during grid outages
• Protection for critical appliances and communication
• Integration with existing/future solar PV system
• Reduction in generator fuel costs and maintenance
• Enhanced energy security and independence

At ₦{total_system_cost:,.0f}, this system offers reliable backup power with:
• 10+ year expected lifespan
• Minimal maintenance requirements
• Safe operation (LiFePO4 chemistry)
• Seamless integration with renewable energy

This investment provides peace of mind and energy security for the Nigerian household,
particularly valuable given frequent grid outages in the region.

{'='*80}
KEY PERFORMANCE INDICATORS
{'='*80}
• Battery Capacity: {sizing_results['final_battery_capacity_kwh']:.2f} kWh
• Usable Capacity: {sizing_results['usable_capacity_kwh']:.2f} kWh
• Final SOC after 8h: {soc_metrics['final_soc_percent']:.1f}%
• Capacity Utilization: {soc_metrics['battery_capacity_utilization_percent']:.1f}%
• System Efficiency: {sizing_results['round_trip_efficiency_percent']}% round-trip
• Cost per kWh Storage: ₦{battery_cost/sizing_results['final_battery_capacity_kwh']:,.0f}/kWh
"""
    
    plt.text(0.02, 0.98, report_text, fontfamily='monospace', fontsize=9,
             verticalalignment='top', linespacing=1.4,
             bbox=dict(boxstyle='round', facecolor='#FEF9E7', alpha=0.9, pad=12))
    
    plt.title('Battery Backup System: Detailed Technical Report\nEnergy System Management Portfolio - Day 4', 
              fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('battery_backup_detailed_report.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()

def create_performance_analysis_charts(df_soc, sizing_results):
    """Create additional performance analysis charts"""
    
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Dual axis plot: SOC vs Load
    ax1.plot(df_soc['Hour_Local'], df_soc['SOC_Percent'], 'o-', color='#27AE60', 
              linewidth=2, markersize=6, label='SOC')
    ax1.set_xlabel('Blackout Duration (Hours)', fontweight='bold')
    ax1.set_ylabel('State of Charge (%)', fontweight='bold', color='#27AE60')
    ax1.tick_params(axis='y', labelcolor='#27AE60')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(range(1, 9))
    
    ax1_twin = ax1.twinx()
    ax1_twin.plot(df_soc['Hour_Local'], df_soc['Load_kW'], 's-', color='#2980B9',
                   linewidth=2, markersize=6, label='Load')
    ax1_twin.set_ylabel('Critical Load (kW)', fontweight='bold', color='#2980B9')
    ax1_twin.tick_params(axis='y', labelcolor='#2980B9')
    
    ax1.set_title('SOC vs Load During Blackout', fontweight='bold', pad=12)
    
    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    # Battery Sizing Sensitivity
    ax2.set_xlabel('Depth of Discharge (%)', fontweight='bold')
    ax2.set_ylabel('Required Battery Capacity (kWh)', fontweight='bold')
    ax2.set_title('Battery Sizing Sensitivity to DoD', fontweight='bold', pad=12)
    
    dod_values = np.linspace(50, 95, 10)
    capacity_values = []
    for dod in dod_values:
        capacity = sizing_results['battery_energy_required_kwh'] / (dod/100)
        capacity_values.append(capacity)
    
    ax2.plot(dod_values, capacity_values, 'o-', color='#E74C3C', linewidth=2, markersize=6)
    ax2.axvline(x=sizing_results['depth_of_discharge_percent'], color='#2C3E50', 
                 linestyle='--', label=f'Selected ({sizing_results["depth_of_discharge_percent"]}%)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    fig2.suptitle('Battery System Performance Analysis', fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('battery_performance_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()

# ============================================================================
# 7. DATA EXPORT FUNCTIONS
# ============================================================================

def export_analysis_results(df_soc, sizing_results, soc_metrics, system_design, total_system_cost):
    """Export analysis results to CSV files"""
    
    # Hourly analysis data
    df_soc.to_csv('battery_hourly_analysis.csv', index=False)
    
    # System sizing summary
    sizing_summary = {
        'Parameter': [
            'Blackout Duration',
            'Battery Chemistry',
            'Total Battery Capacity (kWh)',
            'Usable Capacity (kWh)',
            'Depth of Discharge (%)',
            'Battery Voltage (V)',
            'Battery Capacity (Ah)',
            'Round-trip Efficiency (%)',
            'Inverter Efficiency (%)',
            'Peak Critical Load (kW)',
            'Recommended Inverter (kW)',
            'Total System Cost (₦)',
            'Final SOC After 8h (%)',
            'Capacity Utilization (%)',
        ],
        'Value': [
            '8 hours',
            sizing_results.get('battery_chemistry', 'LiFePO4'),
            f"{sizing_results['final_battery_capacity_kwh']:.2f}",
            f"{sizing_results['usable_capacity_kwh']:.2f}",
            f"{sizing_results['depth_of_discharge_percent']}",
            f"{sizing_results['nominal_voltage']}",
            f"{sizing_results['battery_capacity_ah']:.0f}",
            f"{sizing_results['round_trip_efficiency_percent']}",
            f"{sizing_results['inverter_efficiency_percent']}",
            f"{system_design['peak_load_kw']:.2f}",
            f"{system_design['recommended_inverter_kw']:.0f}",
            f"₦{total_system_cost:,.0f}",
            f"{soc_metrics['final_soc_percent']:.1f}",
            f"{soc_metrics['battery_capacity_utilization_percent']:.1f}",
        ]
    }
    
    df_sizing = pd.DataFrame(sizing_summary)
    df_sizing.to_csv('battery_system_sizing_summary.csv', index=False)
    
    return df_sizing

# ============================================================================
# 8. MAIN EXECUTION FUNCTION
# ============================================================================

def main():
    """Execute battery backup sizing analysis"""
    
    print("=" * 80)
    print("DAY 4: BATTERY BACKUP SURVIVAL MODEL")
    print("Energy System Management Portfolio Project")
    print("=" * 80)
    
    print("\nANALYSIS OBJECTIVE:")
    print("Size a battery system for 8-hour blackout survival")
    print("Considering: Critical loads only, system losses, depth of discharge")
    
    # Step 1: Define battery parameters
    print("\n1. DEFINING BATTERY SYSTEM PARAMETERS...")
    battery_params = define_battery_parameters()
    print(f"   • Scenario: {battery_params['scenario']}")
    print(f"   • Blackout: {battery_params['blackout_period_hours']} hours starting {battery_params['blackout_start_hour']}:00")
    print(f"   • Battery Chemistry: {battery_params['battery_chemistry']}")
    print(f"   • Depth of Discharge: {battery_params['depth_of_discharge']}%")
    print(f"   • Round-trip Efficiency: {battery_params['round_trip_efficiency']}%")
    
    # Step 2: Identify critical loads
    print("\n2. IDENTIFYING CRITICAL LOADS...")
    critical_loads = identify_critical_loads()
    print(f"   • Critical Load Category: {critical_loads['category']}")
    print(f"   • Number of Critical Appliances: {len(critical_loads['appliances'])}")
    
    # Step 3: Create critical load profile
    print("\n3. CREATING CRITICAL LOAD PROFILE...")
    df_profile, total_energy_kwh = create_critical_load_profile(battery_params, critical_loads)
    print(f"   • Total Critical Energy Required: {total_energy_kwh:.2f} kWh")
    print(f"   • Peak Critical Load: {df_profile['Load_kW'].max():.2f} kW")
    print(f"   • Average Critical Load: {df_profile['Load_kW'].mean():.2f} kW")
    
    # Step 4: Calculate battery sizing
    print("\n4. CALCULATING BATTERY SYSTEM SIZING...")
    sizing_results = calculate_battery_sizing(total_energy_kwh, battery_params)
    print(f"   • Battery Capacity Required: {sizing_results['final_battery_capacity_kwh']:.2f} kWh")
    print(f"   • Usable Capacity: {sizing_results['usable_capacity_kwh']:.2f} kWh")
    print(f"   • Battery Ah Rating: {sizing_results['battery_capacity_ah']:.0f} Ah @ {sizing_results['nominal_voltage']}V")
    
    # Step 5: Simulate state of charge
    print("\n5. SIMULATING STATE OF CHARGE...")
    df_soc, soc_metrics = simulate_state_of_charge(df_profile, sizing_results, battery_params)
    print(f"   • Initial SOC: {soc_metrics['initial_soc_percent']}%")
    print(f"   • Final SOC: {soc_metrics['final_soc_percent']:.1f}%")
    print(f"   • Depth of Discharge Used: {soc_metrics['depth_of_discharge_actual_percent']:.1f}%")
    
    # Step 6: Design inverter system
    print("\n6. DESIGNING INVERTER SYSTEM...")
    system_design = design_inverter_system(df_profile, battery_params)
    print(f"   • Peak Critical Load: {system_design['peak_load_kw']:.2f} kW")
    print(f"   • Recommended Inverter: {system_design['recommended_inverter_kw']:.0f} kW")
    print(f"   • Inverter Cost: ₦{system_design['inverter_cost_ngn']:,.0f}")
    
    # Step 7: Create visualizations
    print("\n7. CREATING PROFESSIONAL VISUALIZATIONS...")
    fig, total_system_cost = create_battery_analysis_dashboard(
        df_soc, sizing_results, soc_metrics, system_design, critical_loads
    )
    
    # Step 8: Export data
    print("\n8. EXPORTING ANALYSIS DATA...")
    df_sizing = export_analysis_results(df_soc, sizing_results, soc_metrics, system_design, total_system_cost)
    
    # Step 9: Print comprehensive findings
    print("\n" + "=" * 80)
    print("BATTERY BACKUP SURVIVAL ANALYSIS - KEY FINDINGS")
    print("=" * 80)
    
    battery_cost = sizing_results['final_battery_capacity_kwh'] * system_design['battery_cost_per_kwh']
    
    findings = f"""
SYSTEM DESIGN SUMMARY:

1. OPTIMAL BATTERY SYSTEM:
   • Battery Capacity: {sizing_results['final_battery_capacity_kwh']:.2f} kWh LiFePO4
   • Configuration: {sizing_results['nominal_voltage']}V, {sizing_results['battery_capacity_ah']:.0f} Ah
   • Inverter: {system_design['recommended_inverter_kw']:.0f} kW pure sine wave
   • Module Configuration: {sum([m['count'] for m in sizing_results.get('recommended_modules', [])])} modules

2. PERFORMANCE EXPECTATIONS:
   • Blackout Survival: 8 hours with critical loads
   • Final State of Charge: {soc_metrics['final_soc_percent']:.1f}%
   • Reserve Margin: {max(0, soc_metrics['final_soc_percent'] - (100 - sizing_results['depth_of_discharge_percent'])):.1f}%
   • Capacity Utilization: {soc_metrics['battery_capacity_utilization_percent']:.1f}% of total capacity

3. CRITICAL LOAD ANALYSIS:
   • Total Critical Energy: {total_energy_kwh:.2f} kWh over 8 hours
   • Peak Critical Load: {system_design['peak_load_kw']:.2f} kW
   • Average Critical Load: {df_profile['Load_kW'].mean():.2f} kW
   • Critical Appliances: Refrigerator, lighting, fans, communication devices

4. FINANCIAL IMPLICATIONS:
   • Total System Cost: ₦{total_system_cost:,.0f}
   • Battery Cost: ₦{battery_cost:,.0f}
   • Inverter Cost: ₦{system_design['inverter_cost_ngn']:,.0f}
   • Installation Cost: ₦{total_system_cost - battery_cost - system_design['inverter_cost_ngn']:,.0f}
   • Cost per kWh Storage: ₦{battery_cost/sizing_results['final_battery_capacity_kwh']:,.0f}/kWh

5. INTEGRATION WITH PREVIOUS ANALYSES:
   • Load Profile (Day 1): Critical loads selected from original 33.2 kWh/day profile
   • Generator (Day 2): Can eliminate {battery_params['blackout_period_hours']} hours of generator runtime
   • Solar PV (Day 3): Battery can be charged by 4.95 kW solar system during day

6. SAFETY AND RELIABILITY:
   • Battery Chemistry: LiFePO4 (inherently safe, no thermal runaway)
   • Temperature Range: {battery_params['temperature_range']}
   • Cycle Life: {sizing_results.get('cycle_life', 6000)} cycles @ {sizing_results['depth_of_discharge_percent']}% DoD
   • Calendar Life: {battery_params['calendar_life_years']} years

7. OPERATIONAL CONSIDERATIONS:
   • Charging Time: ~4-6 hours from grid, ~6-8 hours from solar
   • Maintenance: Minimal (LiFePO4 requires no regular maintenance)
   • Monitoring: Built-in BMS for cell balancing and protection
   • Warranty: Typically 5-10 years for LiFePO4 batteries

RECOMMENDATIONS FOR OPTIMAL PERFORMANCE:

1. LOAD MANAGEMENT STRATEGIES:
   • Stagger high-power appliances to reduce peak load
   • Use energy-efficient DC appliances where possible
   • Implement load shedding for non-critical appliances
   • Educate household members on energy conservation during blackouts

2. SYSTEM OPTIMIZATION:
   • Install in temperature-controlled environment (20-25°C optimal)
   • Ensure adequate ventilation for heat dissipation
   • Use proper cable sizing to minimize losses
   • Install surge protection for grid connection

3. FUTURE EXPANSION:
   • Design for 20-30% capacity expansion
   • Plan for solar PV integration (MPPT charge controller)
   • Consider smart home integration for load automation
   • Design for potential EV charging capability

4. ECONOMIC CONSIDERATIONS:
   • Consider financing options (5-7 year loans available)
   • Calculate ROI based on generator fuel savings
   • Factor in expected battery degradation (2-3% per year)
   • Consider resale value of LiFePO4 batteries

BUSINESS CASE JUSTIFICATION:

The {sizing_results['final_battery_capacity_kwh']:.2f} kWh battery backup system provides:
• 8 hours of essential power during grid outages
• Protection for critical appliances and communication
• Integration with existing/future solar PV system
• Reduction in generator fuel costs and maintenance
• Enhanced energy security and independence

At ₦{total_system_cost:,.0f}, this system offers reliable backup power with:
• 10+ year expected lifespan
• Minimal maintenance requirements
• Safe operation (LiFePO4 chemistry)
• Seamless integration with renewable energy

This investment provides peace of mind and energy security for the Nigerian household,
particularly valuable given frequent grid outages in the region.
"""
    
    print(findings)
    
    print("\n" + "=" * 80)
    print("PROJECT DELIVERABLES:")
    print("=" * 80)
    print("✓ battery_backup_survival_analysis.png - Main analysis dashboard")
    print("✓ battery_performance_analysis.png - Performance charts")
    print("✓ battery_hourly_analysis.csv - Hourly SOC and load data")
    print("✓ battery_system_sizing_summary.csv - System specifications")
    
    print("\n" + "=" * 80)
    print("PROJECT COMPLETE")
    print("Portfolio Achievement: 'Simulated energy storage performance under outage conditions'")
    print("Professional Value: Demonstrates battery system sizing and resilience planning")
    print("=" * 80)

# ============================================================================
# EXECUTE ANALYSIS
# ============================================================================

if __name__ == "__main__":
    main()