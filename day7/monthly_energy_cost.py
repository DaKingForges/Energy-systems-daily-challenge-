"""
DAY 7: Monthly Energy Cost Breakdown Analysis
Energy System Management Portfolio Project

Objective: Perform comprehensive household energy cost audit by combining
grid, generator, solar, and battery costs to understand where money actually goes.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

# ============================================================================
# 1. ENERGY SOURCE COST PARAMETERS (FROM PREVIOUS DAYS)
# ============================================================================

def define_energy_sources():
    """Define all energy sources with costs from previous portfolio days"""
    
    energy_sources = {
        "grid": {
            "source": "National Grid",
            "tariff_per_kwh": 110,
            "monthly_energy_kwh": 0,  # Will be calculated
            "reliability": 0.85,
            "fixed_charges_monthly": 0,
            "notes": "Primary source when available, frequent outages"
        },
        "generator": {
            "source": "Petrol Generator (11kVA)",
            "fuel_cost_per_liter": 900,
            "fuel_efficiency_l_per_kwh": 0.35,
            "cost_per_kwh": 485,  # From Day 2 analysis (with capital & maintenance)
            "monthly_energy_kwh": 0,
            "maintenance_monthly": 5000,
            "notes": "Backup during grid outages, high operating cost"
        },
        "solar_pv": {
            "source": "Solar PV System (4.95 kW)",
            "system_cost": 5940000,  # From Day 3
            "amortized_cost_monthly": 59350,  # Amortized over 10 years @ 15%
            "generation_monthly_kwh": 0,
            "avoided_cost_per_kwh": 110,  # Grid tariff avoided
            "notes": "Renewable source, amortized capital cost"
        },
        "battery_storage": {
            "source": "LiFePO4 Battery (2.64 kWh)",
            "system_cost": 1690000,  # From Day 4
            "amortized_cost_monthly": 16885,  # Amortized over 10 years @ 15%
            "efficiency": 0.92,
            "cycles_per_month": 30,
            "notes": "Energy shifting and backup, amortized capital cost"
        }
    }
    
    return energy_sources

# ============================================================================
# 2. LOAD PROFILE & USAGE SCENARIOS
# ============================================================================

def define_usage_scenarios():
    """Define different energy usage scenarios for analysis"""
    
    scenarios = {
        "current_reality": {
            "description": "Current setup: Grid + Generator",
            "energy_mix": {
                "grid_percent": 69,
                "generator_percent": 31,
                "solar_percent": 0,
                "battery_percent": 0
            },
            "monthly_energy_kwh": 996,  # 33.2 kWh/day × 30 days
            "outage_hours_monthly": 54,  # 4 outages/week × 4.5 hours × 4.33 weeks
            "notes": "Baseline: From Day 1 & 2 analysis"
        },
        "solar_optimistic": {
            "description": "With Solar PV (60% offset)",
            "energy_mix": {
                "grid_percent": 28,
                "generator_percent": 12,
                "solar_percent": 60,
                "battery_percent": 0
            },
            "monthly_energy_kwh": 996,
            "outage_hours_monthly": 54,
            "notes": "Day 3 solar scenario, reduces grid/gen usage"
        },
        "hybrid_optimal": {
            "description": "Hybrid: Grid + Solar + Battery + Minimal Generator",
            "energy_mix": {
                "grid_percent": 35,
                "generator_percent": 5,
                "solar_percent": 50,
                "battery_percent": 10  # Stored solar energy used later
            },
            "monthly_energy_kwh": 996,
            "outage_hours_monthly": 20,  # Reduced by battery backup
            "notes": "Optimal integration from Days 3-6"
        },
        "off_grid_aspirational": {
            "description": "Maximum renewable penetration",
            "energy_mix": {
                "grid_percent": 10,
                "generator_percent": 5,
                "solar_percent": 70,
                "battery_percent": 15
            },
            "monthly_energy_kwh": 850,  # Reduced by efficiency upgrades
            "outage_hours_monthly": 5,
            "notes": "Future scenario with efficiency and storage"
        }
    }
    
    return scenarios

# ============================================================================
# 3. COST BREAKDOWN CALCULATIONS
# ============================================================================

def calculate_cost_breakdown(scenario, energy_sources):
    """Calculate detailed monthly cost breakdown for selected scenario"""
    
    # Get scenario data
    monthly_energy = scenario["monthly_energy_kwh"]
    energy_mix = scenario["energy_mix"]
    
    # Calculate energy from each source
    grid_energy = monthly_energy * (energy_mix["grid_percent"] / 100)
    generator_energy = monthly_energy * (energy_mix["generator_percent"] / 100)
    solar_energy = monthly_energy * (energy_mix["solar_percent"] / 100)
    battery_energy = monthly_energy * (energy_mix["battery_percent"] / 100)
    
    # Calculate costs for each source
    # Grid cost
    grid_cost = grid_energy * energy_sources["grid"]["tariff_per_kwh"]
    grid_cost += energy_sources["grid"]["fixed_charges_monthly"]
    
    # Generator cost (energy + fixed maintenance)
    generator_energy_cost = generator_energy * energy_sources["generator"]["cost_per_kwh"]
    generator_maintenance = energy_sources["generator"]["maintenance_monthly"]
    generator_cost = generator_energy_cost + generator_maintenance
    
    # Solar cost (amortized capital cost)
    solar_cost = energy_sources["solar_pv"]["amortized_cost_monthly"]
    solar_savings = solar_energy * energy_sources["solar_pv"]["avoided_cost_per_kwh"]
    solar_net_cost = max(0, solar_cost - solar_savings)  # Can't be negative
    
    # Battery cost (amortized capital cost)
    battery_cost = energy_sources["battery_storage"]["amortized_cost_monthly"]
    # Battery provides value by shifting solar energy and reducing outages
    
    # Efficiency upgrades amortized cost (from Day 6)
    efficiency_upgrade_monthly = 715000 * (0.15/12) / (1 - (1 + 0.15/12)**(-10*12))
    efficiency_savings_monthly = 93500  # From Day 6 analysis
    efficiency_net_cost = max(0, efficiency_upgrade_monthly - efficiency_savings_monthly)
    
    # Calculate total costs
    total_energy_cost = grid_cost + generator_energy_cost
    total_capital_cost = solar_cost + battery_cost + efficiency_upgrade_monthly
    total_savings = solar_savings + efficiency_savings_monthly
    total_net_cost = grid_cost + generator_cost + solar_net_cost + battery_cost + efficiency_net_cost
    
    # Cost per kWh calculations
    cost_per_kwh_total = total_net_cost / monthly_energy if monthly_energy > 0 else 0
    cost_per_kwh_energy_only = total_energy_cost / monthly_energy if monthly_energy > 0 else 0
    
    # Breakdown percentages
    cost_components = {
        "grid": grid_cost,
        "generator": generator_cost,
        "solar_net": solar_net_cost,
        "battery": battery_cost,
        "efficiency_net": efficiency_net_cost
    }
    
    total = sum(cost_components.values())
    percentages = {k: (v/total*100) if total > 0 else 0 for k, v in cost_components.items()}
    
    # Monthly cash flow analysis (what's actually paid each month)
    cash_outflows = {
        "grid_bill": grid_cost,
        "generator_fuel": generator_energy_cost,
        "generator_maintenance": generator_maintenance,
        "solar_loan": solar_cost if solar_cost > 0 else 0,
        "battery_loan": battery_cost if battery_cost > 0 else 0,
        "efficiency_loan": efficiency_upgrade_monthly if efficiency_upgrade_monthly > 0 else 0
    }
    
    total_cash_outflow = sum(cash_outflows.values())
    
    breakdown = {
        "scenario_name": scenario["description"],
        "monthly_energy_kwh": monthly_energy,
        "energy_by_source": {
            "grid_kwh": grid_energy,
            "generator_kwh": generator_energy,
            "solar_kwh": solar_energy,
            "battery_kwh": battery_energy
        },
        "costs_by_source": {
            "grid_ngn": grid_cost,
            "generator_ngn": generator_cost,
            "solar_ngn": solar_net_cost,
            "battery_ngn": battery_cost,
            "efficiency_ngn": efficiency_net_cost
        },
        "total_costs": {
            "total_net_cost_ngn": total_net_cost,
            "total_energy_cost_ngn": total_energy_cost,
            "total_capital_cost_ngn": total_capital_cost,
            "total_savings_ngn": total_savings
        },
        "unit_costs": {
            "cost_per_kwh_total": cost_per_kwh_total,
            "cost_per_kwh_energy_only": cost_per_kwh_energy_only,
            "grid_tariff": energy_sources["grid"]["tariff_per_kwh"],
            "generator_cost_per_kwh": energy_sources["generator"]["cost_per_kwh"]
        },
        "percentages": percentages,
        "cash_flow": {
            "monthly_outflow_ngn": total_cash_outflow,
            "components": cash_outflows,
            "net_energy_cost": grid_cost + generator_energy_cost
        },
        "efficiency_metrics": {
            "energy_mix_percent": energy_mix,
            "outage_hours_monthly": scenario["outage_hours_monthly"],
            "reliability_percent": (730 - scenario["outage_hours_monthly"]) / 730 * 100
        }
    }
    
    return breakdown

# ============================================================================
# 4. COMPACT VISUALIZATION DASHBOARD
# ============================================================================

def create_cost_breakdown_dashboard(breakdown, scenario_name, energy_sources):
    """Create compact visualization dashboard for cost breakdown"""
    
    # Professional styling
    plt.style.use('seaborn-v0_8-whitegrid')
    mpl.rcParams['font.size'] = 10
    mpl.rcParams['axes.titlesize'] = 12
    mpl.rcParams['figure.figsize'] = [15, 9]  # Adjusted size for 2x2 layout
    
    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(2, 2, hspace=0.25, wspace=0.25)
    
    # 1. Energy Mix by Source (Stacked Bar Chart)
    ax1 = fig.add_subplot(gs[0, 0])
    
    energy_labels = ['Grid', 'Generator', 'Solar', 'Battery\n(Stored Solar)']
    energy_values = [
        breakdown['energy_by_source']['grid_kwh'],
        breakdown['energy_by_source']['generator_kwh'],
        breakdown['energy_by_source']['solar_kwh'],
        breakdown['energy_by_source']['battery_kwh']
    ]
    energy_colors = ['#3498DB', '#E74C3C', '#F39C12', '#2ECC71']
    
    bars1 = ax1.bar(energy_labels, energy_values, color=energy_colors, alpha=0.8)
    ax1.set_ylabel('Monthly Energy (kWh)', fontweight='bold')
    ax1.set_title('Energy Source Mix', fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add percentage labels
    total_energy = sum(energy_values)
    for i, (bar, val) in enumerate(zip(bars1, energy_values)):
        height = bar.get_height()
        percentage = (val / total_energy) * 100
        ax1.text(bar.get_x() + bar.get_width()/2., height + 10,
                f'{percentage:.0f}%', ha='center', va='bottom', fontweight='bold')
        ax1.text(bar.get_x() + bar.get_width()/2., height/2,
                f'{val:.0f}', ha='center', va='center', fontweight='bold', color='white')
    
    # 2. Cost Breakdown by Source (Pie Chart - Primary Deliverable)
    ax2 = fig.add_subplot(gs[0, 1])
    
    cost_labels = ['Grid', 'Generator', 'Solar\n(Net)', 'Battery', 'Efficiency\n(Net)']
    cost_values = [
        breakdown['costs_by_source']['grid_ngn'],
        breakdown['costs_by_source']['generator_ngn'],
        breakdown['costs_by_source']['solar_ngn'],
        breakdown['costs_by_source']['battery_ngn'],
        breakdown['costs_by_source']['efficiency_ngn']
    ]
    cost_colors = ['#3498DB', '#E74C3C', '#F39C12', '#2ECC71', '#9B59B6']
    
    # Filter out zero values
    pie_labels = []
    pie_values = []
    pie_colors = []
    for label, value, color in zip(cost_labels, cost_values, cost_colors):
        if value > 0:
            pie_labels.append(label)
            pie_values.append(value)
            pie_colors.append(color)
    
    wedges, texts, autotexts = ax2.pie(pie_values, labels=pie_labels, colors=pie_colors, 
                                       autopct='%1.0f%%', startangle=90,
                                       textprops={'fontweight': 'bold'})
    ax2.set_title('Monthly Cost Breakdown', fontweight='bold', pad=10)
    
    # 3. Cost per kWh Comparison (Bar Chart)
    ax3 = fig.add_subplot(gs[1, 0])
    
    cost_labels = ['Grid Tariff', 'Generator', 'Scenario\nTotal', 'Energy Only']
    cost_per_kwh = [
        breakdown['unit_costs']['grid_tariff'],
        breakdown['unit_costs']['generator_cost_per_kwh'],
        breakdown['unit_costs']['cost_per_kwh_total'],
        breakdown['unit_costs']['cost_per_kwh_energy_only']
    ]
    colors = ['#3498DB', '#E74C3C', '#2C3E50', '#7F8C8D']
    
    bars3 = ax3.bar(cost_labels, cost_per_kwh, color=colors)
    ax3.set_ylabel('Cost per kWh (₦)', fontweight='bold')
    ax3.set_title('Cost Efficiency Comparison', fontweight='bold', pad=10)
    ax3.grid(True, alpha=0.3, axis='y')
    
    for bar, cost in zip(bars3, cost_per_kwh):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'₦{cost:.0f}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Monthly Cash Flow Breakdown
    ax4 = fig.add_subplot(gs[1, 1])
    
    cash_labels = list(breakdown['cash_flow']['components'].keys())
    cash_values = [v/1000 for v in breakdown['cash_flow']['components'].values()]  # Convert to ₦K
    
    # Clean up labels for display
    display_labels = []
    for label in cash_labels:
        if label == 'grid_bill': display_labels.append('Grid Bill')
        elif label == 'generator_fuel': display_labels.append('Generator\nFuel')
        elif label == 'generator_maintenance': display_labels.append('Generator\nMaint.')
        elif label == 'solar_loan': display_labels.append('Solar\nLoan')
        elif label == 'battery_loan': display_labels.append('Battery\nLoan')
        elif label == 'efficiency_loan': display_labels.append('Efficiency\nLoan')
    
    bars4 = ax4.bar(display_labels, cash_values, 
                    color=['#3498DB', '#E74C3C', '#E67E22', '#F39C12', '#2ECC71', '#9B59B6'])
    ax4.set_ylabel('Monthly Payment (₦ Thousands)', fontweight='bold')
    ax4.set_title('Monthly Cash Outflow Breakdown', fontweight='bold', pad=10)
    ax4.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, val) in enumerate(zip(bars4, cash_values)):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'₦{val:.0f}K', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # Clean scenario name for filename
    clean_scenario_name = scenario_name.replace(":", "").replace("+", "and").replace(" ", "_").lower()
    
    fig.suptitle(f'Monthly Energy Cost Breakdown Analysis: {scenario_name}\nEnergy System Management Portfolio - Day 7', 
                fontsize=14, fontweight='bold', y=1.02)
    
    # Save the chart dashboard
    chart_filename = f'energy_cost_charts_{clean_scenario_name}.png'
    plt.savefig(chart_filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Chart dashboard saved as: {chart_filename}")
    plt.show()
    
    # Now create the text dashboard separately
    create_text_dashboard(breakdown, scenario_name, clean_scenario_name)
    
    return fig

def create_text_dashboard(breakdown, scenario_name, clean_scenario_name):
    """Create a separate text-only dashboard"""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('off')
    
    summary_text = f"""
