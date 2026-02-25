"""
DAY 19: Community Energy Dashboard
Energy System Management Portfolio

Simulate a community microgrid (100 households + community loads) with solar, diesel,
battery, and grid backup. Generate a comprehensive dashboard with:
- Real-time status panel (current load, generation, SOC, traffic lights)
- Energy mix (pie chart)
- Peak & cost panel
- Reliability panel (autonomy, outage risk)
- Emissions tracker
- Load vs generation, SOC, cost accumulation, emissions trend plots
- Automated insights (text alerts)

Outputs:
- dashboard.png (single figure with all panels)
- simulated_data.csv (7 days hourly data)
- insights.txt (automated operational insights)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from datetime import datetime, timedelta

# ============================================================================
# STEP 1 — SIMULATE MICROGRID DATA (7 days, hourly)
# ============================================================================

np.random.seed(42)
n_days = 7
hours = np.arange(24 * n_days)
time_index = pd.date_range(start='2025-01-01', periods=len(hours), freq='H')

# Community load (100 households + community loads) – scaled from Day 15
base_load_shape = np.array([
    0.3, 0.2, 0.2, 0.2, 0.2, 0.4,
    0.8, 1.0, 0.7, 0.5, 0.4, 0.4,
    0.5, 0.5, 0.5, 0.6, 0.8, 1.0,
    1.2, 1.5, 1.8, 1.5, 1.0, 0.5
])
daily_energy = 250  # kWh
load_kW = np.tile(base_load_shape, n_days) * (daily_energy / np.sum(base_load_shape))

# Add random day-to-day variation (±10%)
for d in range(n_days):
    day_factor = 1 + 0.1 * np.random.randn()
    start = d * 24
    end = (d+1) * 24
    load_kW[start:end] *= day_factor

# Solar generation (500 kWp)
solar_capacity = 500
solar_shape = np.array([
    0.0,0.0,0.0,0.0,0.0,0.0,
    0.1,0.3,0.6,0.8,0.9,1.0,
    0.95,0.85,0.7,0.5,0.2,0.05,
    0.0,0.0,0.0,0.0,0.0,0.0
])
solar_daily_kwh = solar_capacity * 5.5 * 0.75
solar_kW = np.tile(solar_shape, n_days) * (solar_daily_kwh / np.sum(solar_shape))

# Add cloud variability (±20%)
for d in range(n_days):
    cloud_factor = 1 + 0.2 * np.random.randn()
    start = d * 24
    end = (d+1) * 24
    solar_kW[start:end] *= cloud_factor
solar_kW = np.clip(solar_kW, 0, solar_capacity)

# Battery parameters
battery_capacity = 400  # kWh usable
battery_power = 200      # kW max charge/discharge
battery_efficiency = 0.92
soc_min = 0.2 * battery_capacity
soc_max = battery_capacity

# Diesel generator
diesel_capacity = 300  # kW
diesel_cost_per_kWh = 485  # ₦/kWh (from Day 2)
diesel_emissions_per_kWh = 2.14  # kg CO₂/kWh

# Grid (available, with tariff)
grid_tariff_energy = 60      # ₦/kWh
grid_tariff_demand = 8000    # ₦/kW per month (we'll pro-rate)
grid_available = True

# Initialize arrays
diesel_kW = np.zeros(len(hours))
grid_kW = np.zeros(len(hours))
soc = np.zeros(len(hours))
soc[0] = battery_capacity * 0.5
battery_discharge = np.zeros(len(hours))
battery_charge = np.zeros(len(hours))
unmet = np.zeros(len(hours))

# Simple dispatch rule:
# 1. Solar meets load first.
# 2. If deficit, battery discharges (if SOC > min) up to power limit.
# 3. If still deficit, diesel runs (if capacity available).
# 4. If still deficit, grid imports (if available).
# 5. If excess solar, charge battery (if SOC < max), else export to grid.

for t in range(len(hours)):
    load = load_kW[t]
    solar = solar_kW[t]
    
    net = load - solar  # positive deficit, negative excess
    
    if net > 0:
        # Deficit
        remaining = net
        
        # Battery discharge
        if soc[t] > soc_min:
            max_discharge = min(battery_power, (soc[t] - soc_min) / battery_efficiency)
            discharge = min(remaining, max_discharge)
            battery_discharge[t] = discharge
            remaining -= discharge
            soc[t] -= discharge / battery_efficiency
        else:
            discharge = 0
        
        # Diesel
        if remaining > 0 and diesel_capacity > 0:
            diesel = min(diesel_capacity, remaining)
            diesel_kW[t] = diesel
            remaining -= diesel
        
        # Grid import
        if remaining > 0 and grid_available:
            grid_kW[t] = remaining
            remaining = 0
        
        # Unmet (if still remaining)
        if remaining > 0:
            unmet[t] = remaining
    else:
        # Excess solar
        excess = -net
        
        # Charge battery
        if soc[t] < soc_max:
            max_charge = min(battery_power, (soc_max - soc[t]) / battery_efficiency)
            charge = min(excess, max_charge)
            battery_charge[t] = charge
            excess -= charge
            soc[t] += charge * battery_efficiency
        else:
            charge = 0
        
        # Export to grid (excess after charging)
        if excess > 0 and grid_available:
            grid_kW[t] = -excess  # negative means export
        # else curtail
    
    soc[t] = np.clip(soc[t], soc_min, soc_max)
    if t < len(hours)-1:
        soc[t+1] = soc[t]

# Compile DataFrame
df = pd.DataFrame({
    'Load_kW': load_kW,
    'Solar_kW': solar_kW,
    'Diesel_kW': diesel_kW,
    'Grid_kW': grid_kW,
    'Battery_Charge_kW': battery_charge,
    'Battery_Discharge_kW': battery_discharge,
    'SOC_kWh': soc,
    'Unmet_kW': unmet
}, index=time_index)

# Compute additional metrics
df['Total_Supply_kW'] = df['Solar_kW'] + df['Diesel_kW'] + df['Battery_Discharge_kW'] + df['Grid_kW'].clip(lower=0)
df['Renewable_Fraction'] = (df['Solar_kW'] + df['Battery_Discharge_kW']) / df['Total_Supply_kW'].replace(0, np.nan)
df['Diesel_Fraction'] = df['Diesel_kW'] / df['Total_Supply_kW'].replace(0, np.nan)
df['Grid_Import_kW'] = df['Grid_kW'].clip(lower=0)
df['Grid_Export_kW'] = -df['Grid_kW'].clip(upper=0)

# Cost and emissions
df['Diesel_Cost_NGN'] = df['Diesel_kW'] * diesel_cost_per_kWh  # hourly cost (₦)
df['Grid_Import_Cost_NGN'] = df['Grid_Import_kW'] * grid_tariff_energy
df['Total_Energy_Cost_NGN'] = df['Diesel_Cost_NGN'] + df['Grid_Import_Cost_NGN']

# Demand charge: compute monthly peak from the 7 days, then pro-rate to daily? We'll just show daily peak.
daily_peak = df.resample('D')['Load_kW'].max()
df['Daily_Peak_kW'] = df.index.floor('D').map(daily_peak)

# Emissions
df['Diesel_Emissions_kg'] = df['Diesel_kW'] * diesel_emissions_per_kWh
df['Grid_Emissions_kg'] = df['Grid_Import_kW'] * 0.85  # kg/kWh grid average
df['Total_Emissions_kg'] = df['Diesel_Emissions_kg'] + df['Grid_Emissions_kg']
df['Solar_Offset_kg'] = df['Solar_kW'] * 0.85  # avoided emissions if solar replaced grid

# Save simulated data
df.to_csv('simulated_data.csv')
print("Simulated data saved to simulated_data.csv")

# ============================================================================
# STEP 2 — BUILD DASHBOARD (single figure with multiple panels)
# ============================================================================

fig = plt.figure(figsize=(16, 12))
gs = GridSpec(4, 3, height_ratios=[1, 1.2, 1.2, 1.2], hspace=0.4, wspace=0.3)

# Helper to get last hour value
last = df.iloc[-1]

# --- Panel 1: Real-time Status (top row, spans 3 columns) ---
ax_status = fig.add_subplot(gs[0, :])
ax_status.axis('off')
status_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           REAL-TIME SYSTEM STATUS                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Current Time: {time_index[-1].strftime('%Y-%m-%d %H:%M')}                                            ║
║  ────────────────────────────────────────────────────────────────────────── ║
║  Load: {last['Load_kW']:.1f} kW        Solar: {last['Solar_kW']:.1f} kW        Diesel: {last['Diesel_kW']:.1f} kW      ║
║  Grid: {last['Grid_kW']:+.1f} kW       SOC: {last['SOC_kWh']:.0f} / {battery_capacity:.0f} kWh ({last['SOC_kWh']/battery_capacity*100:.1f}%)   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
ax_status.text(0.5, 0.5, status_text, ha='center', va='center', fontfamily='monospace', fontsize=10)

# Add traffic light indicators
traffic_x = 0.85
traffic_y = 0.7
# SOC indicator
if last['SOC_kWh'] / battery_capacity > 0.5:
    soc_color = 'green'
elif last['SOC_kWh'] / battery_capacity > 0.2:
    soc_color = 'orange'
else:
    soc_color = 'red'
ax_status.add_patch(plt.Circle((traffic_x, traffic_y), 0.02, color=soc_color, transform=ax_status.transAxes))
ax_status.text(traffic_x+0.03, traffic_y-0.01, 'SOC', transform=ax_status.transAxes, fontsize=8)

# Load relative to peak
peak_ratio = last['Load_kW'] / daily_peak.max()
if peak_ratio < 0.7:
    load_color = 'green'
elif peak_ratio < 0.9:
    load_color = 'orange'
else:
    load_color = 'red'
ax_status.add_patch(plt.Circle((traffic_x, traffic_y-0.1), 0.02, color=load_color, transform=ax_status.transAxes))
ax_status.text(traffic_x+0.03, traffic_y-0.11, 'Load', transform=ax_status.transAxes, fontsize=8)

# Diesel runtime (last 24h)
diesel_runtime = (df['Diesel_kW'].iloc[-24:] > 0).sum()
if diesel_runtime < 6:
    diesel_color = 'green'
elif diesel_runtime < 12:
    diesel_color = 'orange'
else:
    diesel_color = 'red'
ax_status.add_patch(plt.Circle((traffic_x, traffic_y-0.2), 0.02, color=diesel_color, transform=ax_status.transAxes))
ax_status.text(traffic_x+0.03, traffic_y-0.21, 'Diesel run', transform=ax_status.transAxes, fontsize=8)

# --- Panel 2: Energy Mix (pie chart) ---
ax_mix = fig.add_subplot(gs[1, 0])
last_24h = df.iloc[-24:]
total_solar = last_24h['Solar_kW'].sum()
total_diesel = last_24h['Diesel_kW'].sum()
total_grid_import = last_24h['Grid_Import_kW'].sum()
total_battery_discharge = last_24h['Battery_Discharge_kW'].sum()
total_supply = total_solar + total_diesel + total_grid_import + total_battery_discharge

if total_supply > 0:
    sizes = [total_solar, total_diesel, total_grid_import, total_battery_discharge]
    labels = ['Solar', 'Diesel', 'Grid', 'Battery']
    colors = ['gold', 'brown', 'gray', 'blue']
    ax_mix.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax_mix.set_title('Energy Mix (Last 24h)')
else:
    ax_mix.text(0.5,0.5,'No data', ha='center')

# --- Panel 3: Peak & Cost Panel ---
ax_cost = fig.add_subplot(gs[1, 1])
ax_cost.axis('off')
cost_text = f"""
PEAK & COST
───────────
Daily Peak: {daily_peak.max():.1f} kW
Load Factor: {df['Load_kW'].mean() / daily_peak.max():.3f}
Energy today: {last_24h['Load_kW'].sum():.1f} kWh
Cost today: ₦{last_24h['Total_Energy_Cost_NGN'].sum():,.0f}
Est. monthly demand charge: ₦{daily_peak.max() * grid_tariff_demand:,.0f}
"""
ax_cost.text(0.1, 0.7, cost_text, ha='left', va='top', fontfamily='monospace', fontsize=9)

# --- Panel 4: Reliability Panel ---
ax_rel = fig.add_subplot(gs[1, 2])
ax_rel.axis('off')
# Hours of autonomy based on current SOC and average load (last 24h avg)
avg_load_last24 = last_24h['Load_kW'].mean()
if avg_load_last24 > 0:
    autonomy_hours = (last['SOC_kWh'] - soc_min) / avg_load_last24
else:
    autonomy_hours = np.inf
# Outage risk: simple based on SOC and time until next solar rise (assume night)
current_hour = time_index[-1].hour
if current_hour < 6 or current_hour > 18:
    # Night, risk higher if SOC low
    risk = 'HIGH' if last['SOC_kWh'] / battery_capacity < 0.3 else 'MODERATE'
else:
    risk = 'LOW'
# Generator runtime
gen_runtime_24h = diesel_runtime
# ENS (unmet) last 24h
ens_24h = last_24h['Unmet_kW'].sum()

rel_text = f"""
RELIABILITY
───────────
Autonomy: {autonomy_hours:.1f} hours
Outage Risk: {risk}
Generator runtime (24h): {gen_runtime_24h} hours
ENS (24h): {ens_24h:.1f} kWh
"""
ax_rel.text(0.1, 0.7, rel_text, ha='left', va='top', fontfamily='monospace', fontsize=9)

# --- Panel 5: Load vs Generation (last 48h) ---
ax_load = fig.add_subplot(gs[2, :])
last48 = df.iloc[-48:]
ax_load.plot(last48.index, last48['Load_kW'], 'k-', label='Load')
ax_load.plot(last48.index, last48['Solar_kW'], 'y-', label='Solar')
ax_load.plot(last48.index, last48['Diesel_kW'], 'r-', label='Diesel')
ax_load.plot(last48.index, last48['Grid_Import_kW'], 'g-', label='Grid import')
ax_load.fill_between(last48.index, 0, last48['Battery_Discharge_kW'], color='blue', alpha=0.3, label='Battery discharge')
ax_load.set_ylabel('kW')
ax_load.set_title('Load vs Generation (Last 48h)')
ax_load.legend(loc='upper right', fontsize=8)
ax_load.grid(True, alpha=0.3)
ax_load.tick_params(axis='x', rotation=45)

# --- Panel 6: SOC over time (last 7 days) ---
ax_soc = fig.add_subplot(gs[3, 0])
ax_soc.plot(df.index, df['SOC_kWh'], 'b-', linewidth=1)
ax_soc.axhline(soc_min, color='r', linestyle='--', label='Min SOC')
ax_soc.axhline(soc_max, color='g', linestyle='--', label='Max SOC')
ax_soc.set_ylabel('SOC (kWh)')
ax_soc.set_title('Battery State of Charge')
ax_soc.grid(True, alpha=0.3)
ax_soc.legend(fontsize=8)

# --- Panel 7: Cost accumulation (last 7 days) ---
ax_cum = fig.add_subplot(gs[3, 1])
df['Cumulative_Cost'] = df['Total_Energy_Cost_NGN'].cumsum()
ax_cum.plot(df.index, df['Cumulative_Cost'] / 1e6, 'm-', linewidth=1)
ax_cum.set_ylabel('Cumulative Cost (₦ million)')
ax_cum.set_title('Energy Cost Accumulation (7 days)')
ax_cum.grid(True, alpha=0.3)

# --- Panel 8: Emissions trend (daily) ---
ax_emis = fig.add_subplot(gs[3, 2])
daily_emissions = df.resample('D')['Total_Emissions_kg'].sum() / 1000  # tonnes
daily_offset = df.resample('D')['Solar_Offset_kg'].sum() / 1000
ax_emis.bar(daily_emissions.index, daily_emissions, width=0.8, color='red', alpha=0.7, label='Actual emissions')
ax_emis.bar(daily_offset.index, -daily_offset, width=0.8, color='green', alpha=0.5, label='Solar offset')
ax_emis.set_ylabel('Tonnes CO₂')
ax_emis.set_title('Daily Emissions & Solar Offset')
ax_emis.legend(fontsize=8)
ax_emis.grid(True, alpha=0.3, axis='y')

plt.suptitle('COMMUNITY MICROGRID DASHBOARD', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('dashboard.png', dpi=150, bbox_inches='tight')
plt.show()

print("Dashboard saved to dashboard.png")

# ============================================================================
# STEP 3 — AUTOMATED INSIGHTS (text file)
# ============================================================================

# Compute insights
insights = []
# Insight 1: Battery depletion warning
if autonomy_hours < 2:
    insights.append(f"⚠️ Battery will be depleted in {autonomy_hours:.1f} hours if load remains constant.")
elif autonomy_hours < 6:
    insights.append(f"ℹ️ Battery autonomy is {autonomy_hours:.1f} hours. Monitor if solar generation is low.")

# Insight 2: Peak comparison
yesterday_peak = daily_peak.iloc[-2] if len(daily_peak) > 1 else daily_peak.iloc[-1]
today_peak = daily_peak.iloc[-1]
peak_change = (today_peak - yesterday_peak) / yesterday_peak * 100
if abs(peak_change) > 10:
    insights.append(f"📈 Peak demand changed by {peak_change:.1f}% compared to yesterday.")

# Insight 3: Diesel usage trend
diesel_last24 = last_24h['Diesel_kW'].sum()
diesel_prev24 = df.iloc[-48:-24]['Diesel_kW'].sum() if len(df) >= 48 else diesel_last24
if diesel_prev24 > 0:
    diesel_change = (diesel_last24 - diesel_prev24) / diesel_prev24 * 100
    if diesel_change > 20:
        insights.append(f"🛢️ Diesel usage increased by {diesel_change:.1f}% in the last 24h. Check solar generation.")
    elif diesel_change < -20:
        insights.append(f"✅ Diesel usage decreased by {diesel_change:.1f}% in the last 24h. Good solar performance.")

# Insight 4: Renewable fraction
ren_frac_last24 = last_24h['Renewable_Fraction'].mean()
if ren_frac_last24 < 0.3:
    insights.append(f"☀️ Renewable fraction is low ({ren_frac_last24*100:.1f}%). Consider reducing load or increasing solar.")
elif ren_frac_last24 > 0.8:
    insights.append(f"🌱 High renewable fraction ({ren_frac_last24*100:.1f}%). Great!")

# Insight 5: Outage risk
if risk == 'HIGH':
    insights.append("🔴 High outage risk. Prepare backup or reduce non-essential loads.")
elif risk == 'MODERATE':
    insights.append("🟡 Moderate outage risk. Monitor SOC and solar forecast.")

# Insight 6: Emissions saved
total_offset = df['Solar_Offset_kg'].sum() / 1000  # tonnes
insights.append(f"🌍 Total CO₂ avoided by solar in 7 days: {total_offset:.1f} tonnes.")

# Write insights to file
with open('insights.txt', 'w', encoding='utf-8') as f:
    f.write("AUTOMATED OPERATIONAL INSIGHTS\n")
    f.write("==============================\n\n")
    for insight in insights:
        f.write(insight + "\n")
    f.write("\n\nGenerated on: " + datetime.now().strftime('%Y-%m-%d %H:%M'))
print("Insights saved to insights.txt")

# ============================================================================
# STEP 4 — DOCUMENTATION (summary text)
# ============================================================================

doc_text = """
COMMUNITY ENERGY DASHBOARD – USER GUIDE
========================================

