"""
DAY 16: Peak Shaving & Demand Response
Energy System Management Portfolio

Objective: Use real-world load data (synthetic but realistic commercial building)
to design curtailment and battery-based peak shaving strategies, quantify savings,
and provide a technical recommendation.

Outputs:
- original_load_profile.png
- dr_curtailment_profile.png
- battery_shaving_profile.png
- comparison_table.csv
- recommendations.txt
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================================
# STEP 1 — GENERATE REALISTIC COMMERCIAL BUILDING LOAD DATA (1 week, hourly)
# ============================================================================

np.random.seed(42)
hours_in_week = 24 * 7
time_index = pd.date_range(start='2025-01-01', periods=hours_in_week, freq='H')

# Base load pattern: weekday vs weekend
# Weekday: office hours 8-18 high, evening moderate, night low
# Weekend: lower overall

def commercial_load_pattern(hour_of_day, is_weekday):
    """
    Returns a normalized load factor for a given hour and weekday/weekend.
    """
    if is_weekday:
        # Weekday profile
        if 8 <= hour_of_day < 18:
            # Business hours
            return 0.9 + 0.2 * np.sin((hour_of_day - 8) * np.pi / 10)  # peak around noon
        elif 18 <= hour_of_day < 22:
            # Evening
            return 0.5 + 0.1 * np.random.random()
        else:
            # Night
            return 0.2 + 0.1 * np.random.random()
    else:
        # Weekend
        if 10 <= hour_of_day < 20:
            # Some activity
            return 0.4 + 0.2 * np.random.random()
        else:
            # Low
            return 0.15 + 0.1 * np.random.random()

# Generate hourly load (kW) for a medium commercial building (baseline 500 kW peak)
base_peak = 500  # kW
load = np.zeros(hours_in_week)

for i, ts in enumerate(time_index):
    hour = ts.hour
    weekday = ts.weekday() < 5  # Monday=0, Friday=4
    factor = commercial_load_pattern(hour, weekday)
    # Add some random variation
    noise = np.random.normal(1.0, 0.05)
    load[i] = base_peak * factor * noise

# Ensure no negative
load = np.maximum(load, 10)

# Convert to DataFrame
df = pd.DataFrame({'load_kW': load}, index=time_index)

print("=== ORIGINAL LOAD PROFILE (1 WEEK) ===")
print(f"Peak load: {df['load_kW'].max():.1f} kW")
print(f"Average load: {df['load_kW'].mean():.1f} kW")
load_factor = df['load_kW'].mean() / df['load_kW'].max()
print(f"Load factor: {load_factor:.3f}")

# ============================================================================
# STEP 2 — TARIFF ASSUMPTIONS
# ============================================================================

energy_rate = 60      # ₦/kWh
demand_charge = 8000  # ₦/kW per month (based on peak demand)

# Calculate monthly cost for this week (we'll assume this week is representative)
# For simplicity, we treat this week as a full month for comparison.
# In reality, demand charge is based on the peak of the billing month.

original_peak = df['load_kW'].max()
original_energy = df['load_kW'].sum()
original_energy_cost = original_energy * energy_rate
original_demand_cost = original_peak * demand_charge
original_total_cost = original_energy_cost + original_demand_cost

print("\n=== ORIGINAL COSTS (WEEKLY, but demand charge applied as monthly) ===")
print(f"Energy consumption: {original_energy:.0f} kWh → ₦{original_energy_cost:,.0f}")
print(f"Peak demand: {original_peak:.1f} kW → ₦{original_demand_cost:,.0f}")
print(f"Total weekly cost: ₦{original_total_cost:,.0f}")
print(f"(If extrapolated to month: ~₦{original_total_cost*4:,.0f})")

# ============================================================================
# STEP 3 — IDENTIFY PEAK HOURS
# ============================================================================

# Find daily peaks and top 3 peak hours overall
daily_peaks = df.resample('D').max()
top_peak_hours = df.nlargest(3, 'load_kW').index
print("\nTop 3 peak hours:")
for ts in top_peak_hours:
    print(f"  {ts}: {df.loc[ts, 'load_kW']:.1f} kW")

# ============================================================================
# STEP 4 — STRATEGY A: LOAD CURTAILMENT
# ============================================================================

# Assume we can reduce load by 15% during the top 3 peak hours each day.
# For simplicity, we'll curtail the top 3 hours of each day.

df_curtail = df.copy()
daily_curtailed_energy = 0

for day, day_data in df.resample('D'):
    if len(day_data) == 0:
        continue
    # Get indices of top 3 load hours in this day
    top3_idx = day_data.nlargest(3, 'load_kW').index
    reduction_factor = 0.15  # 15% reduction
    for idx in top3_idx:
        original = df_curtail.loc[idx, 'load_kW']
        df_curtail.loc[idx, 'load_kW'] = original * (1 - reduction_factor)
        daily_curtailed_energy += original * reduction_factor

curtail_peak = df_curtail['load_kW'].max()
curtail_energy = df_curtail['load_kW'].sum()
curtail_energy_cost = curtail_energy * energy_rate
curtail_demand_cost = curtail_peak * demand_charge
curtail_total_cost = curtail_energy_cost + curtail_demand_cost

print("\n=== STRATEGY A: CURTAILMENT (15% reduction during top 3 daily peak hours) ===")
print(f"New peak: {curtail_peak:.1f} kW (reduction {original_peak - curtail_peak:.1f} kW)")
print(f"Energy consumed: {curtail_energy:.0f} kWh")
print(f"Energy cost: ₦{curtail_energy_cost:,.0f}")
print(f"Demand cost: ₦{curtail_demand_cost:,.0f}")
print(f"Total weekly cost: ₦{curtail_total_cost:,.0f}")
print(f"Savings: ₦{original_total_cost - curtail_total_cost:,.0f}")

# ============================================================================
# STEP 5 — STRATEGY B: BATTERY STORAGE PEAK SHAVING
# ============================================================================

# Target peak reduction: aim for 15% peak reduction (same as curtailment for comparison)
target_peak = original_peak * 0.85  # kW

# We need to size a battery to discharge during peak hours to keep load ≤ target_peak.
# Simplistic sizing: find the worst day where the load exceeds target_peak, and integrate excess.

# Determine discharge window: assume we can discharge from 8am to 8pm? But we need to pick the peak period.
# Let's identify the daily periods where load > target_peak. We'll simulate battery operation with a given capacity.

def size_battery_for_peak_shaving(load_series, target_peak, discharge_hours, efficiency=0.92, dod=0.8):
    """
    Determine required battery capacity (kWh) to keep load ≤ target_peak during discharge_hours.
    """
    # Convert target_peak to a series
    excess = load_series - target_peak
    excess = np.maximum(excess, 0)
    # Sum excess during discharge hours
    total_excess = 0
    max_daily_excess = 0
    for day, day_data in excess.resample('D'):
        # Only consider discharge hours
        day_excess = day_data.between_time(f'{discharge_hours[0]:02d}:00', f'{discharge_hours[1]:02d}:00').sum()
        total_excess += day_excess
        if day_excess > max_daily_excess:
            max_daily_excess = day_excess
    # Required battery capacity (account for DoD and efficiency)
    # The battery must supply the excess during discharge, but charging happens earlier.
    # For sizing, we need to cover the maximum daily excess, accounting for round-trip efficiency and DoD.
    # The energy discharged = excess, so stored energy needed = excess / efficiency (discharge) but we charge with same efficiency? Round-trip matters.
    # Actually, if we discharge at efficiency η_discharge, the energy taken from battery = excess / η_discharge.
    # The battery usable capacity must be at least that, considering DoD.
    # But we also need to ensure we can charge enough. Let's simplify: required usable capacity = max_daily_excess / η_discharge.
    # Then gross capacity = usable / DoD.
    usable_needed = max_daily_excess / efficiency  # efficiency here is discharge efficiency
    capacity = usable_needed / dod
    return capacity

# Choose discharge window: peak hours typically 14:00-18:00 (afternoon)
discharge_start, discharge_end = 14, 18  # 2pm to 6pm
battery_capacity = size_battery_for_peak_shaving(df['load_kW'], target_peak, (discharge_start, discharge_end))
print(f"\nBattery capacity needed for 15% peak reduction: {battery_capacity:.1f} kWh (gross)")

# Simulate battery operation with this capacity
battery_power_max = 100  # kW max discharge rate (assume sufficient)
battery_efficiency = 0.92  # round-trip
soc = np.zeros(len(df))
soc_min = 0.2 * battery_capacity
soc_max = battery_capacity
soc[0] = soc_max * 0.5  # start at 50%

load_battery = df['load_kW'].copy()
battery_discharge = np.zeros(len(df))
battery_charge = np.zeros(len(df))
unmet = np.zeros(len(df))

for i, ts in enumerate(df.index):
    current_load = load_battery.iloc[i] if i == 0 else load_battery.iloc[i]  # we'll modify load_battery
    hour = ts.hour
    
    # Discharge during peak window if load > target_peak and battery available
    if discharge_start <= hour < discharge_end:
        # How much we need to reduce to reach target_peak?
        reduction_needed = max(0, current_load - target_peak)
        if reduction_needed > 0:
            max_discharge = min(battery_power_max, (soc[i] - soc_min) / battery_efficiency)
            discharge = min(reduction_needed, max_discharge)
            battery_discharge[i] = discharge
            load_battery.iloc[i] = current_load - discharge
            soc[i] -= discharge / battery_efficiency
        else:
            # No need to discharge, but could charge if excess? We'll charge later.
            pass
    else:
        # Off-peak: charge if possible (e.g., during night/early morning)
        # We'll charge at max rate until full, but only if load is low.
        # Simple rule: charge at max rate if SOC < max and hour is 0-6 (night)
        if 0 <= hour < 6 and soc[i] < soc_max:
            max_charge = min(battery_power_max, (soc_max - soc[i]) * battery_efficiency)
            # But we can't exceed load? Actually charging adds to load.
            # We assume charging is done from grid, so it increases load.
            # To avoid increasing peak, we should charge during low-load periods.
            # We'll simulate charging separately: we add charge to load, but then that load is part of demand.
            # For simplicity, we'll just track SOC and not modify load for charging (since it's net load seen by grid).
            # Better: net load = original load + charge - discharge.
            # We'll calculate net load after both.
            pass
    
    # Propagate SOC
    if i < len(df)-1:
        soc[i+1] = soc[i]
    
    # Ensure bounds
    soc[i] = np.clip(soc[i], soc_min, soc_max)

# Now we need to recompute net load including charging. Let's do a proper simulation with both charge/discharge.

# Reset SOC
soc = np.zeros(len(df))
soc[0] = soc_max * 0.5

net_load = np.zeros(len(df))

for i, ts in enumerate(df.index):
    hour = ts.hour
    original = df['load_kW'].iloc[i]
    net = original
    
    # Discharge during peak if needed and battery available
    if discharge_start <= hour < discharge_end:
        reduction_needed = max(0, net - target_peak)
        if reduction_needed > 0:
            max_discharge = min(battery_power_max, (soc[i] - soc_min) / battery_efficiency)
            discharge = min(reduction_needed, max_discharge)
            net -= discharge
            soc[i] -= discharge / battery_efficiency
            battery_discharge[i] = discharge
    else:
        # Charge during low-load periods (0-6) if battery not full
        if 0 <= hour < 6 and soc[i] < soc_max:
            # How much can we charge? Use max rate, but also we might want to limit to avoid creating new peak.
            # Since load is low in early morning, charging is safe.
            max_charge = min(battery_power_max, (soc_max - soc[i]) * battery_efficiency)
            charge = max_charge
            net += charge  # charging adds to load
            soc[i] += charge * battery_efficiency
            battery_charge[i] = charge
    
    net_load[i] = net
    
    if i < len(df)-1:
        soc[i+1] = soc[i]
    
    soc[i] = np.clip(soc[i], soc_min, soc_max)

battery_peak = np.max(net_load)
battery_energy = np.sum(net_load)
battery_energy_cost = battery_energy * energy_rate
battery_demand_cost = battery_peak * demand_charge
battery_total_cost = battery_energy_cost + battery_demand_cost

print("\n=== STRATEGY B: BATTERY PEAK SHAVING ===")
print(f"Battery capacity: {battery_capacity:.1f} kWh, power limit: {battery_power_max} kW")
print(f"New peak: {battery_peak:.1f} kW (reduction {original_peak - battery_peak:.1f} kW)")
print(f"Energy consumed (net): {battery_energy:.0f} kWh")
print(f"Energy cost: ₦{battery_energy_cost:,.0f}")
print(f"Demand cost: ₦{battery_demand_cost:,.0f}")
print(f"Total weekly cost: ₦{battery_total_cost:,.0f}")
print(f"Savings: ₦{original_total_cost - battery_total_cost:,.0f}")

# ============================================================================
# STEP 6 — COMPARISON TABLE
# ============================================================================

comparison = pd.DataFrame({
    'Scenario': ['No DR', 'Curtailment', 'Battery'],
    'Peak (kW)': [original_peak, curtail_peak, battery_peak],
    'Load Factor': [load_factor,
                    curtail_energy / (len(df) * curtail_peak),
                    battery_energy / (len(df) * battery_peak)],
    'Energy Cost (₦)': [original_energy_cost, curtail_energy_cost, battery_energy_cost],
    'Demand Cost (₦)': [original_demand_cost, curtail_demand_cost, battery_demand_cost],
    'Total Cost (₦)': [original_total_cost, curtail_total_cost, battery_total_cost],
    'Savings (₦)': [0,
                    original_total_cost - curtail_total_cost,
                    original_total_cost - battery_total_cost]
})

print("\n=== COMPARISON TABLE ===")
print(comparison.round({'Peak (kW)': 1,
                        'Load Factor': 3,
                        'Energy Cost (₦)': 0,
                        'Demand Cost (₦)': 0,
                        'Total Cost (₦)': 0,
                        'Savings (₦)': 0}).to_string(index=False))

# Save table
comparison.to_csv('peak_shaving_comparison.csv', index=False)

# ============================================================================
# STEP 7 — VISUALIZATIONS
# ============================================================================

# Plot original load profile (first 48 hours for clarity)
plot_hours = 48
df_plot = df.iloc[:plot_hours]

plt.figure(figsize=(12,4))
plt.plot(df_plot.index, df_plot['load_kW'], 'b-', linewidth=1.5)
plt.axhline(original_peak, color='r', linestyle='--', label=f'Peak: {original_peak:.1f} kW')
plt.title('Original Load Profile (First 48 Hours)')
plt.ylabel('Load (kW)')
plt.xlabel('Time')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('original_load_profile.png', dpi=150)
plt.show()

# Plot curtailment vs original (first 48h)
df_curtail_plot = df_curtail.iloc[:plot_hours]
plt.figure(figsize=(12,4))
plt.plot(df_plot.index, df_plot['load_kW'], 'b-', alpha=0.5, label='Original')
plt.plot(df_curtail_plot.index, df_curtail_plot['load_kW'], 'g-', linewidth=1.5, label='Curtailment')
plt.fill_between(df_plot.index, df_plot['load_kW'], df_curtail_plot['load_kW'],
                 where=(df_plot['load_kW'] > df_curtail_plot['load_kW']),
                 color='green', alpha=0.3, label='Reduction')
plt.title('Load Curtailment Strategy')
plt.ylabel('Load (kW)')
plt.xlabel('Time')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('dr_curtailment_profile.png', dpi=150)
plt.show()

# Plot battery shaving vs original (first 48h)
df_battery_plot = pd.DataFrame({'original': df['load_kW'].iloc[:plot_hours],
                                 'net': net_load[:plot_hours]}, index=df.index[:plot_hours])
plt.figure(figsize=(12,4))
plt.plot(df_battery_plot.index, df_battery_plot['original'], 'b-', alpha=0.5, label='Original')
plt.plot(df_battery_plot.index, df_battery_plot['net'], 'm-', linewidth=1.5, label='With Battery')
plt.fill_between(df_battery_plot.index, df_battery_plot['original'], df_battery_plot['net'],
                 where=(df_battery_plot['original'] > df_battery_plot['net']),
                 color='purple', alpha=0.3, label='Shaved')
plt.title('Battery Peak Shaving Strategy')
plt.ylabel('Load (kW)')
plt.xlabel('Time')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('battery_shaving_profile.png', dpi=150)
plt.show()

# ============================================================================
# STEP 8 — RECOMMENDATIONS & INSIGHTS
# ============================================================================

recommendation_text = f"""
PEAK SHAVING & DEMAND RESPONSE SIMULATION - RECOMMENDATIONS
============================================================

