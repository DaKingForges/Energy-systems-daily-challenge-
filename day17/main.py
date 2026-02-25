"""
DAY 17 — Real Fuel Price Shock Simulation (Corrected)
Energy System Management Portfolio

Simulate a gas price shock (+150%) on a representative national power system,
quantify impacts on generation cost, merit order, and system vulnerability,
then evaluate mitigation through battery storage and demand response.

Outputs:
- merit_order_before.png / after.png
- hourly_dispatch_comparison.png
- cost_emissions_comparison.csv
- recommendations.txt
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================================
# STEP 1 — DEFINE SYSTEM (with sufficient capacity to meet peak load)
# ============================================================================

# Generation fleet – capacities increased to ensure total > peak load (5000 MW)
# Marginal costs in ₦/MWh (Nigerian Naira)
# Gas: $8/MMBtu, heat rate 7 MMBtu/MWh → $56/MWh → at ₦1500/$ = ₦84,000/MWh
# Coal: $60/ton, heat rate 10 MMBtu/MWh, 1 ton coal ~24 MMBtu → cost ~$25/MWh → ₦37,500/MWh
# Diesel peaker: higher cost

plants = pd.DataFrame({
    'Plant': ['Hydro 1', 'Hydro 2', 'Solar PV', 'Wind', 'Gas CCGT 1', 'Gas CCGT 2',
              'Gas OCGT', 'Coal 1', 'Coal 2', 'Diesel Peakers', 'Imported'],
    'Fuel': ['Hydro', 'Hydro', 'Solar', 'Wind', 'Gas', 'Gas', 'Gas', 'Coal', 'Coal', 'Diesel', 'Import'],
    'Capacity_MW': [800, 400, 500, 300, 1200, 1000, 600, 500, 400, 300, 200],
    'Marginal_Cost_NGN_per_MWh': [0, 0, 0, 0, 84000, 84000, 95000, 37500, 37500, 120000, 110000],
    'Emissions_kgCO2_per_MWh': [0, 0, 0, 0, 400, 400, 450, 900, 900, 700, 500],
    'Must_Run': [True, True, True, True, False, False, False, False, False, False, False]
})
# Total installed capacity = 6200 MW > 5000 MW peak.

# ============================================================================
# STEP 2 — LOAD PROFILE (hourly for a representative day)
# ============================================================================

hours = np.arange(24)
load_shape = np.array([
    0.5, 0.45, 0.4, 0.38, 0.4, 0.5,   # 0-5
    0.7, 0.85, 0.9, 0.92, 0.9, 0.88,  # 6-11
    0.85, 0.8, 0.82, 0.9, 1.0, 1.1,   # 12-17
    1.2, 1.3, 1.25, 1.1, 0.9, 0.7     # 18-23
])
peak_load = 5000  # MW
load_MW = load_shape * (peak_load / np.max(load_shape))

# ============================================================================
# STEP 3 — RENEWABLE AVAILABILITY PROFILES
# ============================================================================

# Solar availability (6am-6pm)
solar_shape = np.array([
    0.0,0.0,0.0,0.0,0.0,0.0,
    0.1,0.3,0.6,0.8,0.9,1.0,
    0.95,0.85,0.7,0.5,0.2,0.05,
    0.0,0.0,0.0,0.0,0.0,0.0
])
solar_capacity = plants.loc[plants['Fuel'] == 'Solar', 'Capacity_MW'].sum()
solar_available_MW = solar_shape * solar_capacity

# Wind availability (constant 40% of capacity)
wind_capacity = plants.loc[plants['Fuel'] == 'Wind', 'Capacity_MW'].sum()
wind_available_MW = np.ones(24) * 0.4 * wind_capacity

# Hydro availability (constant 60% of capacity)
hydro_capacity = plants.loc[plants['Fuel'] == 'Hydro', 'Capacity_MW'].sum()
hydro_available_MW = np.ones(24) * 0.6 * hydro_capacity

# ============================================================================
# STEP 4 — BASELINE DISPATCH SIMULATION (merit order, no shock)
# ============================================================================

def merit_order_dispatch(load, plants, hydro_avail, solar_avail, wind_avail,
                         marginal_cost_multiplier=1.0, return_unmet=False):
    """
    Simulate hourly dispatch using merit order.
    Returns DataFrame with dispatch by plant per hour and total cost.
    If return_unmet=True, also returns array of unmet load per hour.
    """
    n_hours = len(load)
    n_plants = len(plants)
    dispatch = np.zeros((n_hours, n_plants))
    marginal_cost = plants['Marginal_Cost_NGN_per_MWh'].values * marginal_cost_multiplier

    # Identify must-run renewables by fuel type
    must_run_fuels = ['Hydro', 'Solar', 'Wind']
    must_run_indices = plants[plants['Fuel'].isin(must_run_fuels)].index.tolist()
    thermal_indices = [i for i in range(n_plants) if i not in must_run_indices]

    # Sort thermal plants by marginal cost (ascending)
    thermal_indices_sorted = sorted(thermal_indices, key=lambda i: marginal_cost[i])

    # Prepare availability per plant per hour (only for must-run)
    # We'll create a dictionary for quick access
    avail = {'Hydro': hydro_avail.copy(), 'Solar': solar_avail.copy(), 'Wind': wind_avail.copy()}

    hourly_data = []
    unmet = np.zeros(n_hours)

    for t in range(n_hours):
        remaining_load = load[t]
        hour_dispatch = np.zeros(n_plants)

        # Dispatch must-run renewables in order (hydro first, then solar, then wind)
        for fuel in ['Hydro', 'Solar', 'Wind']:
            plant_indices = plants[plants['Fuel'] == fuel].index.tolist()
            total_avail = avail[fuel][t]
            # Distribute available energy among plants of same fuel proportionally
            if total_avail > 0 and plant_indices:
                capacities = plants.loc[plant_indices, 'Capacity_MW'].values
                frac = capacities / capacities.sum()
                dispatch_vals = np.minimum(frac * total_avail, remaining_load)
                # Ensure we don't assign more than individual capacity (frac*avail <= capacity by construction)
                for idx, val in zip(plant_indices, dispatch_vals):
                    hour_dispatch[idx] = val
                remaining_load -= dispatch_vals.sum()

        # Now dispatch thermal plants in merit order until load is met
        for i in thermal_indices_sorted:
            if remaining_load <= 1e-6:  # tolerance
                break
            capacity = plants.loc[i, 'Capacity_MW']
            dispatch_t = min(capacity, remaining_load)
            hour_dispatch[i] = dispatch_t
            remaining_load -= dispatch_t

        # Record any unmet load (should be zero if capacity is sufficient)
        unmet[t] = remaining_load if remaining_load > 1e-6 else 0.0

        hourly_data.append(hour_dispatch)

    df_dispatch = pd.DataFrame(hourly_data, columns=plants['Plant'])
    df_dispatch['Hour'] = hours

    if return_unmet:
        return df_dispatch, unmet
    else:
        return df_dispatch

# Baseline dispatch (no shock)
dispatch_before, unmet_before = merit_order_dispatch(
    load_MW, plants,
    hydro_avail=hydro_available_MW,
    solar_avail=solar_available_MW,
    wind_avail=wind_available_MW,
    marginal_cost_multiplier=1.0,
    return_unmet=True
)

if np.any(unmet_before > 0.1):
    print("Warning: Baseline has unmet load in some hours. Check capacities.")

# Calculate total generation cost
generation_before = dispatch_before.drop('Hour', axis=1).values
cost_per_plant = plants['Marginal_Cost_NGN_per_MWh'].values.reshape(1, -1)
total_cost_before = np.sum(generation_before * cost_per_plant)
avg_cost_before = total_cost_before / np.sum(load_MW)

print("=== BASELINE (No Shock) ===")
print(f"Total daily generation cost: ₦{total_cost_before:,.0f}")
print(f"Average cost: ₦{avg_cost_before:,.0f}/MWh")
print(f"Unmet load (max): {np.max(unmet_before):.2f} MW")

# ============================================================================
# STEP 5 — APPLY FUEL SHOCK (gas price +150%)
# ============================================================================

# Shock multiplier for gas plants: original cost * 2.5
plants_shocked = plants.copy()
gas_indices = plants_shocked[plants_shocked['Fuel'] == 'Gas'].index
plants_shocked.loc[gas_indices, 'Marginal_Cost_NGN_per_MWh'] *= 2.5

# Re-dispatch with shocked costs
dispatch_shocked, unmet_shocked = merit_order_dispatch(
    load_MW, plants_shocked,
    hydro_avail=hydro_available_MW,
    solar_avail=solar_available_MW,
    wind_avail=wind_available_MW,
    marginal_cost_multiplier=1.0,
    return_unmet=True
)

# Calculate new total cost
generation_shocked = dispatch_shocked.drop('Hour', axis=1).values
cost_per_plant_shocked = plants_shocked['Marginal_Cost_NGN_per_MWh'].values.reshape(1, -1)
total_cost_shocked = np.sum(generation_shocked * cost_per_plant_shocked)
avg_cost_shocked = total_cost_shocked / np.sum(load_MW)

print("\n=== AFTER GAS PRICE SHOCK (+150%) ===")
print(f"Total daily generation cost: ₦{total_cost_shocked:,.0f}")
print(f"Average cost: ₦{avg_cost_shocked:,.0f}/MWh")
print(f"Cost increase: {100*(total_cost_shocked - total_cost_before)/total_cost_before:.1f}%")
print(f"Unmet load (max): {np.max(unmet_shocked):.2f} MW")

# ============================================================================
# STEP 6 — MITIGATION STRATEGIES
# ============================================================================

# ------------------------------------------------------------
# Strategy A: Battery storage (200 MW / 800 MWh)
# ------------------------------------------------------------
battery_power = 200      # MW
battery_capacity = 800   # MWh
battery_efficiency = 0.92
battery_soc_min = 0.1 * battery_capacity
battery_soc_max = battery_capacity

# To decide when to charge/discharge, we use the marginal cost of the last
# dispatched plant in the shocked scenario (without battery). This gives a
# price signal. We'll compute that from the shocked dispatch.
# For each hour, find the most expensive plant that is dispatched (excluding must-run?).
# Simpler: use the marginal cost of the marginal plant (the one with highest cost among those running).
# We'll approximate by taking the maximum marginal cost among plants with positive generation in that hour.
marginal_price_hourly = np.zeros(24)
for t in range(24):
    gen_t = generation_shocked[t, :]
    running = gen_t > 0.1
    if np.any(running):
        marginal_price_hourly[t] = np.max(cost_per_plant_shocked[0, running])
    else:
        marginal_price_hourly[t] = 0

# Battery optimization: charge when price is low, discharge when price is high.
# Sort hours by price.
price_rank = np.argsort(marginal_price_hourly)
# Designate cheapest 8 hours for charging, most expensive 6 hours for discharging.
charge_hours = price_rank[:8]
discharge_hours = price_rank[-6:]

# Simulate battery operation
soc = np.zeros(24)
soc[0] = battery_capacity * 0.3   # start at 30%
battery_net = np.zeros(24)         # positive = charging (adds to load), negative = discharging (reduces load)

for t in range(24):
    if t in discharge_hours and soc[t] > battery_soc_min + 1:
        # discharge as much as possible up to battery power
        discharge = min(battery_power, soc[t] - battery_soc_min)
        battery_net[t] = -discharge   # negative means reduces load
        soc[t] -= discharge / battery_efficiency
    elif t in charge_hours and soc[t] < battery_soc_max - 1:
        # charge as much as possible
        charge = min(battery_power, (battery_soc_max - soc[t]) / battery_efficiency)
        battery_net[t] = charge        # positive means increases load
        soc[t] += charge * battery_efficiency

    # Update next hour's SOC
    if t < 23:
        soc[t+1] = soc[t]

# Apply battery to load: net load = original load + charging - discharging
net_load_battery = load_MW + battery_net

# Re-dispatch with shocked costs using net load
dispatch_battery, unmet_battery = merit_order_dispatch(
    net_load_battery, plants_shocked,
    hydro_avail=hydro_available_MW,
    solar_avail=solar_available_MW,
    wind_avail=wind_available_MW,
    marginal_cost_multiplier=1.0,
    return_unmet=True
)

generation_battery = dispatch_battery.drop('Hour', axis=1).values
total_cost_battery = np.sum(generation_battery * cost_per_plant_shocked)
# Note: total energy served is still original load (battery losses are internal)
avg_cost_battery = total_cost_battery / np.sum(load_MW)

print("\n=== MITIGATION A: Battery Storage (200 MW / 800 MWh) ===")
print(f"Total daily generation cost: ₦{total_cost_battery:,.0f}")
print(f"Average cost: ₦{avg_cost_battery:,.0f}/MWh")
print(f"Cost reduction vs shocked: {100*(total_cost_shocked - total_cost_battery)/total_cost_shocked:.1f}%")
print(f"Unmet load (max): {np.max(unmet_battery):.2f} MW")

# ------------------------------------------------------------
# Strategy B: Demand Response (10% peak reduction)
# ------------------------------------------------------------
load_dr = load_MW.copy()
peak_hours = [17, 18, 19, 20, 21, 22]
for h in peak_hours:
    load_dr[h] *= 0.9

dispatch_dr, unmet_dr = merit_order_dispatch(
    load_dr, plants_shocked,
    hydro_avail=hydro_available_MW,
    solar_avail=solar_available_MW,
    wind_avail=wind_available_MW,
    marginal_cost_multiplier=1.0,
    return_unmet=True
)

generation_dr = dispatch_dr.drop('Hour', axis=1).values
total_cost_dr = np.sum(generation_dr * cost_per_plant_shocked)
avg_cost_dr = total_cost_dr / np.sum(load_dr)   # load served is slightly lower

print("\n=== MITIGATION B: Demand Response (10% peak reduction) ===")
print(f"Total daily generation cost: ₦{total_cost_dr:,.0f}")
print(f"Average cost: ₦{avg_cost_dr:,.0f}/MWh (based on reduced load)")
print(f"Cost reduction vs shocked: {100*(total_cost_shocked - total_cost_dr)/total_cost_shocked:.1f}%")
print(f"Unmet load (max): {np.max(unmet_dr):.2f} MW")

# ============================================================================
# STEP 7 — COMPARISON TABLE
# ============================================================================

def total_emissions(gen_matrix, plants_df):
    return np.sum(gen_matrix * plants_df['Emissions_kgCO2_per_MWh'].values.reshape(1, -1)) / 1000  # tonnes

comparison = pd.DataFrame({
    'Scenario': ['Baseline', 'Gas Shock (+150%)', 'Battery Mitigation', 'DR Mitigation'],
    'Total Cost (₦ million)': [total_cost_before/1e6, total_cost_shocked/1e6,
                                total_cost_battery/1e6, total_cost_dr/1e6],
    'Avg Cost (₦/MWh)': [avg_cost_before, avg_cost_shocked, avg_cost_battery, avg_cost_dr],
    'Peak Marginal Cost (₦/MWh)': [
        plants['Marginal_Cost_NGN_per_MWh'].max(),
        plants_shocked['Marginal_Cost_NGN_per_MWh'].max(),
        plants_shocked['Marginal_Cost_NGN_per_MWh'].max(),
        plants_shocked['Marginal_Cost_NGN_per_MWh'].max()
    ],
    'Emissions (tonnes CO2)': [
        total_emissions(generation_before, plants),
        total_emissions(generation_shocked, plants_shocked),
        total_emissions(generation_battery, plants_shocked),
        total_emissions(generation_dr, plants_shocked)
    ]
})

print("\n=== COMPARISON TABLE ===")
print(comparison.round(2).to_string(index=False))
comparison.to_csv('cost_emissions_comparison.csv', index=False)

# ============================================================================
# STEP 8 — VISUALIZATIONS
# ============================================================================

# 8.1 Merit order curves (before and after shock)
def plot_merit_order(plants, title, filename):
    sorted_plants = plants.sort_values('Marginal_Cost_NGN_per_MWh')
    cumulative_cap = np.cumsum(sorted_plants['Capacity_MW'])
    colors = {'Hydro': 'blue', 'Solar': 'gold', 'Wind': 'lightblue',
              'Gas': 'orange', 'Coal': 'brown', 'Diesel': 'red', 'Import': 'purple'}
    fig, ax = plt.subplots(figsize=(10, 5))
    prev = 0
    added_fuels = set()

    for idx, row in sorted_plants.iterrows():
        fuel = row['Fuel']
        color = colors.get(fuel, 'gray')
        label = fuel if fuel not in added_fuels else ""
        added_fuels.add(fuel)

        ax.barh('Merit Order', row['Capacity_MW'], left=prev, color=color, label=label)
        # Annotate marginal cost (in thousand ₦)
        ax.text(prev + row['Capacity_MW']/2, 0,
                f'{row["Marginal_Cost_NGN_per_MWh"]/1000:.0f}k',
                ha='center', va='center', fontsize=8)
        prev += row['Capacity_MW']

    ax.set_xlabel('Cumulative Capacity (MW)')
    ax.set_title(title)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    # Add peak load line
    ax.axvline(x=peak_load, color='red', linestyle='--', alpha=0.7, label=f'Peak Load ({peak_load} MW)')
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.show()

plot_merit_order(plants, 'Merit Order Before Shock', 'merit_order_before.png')
plot_merit_order(plants_shocked, 'Merit Order After Gas Price Shock', 'merit_order_after.png')

# 8.2 Hourly dispatch comparison
fig, axes = plt.subplots(4, 1, figsize=(12, 12), sharex=True)

# Helper to stack by fuel
def stack_by_fuel(dispatch_df, plants_df):
    dispatch = dispatch_df.set_index('Hour')
    fuel_groups = {}
    for fuel in plants_df['Fuel'].unique():
        cols = plants_df[plants_df['Fuel'] == fuel]['Plant'].tolist()
        if cols:
            fuel_groups[fuel] = dispatch[cols].sum(axis=1).values
    return fuel_groups

# Baseline
fuel_before = stack_by_fuel(dispatch_before, plants)
ax = axes[0]
bottom = np.zeros(24)
for fuel, values in fuel_before.items():
    color = {'Hydro':'blue', 'Solar':'gold', 'Wind':'lightblue',
             'Gas':'orange', 'Coal':'brown', 'Diesel':'red', 'Import':'purple'}.get(fuel, 'gray')
    ax.bar(hours, values, bottom=bottom, label=fuel, color=color, alpha=0.7, width=0.8)
    bottom += values
ax.plot(hours, load_MW, 'k--', linewidth=2, label='Load')
ax.set_ylabel('MW')
ax.set_title('Baseline Dispatch')
ax.legend(loc='upper right', ncol=3)
ax.grid(True, alpha=0.3)

# Shocked
fuel_shocked = stack_by_fuel(dispatch_shocked, plants_shocked)
ax = axes[1]
bottom = np.zeros(24)
for fuel, values in fuel_shocked.items():
    color = {'Hydro':'blue', 'Solar':'gold', 'Wind':'lightblue',
             'Gas':'orange', 'Coal':'brown', 'Diesel':'red', 'Import':'purple'}.get(fuel, 'gray')
    ax.bar(hours, values, bottom=bottom, label=fuel, color=color, alpha=0.7, width=0.8)
    bottom += values
ax.plot(hours, load_MW, 'k--', linewidth=2, label='Load')
ax.set_ylabel('MW')
ax.set_title('After Gas Shock')
ax.legend(loc='upper right', ncol=3)
ax.grid(True, alpha=0.3)

# Battery mitigation
fuel_battery = stack_by_fuel(dispatch_battery, plants_shocked)
ax = axes[2]
bottom = np.zeros(24)
for fuel, values in fuel_battery.items():
    color = {'Hydro':'blue', 'Solar':'gold', 'Wind':'lightblue',
             'Gas':'orange', 'Coal':'brown', 'Diesel':'red', 'Import':'purple'}.get(fuel, 'gray')
    ax.bar(hours, values, bottom=bottom, label=fuel, color=color, alpha=0.7, width=0.8)
    bottom += values
# Show battery charge/discharge as separate bars
charge_h = np.where(battery_net > 0, battery_net, 0)
discharge_h = np.where(battery_net < 0, -battery_net, 0)
ax.bar(hours, charge_h, bottom=load_MW, color='green', alpha=0.3, label='Battery charge', width=0.8)
ax.bar(hours, -discharge_h, bottom=0, color='blue', alpha=0.3, label='Battery discharge', width=0.8)
ax.plot(hours, load_MW, 'k--', linewidth=2, label='Load')
ax.set_ylabel('MW')
ax.set_title('With Battery Mitigation')
ax.legend(loc='upper right', ncol=3)
ax.grid(True, alpha=0.3)

# DR mitigation
fuel_dr = stack_by_fuel(dispatch_dr, plants_shocked)
ax = axes[3]
bottom = np.zeros(24)
for fuel, values in fuel_dr.items():
    color = {'Hydro':'blue', 'Solar':'gold', 'Wind':'lightblue',
             'Gas':'orange', 'Coal':'brown', 'Diesel':'red', 'Import':'purple'}.get(fuel, 'gray')
    ax.bar(hours, values, bottom=bottom, label=fuel, color=color, alpha=0.7, width=0.8)
    bottom += values
ax.plot(hours, load_dr, 'k--', linewidth=2, label='Load (after DR)')
ax.set_xlabel('Hour')
ax.set_ylabel('MW')
ax.set_title('With Demand Response Mitigation')
ax.legend(loc='upper right', ncol=3)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('hourly_dispatch_comparison.png', dpi=150)
plt.show()

# ============================================================================
# STEP 9 — RECOMMENDATIONS
# ============================================================================

recommendation_text = f"""
FUEL PRICE SHOCK SIMULATION - RESILIENCE REPORT
================================================