This dashboard provides real-time and historical insights for a microgrid serving
100 households plus community loads (clinic, school, market). The system includes:
- 500 kWp solar PV
- 300 kW diesel generator (backup)
- 400 kWh battery (usable)
- Grid connection (optional import/export)

Data is simulated at hourly resolution for 7 days but can be replaced with real data.

Dashboard Panels:
1. Real-Time Status: Current load, solar, diesel, grid flow, battery SOC, with traffic light indicators.
2. Energy Mix: Last 24h generation breakdown (pie chart).
3. Peak & Cost: Daily peak, load factor, energy consumed, estimated cost, and demand charge.
4. Reliability: Hours of autonomy, outage risk, generator runtime, energy not supplied (ENS).
5. Load vs Generation: Last 48h time series of load, solar, diesel, grid, battery discharge.
6. Battery SOC: Full history.
7. Cost Accumulation: Cumulative energy cost over the period.
8. Emissions Trend: Daily actual emissions and solar offset.

Automated Insights (in insights.txt) provide actionable alerts:
- Battery depletion warnings
- Peak demand changes
- Diesel usage trends
- Renewable fraction
- Outage risk
- Emissions saved

How this helps operators:
- Quickly identify if the system is under stress.
- Plan maintenance or load shifting based on trends.
- Monitor cost and environmental performance.
- Receive early warnings before outages occur.

Data Source: Simulated using Day 15 microgrid parameters with realistic variability.
"""

with open('recommendations.txt', 'w', encoding='utf-8') as f:    f.write(doc_text)
print("Documentation saved to dashboard_description.txt")

print("\n=== DAY 19 COMPLETE ===")