# ============================================================================
# DAY 1: HOUSEHOLD LOAD PROFILE - NIGERIAN HOUSEHOLD
# Energy System Manager Portfolio Project
# ============================================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime

# ============================================================================
# 1. DATA DEFINITION
# ============================================================================

# Nigerian household load profile (kW) - 24 hours
hours = list(range(24))

# Load values in kW (from our analysis)
load_kw = [
    0.4, 0.4, 0.4, 0.4, 0.4,      # 12AM-4AM: Sleeping
    1.8, 2.5, 1.2, 0.6, 0.5,      # 5AM-9AM: Morning activities
    0.5, 0.5, 1.5, 1.0, 0.7,      # 10AM-2PM: Midday
    0.6, 1.3, 1.0, 2.2, 2.5,      # 3PM-7PM: Evening (with generator)
    2.0, 1.8, 1.2, 0.5            # 8PM-11PM: Night
]

# Grid status (1 = Grid available, 0 = Grid down, generator used)
grid_status = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1]

# Appliance breakdown for peak hours (for additional insight)
appliances = {
    'Morning Peak (6AM)': {'Iron': 1.2, 'Water Heater': 1.0, 'Lighting': 0.3},
    'Evening Peak (7PM)': {'Refrigerator': 0.2, 'Lighting': 0.5, 'TV': 0.3, 
                          'Fans (x4)': 0.3, 'AC (1 unit)': 1.2}
}

# ============================================================================
# 2. ENERGY CALCULATIONS
# ============================================================================

# Create DataFrame for analysis
df = pd.DataFrame({
    'Hour': hours,
    'Load_kW': load_kw,
    'Grid_Status': grid_status,
    'Hour_Label': [f'{h:02d}:00' for h in hours]
})

# Calculate energy consumption
df['Energy_kWh'] = df['Load_kW']  # For hourly, energy = power × 1 hour

# Separate grid and generator energy
grid_energy = df[df['Grid_Status'] == 1]['Energy_kWh'].sum()
generator_energy = df[df['Grid_Status'] == 0]['Energy_kWh'].sum()
total_energy = grid_energy + generator_energy

# Calculate metrics
peak_load = df['Load_kW'].max()
load_factor = total_energy / (peak_load * 24)
generator_hours = len(df[df['Grid_Status'] == 0])

# ============================================================================
# 3. VISUALIZATIONS
# ============================================================================

# Set style for professional plots
plt.style.use('seaborn-v0_8-darkgrid')
mpl.rcParams['font.size'] = 10
mpl.rcParams['axes.titlesize'] = 14
mpl.rcParams['axes.labelsize'] = 12

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Day 1: Nigerian Household Load Analysis\nEnergy System Manager Portfolio', 
             fontsize=16, fontweight='bold', y=1.02)

# ----------------------------------------------------------------------------
# Plot 1: Main Load Curve
# ----------------------------------------------------------------------------
ax1 = axes[0, 0]
bars = ax1.bar(df['Hour'], df['Load_kW'], 
               color=['#2E86AB' if status == 1 else '#A23B72' for status in grid_status],
               edgecolor='white', linewidth=0.5)

ax1.set_xlabel('Hour of Day')
ax1.set_ylabel('Load (kW)')
ax1.set_title('Hourly Load Profile with Grid/Generator Status', pad=15)
ax1.set_xticks(range(0, 24, 3))
ax1.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 3)])
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 3.0)

# Add annotations for peaks
ax1.annotate('Morning Peak\n(6AM: 2.5 kW)', xy=(6, 2.5), xytext=(8, 2.7),
             arrowprops=dict(arrowstyle='->', color='darkred'), color='darkred')
ax1.annotate('Evening Peak\n(7PM: 2.5 kW)', xy=(19, 2.5), xytext=(15, 2.7),
             arrowprops=dict(arrowstyle='->', color='darkred'), color='darkred')

# Add legend for grid/generator
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#2E86AB', label='Grid Supply'),
                   Patch(facecolor='#A23B72', label='Generator Supply')]
ax1.legend(handles=legend_elements, loc='upper right')

# ----------------------------------------------------------------------------
# Plot 2: Energy Distribution Pie Chart
# ----------------------------------------------------------------------------
ax2 = axes[0, 1]
energy_sources = ['Grid Supply', 'Generator Supply']
energy_values = [grid_energy, generator_energy]
colors = ['#2E86AB', '#A23B72']
explode = (0, 0.1)

wedges, texts, autotexts = ax2.pie(energy_values, explode=explode, colors=colors,
                                    autopct='%1.1f%%', startangle=90,
                                    textprops={'color': 'white', 'fontweight': 'bold'})