Community: Commercial building (representative profile)
Tariff: ₦{energy_rate}/kWh energy, ₦{demand_charge:,.0f}/kW demand charge (monthly)

ORIGINAL METRICS:
-----------------
Peak demand: {original_peak:.1f} kW
Load factor: {load_factor:.3f}
Monthly energy: {original_energy*4:.0f} kWh (extrapolated)
Monthly demand cost: ₦{original_demand_cost*4:,.0f}
Monthly total cost: ₦{original_total_cost*4:,.0f}

STRATEGY COMPARISON (WEEKLY):
-----------------------------
{comparison.round({'Peak (kW)':1, 'Load Factor':3, 'Energy Cost (₦)':0, 'Demand Cost (₦)':0, 'Total Cost (₦)':0, 'Savings (₦)':0}).to_string(index=False)}

KEY FINDINGS:
-------------
- Curtailment reduces peak by {original_peak - curtail_peak:.1f} kW ({100*(original_peak - curtail_peak)/original_peak:.1f}%) with no capital cost.
- Battery reduces peak by {original_peak - battery_peak:.1f} kW ({100*(original_peak - battery_peak)/original_peak:.1f}%) but requires investment.
- Both strategies improve load factor (curtailment: {curtail_energy/(len(df)*curtail_peak):.3f}, battery: {battery_energy/(len(df)*battery_peak):.3f}).