SCENARIO SUMMARY: {scenario_name}

MONTHLY TOTALS:
• Energy Consumption: {breakdown['monthly_energy_kwh']:,.0f} kWh
• Total Net Cost: ₦{breakdown['total_costs']['total_net_cost_ngn']:,.0f}
• Cash Outflow: ₦{breakdown['cash_flow']['monthly_outflow_ngn']:,.0f}
• Cost per kWh: ₦{breakdown['unit_costs']['cost_per_kwh_total']:.0f}
• Annual Energy Budget: ₦{breakdown['total_costs']['total_net_cost_ngn'] * 12:,.0f}

ENERGY MIX:
• Grid: {breakdown['energy_by_source']['grid_kwh']:.0f} kWh ({breakdown['efficiency_metrics']['energy_mix_percent']['grid_percent']}%)
• Generator: {breakdown['energy_by_source']['generator_kwh']:.0f} kWh ({breakdown['efficiency_metrics']['energy_mix_percent']['generator_percent']}%)
• Solar: {breakdown['energy_by_source']['solar_kwh']:.0f} kWh ({breakdown['efficiency_metrics']['energy_mix_percent']['solar_percent']}%)
• Battery: {breakdown['energy_by_source']['battery_kwh']:.0f} kWh ({breakdown['efficiency_metrics']['energy_mix_percent']['battery_percent']}%)

