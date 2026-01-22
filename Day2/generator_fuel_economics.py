"""
DAY 2: Generator Fuel Economics Model
Professional Energy System Management Portfolio

Analysis of backup power operational costs with current Nigerian fuel prices
and appropriately sized generator specifications.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# ============================================================================
# 1. UPDATED GENERATOR PARAMETERS (CURRENT MARKET)
# ============================================================================

def define_generator_parameters():
    """Define current market specifications for petrol generator"""
    
    generator = {
        "type": "Petrol Generator (PMS)",
        "rating_kVA": 11,
        "rating_kW": 11,  # Assuming power factor of 1.0 for residential use
        "fuel_type": "Petrol (PMS)",
        "fuel_price": 900,  # ₦/liter (Current March 2025 price)
        "purchase_price": 850000,  # ₦ approximate for 11kVA generator
        "load_efficiency": {
            "25%_load": {"fuel_rate": 2.0, "efficiency": 60},  # L/hr at 2.75 kW
            "50%_load": {"fuel_rate": 3.5, "efficiency": 70},  # L/hr at 5.5 kW
            "75%_load": {"fuel_rate": 5.0, "efficiency": 75},  # L/hr at 8.25 kW
            "100%_load": {"fuel_rate": 6.5, "efficiency": 78},  # L/hr at 11 kW
        },
        "maintenance_schedule": {
            "oil_change_hrs": 100,
            "spark_plugs_hrs": 500,
            "air_filter_hrs": 250,
            "major_service_hrs": 1000
        }
    }
    
    # Operational assumptions for 24-hour scenario
    operational = {
        "runtime_scenario": "24-hour continuous operation",
        "maintenance_factor": 1.20,  # 20% additional for maintenance (higher for 24/7)
        "lifespan_years": 3,  # Reduced lifespan for continuous operation
        "resale_value_rate": 0.3,  # 30% of purchase price after lifespan
        "fuel_price_volatility": 0.25  # 25% monthly price fluctuation
    }
    
    return generator, operational

# ============================================================================
# 2. HOUSEHOLD LOAD PROFILE (CONSISTENT WITH DAY 1)
# ============================================================================

def get_household_load_profile():
    """24-hour load profile for typical Nigerian household"""
    
    # Updated to reflect more realistic middle-class household
    hourly_load = [
        0.45, 0.45, 0.45, 0.45, 0.45, 0.45,  # 00:00-05:00 (Base load + fans)
        2.20, 3.50, 1.80, 0.80, 0.65, 0.65,  # 06:00-11:00 (Morning peak)
        0.65, 1.80, 1.40, 0.90, 0.80, 1.60,  # 12:00-17:00 (Daytime)
        1.40, 2.80, 3.20, 2.40, 2.10, 1.50   # 18:00-23:00 (Evening peak)
    ]
    
    hours = list(range(24))
    hour_labels = [f"{h:02d}:00" for h in hours]
    
    df = pd.DataFrame({
        'Hour': hours,
        'Time': hour_labels,
        'Load_kW': hourly_load,
        'Load_Percent': [min(l/11*100, 100) for l in hourly_load]  # Percent of 11kW capacity
    })
    
    return df

# ============================================================================
# 3. FUEL CONSUMPTION MODEL (LINEAR INTERPOLATION)
# ============================================================================

def calculate_fuel_consumption(df_load, generator):
    """Calculate fuel consumption with linear interpolation"""
    
    fuel_rates = []
    fuel_costs = []
    cumulative_fuel = []
    cumulative_cost = []
    
    total_fuel = 0
    total_cost = 0
    
    for idx, row in df_load.iterrows():
        load_kw = row['Load_kW']
        load_percent = min(load_kw / generator['rating_kW'] * 100, 100)
        
        # Linear interpolation between efficiency points
        if load_percent <= 25:
            # 0-25%: Interpolate between 0 and 25%
            fuel_lph = 2.0 * (load_percent / 25)
        elif load_percent <= 50:
            # 25-50%: Interpolate between 25% and 50%
            fuel_lph = 2.0 + (3.5-2.0) * ((load_percent-25)/25)
        elif load_percent <= 75:
            # 50-75%: Interpolate between 50% and 75%
            fuel_lph = 3.5 + (5.0-3.5) * ((load_percent-50)/25)
        else:
            # 75-100%: Interpolate between 75% and 100%
            fuel_lph = 5.0 + (6.5-5.0) * ((load_percent-75)/25)
        
        # Hourly fuel cost at current prices
        hourly_cost = fuel_lph * generator['fuel_price']
        
        fuel_rates.append(fuel_lph)
        fuel_costs.append(hourly_cost)
        
        total_fuel += fuel_lph
        total_cost += hourly_cost
        cumulative_fuel.append(total_fuel)
        cumulative_cost.append(total_cost)
    
    df_load['Fuel_L_per_hour'] = fuel_rates
    df_load['Hourly_Fuel_Cost_NGN'] = fuel_costs
    df_load['Cumulative_Fuel_L'] = cumulative_fuel
    df_load['Cumulative_Cost_NGN'] = cumulative_cost
    
    return df_load

# ============================================================================
# 4. COMPREHENSIVE ECONOMIC ANALYSIS
# ============================================================================

def perform_comprehensive_analysis(df_load, generator, operational):
    """Complete economic analysis including capital costs"""
    
    # Daily operational metrics
    daily_energy = df_load['Load_kW'].sum()
    daily_fuel = df_load['Fuel_L_per_hour'].sum()
    daily_fuel_cost = df_load['Hourly_Fuel_Cost_NGN'].sum()
    
    # With maintenance factor
    daily_total_cost = daily_fuel_cost * operational['maintenance_factor']
    
    # Cost per kWh metrics
    cost_per_kwh_basic = daily_fuel_cost / daily_energy
    cost_per_kwh_total = daily_total_cost / daily_energy
    
    # Capital cost amortization
    annual_operating_hours = 24 * 365
    lifespan_hours = operational['lifespan_years'] * annual_operating_hours
    residual_value = generator['purchase_price'] * operational['resale_value_rate']
    
    # Annualized capital cost (straight-line depreciation)
    annual_capital_cost = (generator['purchase_price'] - residual_value) / operational['lifespan_years']
    daily_capital_cost = annual_capital_cost / 365
    
    # Total cost including capital
    daily_total_cost_with_capital = daily_total_cost + daily_capital_cost
    cost_per_kwh_with_capital = daily_total_cost_with_capital / daily_energy
    
    # Monthly and annual projections
    monthly_metrics = {
        'fuel_liters': daily_fuel * 30,
        'fuel_cost': daily_fuel_cost * 30,
        'total_cost': daily_total_cost * 30,
        'total_with_capital': daily_total_cost_with_capital * 30
    }
    
    annual_metrics = {
        'fuel_liters': daily_fuel * 365,
        'fuel_cost': daily_fuel_cost * 365,
        'total_cost': daily_total_cost * 365,
        'total_with_capital': daily_total_cost_with_capital * 365,
        'capital_cost': annual_capital_cost
    }
    
    # Efficiency metrics
    average_load = df_load['Load_kW'].mean()
    capacity_factor = (average_load / generator['rating_kW']) * 100
    
    # Theoretical energy content of petrol: ~9.7 kWh/L
    theoretical_energy = daily_fuel * 9.7
    actual_energy = daily_energy
    overall_efficiency = (actual_energy / theoretical_energy) * 100
    
    economics = {
        # Daily operational
        'daily_energy_kwh': daily_energy,
        'daily_fuel_liters': daily_fuel,
        'daily_fuel_cost_ngn': daily_fuel_cost,
        'daily_total_cost_ngn': daily_total_cost,
        'daily_capital_cost_ngn': daily_capital_cost,
        'daily_total_with_capital': daily_total_cost_with_capital,
        
        # Cost per kWh
        'cost_per_kwh_fuel_only': cost_per_kwh_basic,
        'cost_per_kwh_with_maint': cost_per_kwh_total,
        'cost_per_kwh_with_capital': cost_per_kwh_with_capital,
        
        # Monthly projections
        'monthly_fuel_liters': monthly_metrics['fuel_liters'],
        'monthly_fuel_cost': monthly_metrics['fuel_cost'],
        'monthly_total_cost': monthly_metrics['total_cost'],
        'monthly_total_with_capital': monthly_metrics['total_with_capital'],
        
        # Annual projections
        'annual_fuel_liters': annual_metrics['fuel_liters'],
        'annual_fuel_cost': annual_metrics['fuel_cost'],
        'annual_total_cost': annual_metrics['total_cost'],
        'annual_total_with_capital': annual_metrics['total_with_capital'],
        'annual_capital_cost': annual_metrics['capital_cost'],
        
        # Efficiency metrics
        'average_load_kw': average_load,
        'capacity_factor_percent': capacity_factor,
        'overall_efficiency_percent': overall_efficiency,
        'peak_load_kw': df_load['Load_kW'].max(),
        'load_factor': (daily_energy/24) / df_load['Load_kW'].max(),
        
        # System specifications
        'generator_size_kw': generator['rating_kW'],
        'fuel_price_per_liter': generator['fuel_price'],
        'purchase_price': generator['purchase_price']
    }
    
    return economics

# ============================================================================
# 5. PROFESSIONAL VISUALIZATION DASHBOARD
# ============================================================================

def create_economic_dashboard(df_load, generator, economics):
    """Create comprehensive visualization dashboard"""
    
    # Professional styling
    plt.style.use('seaborn-v0_8-whitegrid')
    mpl.rcParams['font.size'] = 9
    mpl.rcParams['axes.titlesize'] = 11
    mpl.rcParams['figure.figsize'] = [16, 12]
    
    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(4, 3)
    
    # 1. Load vs Fuel Consumption Pattern
    ax1 = fig.add_subplot(gs[0, :2])
    
    # Fuel consumption bars
    bars1 = ax1.bar(df_load['Time'], df_load['Fuel_L_per_hour'], 
                    color='#E74C3C', alpha=0.7, width=0.7, label='Fuel Consumption')
    ax1.set_xlabel('Hour of Day', fontweight='bold')
    ax1.set_ylabel('Fuel Rate (L/hr)', fontweight='bold', color='#E74C3C')
    ax1.tick_params(axis='y', labelcolor='#E74C3C')
    ax1.set_xticks(df_load['Time'][::3])
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Electrical load line
    ax1_twin = ax1.twinx()
    line1 = ax1_twin.plot(df_load['Time'], df_load['Load_kW'], 'o-', 
                          color='#2980B9', linewidth=2, markersize=4, 
                          label='Electrical Load')
    ax1_twin.set_ylabel('Electrical Load (kW)', fontweight='bold', color='#2980B9')
    ax1_twin.tick_params(axis='y', labelcolor='#2980B9')
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)
    ax1.set_title('Hourly Load vs Fuel Consumption Pattern', fontweight='bold', pad=10)
    
    # 2. Cumulative Cost Analysis (Primary Deliverable)
    ax2 = fig.add_subplot(gs[0, 2])
    
    hours = list(range(1, 25))
    cumulative_cost = df_load['Cumulative_Cost_NGN'].tolist()
    
    ax2.plot(hours, cumulative_cost, 's-', color='#27AE60', linewidth=2.5, 
             markersize=5, markeredgecolor='white', markeredgewidth=1)
    ax2.fill_between(hours, cumulative_cost, alpha=0.15, color='#27AE60')
    
    # Mark key operational points
    ax2.axvline(x=8, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
    ax2.axvline(x=16, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
    
    ax2.text(8, cumulative_cost[7]*0.3, f'₦{cumulative_cost[7]:,.0f}\n(8 hrs)', 
             ha='center', fontweight='bold', fontsize=8, 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax2.text(16, cumulative_cost[15]*0.6, f'₦{cumulative_cost[15]:,.0f}\n(16 hrs)', 
             ha='center', fontweight='bold', fontsize=8,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax2.text(24, cumulative_cost[-1]*0.9, f'₦{cumulative_cost[-1]:,.0f}\n(24 hrs)', 
             ha='center', fontweight='bold', fontsize=8,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax2.set_xlabel('Runtime (Hours)', fontweight='bold')
    ax2.set_ylabel('Cumulative Fuel Cost (₦)', fontweight='bold')
    ax2.set_title('Runtime vs Cumulative Fuel Cost', fontweight='bold', pad=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0.5, 24.5)
    
    # 3. Cost Breakdown Analysis
    ax3 = fig.add_subplot(gs[1, 0])
    
    cost_components = ['Fuel Cost', '+ Maintenance', '+ Capital Cost']
    daily_values = [
        economics['daily_fuel_cost_ngn'],
        economics['daily_total_cost_ngn'] - economics['daily_fuel_cost_ngn'],
        economics['daily_capital_cost_ngn']
    ]
    cumulative_values = np.cumsum(daily_values)
    
    colors = ['#E74C3C', '#F39C12', '#3498DB']
    bars3 = ax3.bar(range(3), daily_values, color=colors, edgecolor='black', linewidth=0.5)
    
    ax3.set_xticks(range(3))
    ax3.set_xticklabels(cost_components, rotation=45, ha='right', fontsize=8)
    ax3.set_ylabel('Daily Cost (₦)', fontweight='bold')
    ax3.set_title('Daily Cost Breakdown', fontweight='bold', pad=10)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars3, daily_values)):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 500,
                f'₦{val:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 4. Monthly Cost Projection
    ax4 = fig.add_subplot(gs[1, 1])
    
    monthly_labels = ['Fuel Only', 'With Maint.', 'Total Cost']
    monthly_values = [
        economics['monthly_fuel_cost'],
        economics['monthly_total_cost'],
        economics['monthly_total_with_capital']
    ]
    
    bars4 = ax4.bar(monthly_labels, monthly_values, color=['#E74C3C', '#F39C12', '#2ECC71'])
    ax4.set_ylabel('Monthly Cost (₦)', fontweight='bold')
    ax4.set_title('Monthly Cost Projections', fontweight='bold', pad=10)
    ax4.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, val) in enumerate(zip(bars4, monthly_values)):
        height = bar.get_height()
        if val > 1000000:
            text_val = f'₦{val/1000000:.1f}M'
        else:
            text_val = f'₦{val:,.0f}'
        ax4.text(bar.get_x() + bar.get_width()/2., height + 10000,
                text_val, ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 5. Cost per kWh Analysis
    ax5 = fig.add_subplot(gs[1, 2])
    
    hourly_cost_per_kwh = []
    for idx, row in df_load.iterrows():
        if row['Load_kW'] > 0.1:
            cost = row['Hourly_Fuel_Cost_NGN'] / row['Load_kW']
        else:
            cost = 0
        hourly_cost_per_kwh.append(cost)
    
    bars5 = ax5.bar(df_load['Time'], hourly_cost_per_kwh, color='#9B59B6', alpha=0.8)
    ax5.axhline(y=110, color='#2C3E50', linestyle='--', linewidth=1.5, 
                label='Grid Tariff (₦110/kWh)')
    ax5.axhline(y=economics['cost_per_kwh_with_capital'], color='#E74C3C', 
                linestyle='-', linewidth=1.5, 
                label=f'Avg Gen Cost (₦{economics["cost_per_kwh_with_capital"]:.0f}/kWh)')
    
    ax5.set_xlabel('Hour of Day', fontweight='bold')
    ax5.set_ylabel('Cost per kWh (₦)', fontweight='bold')
    ax5.set_title('Generator Cost Efficiency by Hour', fontweight='bold', pad=10)
    ax5.set_xticks(df_load['Time'][::3])
    ax5.grid(True, alpha=0.3, axis='y')
    ax5.legend(loc='upper right', fontsize=8)
    
    # 6. Economic Metrics Summary
    ax6 = fig.add_subplot(gs[2, :])
    ax6.axis('off')
    
    summary_text = f"""
