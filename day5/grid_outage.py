"""
DAY 5: Grid Outage Economic Impact Analysis
Energy System Management Portfolio Project

Objective: Quantify the economic impact of frequent grid blackouts on Nigerian households
through Value of Lost Load (VoLL) analysis and reliability cost calculations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime, timedelta

# ============================================================================
# 1. OUTAGE SCENARIO DEFINITIONS
# ============================================================================

def define_outage_scenarios():
    """Define realistic grid outage scenarios for Nigerian urban areas"""
    
    scenarios = {
        "urban_moderate": {
            "description": "Urban area with moderate grid instability",
            "weekly_outages": 4,
            "avg_duration_hours": 4.5,
            "outage_timing": {
                "peak_hours_ratio": 0.65,  # 65% of outages during peak hours (6-10 PM)
                "off_peak_ratio": 0.35,    # 35% during off-peak
                "typical_times": ["17:00-21:30", "13:00-15:00", "09:00-11:00", "22:00-02:00"]
            },
            "seasonal_variation": {
                "rainy_season_multiplier": 1.3,   # 30% more outages
                "dry_season_multiplier": 0.85,    # 15% fewer outages
                "festive_season_multiplier": 1.5  # 50% more in December
            }
        },
        "urban_severe": {
            "description": "Urban area with severe grid instability",
            "weekly_outages": 7,
            "avg_duration_hours": 6.2,
            "outage_timing": {
                "peak_hours_ratio": 0.80,
                "off_peak_ratio": 0.20,
                "typical_times": ["18:00-23:00", "14:00-18:00", "10:00-14:00", "23:00-04:00"]
            }
        },
        "rural_severe": {
            "description": "Rural area with extremely poor grid access",
            "weekly_outages": 10,
            "avg_duration_hours": 8.5,
            "outage_timing": {
                "peak_hours_ratio": 0.50,
                "off_peak_ratio": 0.50,
                "typical_times": ["All day intermittent"]
            }
        }
    }
    
    # Value of Lost Load (VoLL) assumptions
    # ₦/kWh - What households are willing to pay to avoid outage
    voll_parameters = {
        "residential_sectors": {
            "low_income": {
                "voll_base": 180,  # ₦/kWh
                "peak_multiplier": 2.5,
                "critical_hours": ["18:00-22:00"]
            },
            "middle_income": {
                "voll_base": 320,
                "peak_multiplier": 3.0,
                "critical_hours": ["07:00-09:00", "18:00-23:00"]
            },
            "high_income": {
                "voll_base": 550,
                "peak_multiplier": 3.5,
                "critical_hours": ["06:00-10:00", "18:00-24:00"]
            }
        },
        "time_of_day_factors": {
            "peak": 2.0,      # 18:00-22:00
            "shoulder": 1.5,  # 07:00-09:00, 22:00-24:00
            "off_peak": 1.0   # 00:00-07:00, 09:00-18:00
        },
        "appliance_importance": {
            "critical": 3.0,      # Refrigeration, medical, security
            "important": 2.0,     # Lighting, fans, communication
            "comfort": 1.5,       # Entertainment, air conditioning
            "non_essential": 1.0  # Miscellaneous
        }
    }
    
    return scenarios, voll_parameters

# ============================================================================
# 2. HOUSEHOLD LOAD PROFILE (FROM DAY 1 - STANDARDIZED)
# ============================================================================

def get_standardized_load_profile():
    """Standardized 24-hour load profile for middle-income Nigerian household"""
    
    hourly_load_kw = [
        0.62, 0.62, 0.62, 0.62, 0.62, 0.65,  # 00:00-05:00
        2.85, 2.15, 0.50, 0.50, 0.50, 0.50,  # 06:00-11:00
        0.50, 0.50, 0.50, 0.85, 0.95, 1.55,  # 12:00-17:00
        2.65, 2.45, 1.85, 1.15, 0.62, 0.62   # 18:00-23:00
    ]
    
    hours = list(range(24))
    time_labels = [f"{h:02d}:00" for h in hours]
    
    df = pd.DataFrame({
        'Hour': hours,
        'Time': time_labels,
        'Load_kW': hourly_load_kw,
        'Time_Period': pd.cut(hours, 
                            bins=[-1, 6, 9, 18, 22, 24],
                            labels=['Night', 'Morning_Peak', 'Day', 'Evening_Peak', 'Late_Evening'])
    })
    
    daily_energy_kwh = df['Load_kW'].sum()
    
    return df, daily_energy_kwh

# ============================================================================
# 3. ENERGY NOT SERVED (ENS) CALCULATION (FIXED VERSION)
# ============================================================================

def calculate_energy_not_served(scenario, df_load):
    """Calculate Energy Not Served for given outage scenario"""
    
    weekly_outages = scenario["weekly_outages"]
    avg_duration = scenario["avg_duration_hours"]
    
    # Simulate outages over a month (4.33 weeks)
    num_weeks = 4.33
    monthly_outages = weekly_outages * num_weeks
    
    # Create random outage timing (weighted toward peak hours)
    np.random.seed(42)  # For reproducibility
    
    outage_hours = []
    outage_energy_kwh = []
    
    peak_hour_start = 18
    peak_hour_end = 22
    
    for outage in range(int(monthly_outages)):
        # Weight outage timing toward peak hours
        if np.random.random() < scenario["outage_timing"]["peak_hours_ratio"]:
            # Peak hour outage - FIXED: ensure valid range
            # Use min to ensure we don't get negative or invalid ranges
            max_start_hour = peak_hour_end - 1  # Ensure at least 1 hour duration
            if max_start_hour <= peak_hour_start:
                # If duration is too long, just use peak_hour_start
                start_hour = peak_hour_start
            else:
                start_hour = np.random.randint(peak_hour_start, max_start_hour)
        else:
            # Off-peak outage - FIXED: ensure valid range
            max_start_hour = 24 - 1  # Ensure at least 1 hour duration
            start_hour = np.random.randint(0, max_start_hour)
        
        # Generate duration with normal distribution
        duration = np.random.normal(avg_duration, 1.0)
        duration = max(2.0, min(10.0, duration))  # Bound between 2-10 hours
        
        # Calculate energy not served for this outage
        outage_energy = 0
        for hour_offset in range(int(np.ceil(duration))):
            hour = (start_hour + hour_offset) % 24
            # Calculate fraction of hour affected
            if hour_offset < int(duration):
                fraction = 1.0
            else:
                fraction = duration - int(duration)
            
            # Get load for this hour
            hour_load = df_load.loc[df_load['Hour'] == hour, 'Load_kW'].values[0]
            outage_energy += hour_load * fraction
        
        outage_hours.append({
            'start_hour': start_hour,
            'duration_hours': duration,
            'energy_not_served_kwh': outage_energy
        })
        outage_energy_kwh.append(outage_energy)
    
    # Calculate statistics
    total_ens_kwh = sum(outage_energy_kwh)
    avg_ens_per_outage = np.mean(outage_energy_kwh) if outage_energy_kwh else 0
    max_ens_per_outage = max(outage_energy_kwh) if outage_energy_kwh else 0
    
    # Weekly and monthly aggregates
    weekly_ens_kwh = total_ens_kwh / num_weeks if num_weeks > 0 else 0
    monthly_ens_kwh = total_ens_kwh
    
    # Calculate outage minutes per month
    outage_minutes = sum([o['duration_hours'] * 60 for o in outage_hours])
    system_minutes_per_month = 30 * 24 * 60
    reliability_percentage = 100 * (1 - outage_minutes / system_minutes_per_month)
    
    ens_results = {
        'scenario_description': scenario['description'],
        'weekly_outages': weekly_outages,
        'avg_outage_duration_hours': avg_duration,
        'monthly_outages': monthly_outages,
        'total_monthly_ens_kwh': monthly_ens_kwh,
        'avg_ens_per_outage_kwh': avg_ens_per_outage,
        'max_ens_per_outage_kwh': max_ens_per_outage,
        'weekly_ens_kwh': weekly_ens_kwh,
        'outage_minutes_per_month': outage_minutes,
        'system_reliability_percent': reliability_percentage,
        'detailed_outages': outage_hours,
        'monthly_energy_requirement_kwh': df_load['Load_kW'].sum() * 30,
        'reliability_index': reliability_percentage / 100,
        'energy_availability_factor': 1 - (monthly_ens_kwh / (df_load['Load_kW'].sum() * 30)) if (df_load['Load_kW'].sum() * 30) > 0 else 1
    }
    
    return ens_results
# ============================================================================
# 4. VALUE OF LOST LOAD (VoLL) CALCULATION
# ============================================================================

def calculate_value_of_lost_load(ens_results, voll_parameters, income_level="middle_income"):
    """Calculate economic impact using Value of Lost Load methodology"""
    
    voll_profile = voll_parameters['residential_sectors'][income_level]
    time_factors = voll_parameters['time_of_day_factors']
    
    total_voll_cost = 0
    time_segment_costs = {'peak': 0, 'shoulder': 0, 'off_peak': 0}
    
    # Analyze each outage
    for outage in ens_results['detailed_outages']:
        start_hour = outage['start_hour']
        duration = outage['duration_hours']
        outage_energy = outage['energy_not_served_kwh']
        
        # Determine time-of-day multiplier
        if 18 <= start_hour < 22 or (start_hour < 22 and start_hour + duration > 18):
            # Peak hours (6-10 PM)
            time_multiplier = time_factors['peak']
            segment = 'peak'
        elif (7 <= start_hour < 9) or (22 <= start_hour < 24) or (start_hour + duration > 7 and start_hour < 9):
            # Shoulder hours (7-9 AM, 10 PM-12 AM)
            time_multiplier = time_factors['shoulder']
            segment = 'shoulder'
        else:
            # Off-peak hours
            time_multiplier = time_factors['off_peak']
            segment = 'off_peak'
        
        # Calculate VoLL for this outage
        voll_rate = voll_profile['voll_base'] * time_multiplier
        outage_voll_cost = outage_energy * voll_rate
        
        total_voll_cost += outage_voll_cost
        time_segment_costs[segment] += outage_voll_cost
    
    # Calculate per-kWh metrics
    avg_voll_per_kwh = total_voll_cost / ens_results['total_monthly_ens_kwh'] if ens_results['total_monthly_ens_kwh'] > 0 else 0
    
    # Grid tariff comparison (baseline)
    grid_tariff = 110  # ₦/kWh from Day 1
    grid_cost_of_ens = ens_results['total_monthly_ens_kwh'] * grid_tariff
    
    # Generator cost comparison (alternative)
    generator_cost_per_kwh = 485  # ₦/kWh from Day 2 analysis
    generator_cost_of_ens = ens_results['total_monthly_ens_kwh'] * generator_cost_per_kwh
    
    voll_results = {
        'income_level': income_level,
        'voll_base_rate': voll_profile['voll_base'],
        'total_monthly_voll_ngn': total_voll_cost,
        'avg_voll_per_kwh': avg_voll_per_kwh,
        'time_segment_costs': time_segment_costs,
        'grid_tariff_cost_ngn': grid_cost_of_ens,
        'generator_alternative_cost_ngn': generator_cost_of_ens,
        'voll_premium_over_grid': avg_voll_per_kwh / grid_tariff if grid_tariff > 0 else 0,
        'voll_premium_over_generator': avg_voll_per_kwh / generator_cost_per_kwh if generator_cost_per_kwh > 0 else 0,
        'monthly_voll_per_capita': total_voll_cost / 5,  # Assuming 5-person household
    }
    
    return voll_results

# ============================================================================
# 5. COMPREHENSIVE ECONOMIC IMPACT ANALYSIS
# ============================================================================

def analyze_economic_impact(ens_results, voll_results):
    """Combine ENS and VoLL for comprehensive economic impact"""
    
    # Direct costs (based on grid tariff)
    direct_energy_cost = ens_results['total_monthly_ens_kwh'] * 110
    
    # Indirect costs (VoLL)
    indirect_cost = voll_results['total_monthly_voll_ngn']
    
    # Total economic impact
    total_economic_impact = direct_energy_cost + indirect_cost
    
    # Alternative scenarios
    # 1. Generator backup cost
    generator_cost = ens_results['total_monthly_ens_kwh'] * 485
    
    # 2. Solar + Battery system cost (amortized monthly from Day 3 & 4)
    solar_system_cost = 5940000  # ₦ from Day 3 (4.95 kW system)
    battery_system_cost = 1690000  # ₦ from Day 4 (2.64 kWh system)
    hybrid_system_cost = solar_system_cost + battery_system_cost
    
    # Amortization over 10 years at 15% interest
    monthly_hybrid_cost = hybrid_system_cost * (0.15/12) / (1 - (1 + 0.15/12)**(-10*12))
    
    # 3. Cost of inaction (continuing with outages)
    cost_of_inaction = total_economic_impact
    
    # Return on Investment calculations
    # If hybrid system eliminates 80% of outage impact
    outage_reduction_rate = 0.80
    monthly_savings_with_hybrid = total_economic_impact * outage_reduction_rate
    hybrid_payback_months = hybrid_system_cost / monthly_savings_with_hybrid if monthly_savings_with_hybrid > 0 else float('inf')
    
    impact_analysis = {
        'direct_energy_cost_ngn': direct_energy_cost,
        'indirect_voll_cost_ngn': indirect_cost,
        'total_economic_impact_ngn': total_economic_impact,
        'generator_alternative_cost_ngn': generator_cost,
        'hybrid_system_monthly_cost_ngn': monthly_hybrid_cost,
        'cost_of_inaction_ngn': cost_of_inaction,
        'hybrid_system_payback_months': hybrid_payback_months,
        'hybrid_system_roi_percent': (monthly_savings_with_hybrid / monthly_hybrid_cost - 1) * 100 if monthly_hybrid_cost > 0 else 0,
        'annual_economic_impact_ngn': total_economic_impact * 12,
        'percentage_of_income': (total_economic_impact / 150000) * 100,  # Assuming ₦150k monthly income
        'cost_per_outage_hour_ngn': total_economic_impact / (ens_results['outage_minutes_per_month'] / 60),
        'comparative_metrics': {
            'grid_tariff_multiple': voll_results['voll_premium_over_grid'],
            'generator_cost_ratio': voll_results['voll_premium_over_generator'],
            'energy_availability_factor': ens_results['energy_availability_factor'],
            'system_reliability': ens_results['system_reliability_percent']
        }
    }
    
    return impact_analysis

# ============================================================================
# 6. PROFESSIONAL VISUALIZATION DASHBOARD
# ============================================================================

def create_outage_impact_dashboard(ens_results, voll_results, impact_analysis, scenario_name):
    """Create comprehensive visualization dashboard for outage impact analysis"""
    
    # Professional styling
    plt.style.use('seaborn-v0_8-whitegrid')
    mpl.rcParams['font.size'] = 10
    mpl.rcParams['axes.titlesize'] = 12
    mpl.rcParams['figure.figsize'] = [18, 12]
    
    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
    
    # 1. Weekly Energy Not Served Bar Chart (Primary Deliverable)
    ax1 = fig.add_subplot(gs[0, :2])
    
    # Simulate 4 weeks of data
    weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    weekly_ens = [ens_results['weekly_ens_kwh'] * np.random.uniform(0.8, 1.2) for _ in range(4)]
    
    bars1 = ax1.bar(weeks, weekly_ens, color=['#E74C3C', '#F39C12', '#F1C40F', '#2ECC71'])
    ax1.set_xlabel('Week', fontweight='bold')
    ax1.set_ylabel('Energy Not Served (kWh)', fontweight='bold')
    ax1.set_title('Weekly Energy Not Served Due to Grid Outages', fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, val) in enumerate(zip(bars1, weekly_ens)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # 2. Monthly Cost Impact (Primary Deliverable)
    ax2 = fig.add_subplot(gs[0, 2:])
    
    cost_labels = ['Direct\n(Energy Cost)', 'Indirect\n(VoLL)', 'Total\nImpact', 'Generator\nAlternative']
    cost_values = [
        impact_analysis['direct_energy_cost_ngn'] / 1000,  # Convert to thousands
        impact_analysis['indirect_voll_cost_ngn'] / 1000,
        impact_analysis['total_economic_impact_ngn'] / 1000,
        impact_analysis['generator_alternative_cost_ngn'] / 1000
    ]
    cost_colors = ['#3498DB', '#E74C3C', '#2C3E50', '#F39C12']
    
    bars2 = ax2.bar(cost_labels, cost_values, color=cost_colors)
    ax2.set_ylabel('Monthly Cost (₦ Thousands)', fontweight='bold')
    ax2.set_title('Monthly Economic Impact Breakdown', fontweight='bold', pad=15)
    ax2.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, val) in enumerate(zip(bars2, cost_values)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'₦{val:,.0f}K', ha='center', va='bottom', fontweight='bold')
    
    # 3. Outage Statistics Summary
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.axis('off')
    
    stats_text = f"""