COST BREAKDOWN:
• Grid: ₦{breakdown['costs_by_source']['grid_ngn']:,.0f} ({breakdown['percentages'].get('grid', 0):.1f}%)
• Generator: ₦{breakdown['costs_by_source']['generator_ngn']:,.0f} ({breakdown['percentages'].get('generator', 0):.1f}%)
• Solar (Net): ₦{breakdown['costs_by_source']['solar_ngn']:,.0f} ({breakdown['percentages'].get('solar_net', 0):.1f}%)
• Battery: ₦{breakdown['costs_by_source']['battery_ngn']:,.0f} ({breakdown['percentages'].get('battery', 0):.1f}%)
• Efficiency: ₦{breakdown['costs_by_source']['efficiency_ngn']:,.0f} ({breakdown['percentages'].get('efficiency_net', 0):.1f}%)

RELIABILITY METRICS:
• Outage Hours: {breakdown['efficiency_metrics']['outage_hours_monthly']:.0f} hrs/month
• Reliability: {breakdown['efficiency_metrics']['reliability_percent']:.1f}%
• Outage Cost per Hour: ~₦{(breakdown['total_costs']['total_net_cost_ngn'] / 730 * (breakdown['efficiency_metrics']['outage_hours_monthly'] / 30)):.0f}