SYSTEM SPECIFICATIONS
Generator: {generator['type']}, {generator['rating_kVA']} kVA ({generator['rating_kW']} kW)
Fuel: {generator['fuel_type']} @ ₦{generator['fuel_price']:,}/L
Purchase Price: ₦{generator['purchase_price']:,}
Runtime: 24-hour continuous operation

DAILY OPERATIONAL METRICS
Energy Supplied: {economics['daily_energy_kwh']:.1f} kWh
Fuel Consumption: {economics['daily_fuel_liters']:.1f} L
Fuel Cost: ₦{economics['daily_fuel_cost_ngn']:,.0f}
With Maintenance (20%): ₦{economics['daily_total_cost_ngn']:,.0f}
With Capital Cost: ₦{economics['daily_total_with_capital']:,.0f}

COST PER KWH ANALYSIS
Fuel Only: ₦{economics['cost_per_kwh_fuel_only']:.0f}/kWh
With Maintenance: ₦{economics['cost_per_kwh_with_maint']:.0f}/kWh
With Capital Cost: ₦{economics['cost_per_kwh_with_capital']:.0f}/kWh
Grid Tariff Comparison: ₦110/kWh

MONTHLY PROJECTIONS (30 days)
Fuel Cost: ₦{economics['monthly_fuel_cost']:,.0f}
Total Cost: ₦{economics['monthly_total_with_capital']:,.0f}
Fuel Volume: {economics['monthly_fuel_liters']:,.0f} L