OUTAGE STATISTICS
Scenario: {scenario_name}
Weekly Outages: {ens_results['weekly_outages']}
Avg Duration: {ens_results['avg_outage_duration_hours']:.1f} hours

MONTHLY TOTALS
Outage Events: {ens_results['monthly_outages']:.0f}
Energy Not Served: {ens_results['total_monthly_ens_kwh']:.1f} kWh
Outage Duration: {ens_results['outage_minutes_per_month']/60:.1f} hours

RELIABILITY METRICS
System Reliability: {ens_results['system_reliability_percent']:.1f}%
Energy Availability: {ens_results['energy_availability_factor']*100:.1f}%
SAIDI*: {ens_results['outage_minutes_per_month']/30:.1f} min/day
SAIFI*: {ens_results['monthly_outages']/30:.2f} outages/day

*SAIDI: System Average Interruption Duration Index
*SAIFI: System Average Interruption Frequency Index
"""
    
    ax3.text(0.05, 0.95, stats_text, fontfamily='monospace', fontsize=9,
             verticalalignment='top', linespacing=1.5,
             bbox=dict(boxstyle='round', facecolor='#F8F9F9', alpha=0.9))
    
    # 4. Value of Lost Load Analysis
    ax4 = fig.add_subplot(gs[1, 1])
    
    voll_labels = ['Off-Peak', 'Shoulder', 'Peak']
    voll_values = [
        voll_results['time_segment_costs']['off_peak'] / 1000,
        voll_results['time_segment_costs']['shoulder'] / 1000,
        voll_results['time_segment_costs']['peak'] / 1000
    ]
    voll_colors = ['#2ECC71', '#F1C40F', '#E74C3C']
    
    bars4 = ax4.bar(voll_labels, voll_values, color=voll_colors)
    ax4.set_ylabel('VoLL Cost (₦ Thousands)', fontweight='bold')
    ax4.set_title('Value of Lost Load by Time Segment', fontweight='bold', pad=15)
    ax4.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, val) in enumerate(zip(bars4, voll_values)):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'₦{val:,.0f}K', ha='center', va='bottom', fontweight='bold')
    
    # 5. Cost Comparison Matrix
    ax5 = fig.add_subplot(gs[1, 2:])
    
    comparison_labels = ['Current\n(With Outages)', 'Grid\n(Ideal)', 'Generator\nBackup', 'Hybrid System\n(Solar + Battery)']
    comparison_costs = [
        impact_analysis['total_economic_impact_ngn'] / 1000,
        0,  # Ideal grid has no outage cost
        impact_analysis['generator_alternative_cost_ngn'] / 1000,
        impact_analysis['hybrid_system_monthly_cost_ngn'] / 1000
    ]
    comparison_colors = ['#E74C3C', '#2ECC71', '#F39C12', '#3498DB']
    
    bars5 = ax5.bar(comparison_labels, comparison_costs, color=comparison_colors)
    ax5.set_ylabel('Monthly Cost (₦ Thousands)', fontweight='bold')
    ax5.set_title('Alternative Energy Supply Cost Comparison', fontweight='bold', pad=15)
    ax5.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, cost) in enumerate(zip(bars5, comparison_costs)):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'₦{cost:,.0f}K' if cost > 0 else '₦0',
                ha='center', va='bottom', fontweight='bold')
    
    # 6. Income Impact Analysis
    ax6 = fig.add_subplot(gs[2, 0])
    
    income_labels = ['Energy\nExpenditure', 'Outage\nImpact', 'Total\nEnergy Cost']
    monthly_income = 150000  # ₦ assumed monthly income
    energy_expenditure = ens_results['monthly_energy_requirement_kwh'] * 110
    total_energy_cost = energy_expenditure + impact_analysis['total_economic_impact_ngn']
    
    income_values = [
        energy_expenditure / monthly_income * 100,
        impact_analysis['total_economic_impact_ngn'] / monthly_income * 100,
        total_energy_cost / monthly_income * 100
    ]
    
    bars6 = ax6.bar(income_labels, income_values, color=['#3498DB', '#E74C3C', '#2C3E50'])
    ax6.set_ylabel('Percentage of Monthly Income (%)', fontweight='bold')
    ax6.set_title('Energy Costs as % of Household Income', fontweight='bold', pad=15)
    ax6.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, val) in enumerate(zip(bars6, income_values)):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 7. Outage Timing Distribution
    ax7 = fig.add_subplot(gs[2, 1])
    
    time_segments = ['Night\n(00-06)', 'Morning\nPeak\n(06-09)', 'Day\n(09-18)', 'Evening\nPeak\n(18-22)', 'Late\nEvening\n(22-24)']
    
    # Simulate outage distribution
    outage_distribution = [15, 10, 20, 45, 10]  # Percentages
    
    wedges, texts, autotexts = ax7.pie(outage_distribution, labels=time_segments, autopct='%1.0f%%',
                                       colors=['#2C3E50', '#E74C3C', '#F39C12', '#C0392B', '#7F8C8D'])
    ax7.set_title('Outage Timing Distribution', fontweight='bold', pad=15)
    
    # 8. Economic Impact Summary
    ax8 = fig.add_subplot(gs[2, 2:])
    ax8.axis('off')
    
    summary_text = f"""
