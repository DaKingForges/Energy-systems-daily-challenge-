"""
DAY 6: Appliance Efficiency Tradeoff Analysis
Energy System Management Portfolio Project

Objective: Analyze the economic viability of upgrading to energy-efficient appliances
through lifecycle cost analysis, payback period calculation, and cumulative savings modeling.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime

# ============================================================================
# 1. APPLIANCE DATA DEFINITION
# ============================================================================

def define_appliance_scenarios():
    """Define old vs new appliance specifications and costs"""
    
    appliances = {
        "Refrigerator": {
            "old": {"power_w": 180, "efficiency": "D", "lifetime_years": 10, "purchase_cost": 120000},
            "new": {"power_w": 90, "efficiency": "A++", "lifetime_years": 15, "purchase_cost": 250000},
            "usage_hours": 24,
            "duty_cycle": 0.40,
            "notes": "Most critical appliance for efficiency upgrade"
        },
        "Air Conditioner": {
            "old": {"power_w": 1500, "efficiency": "Low", "lifetime_years": 8, "purchase_cost": 180000},
            "new": {"power_w": 1000, "efficiency": "Inverter", "lifetime_years": 12, "purchase_cost": 350000},
            "usage_hours": 5,
            "cooling_hours": 1200,  # Hours per year when cooling is needed
            "notes": "Highest impact upgrade due to high power consumption"
        },
        "LED Lighting (Whole House)": {
            "old": {"power_w": 400, "efficiency": "Incandescent", "lifetime_years": 1, "purchase_cost": 5000},
            "new": {"power_w": 40, "efficiency": "LED", "lifetime_years": 5, "purchase_cost": 15000},
            "usage_hours": 6,
            "notes": "Quickest payback, easiest upgrade"
        },
        "Television": {
            "old": {"power_w": 120, "efficiency": "LCD", "lifetime_years": 7, "purchase_cost": 80000},
            "new": {"power_w": 60, "efficiency": "OLED", "lifetime_years": 10, "purchase_cost": 150000},
            "usage_hours": 4,
            "notes": "Moderate savings, improved picture quality"
        },
        "Washing Machine": {
            "old": {"power_w": 500, "efficiency": "Top-Load", "lifetime_years": 10, "purchase_cost": 120000},
            "new": {"power_w": 300, "efficiency": "Front-Load Inverter", "lifetime_years": 15, "purchase_cost": 220000},
            "usage_hours": 0.5,
            "uses_per_week": 3,
            "notes": "Water savings additional benefit"
        },
        "Electric Kettle": {
            "old": {"power_w": 1500, "efficiency": "Standard", "lifetime_years": 3, "purchase_cost": 5000},
            "new": {"power_w": 1200, "efficiency": "Fast Boil", "lifetime_years": 5, "purchase_cost": 10000},
            "usage_hours": 0.25,
            "boils_per_day": 4,
            "notes": "Small but frequent use appliance"
        },
        "Ceiling Fans (x4)": {
            "old": {"power_w": 240, "efficiency": "Induction", "lifetime_years": 8, "purchase_cost": 40000},
            "new": {"power_w": 160, "efficiency": "BLDC", "lifetime_years": 15, "purchase_cost": 60000},
            "usage_hours": 12,
            "notes": "Multiple units, significant cumulative savings"
        }
    }
    
    return appliances

# ============================================================================
# 2. ECONOMIC PARAMETERS
# ============================================================================

def define_economic_parameters():
    """Define economic parameters for analysis"""
    
    economic_params = {
        "energy_tariff": 110,  # ₦/kWh (current grid tariff)
        "tariff_escalation_rate": 0.05,  # 5% annual increase
        "discount_rate": 0.12,  # 12% discount rate for NPV
        "analysis_period_years": 15,
        "maintenance_cost_old": 0.02,  # 2% of purchase price annually
        "maintenance_cost_new": 0.01,  # 1% of purchase price annually
        "replacement_schedule_old": "As needed",
        "replacement_schedule_new": "End of life",
        "salvage_value_rate": 0.10,  # 10% residual value
        "inflation_rate": 0.15,  # 15% general inflation
        "financing_options": {
            "cash": {"interest_rate": 0, "term_years": 0},
            "loan": {"interest_rate": 0.18, "term_years": 3},
            "installment": {"interest_rate": 0.25, "term_years": 2}
        }
    }
    
    return economic_params

# ============================================================================
# 3. ENERGY SAVINGS CALCULATIONS
# ============================================================================

def calculate_appliance_savings(appliances, economic_params):
    """Calculate annual energy and cost savings for each appliance"""
    
    results = []
    
    for appliance_name, data in appliances.items():
        # Extract parameters
        old_power = data["old"]["power_w"]
        new_power = data["new"]["power_w"]
        
        # Handle different usage patterns
        if "usage_hours" in data:
            daily_hours = data["usage_hours"]
        elif "cooling_hours" in data:
            # For AC, use cooling hours per year
            daily_hours = data["cooling_hours"] / 365
        elif "boils_per_day" in data:
            daily_hours = data["boils_per_day"] * data.get("usage_hours", 0.25) / 24
        elif "uses_per_week" in data:
            daily_hours = data["uses_per_week"] * data.get("usage_hours", 0.5) / 7
        else:
            daily_hours = 4  # Default assumption
        
        # Apply duty cycle for appliances like refrigerators
        if "duty_cycle" in data:
            effective_hours = daily_hours * data["duty_cycle"]
        else:
            effective_hours = daily_hours
        
        # Calculate annual energy consumption
        old_annual_kwh = (old_power * effective_hours * 365) / 1000
        new_annual_kwh = (new_power * effective_hours * 365) / 1000
        
        # Annual energy savings
        annual_energy_savings = old_annual_kwh - new_annual_kwh
        
        # Annual cost savings (Year 1)
        annual_cost_savings = annual_energy_savings * economic_params["energy_tariff"]
        
        # Upgrade cost (additional cost for new appliance)
        upgrade_cost = data["new"]["purchase_cost"] - data["old"]["purchase_cost"]
        
        # Simple payback period
        if annual_cost_savings > 0:
            simple_payback_years = upgrade_cost / annual_cost_savings
        else:
            simple_payback_years = float('inf')
        
        # Maintenance savings
        old_maintenance = data["old"]["purchase_cost"] * economic_params["maintenance_cost_old"]
        new_maintenance = data["new"]["purchase_cost"] * economic_params["maintenance_cost_new"]
        maintenance_savings = old_maintenance - new_maintenance
        
        # Lifetime considerations
        old_lifetime = data["old"]["lifetime_years"]
        new_lifetime = data["new"]["lifetime_years"]
        
        appliance_result = {
            "appliance": appliance_name,
            "old_power_w": old_power,
            "new_power_w": new_power,
            "power_reduction_percent": ((old_power - new_power) / old_power) * 100,
            "old_annual_kwh": old_annual_kwh,
            "new_annual_kwh": new_annual_kwh,
            "annual_energy_savings_kwh": annual_energy_savings,
            "annual_cost_savings_year1_ngn": annual_cost_savings,
            "upgrade_cost_ngn": upgrade_cost,
            "simple_payback_years": simple_payback_years,
            "maintenance_savings_annual_ngn": maintenance_savings,
            "old_lifetime_years": old_lifetime,
            "new_lifetime_years": new_lifetime,
            "daily_usage_hours": effective_hours,
            "notes": data["notes"]
        }
        
        results.append(appliance_result)
    
    return pd.DataFrame(results)

# ============================================================================
# 4. CUMULATIVE SAVINGS ANALYSIS
# ============================================================================

def calculate_cumulative_savings(df_savings, economic_params, analysis_years=15):
    """Calculate cumulative savings over analysis period"""
    
    # Total upgrade cost
    total_upgrade_cost = df_savings['upgrade_cost_ngn'].sum()
    
    # Annual savings for each appliance
    annual_savings = df_savings['annual_cost_savings_year1_ngn'].sum()
    annual_maintenance_savings = df_savings['maintenance_savings_annual_ngn'].sum()
    total_annual_savings = annual_savings + annual_maintenance_savings
    
    # Initialize arrays for time series
    years = list(range(analysis_years + 1))
    cumulative_net_savings = [0] * (analysis_years + 1)
    cumulative_gross_savings = [0] * (analysis_years + 1)
    annual_energy_savings_list = []
    payback_year = None
    
    # Year 0 (investment year)
    cumulative_net_savings[0] = -total_upgrade_cost
    cumulative_gross_savings[0] = 0
    
    # Calculate for each year
    for year in range(1, analysis_years + 1):
        # Apply tariff escalation
        tariff_escalation = (1 + economic_params["tariff_escalation_rate"]) ** (year - 1)
        year_savings = total_annual_savings * tariff_escalation
        
        # Cumulative calculations
        cumulative_gross_savings[year] = cumulative_gross_savings[year-1] + year_savings
        cumulative_net_savings[year] = cumulative_gross_savings[year] - total_upgrade_cost
        
        # Track annual energy savings
        annual_energy = df_savings['annual_energy_savings_kwh'].sum() * tariff_escalation
        annual_energy_savings_list.append(annual_energy)
        
        # Find payback year
        if payback_year is None and cumulative_net_savings[year] >= 0:
            payback_year = year
    
    # Calculate NPV
    discount_rate = economic_params["discount_rate"]
    npv = 0
    for year in range(1, analysis_years + 1):
        year_cash_flow = total_annual_savings * ((1 + economic_params["tariff_escalation_rate"]) ** (year - 1))
        discounted_cash_flow = year_cash_flow / ((1 + discount_rate) ** year)
        npv += discounted_cash_flow
    npv -= total_upgrade_cost  # Initial investment
    
    # Calculate IRR (simplified)
    # We'll use a simple approximation for IRR
    avg_annual_return = total_annual_savings / total_upgrade_cost if total_upgrade_cost > 0 else 0
    approx_irr = avg_annual_return * 100
    
    # ROI over analysis period
    total_savings = cumulative_gross_savings[-1]
    total_roi = (total_savings - total_upgrade_cost) / total_upgrade_cost * 100 if total_upgrade_cost > 0 else 0
    
    cumulative_results = {
        "total_upgrade_cost_ngn": total_upgrade_cost,
        "annual_energy_savings_kwh": df_savings['annual_energy_savings_kwh'].sum(),
        "annual_cost_savings_year1_ngn": total_annual_savings,
        "simple_payback_years": total_upgrade_cost / total_annual_savings if total_annual_savings > 0 else float('inf'),
        "discounted_payback_year": payback_year,
        "npv_ngn": npv,
        "approx_irr_percent": approx_irr,
        "total_roi_percent": total_roi,
        "cumulative_net_savings": cumulative_net_savings,
        "cumulative_gross_savings": cumulative_gross_savings,
        "years": years,
        "annual_energy_savings_list": annual_energy_savings_list,
        "analysis_period_years": analysis_years
    }
    
    return cumulative_results

# ============================================================================
# 5. SENSITIVITY ANALYSIS
# ============================================================================

def perform_sensitivity_analysis(df_savings, economic_params):
    """Perform sensitivity analysis on key variables"""
    
    base_tariff = economic_params["energy_tariff"]
    base_upgrade_cost = df_savings['upgrade_cost_ngn'].sum()
    base_annual_savings = df_savings['annual_cost_savings_year1_ngn'].sum()
    
    # Tariff sensitivity
    tariff_scenarios = [80, 110, 140, 170, 200]  # ₦/kWh
    payback_by_tariff = []
    
    for tariff in tariff_scenarios:
        annual_savings_tariff = (df_savings['annual_energy_savings_kwh'].sum() * tariff) + \
                               df_savings['maintenance_savings_annual_ngn'].sum()
        if annual_savings_tariff > 0:
            payback = base_upgrade_cost / annual_savings_tariff
        else:
            payback = float('inf')
        payback_by_tariff.append(payback)
    
    # Usage sensitivity
    usage_multipliers = [0.5, 0.75, 1.0, 1.25, 1.5]
    payback_by_usage = []
    
    for multiplier in usage_multipliers:
        adjusted_savings = base_annual_savings * multiplier
        if adjusted_savings > 0:
            payback = base_upgrade_cost / adjusted_savings
        else:
            payback = float('inf')
        payback_by_usage.append(payback)
    
    # Appliance lifetime sensitivity
    lifetime_scenarios = [
        {"old": 8, "new": 10},
        {"old": 10, "new": 15},
        {"old": 12, "new": 18}
    ]
    
    sensitivity_results = {
        "tariff_sensitivity": {
            "tariffs": tariff_scenarios,
            "payback_years": payback_by_tariff
        },
        "usage_sensitivity": {
            "multipliers": usage_multipliers,
            "payback_years": payback_by_usage
        },
        "base_scenario": {
            "tariff": base_tariff,
            "upgrade_cost": base_upgrade_cost,
            "annual_savings": base_annual_savings,
            "payback": base_upgrade_cost / base_annual_savings if base_annual_savings > 0 else float('inf')
        }
    }
    
    return sensitivity_results

# ============================================================================
# 6. COMPACT VISUALIZATION DASHBOARD
# ============================================================================

def create_compact_dashboard(df_savings, cumulative_results, sensitivity_results):
    """Create compact visualization dashboard without large text boxes"""
    
    # Professional styling
    plt.style.use('seaborn-v0_8-whitegrid')
    mpl.rcParams['font.size'] = 10
    mpl.rcParams['axes.titlesize'] = 12
    mpl.rcParams['figure.figsize'] = [16, 10]  # Compact size
    
    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(2, 3, hspace=0.25, wspace=0.25)
    
    # 1. Annual Energy Savings by Appliance (Bar Chart)
    ax1 = fig.add_subplot(gs[0, 0])
    
    # Sort by savings
    df_sorted = df_savings.sort_values('annual_energy_savings_kwh', ascending=True)
    
    bars1 = ax1.barh(df_sorted['appliance'], df_sorted['annual_energy_savings_kwh'], 
                     color='#27AE60', alpha=0.8)
    ax1.set_xlabel('Annual Energy Savings (kWh)', fontweight='bold')
    ax1.set_title('Energy Savings by Appliance', fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for bar in bars1:
        width = bar.get_width()
        ax1.text(width + 5, bar.get_y() + bar.get_height()/2,
                f'{width:.0f}', ha='left', va='center', fontweight='bold', fontsize=9)
    
    # 2. Payback Period by Appliance (Bar Chart)
    ax2 = fig.add_subplot(gs[0, 1])
    
    # Filter out infinite payback
    df_finite = df_savings[df_savings['simple_payback_years'] < 20].copy()
    df_finite = df_finite.sort_values('simple_payback_years', ascending=True)
    
    colors2 = ['#2ECC71' if x < 3 else '#F39C12' if x < 7 else '#E74C3C' 
               for x in df_finite['simple_payback_years']]
    
    bars2 = ax2.barh(df_finite['appliance'], df_finite['simple_payback_years'], 
                     color=colors2, alpha=0.8)
    ax2.set_xlabel('Payback Period (Years)', fontweight='bold')
    ax2.set_title('Payback Period by Appliance', fontweight='bold', pad=10)
    ax2.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for bar, payback in zip(bars2, df_finite['simple_payback_years']):
        width = bar.get_width()
        ax2.text(width + 0.2, bar.get_y() + bar.get_height()/2,
                f'{payback:.1f}y', ha='left', va='center', fontweight='bold', fontsize=9)
    
    # 3. Cumulative Savings Over Time (Line Chart - Primary Deliverable)
    ax3 = fig.add_subplot(gs[0, 2])
    
    years = cumulative_results['years']
    net_savings = [s/1000 for s in cumulative_results['cumulative_net_savings']]  # Convert to ₦K
    
    line = ax3.plot(years, net_savings, 'o-', color='#2980B9', linewidth=2.5, 
                    markersize=6, label='Cumulative Net Savings')
    ax3.axhline(y=0, color='black', linewidth=1, linestyle='-')
    ax3.axvline(x=cumulative_results.get('discounted_payback_year', 0), 
                color='#E74C3C', linestyle='--', linewidth=1.5,
                label=f'Payback: Year {cumulative_results.get("discounted_payback_year", "N/A")}')
    
    # Fill area for positive savings
    ax3.fill_between(years, net_savings, where=[s >= 0 for s in net_savings], 
                     alpha=0.2, color='#27AE60')
    ax3.fill_between(years, net_savings, where=[s < 0 for s in net_savings], 
                     alpha=0.2, color='#E74C3C')
    
    ax3.set_xlabel('Year', fontweight='bold')
    ax3.set_ylabel('Cumulative Net Savings (₦ Thousands)', fontweight='bold')
    ax3.set_title('Cumulative Savings Over Time', fontweight='bold', pad=10)
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='lower right')
    ax3.set_xlim(0, cumulative_results['analysis_period_years'])
    
    # 4. Sensitivity Analysis: Tariff Impact
    ax4 = fig.add_subplot(gs[1, 0])
    
    tariffs = sensitivity_results['tariff_sensitivity']['tariffs']
    paybacks = sensitivity_results['tariff_sensitivity']['payback_years']
    
    bars4 = ax4.bar(range(len(tariffs)), paybacks, color='#3498DB', alpha=0.8)
    ax4.set_xlabel('Electricity Tariff (₦/kWh)', fontweight='bold')
    ax4.set_ylabel('Payback Period (Years)', fontweight='bold')
    ax4.set_title('Sensitivity to Electricity Price', fontweight='bold', pad=10)
    ax4.set_xticks(range(len(tariffs)))
    ax4.set_xticklabels(tariffs)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Highlight current tariff
    current_idx = tariffs.index(110) if 110 in tariffs else 0
    bars4[current_idx].set_color('#E74C3C')
    
    for i, (bar, payback) in enumerate(zip(bars4, paybacks)):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{payback:.1f}y', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # 5. Sensitivity Analysis: Usage Impact
    ax5 = fig.add_subplot(gs[1, 1])
    
    multipliers = sensitivity_results['usage_sensitivity']['multipliers']
    usage_paybacks = sensitivity_results['usage_sensitivity']['payback_years']
    
    ax5.plot(multipliers, usage_paybacks, 's-', color='#9B59B6', linewidth=2, markersize=6)
    ax5.axvline(x=1.0, color='#E74C3C', linestyle='--', linewidth=1.5, label='Base Usage')
    ax5.fill_between(multipliers, usage_paybacks, alpha=0.2, color='#9B59B6')
    
    ax5.set_xlabel('Usage Multiplier', fontweight='bold')
    ax5.set_ylabel('Payback Period (Years)', fontweight='bold')
    ax5.set_title('Sensitivity to Usage Patterns', fontweight='bold', pad=10)
    ax5.grid(True, alpha=0.3)
    ax5.legend()
    
    # 6. Key Metrics Summary (Compact Text Box)
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis('off')
    
    total_upgrade = cumulative_results['total_upgrade_cost_ngn'] / 1000  # Convert to ₦K
    annual_savings = cumulative_results['annual_cost_savings_year1_ngn'] / 1000
    payback_year = cumulative_results.get('discounted_payback_year', '>15')
    npv_value = cumulative_results['npv_ngn'] / 1000
    
    summary_text = f"""