ANNUAL PROJECTIONS
Total Cost: ₦{economics['annual_total_with_capital']:,.0f}
Fuel Volume: {economics['annual_fuel_liters']:,.0f} L
Capital Cost: ₦{economics['annual_capital_cost']:,.0f}

SYSTEM EFFICIENCY
Average Load: {economics['average_load_kw']:.1f} kW
Capacity Factor: {economics['capacity_factor_percent']:.1f}%
Overall Efficiency: {economics['overall_efficiency_percent']:.1f}%
Load Factor: {economics['load_factor']:.2f}
"""
    
    ax6.text(0.02, 0.98, summary_text, fontfamily='monospace', fontsize=8,
            verticalalignment='top', linespacing=1.5,
            bbox=dict(boxstyle='round', facecolor='#F8F9F9', alpha=0.9))
    
    # 7. Annual Cost Breakdown
    ax7 = fig.add_subplot(gs[3, :])
    
    annual_categories = ['Fuel Cost', 'Maintenance', 'Capital Cost', 'Total Annual']
    annual_values = [
        economics['annual_fuel_cost'],
        economics['annual_total_cost'] - economics['annual_fuel_cost'],
        economics['annual_capital_cost'],
        economics['annual_total_with_capital']
    ]
    
    bars7 = ax7.bar(annual_categories, annual_values, 
                    color=['#E74C3C', '#F39C12', '#3498DB', '#2ECC71'])
    ax7.set_ylabel('Annual Cost (₦ Millions)', fontweight='bold')
    ax7.set_title('Annual Cost Breakdown', fontweight='bold', pad=10)
    ax7.grid(True, alpha=0.3, axis='y')
    
    # Format y-axis in millions
    ax7.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: f'₦{x/1000000:.1f}M'))
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars7, annual_values)):
        height = bar.get_height()
        ax7.text(bar.get_x() + bar.get_width()/2., height + 50000,
                f'₦{val/1000000:.1f}M', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    fig.suptitle('Generator Fuel Economics: Backup Power Cost Analysis\nCurrent Market Rates - 11kVA Petrol Generator @ ₦900/L', 
                fontsize=14, fontweight='bold', y=1.02)
    
    plt.savefig('generator_economics_current_market.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    # Additional: Sensitivity Analysis to Fuel Price
    fig2, (ax8, ax9) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Fuel price sensitivity
    fuel_prices = np.linspace(500, 1200, 15)  # ₦500 to ₦1200 per liter
    daily_costs = []
    for price in fuel_prices:
        daily_fuel_cost = df_load['Fuel_L_per_hour'].sum() * price
        daily_total = daily_fuel_cost * 1.2  # With maintenance
        daily_costs.append(daily_total)
    
    ax8.plot(fuel_prices, daily_costs, 'o-', color='#E74C3C', linewidth=2)
    ax8.axvline(x=900, color='gray', linestyle='--', label='Current (₦900/L)')
    ax8.fill_between(fuel_prices, daily_costs, alpha=0.2, color='#E74C3C')
    
    ax8.set_xlabel('Fuel Price (₦/L)', fontweight='bold')
    ax8.set_ylabel('Daily Operating Cost (₦)', fontweight='bold')
    ax8.set_title('Fuel Price Sensitivity Analysis', fontweight='bold', pad=12)
    ax8.grid(True, alpha=0.3)
    ax8.legend()
    
    # Load factor sensitivity
    load_factors = np.linspace(0.1, 0.9, 9)  # 10% to 90% load factor
    efficiency_factors = [60 + (78-60)*lf for lf in load_factors]  # Efficiency improves with load
    
    ax9.plot(load_factors, efficiency_factors, 's-', color='#2980B9', linewidth=2, markersize=6)
    ax9.set_xlabel('Load Factor', fontweight='bold')
    ax9.set_ylabel('Generator Efficiency (%)', fontweight='bold')
    ax9.set_title('Efficiency vs Load Factor', fontweight='bold', pad=12)
    ax9.grid(True, alpha=0.3)
    
    current_load_factor = economics['average_load_kw'] / generator['rating_kW']
    ax9.axvline(x=current_load_factor, color='#E74C3C', linestyle='--', 
                label=f'Current ({current_load_factor:.2f})')
    ax9.legend()
    
    fig2.suptitle('Operational Sensitivity Analysis', fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('generator_sensitivity_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    return fig

# ============================================================================
# 6. DATA EXPORT FUNCTIONS
# ============================================================================

def export_analysis_results(df_load, economics):
    """Export comprehensive analysis results"""
    
    # Detailed hourly analysis
    df_detailed = df_load.copy()
    df_detailed['Cost_per_kWh_NGN'] = df_detailed.apply(
        lambda row: row['Hourly_Fuel_Cost_NGN']/row['Load_kW'] if row['Load_kW'] > 0.1 else 0, 
        axis=1
    )
    df_detailed['Generator_Efficiency_%'] = df_detailed.apply(
        lambda row: (row['Load_kW'] / (row['Fuel_L_per_hour'] * 9.7)) * 100 if row['Fuel_L_per_hour'] > 0 else 0,
        axis=1
    )
    
    df_detailed.to_csv('generator_hourly_analysis_detailed.csv', index=False)
    
    # Economic summary table
    summary_data = {
        'Category': [
            'Generator Specifications',
            'Fuel Parameters',
            'Daily Operational',
            'Cost Metrics',
            'Monthly Projections',
            'Annual Projections',
            'Efficiency Metrics'
        ],
        'Metrics': [
            f"{economics['generator_size_kw']} kW (11 kVA) Petrol Generator",
            f"Petrol @ ₦{economics['fuel_price_per_liter']:,}/L",
            f"{economics['daily_energy_kwh']:.1f} kWh energy, {economics['daily_fuel_liters']:.1f} L fuel",
            f"₦{economics['cost_per_kwh_with_capital']:.0f}/kWh (with all costs)",
            f"₦{economics['monthly_total_with_capital']:,.0f} total monthly cost",
            f"₦{economics['annual_total_with_capital']:,.0f} total annual cost",
            f"{economics['overall_efficiency_percent']:.1f}% overall efficiency"
        ],
        'Values': [
            f"₦{economics['purchase_price']:,} purchase",
            f"₦{economics['daily_fuel_cost_ngn']:,.0f} daily fuel cost",
            f"₦{economics['daily_total_with_capital']:,.0f} total daily cost",
            f"{((economics['cost_per_kwh_with_capital']/110)-1)*100:.0f}% premium vs grid",
            f"{economics['monthly_fuel_liters']:,.0f} L monthly fuel",
            f"{economics['annual_fuel_liters']:,.0f} L annual fuel",
            f"{economics['capacity_factor_percent']:.1f}% capacity factor"
        ]
    }
    
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_csv('generator_economic_summary_detailed.csv', index=False)
    
    return df_detailed, df_summary

# ============================================================================
# 7. MAIN EXECUTION
# ============================================================================

def main():
    """Execute comprehensive generator economics analysis"""
    
    print("=" * 80)
    print("DAY 2: GENERATOR FUEL ECONOMICS MODEL - CURRENT MARKET ANALYSIS")
    print("Professional Energy System Management Portfolio")
    print("=" * 80)
    
    print("\nANALYSIS CONTEXT:")
    print("• Current Nigerian fuel market: Petrol @ ₦900/L (March 2025)")
    print("• Appropriate sizing: 11 kVA (11 kW) generator for household backup")
    print("• Scenario: 24-hour continuous operation")
    print("• Includes: Fuel costs, maintenance (20%), and capital depreciation")
    
    # Step 1: Define current generator parameters
    print("\n1. DEFINING SYSTEM PARAMETERS...")
    generator, operational = define_generator_parameters()
    print(f"   • Generator: {generator['type']}, {generator['rating_kVA']} kVA")
    print(f"   • Fuel Price: ₦{generator['fuel_price']:,}/liter (Current market)")
    print(f"   • Purchase Cost: ₦{generator['purchase_price']:,}")
    print(f"   • Lifespan: {operational['lifespan_years']} years (24/7 operation)")
    
    # Step 2: Load household profile
    print("\n2. LOADING HOUSEHOLD DEMAND PROFILE...")
    df_load = get_household_load_profile()
    print(f"   • Daily Energy Requirement: {df_load['Load_kW'].sum():.1f} kWh")
    print(f"   • Peak Demand: {df_load['Load_kW'].max():.1f} kW")
    print(f"   • Generator Utilization: {(df_load['Load_kW'].mean()/generator['rating_kW']*100):.1f}% of capacity")
    
    # Step 3: Calculate fuel consumption
    print("\n3. MODELING FUEL CONSUMPTION...")
    df_load = calculate_fuel_consumption(df_load, generator)
    print(f"   • Daily Fuel Requirement: {df_load['Fuel_L_per_hour'].sum():.1f} liters")
    print(f"   • Peak Fuel Rate: {df_load['Fuel_L_per_hour'].max():.2f} L/hour")
    print(f"   • Average Fuel Rate: {df_load['Fuel_L_per_hour'].mean():.2f} L/hour")
    
    # Step 4: Economic analysis
    print("\n4. PERFORMING ECONOMIC ANALYSIS...")
    economics = perform_comprehensive_analysis(df_load, generator, operational)
    print(f"   • Daily Fuel Cost: ₦{economics['daily_fuel_cost_ngn']:,.0f}")
    print(f"   • Daily Total Cost (with all factors): ₦{economics['daily_total_with_capital']:,.0f}")
    print(f"   • Cost per kWh (total): ₦{economics['cost_per_kwh_with_capital']:.0f}")
    print(f"   • Monthly Total Cost: ₦{economics['monthly_total_with_capital']:,.0f}")
    
    # Step 5: Create visualizations
    print("\n5. CREATING PROFESSIONAL VISUALIZATIONS...")
    create_economic_dashboard(df_load, generator, economics)
    
    # Step 6: Export data
    print("\n6. EXPORTING ANALYSIS DATA...")
    df_detailed, df_summary = export_analysis_results(df_load, economics)
    
    # Step 7: Print comprehensive findings
    print("\n" + "=" * 80)
    print("KEY FINDINGS: GENERATOR OPERATIONAL ECONOMICS")
    print("=" * 80)
    
    findings = f"""