ECONOMIC IMPACT SUMMARY
Total Monthly Impact: ₦{impact_analysis['total_economic_impact_ngn']:,.0f}
Annual Impact: ₦{impact_analysis['annual_economic_impact_ngn']:,.0f}

COST BREAKDOWN
Direct Energy Cost: ₦{impact_analysis['direct_energy_cost_ngn']:,.0f}
Indirect VoLL Cost: ₦{impact_analysis['indirect_voll_cost_ngn']:,.0f}
Total per Capita: ₦{voll_results['monthly_voll_per_capita']:,.0f}/person

VALUE OF LOST LOAD
Average VoLL: ₦{voll_results['avg_voll_per_kwh']:.0f}/kWh
Grid Tariff Multiple: {voll_results['voll_premium_over_grid']:.1f}x
Generator Cost Ratio: {voll_results['voll_premium_over_generator']:.1f}x

ALTERNATIVE SCENARIOS
Generator Backup: ₦{impact_analysis['generator_alternative_cost_ngn']:,.0f}/month
Hybrid System: ₦{impact_analysis['hybrid_system_monthly_cost_ngn']:,.0f}/month
Payback Period: {impact_analysis['hybrid_system_payback_months']:.1f} months

RECOMMENDATIONS
1. Implement backup solutions for outages >4 hours
2. Prioritize peak hour reliability improvements
3. Consider hybrid systems for >₦{impact_analysis['total_economic_impact_ngn']:,.0f}/month impact
"""
    
    ax8.text(0.02, 0.98, summary_text, fontfamily='monospace', fontsize=9,
             verticalalignment='top', linespacing=1.5,
             bbox=dict(boxstyle='round', facecolor='#FEF9E7', alpha=0.9))
    
    fig.suptitle(f'Grid Outage Economic Impact Analysis: {scenario_name}\nEnergy System Management Portfolio - Day 5', 
                fontsize=16, fontweight='bold', y=1.02)
    
    plt.savefig(f'grid_outage_impact_{scenario_name.lower().replace(" ", "_")}.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    # Additional: Monthly Impact Timeline
    fig2, ax = plt.subplots(figsize=(14, 6))
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Simulate monthly variation (rainy season impact)
    monthly_impact = []
    for i, month in enumerate(months):
        base_impact = impact_analysis['total_economic_impact_ngn']
        if i in [5, 6, 7, 8]:  # Rainy season months
            monthly_impact.append(base_impact * 1.3)
        elif i == 11:  # December festive season
            monthly_impact.append(base_impact * 1.5)
        else:
            monthly_impact.append(base_impact * np.random.uniform(0.9, 1.1))
    
    bars = ax.bar(months, monthly_impact, color=['#3498DB' if i not in [5,6,7,8,11] else '#E74C3C' for i in range(12)])
    ax.axhline(y=impact_analysis['total_economic_impact_ngn'], color='#2C3E50', 
               linestyle='--', label='Annual Average')
    
    ax.set_xlabel('Month', fontweight='bold')
    ax.set_ylabel('Economic Impact (₦)', fontweight='bold')
    ax.set_title('Monthly Economic Impact Variation (Seasonal Effects)', fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend()
    
    # Add value labels for key months
    for i, (bar, val) in enumerate(zip(bars, monthly_impact)):
        if i in [0, 5, 11]:  # Jan, Jun, Dec
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2000,
                   f'₦{val/1000:,.0f}K', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('monthly_impact_timeline.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    return fig, fig2

# ============================================================================
# 7. DATA EXPORT FUNCTIONS
# ============================================================================

def export_analysis_results(ens_results, voll_results, impact_analysis, scenario_name):
    """Export comprehensive analysis results"""
    
    # Create detailed outage log
    outage_log = []
    for i, outage in enumerate(ens_results['detailed_outages']):
        outage_log.append({
            'Outage_ID': i+1,
            'Start_Hour': outage['start_hour'],
            'Duration_hours': outage['duration_hours'],
            'Energy_Not_Served_kWh': outage['energy_not_served_kwh'],
            'Time_Segment': 'Peak' if 18 <= outage['start_hour'] < 22 else 
                           'Shoulder' if (7 <= outage['start_hour'] < 9) or (22 <= outage['start_hour'] < 24) else 
                           'Off-Peak',
            'Estimated_Cost_NGN': outage['energy_not_served_kwh'] * voll_results['avg_voll_per_kwh']
        })
    
    df_outages = pd.DataFrame(outage_log)
    df_outages.to_csv(f'outage_log_{scenario_name.lower().replace(" ", "_")}.csv', index=False)
    
    # Create summary report
    summary_data = {
        'Metric': [
            'Scenario Description',
            'Weekly Outage Frequency',
            'Average Outage Duration (hours)',
            'Monthly Energy Not Served (kWh)',
            'System Reliability (%)',
            'Energy Availability Factor',
            'Average VoLL (₦/kWh)',
            'Total Monthly Economic Impact (₦)',
            'Direct Energy Cost (₦)',
            'Indirect VoLL Cost (₦)',
            'Generator Alternative Cost (₦)',
            'Hybrid System Monthly Cost (₦)',
            'Annual Economic Impact (₦)',
            'Impact as % of Income',
            'Recommended Action Threshold'
        ],
        'Value': [
            ens_results['scenario_description'],
            f"{ens_results['weekly_outages']}",
            f"{ens_results['avg_outage_duration_hours']:.1f}",
            f"{ens_results['total_monthly_ens_kwh']:.1f}",
            f"{ens_results['system_reliability_percent']:.1f}%",
            f"{ens_results['energy_availability_factor']:.3f}",
            f"₦{voll_results['avg_voll_per_kwh']:.0f}",
            f"₦{impact_analysis['total_economic_impact_ngn']:,.0f}",
            f"₦{impact_analysis['direct_energy_cost_ngn']:,.0f}",
            f"₦{impact_analysis['indirect_voll_cost_ngn']:,.0f}",
            f"₦{impact_analysis['generator_alternative_cost_ngn']:,.0f}",
            f"₦{impact_analysis['hybrid_system_monthly_cost_ngn']:,.0f}",
            f"₦{impact_analysis['annual_economic_impact_ngn']:,.0f}",
            f"{impact_analysis['percentage_of_income']:.1f}%",
            f"₦{impact_analysis['total_economic_impact_ngn']:,.0f}/month"
        ]
    }
    
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_csv(f'outage_impact_summary_{scenario_name.lower().replace(" ", "_")}.csv', index=False)
    
    return df_outages, df_summary

# ============================================================================
# 8. MAIN EXECUTION FUNCTION
# ============================================================================

def main():
    """Execute grid outage economic impact analysis"""
    
    print("=" * 80)
    print("DAY 5: GRID OUTAGE ECONOMIC IMPACT ANALYSIS")
    print("Energy System Management Portfolio Project")
    print("=" * 80)
    
    print("\nANALYSIS OBJECTIVE:")
    print("Quantify the economic impact of frequent grid blackouts on Nigerian households")
    print("using Value of Lost Load (VoLL) methodology and reliability cost calculations.")
    
    # Step 1: Define outage scenarios
    print("\n1. DEFINING OUTAGE SCENARIOS...")
    scenarios, voll_parameters = define_outage_scenarios()
    selected_scenario = scenarios["urban_moderate"]
    print(f"   • Selected Scenario: {selected_scenario['description']}")
    print(f"   • Weekly Outages: {selected_scenario['weekly_outages']}")
    print(f"   • Average Duration: {selected_scenario['avg_duration_hours']} hours")
    
    # Step 2: Load standardized load profile
    print("\n2. LOADING STANDARDIZED HOUSEHOLD PROFILE...")
    df_load, daily_energy = get_standardized_load_profile()
    print(f"   • Daily Energy Requirement: {daily_energy:.1f} kWh")
    print(f"   • Monthly Energy Requirement: {daily_energy * 30:.1f} kWh")
    
    # Step 3: Calculate Energy Not Served
    print("\n3. CALCULATING ENERGY NOT SERVED...")
    ens_results = calculate_energy_not_served(selected_scenario, df_load)
    print(f"   • Monthly ENS: {ens_results['total_monthly_ens_kwh']:.1f} kWh")
    print(f"   • System Reliability: {ens_results['system_reliability_percent']:.1f}%")
    print(f"   • Energy Availability: {ens_results['energy_availability_factor']*100:.1f}%")
    
    # Step 4: Calculate Value of Lost Load
    print("\n4. CALCULATING VALUE OF LOST LOAD...")
    voll_results = calculate_value_of_lost_load(ens_results, voll_parameters, "middle_income")
    print(f"   • Average VoLL: ₦{voll_results['avg_voll_per_kwh']:.0f}/kWh")
    print(f"   • Total Monthly VoLL: ₦{voll_results['total_monthly_voll_ngn']:,.0f}")
    print(f"   • Grid Tariff Multiple: {voll_results['voll_premium_over_grid']:.1f}x")
    
    # Step 5: Analyze comprehensive economic impact
    print("\n5. ANALYZING COMPREHENSIVE ECONOMIC IMPACT...")
    impact_analysis = analyze_economic_impact(ens_results, voll_results)
    print(f"   • Total Monthly Impact: ₦{impact_analysis['total_economic_impact_ngn']:,.0f}")
    print(f"   • Annual Impact: ₦{impact_analysis['annual_economic_impact_ngn']:,.0f}")
    print(f"   • % of Income: {impact_analysis['percentage_of_income']:.1f}%")
    
    # Step 6: Create visualizations
    print("\n6. CREATING PROFESSIONAL VISUALIZATIONS...")
    create_outage_impact_dashboard(ens_results, voll_results, impact_analysis, "Urban Moderate")
    
    # Step 7: Export data
    print("\n7. EXPORTING ANALYSIS DATA...")
    export_analysis_results(ens_results, voll_results, impact_analysis, "Urban Moderate")
    
    # Step 8: Print comprehensive findings
    print("\n" + "=" * 80)
    print("GRID OUTAGE IMPACT ANALYSIS - KEY FINDINGS")
    print("=" * 80)
    
    findings = f"""
