"""
DAY 1: ABUJA HOUSEHOLD LOAD PROFILE
Energy System Manager Portfolio Project
Based on actual appliance data for 5-person household
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime, timedelta
import seaborn as sns

# ============================================================================
# 1. LOAD AND PROCESS APPLIANCE DATA
# ============================================================================

def load_appliance_data():
    """Load and process appliance data from CSV"""
    # Create appliance data based on your input
    appliance_data = {
        'Appliance': ['Refrigerator', 'Split_AC_Living', 'Split_AC_Bedroom1', 
                     'Split_AC_Bedroom2', 'Ceiling_Fan', 'LED_TV', 'Laptop',
                     'Desktop_PC', 'Smartphones', 'Router_Modem', 'Microwave',
                     'Electric_Iron', 'Water_Heater', 'Washing_Machine',
                     'Lighting_LED', 'Blender'],
        'Quantity': [1, 1, 1, 1, 4, 2, 3, 1, 5, 1, 1, 1, 1, 1, 10, 1],
        'Power_W': [150, 1500, 1200, 1200, 60, 80, 60, 150, 10, 10, 1000, 
                   1200, 3000, 500, 10, 300],
        'Daily_Hours': [24, 5, 4, 4, 10, 5, 6, 3, 3, 24, 0.5, 0.5, 0.5, 
                       0.14, 6, 0.5],
        'Usage_Pattern': ['24/7 cycling', 'Evenings 19-23', 'Night 22-02', 
                         'Night 22-02', 'Day & evening', 'Evening 19-22',
                         'Day & night', 'Afternoon', 'Morning & night',
                         '24/7', 'Morning & evening', 'Morning', 'Morning',
                         'Weekly avg', 'Evening', 'Morning']
    }
    
    df = pd.DataFrame(appliance_data)
    df['Daily_Energy_Wh'] = df['Quantity'] * df['Power_W'] * df['Daily_Hours']
    df['Power_kW'] = df['Quantity'] * df['Power_W'] / 1000
    
    total_energy = df['Daily_Energy_Wh'].sum()
    print(f"✓ Total Daily Energy: {total_energy/1000:.2f} kWh")
    
    return df

# ============================================================================
# 2. CREATE HOURLY LOAD PROFILE BASED ON BEHAVIORAL PATTERNS
# ============================================================================

def create_hourly_profile():
    """Create realistic hourly load profile for Abuja household"""
    
    hours = list(range(24))
    hour_labels = [f"{h:02d}:00" for h in hours]
    
    # Base load (always on: fridge, router)
    base_load = 0.16  # kW (160W: fridge + router)
    
    # Initialize hourly load array
    hourly_load = [base_load] * 24
    
    # Define activity patterns (in kW)
    # Format: {hour: additional_load, description}
    activity_patterns = {
        # Night (00:00-06:00): Sleeping, fans on
        0: 0.24,   # 4 fans @ 60W = 240W
        1: 0.24,
        2: 0.24,
        3: 0.24,
        4: 0.24,
        5: 0.24,
        
        # Morning peak (06:00-08:00): Water heater, iron, microwave, blender
        6: 4.3,    # Water heater (3kW) + iron (1.2kW) + base
        7: 1.3,    # Microwave (1kW) + blender (0.3kW) + base
        
        # Daytime (08:00-16:00): Laptops, fans, occasional AC
        8: 0.6,    # Laptops + fans
        9: 0.7,
        10: 0.7,
        11: 0.8,
        12: 1.2,   # Lunch prep + AC sometimes
        13: 1.5,   # Afternoon AC (living room)
        14: 1.5,
        15: 1.5,
        
        # Evening rise (16:00-19:00): Return from school/work
        16: 1.8,   # TV, laptops, fans
        17: 2.0,
        18: 2.5,   # Cooking, TV, lights
        
        # Evening peak (19:00-23:00): ACs, TV, lights, laptops
        19: 3.8,   # Living AC + TV + lights
        20: 4.0,   # Living AC + bedroom AC starting
        21: 3.5,   # Both bedroom ACs + fans
        22: 3.2,   # Bedroom ACs + laptops
        
        # Late night (23:00-24:00): Wind down
        23: 0.6    # Fans only
    }
    
    # Apply activity patterns
    for hour, load in activity_patterns.items():
        hourly_load[hour] = load
    
    # Add AC patterns (based on Abuja climate)
    # Evening AC (19:00-23:00): Living room AC
    for h in range(19, 23):
        hourly_load[h] += 1.0  # Living room AC
    
    # Night AC (22:00-02:00): Bedroom ACs
    for h in [22, 23, 0, 1]:
        if h < 24:
            hourly_load[h] += 1.8  # Two bedroom ACs
    
    # Create DataFrame
    df_hourly = pd.DataFrame({
        'Hour': hours,
        'Hour_Label': hour_labels,
        'Load_kW': hourly_load,
        'Load_kWh': hourly_load  # For 1-hour intervals, kWh = kW
    })
    
    # Add time-of-day categories
    df_hourly['Time_Of_Day'] = pd.cut(df_hourly['Hour'], 
                                       bins=[-1, 6, 12, 18, 24],
                                       labels=['Night', 'Morning', 'Afternoon', 'Evening'])
    
    return df_hourly

# ============================================================================
# 3. GRID RELIABILITY AND GENERATOR USAGE
# ============================================================================

def add_grid_simulation(df_hourly):
    """Simulate grid outages and generator usage"""
    
    # Abuja typical outage pattern (based on your input)
    # 0 = Grid available, 1 = Grid down
    grid_pattern = {
        0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1,  # Night outages common
        6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0,  # Morning usually stable
        12: 1, 13: 1, 14: 0, 15: 0, 16: 0, 17: 0,  # Afternoon outages
        18: 0, 19: 1, 20: 1, 21: 1, 22: 1, 23: 0   # Evening outages
    }
    
    df_hourly['Grid_Available'] = df_hourly['Hour'].map(grid_pattern)
    df_hourly['Grid_Available'] = 1 - df_hourly['Grid_Available']  # Invert: 1=available
    
    # Generator runs when grid is down AND load > 0.5 kW
    df_hourly['Generator_Used'] = ((df_hourly['Grid_Available'] == 0) & 
                                   (df_hourly['Load_kW'] > 0.5)).astype(int)
    
    # Calculate energy sources
    df_hourly['Energy_Grid_kWh'] = df_hourly.apply(
        lambda x: x['Load_kWh'] if x['Grid_Available'] == 1 else 0, axis=1)
    
    df_hourly['Energy_Generator_kWh'] = df_hourly.apply(
        lambda x: x['Load_kWh'] if x['Generator_Used'] == 1 else 0, axis=1)
    
    # Some hours might have no power if grid is down and generator not used
    df_hourly['Energy_Unserved_kWh'] = df_hourly.apply(
        lambda x: x['Load_kWh'] if (x['Grid_Available'] == 0 and 
                                    x['Generator_Used'] == 0) else 0, axis=1)
    
    return df_hourly

# ============================================================================
# 4. CALCULATE METRICS AND COSTS
# ============================================================================

def calculate_metrics(df_hourly, df_appliances):
    """Calculate key energy metrics and costs"""
    
    total_energy = df_hourly['Load_kWh'].sum()
    peak_load = df_hourly['Load_kW'].max()
    avg_load = df_hourly['Load_kW'].mean()
    load_factor = avg_load / peak_load
    
    grid_energy = df_hourly['Energy_Grid_kWh'].sum()
    generator_energy = df_hourly['Energy_Generator_kWh'].sum()
    unserved_energy = df_hourly['Energy_Unserved_kWh'].sum()
    
    # Abuja-specific costs (NGN)
    grid_tariff = 100  # NGN/kWh (average ₦90-₦110)
    generator_cost_per_kwh = 150  # NGN/kWh (diesel)
    
    grid_cost = grid_energy * grid_tariff
    generator_cost = generator_energy * generator_cost_per_kwh
    total_daily_cost = grid_cost + generator_cost
    
    # Appliance-level insights
    top_appliances = df_appliances.nlargest(5, 'Daily_Energy_Wh')[['Appliance', 'Daily_Energy_Wh']]
    
    metrics = {
        'total_energy_kwh': total_energy,
        'peak_load_kw': peak_load,
        'avg_load_kw': avg_load,
        'load_factor': load_factor,
        'grid_energy_kwh': grid_energy,
        'generator_energy_kwh': generator_energy,
        'unserved_energy_kwh': unserved_energy,
        'grid_reliability_percent': (grid_energy / total_energy) * 100,
        'daily_grid_cost_ngn': grid_cost,
        'daily_generator_cost_ngn': generator_cost,
        'total_daily_cost_ngn': total_daily_cost,
        'top_appliances': top_appliances
    }
    
    return metrics

# ============================================================================
# 5. VISUALIZATION FUNCTIONS
# ============================================================================

def create_visualizations(df_hourly, df_appliances, metrics):
    """Create comprehensive visualizations"""
    
    plt.style.use('seaborn-v0_8-darkgrid')
    mpl.rcParams['font.size'] = 10
    mpl.rcParams['axes.titlesize'] = 14
    
    # Figure 1: Main load profile
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Load curve with grid status
    colors = ['#2E86AB' if g == 1 else '#A23B72' for g in df_hourly['Grid_Available']]
    bars = ax1.bar(df_hourly['Hour_Label'], df_hourly['Load_kW'], color=colors, edgecolor='white')
    ax1.set_title('Abuja Household: 24-Hour Load Profile', fontweight='bold', pad=15)
    ax1.set_xlabel('Hour of Day')
    ax1.set_ylabel('Load (kW)')
    ax1.set_xticks(df_hourly['Hour_Label'][::2])
    ax1.grid(True, alpha=0.3)
    
    # Add annotations for peaks
    peak_hour = df_hourly.loc[df_hourly['Load_kW'].idxmax(), 'Hour_Label']
    ax1.annotate(f'Peak: {metrics["peak_load_kw"]:.1f} kW\n({peak_hour})', 
                xy=(df_hourly['Load_kW'].idxmax(), metrics["peak_load_kw"]),
                xytext=(10, metrics["peak_load_kw"] * 0.8),
                arrowprops=dict(arrowstyle='->', color='darkred'),
                fontweight='bold')
    
    # Energy source breakdown
    sources = ['Grid', 'Generator', 'Unserved']
    energy_values = [metrics['grid_energy_kwh'], 
                     metrics['generator_energy_kwh'], 
                     metrics['unserved_energy_kwh']]
    colors_source = ['#2E86AB', '#A23B72', '#8B8B8B']
    
    ax2.pie(energy_values, labels=sources, colors=colors_source, autopct='%1.1f%%',
            startangle=90, textprops={'fontweight': 'bold'})
    ax2.set_title(f'Energy Source Distribution\nTotal: {metrics["total_energy_kwh"]:.1f} kWh', pad=15)
    
    plt.tight_layout()
    plt.savefig('abuja_load_profile_main.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Figure 2: Appliance analysis
    fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Top energy-consuming appliances
    top_5 = df_appliances.nlargest(5, 'Daily_Energy_Wh')
    ax3.barh(top_5['Appliance'], top_5['Daily_Energy_Wh'] / 1000, color='#2E86AB')
    ax3.set_xlabel('Daily Energy (kWh)')
    ax3.set_title('Top 5 Energy-Consuming Appliances', pad=15)
    ax3.invert_yaxis()
    
    # Load duration curve
    sorted_load = np.sort(df_hourly['Load_kW'])[::-1]
    ax4.plot(range(1, 25), sorted_load, 'o-', color='#2E86AB', linewidth=2)
    ax4.fill_between(range(1, 25), sorted_load, alpha=0.2, color='#2E86AB')
    ax4.axhline(y=metrics['avg_load_kw'], color='red', linestyle='--', 
                label=f'Avg: {metrics["avg_load_kw"]:.2f} kW')
    ax4.set_xlabel('Hours (sorted)')
    ax4.set_ylabel('Load (kW)')
    ax4.set_title('Load Duration Curve', pad=15)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('abuja_appliance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Figure 3: Cost analysis
    fig3, ax5 = plt.subplots(figsize=(10, 6))
    
    cost_categories = ['Grid Energy', 'Generator Energy']
    costs = [metrics['daily_grid_cost_ngn'], metrics['daily_generator_cost_ngn']]
    
    bars = ax5.bar(cost_categories, costs, color=['#2E86AB', '#A23B72'])
    ax5.set_ylabel('Cost (₦)')
    ax5.set_title('Daily Energy Costs - Abuja Household', pad=15)
    ax5.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, cost in zip(bars, costs):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 100,
                f'₦{cost:,.0f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('abuja_energy_costs.png', dpi=300, bbox_inches='tight')
    plt.show()

# ============================================================================
# 6. MAIN ANALYSIS FUNCTION
# ============================================================================

def main():
    """Main analysis function"""
    
    print("=" * 70)
    print("DAY 1: ABUJA HOUSEHOLD LOAD PROFILE ANALYSIS")
    print("=" * 70)
    
    # Load appliance data
    print("\n📊 Loading appliance data...")
    df_appliances = load_appliance_data()
    
    # Create hourly profile
    print("📈 Creating hourly load profile...")
    df_hourly = create_hourly_profile()
    
    # Add grid reliability simulation
    print("⚡ Simulating grid reliability...")
    df_hourly = add_grid_simulation(df_hourly)
    
    # Calculate metrics
    print("🧮 Calculating energy metrics...")
    metrics = calculate_metrics(df_hourly, df_appliances)
    
    # Save data to CSV
    print("💾 Saving data files...")
    df_appliances.to_csv('abuja_appliance_data.csv', index=False)
    df_hourly.to_csv('abuja_hourly_load_profile.csv', index=False)
    
    # Create visualizations
    print("🎨 Generating visualizations...")
    create_visualizations(df_hourly, df_appliances, metrics)
    
    # Print summary report
    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    
    summary = f"""