CRITICAL BUSINESS INSIGHTS:

1. FINANCIAL IMPACT (CURRENT MARKET):
   • Daily operational cost: ₦{economics['daily_total_with_capital']:,.0f}
   • Monthly expenditure: ₦{economics['monthly_total_with_capital']:,.0f}
   • Annual budget impact: ₦{economics['annual_total_with_capital']:,.0f}
   • 3-year total cost of ownership: ₦{economics['annual_total_with_capital']*3:,.0f}

2. COST COMPETITIVENESS ANALYSIS:
   • Generator cost per kWh: ₦{economics['cost_per_kwh_with_capital']:.0f}
   • Grid tariff benchmark: ₦110/kWh
   • Generator premium: {((economics['cost_per_kwh_with_capital']/110)-1)*100:.0f}% higher
   • Economic implication: Generator power is {economics['cost_per_kwh_with_capital']/110:.1f}x more expensive than grid

3. OPERATIONAL EFFICIENCY:
   • Average load: {economics['average_load_kw']:.1f} kW ({economics['capacity_factor_percent']:.1f}% of capacity)
   • Overall efficiency: {economics['overall_efficiency_percent']:.1f}%
   • Fuel consumption rate: {economics['daily_fuel_liters']/24:.2f} L/hour average
   • Load factor: {economics['load_factor']:.2f} (ideal > 0.5)