SYSTEM: Representative national grid with gas-dominated generation.
SHOCK: Natural gas price increase of 150% (e.g., 2022 global gas crisis).

KEY IMPACTS:
------------
- Total daily generation cost increased by {100*(total_cost_shocked - total_cost_before)/total_cost_before:.1f}%.
- Average cost rose from ₦{avg_cost_before:,.0f}/MWh to ₦{avg_cost_shocked:,.0f}/MWh.
- Peak marginal cost climbed to ₦{plants_shocked['Marginal_Cost_NGN_per_MWh'].max():,.0f}/MWh.
- Emissions: {total_emissions(generation_shocked, plants_shocked):.1f} tonnes CO2/day.

MITIGATION EFFECTIVENESS:
-------------------------
1. **Battery Storage (200 MW / 800 MWh):**
   - Reduced cost by {100*(total_cost_shocked - total_cost_battery)/total_cost_shocked:.1f}% vs shocked.
   - Shifts cheap solar energy to peak hours, displacing expensive gas and diesel.
   - Estimated annual savings: ₦{(total_cost_shocked - total_cost_battery)*365:,.0f}.
   - Payback period (rough): {800*450e3 / ((total_cost_shocked - total_cost_battery)*365):.1f} years at ₦450k/kWh.

2. **Demand Response (10% peak reduction):**
   - Reduced cost by {100*(total_cost_shocked - total_cost_dr)/total_cost_shocked:.1f}% vs shocked.
   - Minimal capital cost; requires customer engagement programs.
   - Avoided cost: ₦{(total_cost_shocked - total_cost_dr):,.0f} per day.