CRITICAL INSIGHTS:

1. RELIABILITY METRICS:
   • System Reliability: {ens_results['system_reliability_percent']:.1f}%
   • Energy Availability: {ens_results['energy_availability_factor']*100:.1f}%
   • Monthly Outage Duration: {ens_results['outage_minutes_per_month']/60:.1f} hours
   • SAIDI: {ens_results['outage_minutes_per_month']/30:.1f} minutes/day
   • SAIFI: {ens_results['monthly_outages']/30:.2f} outages/day

2. ENERGY NOT SERVED:
   • Monthly ENS: {ens_results['total_monthly_ens_kwh']:.1f} kWh
   • Weekly Average: {ens_results['weekly_ens_kwh']:.1f} kWh
   • Percentage of Total: {(ens_results['total_monthly_ens_kwh']/(daily_energy*30))*100:.1f}%

3. ECONOMIC IMPACT BREAKDOWN:
   • Direct Energy Cost: ₦{impact_analysis['direct_energy_cost_ngn']:,.0f}
   • Indirect VoLL Cost: ₦{impact_analysis['indirect_voll_cost_ngn']:,.0f}
   • Total Monthly Impact: ₦{impact_analysis['total_economic_impact_ngn']:,.0f}
   • Annual Impact: ₦{impact_analysis['annual_economic_impact_ngn']:,.0f}