4. SENSITIVITY TO FUEL PRICE:
   • At ₦500/L: ₦{(df_load['Fuel_L_per_hour'].sum()*500*1.2):,.0f} daily
   • At ₦900/L (current): ₦{economics['daily_total_cost_ngn']:,.0f} daily
   • At ₦1200/L: ₦{(df_load['Fuel_L_per_hour'].sum()*1200*1.2):,.0f} daily
   • Fuel represents {economics['daily_fuel_cost_ngn']/economics['daily_total_with_capital']*100:.0f}% of total cost

5. ENVIRONMENTAL IMPACT:
   • Daily CO2 emissions: {economics['daily_fuel_liters']*2.3:.1f} kg
   • Monthly emissions: {economics['monthly_fuel_liters']*2.3/1000:.1f} tons
   • Annual emissions: {economics['annual_fuel_liters']*2.3/1000:.0f} tons CO2

RECOMMENDATIONS FOR ENERGY MANAGEMENT:

1. OPERATIONAL OPTIMIZATION:
   • Avoid generator use for low-load periods (<1 kW)
   • Schedule high-consumption activities during optimal load hours
   • Regular maintenance is critical for efficiency (20% cost impact)

2. FINANCIAL PLANNING:
   • Budget ₦{economics['monthly_total_with_capital']/1000000:.1f}M monthly for 24/7 operation
   • Consider fuel price volatility buffer of 25%
   • Account for generator replacement every 3 years