COST EFFICIENCY:
• Grid Tariff: ₦{breakdown['unit_costs']['grid_tariff']}/kWh
• Generator Cost: ₦{breakdown['unit_costs']['generator_cost_per_kwh']}/kWh
• Scenario Average: ₦{breakdown['unit_costs']['cost_per_kwh_total']:.0f}/kWh
• Energy Only Cost: ₦{breakdown['unit_costs']['cost_per_kwh_energy_only']:.0f}/kWh (excluding capital)

CASH FLOW DETAILS:
• Grid Bill: ₦{breakdown['cash_flow']['components']['grid_bill']:,.0f}
• Generator Fuel: ₦{breakdown['cash_flow']['components']['generator_fuel']:,.0f}
• Generator Maintenance: ₦{breakdown['cash_flow']['components']['generator_maintenance']:,.0f}
• Solar Loan: ₦{breakdown['cash_flow']['components']['solar_loan']:,.0f}
• Battery Loan: ₦{breakdown['cash_flow']['components']['battery_loan']:,.0f}
• Efficiency Loan: ₦{breakdown['cash_flow']['components']['efficiency_loan']:,.0f}

KEY INSIGHTS:
• Largest Cost Component: {max(breakdown['percentages'], key=breakdown['percentages'].get).upper()} at {breakdown['percentages'][max(breakdown['percentages'], key=breakdown['percentages'].get)]:.1f}%
• Generator vs Grid: Generator costs are {breakdown['costs_by_source']['generator_ngn']/breakdown['costs_by_source']['grid_ngn']:.1f}x grid costs
• Renewable Share: {breakdown['percentages'].get('solar_net', 0) + breakdown['percentages'].get('battery', 0):.1f}% of total costs
• Monthly Savings: ₦{breakdown['total_costs']['total_savings_ngn']:,.0f} from solar and efficiency

BUDGETING RECOMMENDATIONS:
• Fixed Monthly Allocation: ₦{breakdown['cash_flow']['monthly_outflow_ngn'] * 1.1:,.0f} (with 10% buffer)
• Variable Cost Buffer: ₦{breakdown['total_costs']['total_energy_cost_ngn'] * 0.15:,.0f} for tariff increases
• Maintenance Reserve: ₦{breakdown['cash_flow']['components']['generator_maintenance'] * 3:,.0f} quarterly
• Emergency Fund: ₦{breakdown['total_costs']['total_net_cost_ngn'] * 2:,.0f} for unexpected outages