RECOMMENDATION:
---------------
- **Immediate, low-cost action:** Implement load curtailment during the top 3 peak hours each day. Expected savings: ₦{original_total_cost - curtail_total_cost:,.0f} per week (₦{(original_total_cost - curtail_total_cost)*52:,.0f} annually). No investment needed, but may affect occupant comfort if HVAC is curtailed.
- **For longer-term, greater savings:** Consider a battery system of ~{battery_capacity:.0f} kWh. At current costs (₦450,000/kWh), CAPEX ≈ ₦{battery_capacity*450e3:,.0f}. Weekly savings of ₦{original_total_cost - battery_total_cost:,.0f} → annual ₦{(original_total_cost - battery_total_cost)*52:,.0f} → simple payback ~{battery_capacity*450e3 / ((original_total_cost - battery_total_cost)*52):.1f} years. Battery also provides backup during outages.
- **Hybrid approach:** Combine curtailment with a smaller battery to further reduce peak and improve ROI.

PRACTICAL CONSTRAINTS:
----------------------
- Curtailment: HVAC reduction may affect thermal comfort; industrial process shifting may require production schedule changes.
- Battery: Requires space, maintenance, and has degradation (10‑15 year life). Response time is excellent for grid services.
- Both strategies are feasible with existing building automation systems.

NEXT STEPS:
-----------
1. Conduct detailed energy audit to identify exact curtailable loads.
2. Obtain quotes for battery storage and evaluate financing options (PPA, leasing).
3. Explore utility demand response programs for additional revenue.

PORTFOLIO VALUE STATEMENT:
--------------------------
'Simulated demand response and battery-based peak shaving for a commercial building load profile using realistic tariff structures. Quantified weekly savings of up to ₦{original_total_cost - battery_total_cost:,.0f} (₦{(original_total_cost - battery_total_cost)*52:,.0f} annually) with curtailment and battery options. Provided techno-economic comparison and actionable recommendations for facility managers.'
"""

with open('recommendations.txt', 'w', encoding='utf-8') as f:
    f.write(recommendation_text)

print("\nRecommendations saved to recommendations.txt")
print("\n=== DAY 16 COMPLETE ===")