🏠 HOUSEHOLD PROFILE:
• Location: Abuja, Nigeria
• Occupants: 5 (2 parents, 3 children)
• Type: 3-bedroom apartment
• Lifestyle: Middle-class with AC usage

📊 ENERGY METRICS:
• Total Daily Energy: {metrics['total_energy_kwh']:.1f} kWh
• Peak Load: {metrics['peak_load_kw']:.1f} kW
• Average Load: {metrics['avg_load_kw']:.1f} kW
• Load Factor: {metrics['load_factor']:.2f}

⚡ ENERGY SOURCES:
• Grid Supply: {metrics['grid_energy_kwh']:.1f} kWh ({metrics['grid_reliability_percent']:.1f}%)
• Generator Supply: {metrics['generator_energy_kwh']:.1f} kWh
• Unserved Energy: {metrics['unserved_energy_kwh']:.1f} kWh

💰 DAILY COSTS (₦):
• Grid Energy: ₦{metrics['daily_grid_cost_ngn']:,.0f}
• Generator Energy: ₦{metrics['daily_generator_cost_ngn']:,.0f}
• Total Daily Cost: ₦{metrics['total_daily_cost_ngn']:,.0f}
• Monthly Estimate (30 days): ₦{metrics['total_daily_cost_ngn'] * 30:,.0f}