OPTIMIZATION OPPORTUNITIES:
• Reduce Generator Use: Each kWh saved from generator saves ₦{breakdown['unit_costs']['generator_cost_per_kwh'] - breakdown['unit_costs']['grid_tariff']} vs grid
• Increase Solar Self-Consumption: Each additional solar kWh self-consumed saves ₦{breakdown['unit_costs']['grid_tariff']}
• Load Shifting: Move loads to solar hours to maximize self-consumption
"""
    
    ax.text(0.02, 0.98, summary_text, fontfamily='monospace', fontsize=9,
            verticalalignment='top', linespacing=1.5,
            bbox=dict(boxstyle='round', facecolor='#F8F9F9', alpha=0.9))
    
    fig.suptitle(f'Energy Cost Analysis - Text Dashboard: {scenario_name}\nEnergy System Management Portfolio - Day 7', 
                fontsize=14, fontweight='bold', y=0.95)
    
    # Save the text dashboard
    text_filename = f'energy_cost_text_dashboard_{clean_scenario_name}.png'
    plt.savefig(text_filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Text dashboard saved as: {text_filename}")
    plt.show()

def create_scenario_comparison_chart(energy_sources):
    """Create comparison chart across all scenarios"""
    
    scenarios = define_usage_scenarios()
    all_breakdowns = {}
    
    # Calculate breakdown for each scenario
    for key, scenario in scenarios.items():
        all_breakdowns[key] = calculate_cost_breakdown(scenario, energy_sources)
    
    # Create comparison chart
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Total Monthly Cost Comparison
    scenario_names = [s["description"] for s in scenarios.values()]
    total_costs = [b['total_costs']['total_net_cost_ngn']/1000 for b in all_breakdowns.values()]
    
    bars1 = ax1.bar(range(len(scenario_names)), total_costs, 
                   color=['#E74C3C', '#F39C12', '#2ECC71', '#3498DB'])
    ax1.set_ylabel('Total Monthly Cost (₦ Thousands)', fontweight='bold')
    ax1.set_title('Total Cost Comparison Across Scenarios', fontweight='bold', pad=10)
    ax1.set_xticks(range(len(scenario_names)))
    ax1.set_xticklabels(scenario_names, rotation=45, ha='right')
    ax1.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, cost) in enumerate(zip(bars1, total_costs)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'₦{cost:.0f}K', ha='center', va='bottom', fontweight='bold')
    
    # 2. Cost per kWh Comparison
    costs_per_kwh = [b['unit_costs']['cost_per_kwh_total'] for b in all_breakdowns.values()]
    grid_line = [110] * len(scenario_names)
    generator_line = [485] * len(scenario_names)
    
    bars2 = ax2.bar(range(len(scenario_names)), costs_per_kwh, 
                   color=['#E74C3C', '#F39C12', '#2ECC71', '#3498DB'])
    ax2.plot(range(len(scenario_names)), grid_line, '--', color='#3498DB', linewidth=2, label='Grid Tariff (₦110)')
    ax2.plot(range(len(scenario_names)), generator_line, '--', color='#E74C3C', linewidth=2, label='Generator (₦485)')
    ax2.set_ylabel('Cost per kWh (₦)', fontweight='bold')
    ax2.set_title('Cost Efficiency Comparison', fontweight='bold', pad=10)
    ax2.set_xticks(range(len(scenario_names)))
    ax2.set_xticklabels(scenario_names, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    for i, (bar, cost) in enumerate(zip(bars2, costs_per_kwh)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'₦{cost:.0f}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Energy Mix Comparison (Stacked Bar)
    ax3.set_ylabel('Energy Mix Percentage (%)', fontweight='bold')
    ax3.set_title('Energy Source Distribution by Scenario', fontweight='bold', pad=10)
    
    grid_percents = [s["energy_mix"]["grid_percent"] for s in scenarios.values()]
    gen_percents = [s["energy_mix"]["generator_percent"] for s in scenarios.values()]
    solar_percents = [s["energy_mix"]["solar_percent"] for s in scenarios.values()]
    battery_percents = [s["energy_mix"]["battery_percent"] for s in scenarios.values()]
    
    x = range(len(scenario_names))
    width = 0.6
    
    bars3a = ax3.bar(x, grid_percents, width, color='#3498DB', label='Grid')
    bars3b = ax3.bar(x, gen_percents, width, bottom=grid_percents, color='#E74C3C', label='Generator')
    bars3c = ax3.bar(x, solar_percents, width, 
                     bottom=[g+ge for g, ge in zip(grid_percents, gen_percents)], 
                     color='#F39C12', label='Solar')
    bars3d = ax3.bar(x, battery_percents, width, 
                     bottom=[g+ge+s for g, ge, s in zip(grid_percents, gen_percents, solar_percents)], 
                     color='#2ECC71', label='Battery')
    
    ax3.set_xticks(x)
    ax3.set_xticklabels(scenario_names, rotation=45, ha='right')
    ax3.set_ylim(0, 105)
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.legend(loc='upper right', fontsize=8)
    
    # 4. Cash Outflow Comparison
    cash_outflows = [b['cash_flow']['monthly_outflow_ngn']/1000 for b in all_breakdowns.values()]
    
    bars4 = ax4.bar(range(len(scenario_names)), cash_outflows,
                   color=['#E74C3C', '#F39C12', '#2ECC71', '#3498DB'])
    ax4.set_ylabel('Monthly Cash Outflow (₦ Thousands)', fontweight='bold')
    ax4.set_title('Actual Monthly Payments Comparison', fontweight='bold', pad=10)
    ax4.set_xticks(range(len(scenario_names)))
    ax4.set_xticklabels(scenario_names, rotation=45, ha='right')
    ax4.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, cash) in enumerate(zip(bars4, cash_outflows)):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'₦{cash:.0f}K', ha='center', va='bottom', fontweight='bold')
    
    plt.suptitle('Energy Cost Scenario Comparison Analysis\nPortfolio Days 1-7 Integration', 
                fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    # Save the scenario comparison chart
    comparison_filename = 'energy_cost_scenario_comparison.png'
    plt.savefig(comparison_filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Scenario comparison chart saved as: {comparison_filename}")
    plt.show()
    
    return all_breakdowns

# ============================================================================
# 5. COST DRIVER ANALYSIS
# ============================================================================

def analyze_cost_drivers(breakdown):
    """Identify and analyze major cost drivers"""
    
    # Calculate what percentage of costs are fixed vs variable
    variable_costs = breakdown['costs_by_source']['grid_ngn'] + \
                    (breakdown['costs_by_source']['generator_ngn'] - 5000)  # Exclude fixed maintenance
    
    fixed_costs = 5000 + breakdown['costs_by_source']['solar_ngn'] + \
                  breakdown['costs_by_source']['battery_ngn'] + \
                  breakdown['costs_by_source']['efficiency_ngn']
    
    total_costs = variable_costs + fixed_costs
    
    # Identify biggest cost component
    cost_components = breakdown['costs_by_source']
    max_component = max(cost_components, key=cost_components.get)
    max_value = cost_components[max_component]
    
    # Calculate cost sensitivity to usage
    # For every 10% increase in energy use, how much do costs increase?
    grid_sensitivity = breakdown['energy_by_source']['grid_kwh'] * 0.1 * 110
    gen_sensitivity = breakdown['energy_by_source']['generator_kwh'] * 0.1 * 485
    total_sensitivity = grid_sensitivity + gen_sensitivity
    
    # Opportunity cost of outages (from Day 5)
    outage_cost_per_hour = breakdown['total_costs']['total_net_cost_ngn'] / 730 * \
                          (breakdown['efficiency_metrics']['outage_hours_monthly'] / 30)
    
    drivers = {
        "cost_structure": {
            "variable_costs_ngn": variable_costs,
            "fixed_costs_ngn": fixed_costs,
            "variable_percent": (variable_costs / total_costs) * 100,
            "fixed_percent": (fixed_costs / total_costs) * 100
        },
        "biggest_driver": {
            "component": max_component,
            "cost_ngn": max_value,
            "percentage": (max_value / total_costs) * 100
        },
        "sensitivity": {
            "per_10pct_usage_increase_ngn": total_sensitivity,
            "grid_cost_per_additional_kwh": 110,
            "generator_cost_per_additional_kwh": 485
        },
        "efficiency_opportunities": {
            "outage_cost_per_hour_ngn": outage_cost_per_hour,
            "potential_savings_from_battery_ngn": min(breakdown['efficiency_metrics']['outage_hours_monthly'] * 1000, 
                                                     breakdown['costs_by_source']['generator_ngn']),
            "solar_self_consumption_opportunity": breakdown['energy_by_source']['solar_kwh'] * 110
        },
        "optimization_recommendations": []
    }
    
    # Generate recommendations based on cost structure
    if drivers["cost_structure"]["variable_percent"] > 70:
        drivers["optimization_recommendations"].append("Focus on reducing energy consumption (variable costs are high)")
    
    if breakdown['costs_by_source']['generator_ngn'] > breakdown['costs_by_source']['grid_ngn']:
        drivers["optimization_recommendations"].append("Generator costs exceed grid costs - prioritize solar/battery to reduce generator use")
    
    if breakdown['unit_costs']['cost_per_kwh_total'] > 200:
        drivers["optimization_recommendations"].append("Total cost per kWh is high (>₦200) - consider efficiency improvements")
    
    return drivers

# ============================================================================
# 6. DATA EXPORT FUNCTIONS
# ============================================================================

def export_analysis_results(breakdown, cost_drivers, scenario_name):
    """Export analysis results to CSV files"""
    
    # Clean the scenario name for filename
    clean_scenario_name = scenario_name.replace(":", "").replace("+", "and").replace(" ", "_").lower()
    
    # Monthly cost breakdown table
    cost_table = {
        'Cost_Category': [
            'Grid Electricity',
            'Generator Fuel',
            'Generator Maintenance',
            'Solar System (Amortized)',
            'Battery System (Amortized)',
            'Efficiency Upgrades (Amortized)',
            'Total Energy Cost (Grid+Gen)',
            'Total Capital Cost',
            'Total Net Cost',
            'Monthly Cash Outflow'
        ],
        'Monthly_Cost_NGN': [
            breakdown['costs_by_source']['grid_ngn'],
            breakdown['costs_by_source']['generator_ngn'] - 5000,
            5000,
            breakdown['costs_by_source']['solar_ngn'],
            breakdown['costs_by_source']['battery_ngn'],
            breakdown['costs_by_source']['efficiency_ngn'],
            breakdown['total_costs']['total_energy_cost_ngn'],
            breakdown['total_costs']['total_capital_cost_ngn'],
            breakdown['total_costs']['total_net_cost_ngn'],
            breakdown['cash_flow']['monthly_outflow_ngn']
        ],
        'Percentage_of_Total': [
            f"{(breakdown['costs_by_source']['grid_ngn'] / breakdown['total_costs']['total_net_cost_ngn'] * 100):.1f}%" if breakdown['total_costs']['total_net_cost_ngn'] > 0 else "0.0%",
            f"{((breakdown['costs_by_source']['generator_ngn'] - 5000) / breakdown['total_costs']['total_net_cost_ngn'] * 100):.1f}%" if breakdown['total_costs']['total_net_cost_ngn'] > 0 else "0.0%",
            f"{(5000 / breakdown['total_costs']['total_net_cost_ngn'] * 100):.1f}%" if breakdown['total_costs']['total_net_cost_ngn'] > 0 else "0.0%",
            f"{(breakdown['costs_by_source']['solar_ngn'] / breakdown['total_costs']['total_net_cost_ngn'] * 100):.1f}%" if breakdown['total_costs']['total_net_cost_ngn'] > 0 else "0.0%",
            f"{(breakdown['costs_by_source']['battery_ngn'] / breakdown['total_costs']['total_net_cost_ngn'] * 100):.1f}%" if breakdown['total_costs']['total_net_cost_ngn'] > 0 else "0.0%",
            f"{(breakdown['costs_by_source']['efficiency_ngn'] / breakdown['total_costs']['total_net_cost_ngn'] * 100):.1f}%" if breakdown['total_costs']['total_net_cost_ngn'] > 0 else "0.0%",
            f"{(breakdown['total_costs']['total_energy_cost_ngn'] / breakdown['total_costs']['total_net_cost_ngn'] * 100):.1f}%" if breakdown['total_costs']['total_net_cost_ngn'] > 0 else "0.0%",
            f"{(breakdown['total_costs']['total_capital_cost_ngn'] / breakdown['total_costs']['total_net_cost_ngn'] * 100):.1f}%" if breakdown['total_costs']['total_net_cost_ngn'] > 0 else "0.0%",
            '100%',
            f"{(breakdown['cash_flow']['monthly_outflow_ngn'] / breakdown['total_costs']['total_net_cost_ngn'] * 100):.1f}%" if breakdown['total_costs']['total_net_cost_ngn'] > 0 else "0.0%"
        ]
    }
    
    df_cost = pd.DataFrame(cost_table)
    cost_filename = f'energy_cost_breakdown_{clean_scenario_name}.csv'
    df_cost.to_csv(cost_filename, index=False)
    print(f"✓ Cost breakdown saved as: {cost_filename}")
    
    # Energy source table
    energy_table = {
        'Energy_Source': ['Grid', 'Generator', 'Solar PV', 'Battery Storage'],
        'Monthly_Energy_kWh': [
            breakdown['energy_by_source']['grid_kwh'],
            breakdown['energy_by_source']['generator_kwh'],
            breakdown['energy_by_source']['solar_kwh'],
            breakdown['energy_by_source']['battery_kwh']
        ],
        'Percentage_of_Total': [
            f"{(breakdown['energy_by_source']['grid_kwh'] / breakdown['monthly_energy_kwh'] * 100):.1f}%" if breakdown['monthly_energy_kwh'] > 0 else "0.0%",
            f"{(breakdown['energy_by_source']['generator_kwh'] / breakdown['monthly_energy_kwh'] * 100):.1f}%" if breakdown['monthly_energy_kwh'] > 0 else "0.0%",
            f"{(breakdown['energy_by_source']['solar_kwh'] / breakdown['monthly_energy_kwh'] * 100):.1f}%" if breakdown['monthly_energy_kwh'] > 0 else "0.0%",
            f"{(breakdown['energy_by_source']['battery_kwh'] / breakdown['monthly_energy_kwh'] * 100):.1f}%" if breakdown['monthly_energy_kwh'] > 0 else "0.0%"
        ],
        'Cost_per_kWh_NGN': [110, 485, 'Amortized', 'Amortized'],
        'Monthly_Cost_NGN': [
            breakdown['costs_by_source']['grid_ngn'],
            breakdown['costs_by_source']['generator_ngn'],
            breakdown['costs_by_source']['solar_ngn'],
            breakdown['costs_by_source']['battery_ngn']
        ]
    }
    
    df_energy = pd.DataFrame(energy_table)
    energy_filename = f'energy_source_analysis_{clean_scenario_name}.csv'
    df_energy.to_csv(energy_filename, index=False)
    print(f"✓ Energy source analysis saved as: {energy_filename}")
    
    # Create a summary text file
    summary_filename = f'energy_analysis_summary_{clean_scenario_name}.txt'
    with open(summary_filename, 'w') as f:
        f.write(f"Energy Cost Analysis Summary - {scenario_name}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total Monthly Cost: ₦{breakdown['total_costs']['total_net_cost_ngn']:,.0f}\n")
        f.write(f"Cost per kWh: ₦{breakdown['unit_costs']['cost_per_kwh_total']:.0f}\n")
        f.write(f"Monthly Cash Outflow: ₦{breakdown['cash_flow']['monthly_outflow_ngn']:,.0f}\n")
        f.write(f"Annual Budget: ₦{breakdown['total_costs']['total_net_cost_ngn'] * 12:,.0f}\n\n")
        f.write("Biggest Cost Driver:\n")
        f.write(f"  - {cost_drivers['biggest_driver']['component']}: {cost_drivers['biggest_driver']['percentage']:.1f}%\n\n")
        f.write("Optimization Recommendations:\n")
        for rec in cost_drivers['optimization_recommendations']:
            f.write(f"  - {rec}\n")
    
    print(f"✓ Analysis summary saved as: {summary_filename}")
    
    return df_cost, df_energy

# ============================================================================
# 7. MAIN EXECUTION FUNCTION
# ============================================================================

def main():
    """Execute comprehensive energy cost breakdown analysis"""
    
    print("=" * 80)
    print("DAY 7: COMPREHENSIVE MONTHLY ENERGY COST BREAKDOWN")
    print("Energy System Management Portfolio Project")
    print("=" * 80)
    
    print("\nANALYSIS OBJECTIVE:")
    print("Perform comprehensive household energy cost audit by combining")
    print("grid, generator, solar, and battery costs to understand where money actually goes.")
    
    # Step 1: Define energy sources
    print("\n1. DEFINING ENERGY SOURCES & COSTS...")
    energy_sources = define_energy_sources()
    print(f"   • Grid Tariff: ₦{energy_sources['grid']['tariff_per_kwh']}/kWh")
    print(f"   • Generator Cost: ₦{energy_sources['generator']['cost_per_kwh']}/kWh (incl. capital)")
    print(f"   • Solar Amortized: ₦{energy_sources['solar_pv']['amortized_cost_monthly']:,.0f}/month")
    print(f"   • Battery Amortized: ₦{energy_sources['battery_storage']['amortized_cost_monthly']:,.0f}/month")
    
    # Step 2: Define usage scenarios
    print("\n2. DEFINING USAGE SCENARIOS...")
    scenarios = define_usage_scenarios()
    selected_scenario = scenarios["hybrid_optimal"]
    print(f"   • Selected Scenario: {selected_scenario['description']}")
    print(f"   • Monthly Energy: {selected_scenario['monthly_energy_kwh']:,.0f} kWh")
    print(f"   • Energy Mix: Grid {selected_scenario['energy_mix']['grid_percent']}%, "
          f"Gen {selected_scenario['energy_mix']['generator_percent']}%, "
          f"Solar {selected_scenario['energy_mix']['solar_percent']}%")
    
    # Step 3: Calculate cost breakdown
    print("\n3. CALCULATING COST BREAKDOWN...")
    breakdown = calculate_cost_breakdown(selected_scenario, energy_sources)
    print(f"   • Total Monthly Cost: ₦{breakdown['total_costs']['total_net_cost_ngn']:,.0f}")
    print(f"   • Cost per kWh: ₦{breakdown['unit_costs']['cost_per_kwh_total']:.0f}")
    print(f"   • Monthly Cash Outflow: ₦{breakdown['cash_flow']['monthly_outflow_ngn']:,.0f}")
    
    # Step 4: Analyze cost drivers
    print("\n4. ANALYZING COST DRIVERS...")
    cost_drivers = analyze_cost_drivers(breakdown)
    print(f"   • Biggest Cost Driver: {cost_drivers['biggest_driver']['component']} "
          f"({cost_drivers['biggest_driver']['percentage']:.1f}%)")
    print(f"   • Variable vs Fixed: {cost_drivers['cost_structure']['variable_percent']:.1f}% variable, "
          f"{cost_drivers['cost_structure']['fixed_percent']:.1f}% fixed")
    
    # Step 5: Create visualizations
    print("\n5. CREATING VISUALIZATIONS...")
    print("   • Creating chart dashboard...")
    create_cost_breakdown_dashboard(breakdown, selected_scenario["description"], energy_sources)
    
    # Step 6: Create scenario comparison
    print("   • Creating scenario comparison chart...")
    create_scenario_comparison_chart(energy_sources)
    
    # Step 7: Export data
    print("\n6. EXPORTING ANALYSIS DATA...")
    export_analysis_results(breakdown, cost_drivers, selected_scenario["description"])
    
    # Step 8: Print comprehensive findings
    print("\n" + "=" * 80)
    print("ENERGY COST BREAKDOWN ANALYSIS - KEY FINDINGS")
    print("=" * 80)
    
    findings = f"""