ax2.set_title(f'Daily Energy Distribution\nTotal: {total_energy:.1f} kWh', pad=15)
ax2.legend(wedges, [f'{label}: {val:.1f} kWh' for label, val in zip(energy_sources, energy_values)],
           loc='center left', bbox_to_anchor=(0.9, 0, 0.5, 1))

# ----------------------------------------------------------------------------
# Plot 3: Load Duration Curve
# ----------------------------------------------------------------------------
ax3 = axes[1, 0]
sorted_load = np.sort(df['Load_kW'])[::-1]  # Descending
ax3.plot(range(1, 25), sorted_load, 'o-', color='#2E86AB', linewidth=2, markersize=4)
ax3.fill_between(range(1, 25), sorted_load, alpha=0.2, color='#2E86AB')

ax3.set_xlabel('Hours (sorted by load)')
ax3.set_ylabel('Load (kW)')
ax3.set_title('Load Duration Curve', pad=15)
ax3.grid(True, alpha=0.3)
ax3.set_xticks(range(1, 25, 3))

# Add horizontal line for average load
avg_load = total_energy / 24
ax3.axhline(y=avg_load, color='red', linestyle='--', alpha=0.7, label=f'Avg: {avg_load:.2f} kW')
ax3.legend()

# ----------------------------------------------------------------------------
# Plot 4: Key Metrics Summary
# ----------------------------------------------------------------------------
ax4 = axes[1, 1]
ax4.axis('off')  # Turn off axis for text display

# Create summary text
summary_text = f"""
DAILY ENERGY SUMMARY
{'-' * 30}

Total Energy Consumption: {total_energy:.1f} kWh
• Grid Supply: {grid_energy:.1f} kWh ({grid_energy/total_energy*100:.1f}%)
• Generator Supply: {generator_energy:.1f} kWh ({generator_energy/total_energy*100:.1f}%)

Peak Load: {peak_load:.1f} kW
Load Factor: {load_factor:.2f}

Generator Usage: {generator_hours} hours/day
Fuel Cost Estimate*: ₦{generator_energy * 150:.0f} daily
(Assuming 1kWh = ₦150 for diesel generator)

Grid Reliability: {(24-generator_hours)/24*100:.1f}% uptime

*Typical Lagos diesel cost: ₦800/liter, ~0.3 liters/kWh
"""

ax4.text(0.1, 0.95, summary_text, fontfamily='monospace', fontsize=11,
         verticalalignment='top', linespacing=1.5)

# Add footer note
fig.text(0.5, 0.01, 'Energy System Manager Portfolio • Day 1: Household Load Reality • Data: Typical Nigerian urban household',
         ha='center', fontsize=9, style='italic', alpha=0.7)

# Adjust layout and save
plt.tight_layout()
plt.savefig('Nigerian_Household_Load_Profile.png', dpi=300, bbox_inches='tight')
plt.show()

# ============================================================================
# 4. DATA EXPORT AND ADDITIONAL ANALYSIS
# ============================================================================

print("=" * 70)
print("DAY 1: HOUSEHOLD LOAD PROFILE - ANALYSIS COMPLETE")
print("=" * 70)

# Export data to CSV
df.to_csv('household_load_profile_data.csv', index=False)
print(f"✓ Data exported to 'household_load_profile_data.csv'")
print(f"✓ Visualization saved as 'Nigerian_Household_Load_Profile.png'")

# Print key findings
print("\n" + "=" * 70)
print("KEY FINDINGS")
print("=" * 70)
print(f"1. Daily Consumption: {total_energy:.1f} kWh")
print(f"2. Generator Dependency: {generator_energy/total_energy*100:.1f}% of total energy")
print(f"3. Peak Demand: {peak_load} kW (occurs at 6AM and 7PM)")
print(f"4. Load Factor: {load_factor:.3f} (ideal > 0.5)")
print(f"5. Grid Reliability: Only {(24-generator_hours)} hours of stable supply")

# Cost implications
print(f"\nCOST IMPLICATIONS (Approximate):")
print(f"• Monthly Grid Cost: ₦{grid_energy * 30 * 50:.0f} (₦50/kWh)")
print(f"• Monthly Generator Cost: ₦{generator_energy * 30 * 150:.0f} (₦150/kWh)")
print(f"• Total Monthly Energy Cost: ₦{(grid_energy*50 + generator_energy*150)*30:.0f}")

# Recommendations
print("\nRECOMMENDATIONS:")
print("1. Consider solar PV with battery storage for evening peak")
print("2. Load shifting: Move ironing to midday when grid is stable")
print("3. Energy efficiency: Replace incandescent bulbs with LEDs")
print("4. Power management: Use timer for water heater")