3. ALTERNATIVE ENERGY CONSIDERATION:
   • Solar PV system payback: 2-3 years at current generator costs
   • Battery storage for evening peak: 4-6 hour autonomy sufficient
   • Hybrid system (solar + minimal generator) optimal for reliability

4. POLICY IMPLICATIONS:
   • Grid reliability improvements offer immediate cost savings
   • Fuel price stabilization mechanisms reduce operational risk
   • Renewable energy incentives accelerate adoption

RISK ASSESSMENT:
• High operational risk: Fuel price volatility, maintenance requirements
• Financial risk: Capital-intensive with rapid depreciation
• Environmental risk: Significant carbon footprint
• Reliability risk: Single-point failure for power supply
"""
    
    print(findings)
    
    print("\n" + "=" * 80)
    print("PROJECT DELIVERABLES:")
    print("=" * 80)
    print("✓ generator_economics_current_market.png - Main economic dashboard")
    print("✓ generator_sensitivity_analysis.png - Fuel price sensitivity")
    print("✓ generator_hourly_analysis_detailed.csv - Hour-by-hour analysis")
    print("✓ generator_economic_summary_detailed.csv - Comprehensive metrics")
    
    print("\n" + "=" * 80)
    print("PROJECT COMPLETE")
    print("Portfolio Achievement: 'Modeled operational cost of 11kVA petrol generator at current fuel prices'")
    print("Professional Value: Demonstrates understanding of backup power economics in volatile markets")
    print("=" * 80)

# ============================================================================
# EXECUTE ANALYSIS
# ============================================================================

if __name__ == "__main__":
    main()