COMPREHENSIVE COST AUDIT RESULTS:

1. MONTHLY FINANCIAL SUMMARY:
   • Total Energy Consumption: {breakdown['monthly_energy_kwh']:,.0f} kWh
   • Total Monthly Cost: ₦{breakdown['total_costs']['total_net_cost_ngn']:,.0f}
   • Cost per kWh: ₦{breakdown['unit_costs']['cost_per_kwh_total']:.0f}
   • Monthly Cash Outflow: ₦{breakdown['cash_flow']['monthly_outflow_ngn']:,.0f}
   • Annual Energy Budget: ₦{breakdown['total_costs']['total_net_cost_ngn'] * 12:,.0f}

2. ENERGY SOURCE BREAKDOWN:
   • Grid: {breakdown['energy_by_source']['grid_kwh']:.0f} kWh ({breakdown['efficiency_metrics']['energy_mix_percent']['grid_percent']}%) → ₦{breakdown['costs_by_source']['grid_ngn']:,.0f}
   • Generator: {breakdown['energy_by_source']['generator_kwh']:.0f} kWh ({breakdown['efficiency_metrics']['energy_mix_percent']['generator_percent']}%) → ₦{breakdown['costs_by_source']['generator_ngn']:,.0f}
   • Solar PV: {breakdown['energy_by_source']['solar_kwh']:.0f} kWh ({breakdown['efficiency_metrics']['energy_mix_percent']['solar_percent']}%) → ₦{breakdown['costs_by_source']['solar_ngn']:,.0f}
   • Battery: {breakdown['energy_by_source']['battery_kwh']:.0f} kWh ({breakdown['efficiency_metrics']['energy_mix_percent']['battery_percent']}%) → ₦{breakdown['costs_by_source']['battery_ngn']:,.0f}