4. VALUE OF LOST LOAD ANALYSIS:
   • Average VoLL: ₦{voll_results['avg_voll_per_kwh']:.0f}/kWh
   • Grid Tariff Multiple: {voll_results['voll_premium_over_grid']:.1f}x higher
   • Generator Cost Ratio: {voll_results['voll_premium_over_generator']:.1f}x
   • Peak Hour VoLL: ₦{voll_results['voll_base_rate']*voll_parameters['time_of_day_factors']['peak']:.0f}/kWh

5. ALTERNATIVE SCENARIO COMPARISON:
   • Generator Backup: ₦{impact_analysis['generator_alternative_cost_ngn']:,.0f}/month
   • Hybrid System (Solar+Battery): ₦{impact_analysis['hybrid_system_monthly_cost_ngn']:,.0f}/month
   • Cost of Inaction: ₦{impact_analysis['cost_of_inaction_ngn']:,.0f}/month
   • Hybrid System Payback: {impact_analysis['hybrid_system_payback_months']:.1f} months

6. HOUSEHOLD BUDGET IMPACT:
   • Total Energy Cost: ₦{((daily_energy*30)*110 + impact_analysis['total_economic_impact_ngn']):,.0f}/month
   • Percentage of Income: {impact_analysis['percentage_of_income']:.1f}%
   • Per Capita Impact: ₦{voll_results['monthly_voll_per_capita']:,.0f}/person/month