🔧 TOP ENERGY CONSUMERS:
"""
    print(summary)
    
    for idx, row in metrics['top_appliances'].iterrows():
        print(f"  {row['Appliance']}: {row['Daily_Energy_Wh']/1000:.1f} kWh/day")
    
    print("\n" + "=" * 70)
    print("KEY INSIGHTS FOR ENERGY SYSTEM MANAGER")
    print("=" * 70)
    
    insights = """
1. HIGH GENERATOR DEPENDENCY: {:.1f}% of energy comes from generator
   → Opportunity for solar + battery investment

2. EVENING PEAK COINCIDES WITH GRID OUTAGES:
   • Peak demand: {:.1f} kW at {}
   • Grid often unavailable during this period
   → Battery storage can provide 4-5 hours of backup

3. AC ACCOUNTS FOR MAJORITY OF LOAD:
   • Cooling represents ~60% of total energy
   → Consider energy-efficient AC units
   → Explore solar-powered DC mini-split systems

4. MONTHLY ENERGY COST: ₦{:,}
   → Solar ROI possible within 2-3 years
   → Load management could save 20-30%

5. LOAD FACTOR: {:.2f} (Ideal > 0.5)
   → Opportunity for load shifting
   → Consider time-of-use incentives
""".format(
        (metrics['generator_energy_kwh'] / metrics['total_energy_kwh']) * 100,
        metrics['peak_load_kw'],
        df_hourly.loc[df_hourly['Load_kW'].idxmax(), 'Hour_Label'],
        int(metrics['total_daily_cost_ngn'] * 30),
        metrics['load_factor']
    )
    
    print(insights)
    
    print("\n" + "=" * 70)
    print("FILES GENERATED:")
    print("=" * 70)
    print("✓ abuja_appliance_data.csv - Appliance specifications and usage")
    print("✓ abuja_hourly_load_profile.csv - 24-hour load curve")
    print("✓ abuja_load_profile_main.png - Main visualization")
    print("✓ abuja_appliance_analysis.png - Appliance and duration analysis")
    print("✓ abuja_energy_costs.png - Cost breakdown")
    print("\n✅ ANALYSIS COMPLETE - Ready for GitHub portfolio!")

# ============================================================================
# EXECUTE ANALYSIS
# ============================================================================

if __name__ == "__main__":
    main()