COMPARISON METRICS:
-------------------
{comparison.round(2).to_string(index=False)}

RECOMMENDATION:
---------------
- **Immediate:** Implement demand response programs targeting large industrial customers to shave the most expensive peak hours.
- **Medium-term:** Procure battery storage (200 MW / 800 MWh) to provide daily peak shaving and enhance grid flexibility. The battery alone can reduce the cost impact of future gas shocks by ~{100*(total_cost_shocked - total_cost_battery)/total_cost_shocked:.1f}%.
- **Long-term:** Diversify the generation mix with additional renewables (solar, wind) to reduce dependency on imported gas. Accelerate coal phase-out if emissions reduction is a priority.

The system remains vulnerable to fuel price volatility due to gas dependency. Strategic investments in storage and demand-side management significantly improve resilience and reduce exposure to fuel price shocks.

PORTFOLIO VALUE STATEMENT:
--------------------------
'Simulated a realistic gas price shock (+150%) on a national power system, quantifying cost and dispatch impacts. Designed and evaluated battery storage and demand response mitigation, demonstrating cost reductions of {100*(total_cost_shocked - total_cost_battery)/total_cost_shocked:.1f}% and {100*(total_cost_shocked - total_cost_dr)/total_cost_shocked:.1f}% respectively. Provided actionable recommendations for enhancing system resilience.'
"""

with open('recommendations.txt', 'w', encoding='utf-8') as f:
    f.write(recommendation_text)

print("\nRecommendations saved to recommendations.txt")
print("\n=== DAY 17 COMPLETE ===")