3. COST DRIVER ANALYSIS:
   • Primary Driver: {cost_drivers['biggest_driver']['component'].upper()} → {cost_drivers['biggest_driver']['percentage']:.1f}% of total
   • Cost Structure: {cost_drivers['cost_structure']['variable_percent']:.1f}% variable, {cost_drivers['cost_structure']['fixed_percent']:.1f}% fixed
   • Grid vs Generator: Generator costs are {breakdown['costs_by_source']['generator_ngn']/breakdown['costs_by_source']['grid_ngn']:.1f}x grid costs
   • Efficiency Impact: Efficiency upgrades save ₦{breakdown['total_costs']['total_savings_ngn']:,.0f}/month

4. OPTIMIZATION RECOMMENDATIONS:
"""
    
    for i, rec in enumerate(cost_drivers['optimization_recommendations'], 1):
        findings += f"   {i}. {rec}\n"
    
    findings += f"""
PORTFOLIO VALUE:
This comprehensive cost audit demonstrates ability to:
• Integrate multiple energy source cost models
• Perform detailed financial analysis
• Identify cost drivers and optimization opportunities
• Create actionable budgeting recommendations
• Communicate complex energy economics clearly
"""

    print(findings)
    
    print("\n" + "=" * 80)
    print("PROJECT DELIVERABLES:")
    print("=" * 80)
    print("✓ Chart Dashboard: energy_cost_charts_hybrid_grid_and_solar_and_battery_and_minimal_generator.png")
    print("✓ Text Dashboard: energy_cost_text_dashboard_hybrid_grid_and_solar_and_battery_and_minimal_generator.png")
    print("✓ Scenario Comparison: energy_cost_scenario_comparison.png")
    print("✓ Cost Breakdown CSV: energy_cost_breakdown_hybrid_grid_and_solar_and_battery_and_minimal_generator.csv")
    print("✓ Energy Source CSV: energy_source_analysis_hybrid_grid_and_solar_and_battery_and_minimal_generator.csv")
    print("✓ Analysis Summary: energy_analysis_summary_hybrid_grid_and_solar_and_battery_and_minimal_generator.txt")
    
    print("\n" + "=" * 80)
    print("PORTFOLIO ANGLE ACHIEVED:")
    print("=" * 80)
    print("'Performed a comprehensive household energy cost audit by analyzing")
    print("grid, generator, solar, and battery costs to identify cost drivers")
    print("and optimization opportunities.'")
    
    print("\n" + "=" * 80)
    print("WEEK 1 PORTFOLIO COMPLETE: 7 DAYS OF ENERGY SYSTEM ANALYSIS")
    print("=" * 80)
    print("Day 1: Household load profiling ✓")
    print("Day 2: Generator economics ✓")
    print("Day 3: Solar PV sizing ✓")
    print("Day 4: Battery storage sizing ✓")
    print("Day 5: Grid outage impact ✓")
    print("Day 6: Appliance efficiency ✓")
    print("Day 7: Comprehensive cost audit ✓")
    print("\nTotal portfolio deliverables: 30+ files, 7+ days of analysis")
    print("Skills demonstrated: Python, Data Analysis, Energy Modeling, Financial Analysis")
    print("Professional value: Real-world Nigerian energy system optimization")

# ============================================================================
# EXECUTE ANALYSIS
# ============================================================================

if __name__ == "__main__":
    main()