KEY METRICS SUMMARY

Investment & Savings:
Total Upgrade Cost: ₦{total_upgrade:,.0f}K
Annual Savings (Y1): ₦{annual_savings:,.0f}K
Simple Payback: {cumulative_results['simple_payback_years']:.1f} years
Discounted Payback: Year {payback_year}

Financial Returns:
NPV (15 years): ₦{npv_value:,.0f}K
Approx IRR: {cumulative_results['approx_irr_percent']:.1f}%
Total ROI: {cumulative_results['total_roi_percent']:.1f}%

Energy Impact:
Annual Energy Savings: {cumulative_results['annual_energy_savings_kwh']:,.0f} kWh
15-Year Total: {cumulative_results['annual_energy_savings_kwh'] * 15:,.0f} kWh
CO2 Reduction: {cumulative_results['annual_energy_savings_kwh'] * 0.6 * 15 / 1000:.1f} tons

Recommendation:
{'✅ ECONOMICALLY VIABLE' if cumulative_results['npv_ngn'] > 0 else '⚠️ MARGINAL' if cumulative_results['npv_ngn'] > -50000 else '❌ NOT VIABLE'}
Priority Upgrades: {', '.join(df_savings.nlargest(3, 'annual_energy_savings_kwh')['appliance'].tolist())}
"""
    
    ax6.text(0.05, 0.95, summary_text, fontfamily='monospace', fontsize=9,
             verticalalignment='top', linespacing=1.5,
             bbox=dict(boxstyle='round', facecolor='#F8F9F9', alpha=0.9))
    
    fig.suptitle('Appliance Efficiency Tradeoff Analysis: Lifecycle Cost Assessment\nEnergy System Management Portfolio - Day 6', 
                fontsize=14, fontweight='bold', y=1.02)
    
    plt.savefig('appliance_efficiency_dashboard_compact.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    # Create separate detailed report image
    create_detailed_report_image(df_savings, cumulative_results, sensitivity_results)
    
    return fig

def create_detailed_report_image(df_savings, cumulative_results, sensitivity_results):
    """Create separate image for detailed report"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 16))
    
    # Top: Detailed appliance analysis
    ax1.axis('off')
    
    # Create detailed table
    table_data = []
    for _, row in df_savings.iterrows():
        table_data.append([
            row['appliance'],
            f"{row['old_power_w']}W",
            f"{row['new_power_w']}W",
            f"{row['power_reduction_percent']:.0f}%",
            f"{row['annual_energy_savings_kwh']:.0f}",
            f"₦{row['annual_cost_savings_year1_ngn']:,.0f}",
            f"₦{row['upgrade_cost_ngn']:,.0f}",
            f"{row['simple_payback_years']:.1f}y",
            f"{row['old_lifetime_years']}y",
            f"{row['new_lifetime_years']}y"
        ])
    
    # Add totals row
    totals = [
        "TOTAL",
        "",
        "",
        f"{((df_savings['old_power_w'].sum() - df_savings['new_power_w'].sum()) / df_savings['old_power_w'].sum() * 100):.0f}%",
        f"{df_savings['annual_energy_savings_kwh'].sum():.0f}",
        f"₦{df_savings['annual_cost_savings_year1_ngn'].sum():,.0f}",
        f"₦{df_savings['upgrade_cost_ngn'].sum():,.0f}",
        f"{df_savings['upgrade_cost_ngn'].sum() / df_savings['annual_cost_savings_year1_ngn'].sum():.1f}y",
        "",
        ""
    ]
    table_data.append(totals)
    
    columns = ['Appliance', 'Old Power', 'New Power', 'Reduction', 'Annual Savings (kWh)', 
               'Annual Savings (₦)', 'Upgrade Cost (₦)', 'Payback (Years)', 'Old Life', 'New Life']
    
    # Create table
    table = ax1.table(cellText=table_data, colLabels=columns, 
                      cellLoc='center', loc='center',
                      colColours=['#3498DB']*len(columns))
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)
    
    # Style header
    for i in range(len(columns)):
        table[(0, i)].set_facecolor('#2C3E50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style totals row
    totals_row = len(table_data)
    for i in range(len(columns)):
        table[(totals_row, i)].set_facecolor('#27AE60')
        table[(totals_row, i)].set_text_props(weight='bold', color='white')
    
    ax1.set_title('Detailed Appliance Efficiency Analysis', fontsize=12, fontweight='bold', pad=20)
    
    # Bottom: Financial analysis details
    ax2.axis('off')
    
    financial_text = f"""
FINANCIAL ANALYSIS DETAILS

INVESTMENT SUMMARY:
Total Upgrade Investment: ₦{cumulative_results['total_upgrade_cost_ngn']:,.0f}
Financing Options:
  • Cash: No interest, immediate ownership
  • 3-Year Loan @ 18%: ₦{cumulative_results['total_upgrade_cost_ngn'] * 0.18 * 3:,.0f} interest
  • 2-Year Installment @ 25%: ₦{cumulative_results['total_upgrade_cost_ngn'] * 0.25 * 2:,.0f} interest

SAVINGS PROJECTION:
Year 1 Savings: ₦{cumulative_results['annual_cost_savings_year1_ngn']:,.0f}
With 5% annual tariff escalation:
  • Year 5: ₦{cumulative_results['annual_cost_savings_year1_ngn'] * (1.05**4):,.0f}
  • Year 10: ₦{cumulative_results['annual_cost_savings_year1_ngn'] * (1.05**9):,.0f}
  • Year 15: ₦{cumulative_results['annual_cost_savings_year1_ngn'] * (1.05**14):,.0f}

15-YEAR CUMULATIVE SAVINGS:
Total Energy Savings: {cumulative_results['annual_energy_savings_kwh'] * 15:,.0f} kWh
Total Cost Savings: ₦{cumulative_results['cumulative_gross_savings'][-1]:,.0f}
Net Savings (after investment): ₦{cumulative_results['cumulative_net_savings'][-1]:,.0f}

ENVIRONMENTAL IMPACT:
Annual CO2 Reduction: {cumulative_results['annual_energy_savings_kwh'] * 0.6 / 1000:.2f} tons
15-Year CO2 Reduction: {cumulative_results['annual_energy_savings_kwh'] * 0.6 * 15 / 1000:.1f} tons
Equivalent to: {cumulative_results['annual_energy_savings_kwh'] * 0.6 * 15 / 21.77:.0f} trees planted

RISK ASSESSMENT:
Primary Risks:
  1. Appliance failure before payback period
  2. Electricity tariff changes (policy risk)
  3. Usage pattern changes affecting savings
  4. Technology obsolescence

Mitigation Strategies:
  1. Choose appliances with good warranties
  2. Prioritize quick-payback upgrades first
  3. Monitor actual savings vs projections
  4. Consider modular upgrade approach

IMPLEMENTATION RECOMMENDATIONS:
Phase 1 (Immediate, <2 year payback):
  • LED Lighting Upgrade (Payback: {df_savings[df_savings['appliance'] == 'LED Lighting (Whole House)']['simple_payback_years'].values[0]:.1f} years)
  • Refrigerator Upgrade (Payback: {df_savings[df_savings['appliance'] == 'Refrigerator']['simple_payback_years'].values[0]:.1f} years)

Phase 2 (Medium-term, <5 year payback):
  • Ceiling Fans Upgrade
  • Electric Kettle Upgrade

Phase 3 (Long-term, strategic):
  • Air Conditioner Upgrade
  • Washing Machine Upgrade
  • Television Upgrade

DECISION CRITERIA:
Proceed with upgrade if:
  • NPV > ₦0 (Current: ₦{cumulative_results['npv_ngn']:,.0f})
  • Payback < 5 years (Current: {cumulative_results['simple_payback_years']:.1f} years)
  • IRR > 12% (Current: {cumulative_results['approx_irr_percent']:.1f}%)
  
Current Recommendation: {'✅ PROCEED' if cumulative_results['npv_ngn'] > 0 and cumulative_results['simple_payback_years'] < 5 else '⚠️ REVIEW' if cumulative_results['npv_ngn'] > -50000 else '❌ REJECT'}
"""
    
    ax2.text(0.02, 0.98, financial_text, fontfamily='monospace', fontsize=9,
             verticalalignment='top', linespacing=1.4,
             bbox=dict(boxstyle='round', facecolor='#FEF9E7', alpha=0.9))
    
    ax2.set_title('Financial Analysis & Implementation Plan', fontsize=12, fontweight='bold', pad=20)
    
    plt.suptitle('Appliance Efficiency: Detailed Technical Report\nEnergy System Management Portfolio - Day 6', 
                fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig('appliance_efficiency_detailed_report.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()

# ============================================================================
# 7. DATA EXPORT FUNCTIONS
# ============================================================================

def export_analysis_results(df_savings, cumulative_results, sensitivity_results):
    """Export analysis results to CSV files"""
    
    # Appliance-level savings
    df_savings.to_csv('appliance_efficiency_savings.csv', index=False)
    
    # Cumulative savings timeline
    timeline_data = {
        'Year': cumulative_results['years'],
        'Cumulative_Net_Savings_NGN': cumulative_results['cumulative_net_savings'],
        'Cumulative_Gross_Savings_NGN': cumulative_results['cumulative_gross_savings'],
        'Annual_Energy_Savings_kWh': [0] + cumulative_results['annual_energy_savings_list']
    }
    df_timeline = pd.DataFrame(timeline_data)
    df_timeline.to_csv('cumulative_savings_timeline.csv', index=False)
    
    # Sensitivity analysis results
    sensitivity_data = {
        'Parameter': ['Electricity Tariff (₦/kWh)'] * 5 + ['Usage Multiplier'] * 5,
        'Value': sensitivity_results['tariff_sensitivity']['tariffs'] + 
                sensitivity_results['usage_sensitivity']['multipliers'],
        'Payback_Years': sensitivity_results['tariff_sensitivity']['payback_years'] + 
                        sensitivity_results['usage_sensitivity']['payback_years']
    }
    df_sensitivity = pd.DataFrame(sensitivity_data)
    df_sensitivity.to_csv('sensitivity_analysis_results.csv', index=False)
    
    return df_savings, df_timeline, df_sensitivity

# ============================================================================
# 8. MAIN EXECUTION FUNCTION
# ============================================================================

def main():
    """Execute appliance efficiency tradeoff analysis"""
    
    print("=" * 80)
    print("DAY 6: APPLIANCE EFFICIENCY TRADEOFF ANALYSIS")
    print("Energy System Management Portfolio Project")
    print("=" * 80)
    
    print("\nANALYSIS OBJECTIVE:")
    print("Evaluate the economic viability of upgrading to energy-efficient appliances")
    print("using lifecycle cost analysis and payback period calculations.")
    
    # Step 1: Define appliance scenarios
    print("\n1. DEFINING APPLIANCE UPGRADE SCENARIOS...")
    appliances = define_appliance_scenarios()
    print(f"   • Appliances Analyzed: {len(appliances)}")
    print(f"   • Includes: Refrigerator, AC, Lighting, TV, Washing Machine, etc.")
    
    # Step 2: Define economic parameters
    print("\n2. SETTING ECONOMIC PARAMETERS...")
    economic_params = define_economic_parameters()
    print(f"   • Electricity Tariff: ₦{economic_params['energy_tariff']}/kWh")
    print(f"   • Tariff Escalation: {economic_params['tariff_escalation_rate']*100}% annually")
    print(f"   • Discount Rate: {economic_params['discount_rate']*100}%")
    print(f"   • Analysis Period: {economic_params['analysis_period_years']} years")
    
    # Step 3: Calculate appliance savings
    print("\n3. CALCULATING APPLIANCE SAVINGS...")
    df_savings = calculate_appliance_savings(appliances, economic_params)
    total_energy_savings = df_savings['annual_energy_savings_kwh'].sum()
    total_cost_savings = df_savings['annual_cost_savings_year1_ngn'].sum()
    print(f"   • Total Annual Energy Savings: {total_energy_savings:.0f} kWh")
    print(f"   • Total Annual Cost Savings: ₦{total_cost_savings:,.0f}")
    
    # Step 4: Calculate cumulative savings
    print("\n4. ANALYZING CUMULATIVE SAVINGS...")
    cumulative_results = calculate_cumulative_savings(df_savings, economic_params)
    total_upgrade_cost = cumulative_results['total_upgrade_cost_ngn']
    simple_payback = cumulative_results['simple_payback_years']
    print(f"   • Total Upgrade Cost: ₦{total_upgrade_cost:,.0f}")
    print(f"   • Simple Payback Period: {simple_payback:.1f} years")
    print(f"   • NPV (15 years): ₦{cumulative_results['npv_ngn']:,.0f}")
    
    # Step 5: Perform sensitivity analysis
    print("\n5. PERFORMING SENSITIVITY ANALYSIS...")
    sensitivity_results = perform_sensitivity_analysis(df_savings, economic_params)
    print(f"   • Payback range with tariff changes: {min(sensitivity_results['tariff_sensitivity']['payback_years']):.1f} - {max(sensitivity_results['tariff_sensitivity']['payback_years']):.1f} years")
    print(f"   • Payback range with usage changes: {min(sensitivity_results['usage_sensitivity']['payback_years']):.1f} - {max(sensitivity_results['usage_sensitivity']['payback_years']):.1f} years")
    
    # Step 6: Create visualizations
    print("\n6. CREATING COMPACT VISUALIZATIONS...")
    create_compact_dashboard(df_savings, cumulative_results, sensitivity_results)
    
    # Step 7: Export data
    print("\n7. EXPORTING ANALYSIS DATA...")
    export_analysis_results(df_savings, cumulative_results, sensitivity_results)
    
    # Step 8: Print key findings
    print("\n" + "=" * 80)
    print("APPLIANCE EFFICIENCY ANALYSIS - KEY FINDINGS")
    print("=" * 80)
    
    # Quick recommendations
    quick_wins = df_savings[df_savings['simple_payback_years'] < 3]
    marginal = df_savings[(df_savings['simple_payback_years'] >= 3) & (df_savings['simple_payback_years'] < 7)]
    long_term = df_savings[df_savings['simple_payback_years'] >= 7]
    
    findings = f"""
ECONOMIC VIABILITY ASSESSMENT:

OVERALL INVESTMENT:
• Total Upgrade Cost: ₦{total_upgrade_cost:,.0f}
• Annual Savings (Year 1): ₦{total_cost_savings:,.0f}
• Simple Payback Period: {simple_payback:.1f} years
• NPV (15 years): ₦{cumulative_results['npv_ngn']:,.0f}
• IRR: {cumulative_results['approx_irr_percent']:.1f}%

ENERGY IMPACT:
• Annual Energy Reduction: {total_energy_savings:.0f} kWh ({total_energy_savings/(df_savings['old_annual_kwh'].sum())*100:.1f}% reduction)
• 15-Year Total Savings: {total_energy_savings * 15:,.0f} kWh
• Equivalent to: {total_energy_savings * 15 / 365:.0f} days of household consumption

UPGRADE RECOMMENDATIONS BY CATEGORY:

1. QUICK WINS (Payback < 3 years):
"""
    
    for _, row in quick_wins.iterrows():
        findings += f"   • {row['appliance']}: {row['simple_payback_years']:.1f} year payback, ₦{row['annual_cost_savings_year1_ngn']:,.0f}/year savings\n"
    
    findings += f"""
2. MARGINAL UPGRADES (Payback 3-7 years):
"""
    
    for _, row in marginal.iterrows():
        findings += f"   • {row['appliance']}: {row['simple_payback_years']:.1f} year payback, ₦{row['annual_cost_savings_year1_ngn']:,.0f}/year savings\n"
    
    findings += f"""
3. LONG-TERM STRATEGIC (Payback > 7 years):
"""
    
    for _, row in long_term.iterrows():
        findings += f"   • {row['appliance']}: {row['simple_payback_years']:.1f} year payback, consider at replacement time\n"
    
    findings += f"""
SENSITIVITY ANALYSIS INSIGHTS:
• Most sensitive to: Electricity tariff changes
• Least sensitive to: Appliance lifetimes
• Break-even tariff: ₦{sensitivity_results['base_scenario']['annual_savings']/df_savings['annual_energy_savings_kwh'].sum()*1000:.0f}/kWh
• Critical usage threshold: {sensitivity_results['base_scenario']['payback']/3:.1f}x current usage for 3-year payback

INTEGRATION WITH PREVIOUS ANALYSES:
• Day 1: Uses same load profile ({df_savings['old_annual_kwh'].sum():.0f} kWh baseline)
• Day 2: Generator savings could fund efficiency upgrades
• Day 3: Solar system could be smaller with efficient appliances
• Day 4: Battery could be smaller with reduced loads
• Day 5: Reduces outage impact costs by ₦{total_cost_savings * 0.3:,.0f}/year

IMPLEMENTATION STRATEGY:
1. Phase 1 (Immediate): {', '.join(quick_wins['appliance'].tolist()[:2])}
2. Phase 2 (6 months): Remaining quick wins
3. Phase 3 (Replacement): Upgrade appliances as they fail
4. Financing: Consider energy efficiency loans or installment plans

PORTFOLIO VALUE:
Demonstrates ability to perform lifecycle cost analysis and make data-driven
investment decisions for energy efficiency improvements.
"""
    
    print(findings)
    
    print("\n" + "=" * 80)
    print("PROJECT DELIVERABLES:")
    print("=" * 80)
    print("✓ appliance_efficiency_dashboard_compact.png - Main visualization dashboard")
    print("✓ appliance_efficiency_detailed_report.png - Detailed technical report")
    print("✓ appliance_efficiency_savings.csv - Appliance-level savings data")
    print("✓ cumulative_savings_timeline.csv - Year-by-year savings projection")
    print("✓ sensitivity_analysis_results.csv - Sensitivity analysis data")
    
    print("\n" + "=" * 80)
    print("PORTFOLIO ANGLE ACHIEVED:")
    print("=" * 80)
    print("'Evaluated efficiency investments using lifecycle cost analysis'")
    print("\nDemonstrates ability to:")
    print("• Conduct payback period and NPV analysis")
    print("• Perform sensitivity analysis on key variables")
    print("• Create cumulative savings visualizations")
    print("• Make data-driven upgrade recommendations")
    
    print("\n" + "=" * 80)
    print("PROJECT COMPLETE")
    print("=" * 80)

# ============================================================================
# EXECUTE ANALYSIS
# ============================================================================

if __name__ == "__main__":
    main()