7. TIME-OF-DAY ANALYSIS:
   • Peak Hour Impact: {voll_results['time_segment_costs']['peak']/voll_results['total_monthly_voll_ngn']*100:.1f}%
   • Shoulder Hour Impact: {voll_results['time_segment_costs']['shoulder']/voll_results['total_monthly_voll_ngn']*100:.1f}%
   • Off-Peak Impact: {voll_results['time_segment_costs']['off_peak']/voll_results['total_monthly_voll_ngn']*100:.1f}%

8. INTEGRATION WITH PREVIOUS ANALYSES:
   • Generator Savings: ₦{impact_analysis['generator_alternative_cost_ngn'] - impact_analysis['hybrid_system_monthly_cost_ngn']:,.0f}/month vs hybrid
   • Solar PV Contribution: Could eliminate {(ens_results['total_monthly_ens_kwh']/(daily_energy*30))*100:.1f}% of outage impact
   • Battery Storage: Critical for {ens_results['avg_outage_duration_hours']:.1f} hour outages

BUSINESS IMPLICATIONS:

1. GRID IMPROVEMENT ROI:
   • Every 1% reliability improvement saves: ₦{impact_analysis['total_economic_impact_ngn']*(0.01/ens_results['system_reliability_percent']*100):,.0f}/month
   • Peak hour reliability most valuable: ₦{voll_results['voll_base_rate']*voll_parameters['time_of_day_factors']['peak']:.0f}/kWh

2. BACKUP SYSTEM JUSTIFICATION:
   • Generator break-even: {impact_analysis['generator_alternative_cost_ngn']/impact_analysis['total_economic_impact_ngn']:.1f} months
   • Hybrid system break-even: {impact_analysis['hybrid_system_payback_months']:.1f} months
   • NPV positive if outages continue > {impact_analysis['hybrid_system_payback_months']/12:.1f} years

3. POLICY RECOMMENDATIONS:
   • Minimum reliability standard: >95% for urban areas
   • Peak hour protection priority
   • Backup system subsidies for >₦{impact_analysis['total_economic_impact_ngn']:,.0f}/month impact
   • Time-of-use tariffs to reflect true outage costs

4. INVESTMENT DECISION FRAMEWORK:
   • Invest in backup if: Monthly impact > ₦{impact_analysis['hybrid_system_monthly_cost_ngn']:,.0f}
   • Invest in grid if: Improvement cost < ₦{impact_analysis['annual_economic_impact_ngn']:,.0f}/year
   • Hybrid optimal if: Outages > {ens_results['weekly_outages']} times/week
"""
    
    print(findings)
    
    print("\n" + "=" * 80)
    print("PROJECT DELIVERABLES:")
    print("=" * 80)
    print(f"✓ grid_outage_impact_urban_moderate.png - Main analysis dashboard")
    print(f"✓ monthly_impact_timeline.png - Seasonal variation analysis")
    print(f"✓ outage_log_urban_moderate.csv - Detailed outage-by-outage data")
    print(f"✓ outage_impact_summary_urban_moderate.csv - Comprehensive metrics")
    
    print("\n" + "=" * 80)
    print("PORTFOLIO VALUE STATEMENT:")
    print("=" * 80)
    print("'Analyzed reliability impacts of grid instability on households using")
    print("Value of Lost Load methodology to quantify true economic costs of blackouts.'")
    print("\nDemonstrates ability to:")
    print("• Apply reliability engineering concepts (SAIDI, SAIFI)")
    print("• Quantify indirect economic impacts")
    print("• Perform cost-benefit analysis of infrastructure improvements")
    print("• Integrate with previous energy system models")
    
    print("\n" + "=" * 80)
    print("PROJECT COMPLETE")
    print("=" * 80)

# ============================================================================
# EXECUTE ANALYSIS
# ============================================================================

if __name__ == "__main__":
    main()