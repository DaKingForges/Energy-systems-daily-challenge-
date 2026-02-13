"""
DAY 15: Rural Electrification Scenario
Energy System Management Portfolio

Objective: Evaluate three electrification options for a rural community:
- Option A: Grid extension
- Option B: Solar PV + battery mini-grid
- Option C: Solar PV + pumped hydro storage (PHS) mini-grid

Outputs: comparison table, visualizations (load vs generation, cost breakdown, CO₂),
         recommendations.txt
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================================
# STEP 1 — DEFINE THE COMMUNITY LOAD PROFILE
# ============================================================================

# Community: 75 households + school + health center + small market
n_households = 75
hh_daily = 2.0           # kWh/household/day
school_daily = 10.0      # kWh/day
health_daily = 8.0       # kWh/day
market_daily = 5.0       # kWh/day

total_daily_energy = n_households * hh_daily + school_daily + health_daily + market_daily
print(f"Total daily energy demand: {total_daily_energy:.1f} kWh")

# Normalized load shape (rural with morning and evening peaks)
hours = np.arange(24)
load_shape = np.array([
    0.3, 0.2, 0.2, 0.2, 0.2, 0.4,   # 0-5
    0.8, 1.0, 0.7, 0.5, 0.4, 0.4,   # 6-11
    0.5, 0.5, 0.5, 0.6, 0.8, 1.0,   # 12-17
    1.2, 1.5, 1.8, 1.5, 1.0, 0.5    # 18-23
])

# Scale to total daily energy
load_kw = load_shape * (total_daily_energy / np.sum(load_shape))
peak_load = np.max(load_kw)
print(f"Peak load: {peak_load:.1f} kW")

# ============================================================================
# STEP 2 — DEFINE COST & TECHNICAL PARAMETERS
# ============================================================================

# Grid extension parameters
grid_dist_km = 8                     # distance to nearest grid
line_cost_per_km = 15e6               # ₦15M per km
substation_cost = 50e6                # ₦50M for transformer
grid_tariff = 110                      # ₦/kWh
grid_availability = 0.65               # 65% of time available
grid_emissions = 0.85                   # kg CO₂/kWh

# Solar PV parameters
solar_capex_per_kw = 1.2e6             # ₦/kWp
solar_opex_percent = 1.0                # % of capex per year
solar_lifetime = 25
peak_sun_hours = 5.5
solar_derating = 0.75
solar_degradation = 0.005

# Battery parameters
battery_capex_per_kwh = 450e3           # ₦/kWh
battery_opex_percent = 1.5
battery_lifetime = 10
battery_replacement_cost = 400e3         # ₦/kWh (assumed lower in future)
battery_rte = 0.92                        # round-trip efficiency
battery_max_dod = 0.8                     # depth of discharge
battery_max_charge_rate = 0.5              # C-rate
battery_max_discharge_rate = 1.0           # C-rate

# PHS parameters
phs_turbine_capex_per_kw = 150e3          # ₦/kW
phs_storage_capex_per_kwh = 40e3          # ₦/kWh (reservoir equivalent)
phs_opex_percent = 1.0
phs_lifetime = 50
phs_turbine_efficiency = 0.90
phs_pump_efficiency = 0.89
phs_rte = phs_turbine_efficiency * phs_pump_efficiency  # ~0.80
phs_min_soc = 0.1

# Diesel generator (backup) parameters
gen_lcoe = 485                             # ₦/kWh (from Day 2)
gen_emissions_per_kwh = 2.14                # kg CO₂/kWh (diesel)

# Financial parameters
discount_rate = 0.12
analysis_years = 20
inflation = 0.15

# ============================================================================
# STEP 3 — OPTION A: GRID EXTENSION
# ============================================================================

def option_grid(load_kw, total_daily_energy):
    """Evaluate grid extension option."""
    # Capital cost
    capex = grid_dist_km * line_cost_per_km + substation_cost
    
    # Annual energy purchased
    annual_energy = total_daily_energy * 365
    
    # Annual energy cost
    annual_energy_cost = annual_energy * grid_tariff
    
    # O&M (2% of capex for line maintenance)
    annual_om = capex * 0.02
    
    # Total annual cost
    annual_total = annual_energy_cost + annual_om
    
    # Discounted lifecycle cost
    pv = 0
    for year in range(1, analysis_years + 1):
        pv += annual_total / ((1 + discount_rate) ** year)
    total_lifecycle = capex + pv
    
    # Reliability = grid availability
    reliability = grid_availability * 100
    
    # CO2 emissions
    annual_co2 = annual_energy * grid_emissions / 1000   # tonnes
    total_co2 = annual_co2 * analysis_years
    
    # LCOE (simplified)
    total_energy_lifetime = annual_energy * analysis_years
    lcoe = total_lifecycle / total_energy_lifetime if total_energy_lifetime > 0 else np.inf
    
    return {
        'Option': 'Grid Extension',
        'CAPEX (₦M)': capex / 1e6,
        'Annual OM (₦M)': annual_om / 1e6,
        'Annual Energy Cost (₦M)': annual_energy_cost / 1e6,
        'Total Lifecycle Cost (₦M)': total_lifecycle / 1e6,
        'LCOE (₦/kWh)': lcoe,
        'Reliability (%)': reliability,
        'CO₂ (tonnes/yr)': annual_co2,
        'Total CO₂ (tonnes)': total_co2
    }

# ============================================================================
# STEP 4 — OPTION B: SOLAR + BATTERY MINI-GRID
# ============================================================================

def size_solar_battery(load_kw, total_daily_energy, peak_load):
    """Size solar PV and battery for the mini-grid."""
    # Estimate night energy (6pm-6am)
    night_energy = np.sum(load_kw[18:]) + np.sum(load_kw[0:6])
    # Day energy
    day_energy = total_daily_energy - night_energy
    
    # Solar sizing: need to generate day energy + losses for night storage
    # Assume 40% of night energy goes through battery (rest directly from solar in evening)
    battery_night_energy = night_energy * 0.7  # 70% of night from battery, rest from solar evening
    extra_generation = battery_night_energy / battery_rte  # due to battery losses
    total_needed = day_energy + extra_generation
    
    solar_daily_per_kw = peak_sun_hours * solar_derating  # kWh/kWp/day
    solar_kw = total_needed / solar_daily_per_kw
    solar_kw = np.ceil(solar_kw / 5) * 5  # round to 5 kW
    
    # Battery sizing: need to supply battery_night_energy, accounting for DoD
    battery_kwh = battery_night_energy / (battery_max_dod * battery_rte)
    # Also check power: need to cover peak load during night
    night_peak = np.max(load_kw[18:22])  # evening peak
    if battery_kwh * battery_max_discharge_rate < night_peak:
        battery_kwh = night_peak / battery_max_discharge_rate
    battery_kwh = np.ceil(battery_kwh / 10) * 10  # round to 10 kWh
    
    return solar_kw, battery_kwh

def simulate_solar_battery(load_kw, solar_kw, battery_kwh):
    """Simulate daily operation with solar+battery."""
    # Solar generation profile
    solar_shape = np.array([
        0.0,0.0,0.0,0.0,0.0,0.0,
        0.1,0.3,0.6,0.8,0.9,1.0,
        0.95,0.85,0.7,0.5,0.2,0.05,
        0.0,0.0,0.0,0.0,0.0,0.0
    ])
    solar_daily = solar_kw * peak_sun_hours * solar_derating
    solar_gen = solar_shape * (solar_daily / np.sum(solar_shape))
    
    # Battery parameters
    soc = np.zeros(24)
    soc_min = (1 - battery_max_dod) * battery_kwh
    soc_max = battery_kwh
    soc[0] = soc_max * 0.5  # start at 50%
    
    discharge = np.zeros(24)
    charge = np.zeros(24)
    unmet = np.zeros(24)
    excess = np.zeros(24)
    
    for t in range(24):
        net = load_kw[t] - solar_gen[t]   # positive deficit, negative excess
        
        if net > 0:  # need to discharge
            max_discharge = min(battery_kwh * battery_max_discharge_rate, soc[t] - soc_min)
            discharge[t] = min(net, max_discharge)
            unmet[t] = net - discharge[t]
            soc[t] -= discharge[t] / battery_rte   # energy taken from battery (electrical)
        else:  # excess solar, can charge
            excess_avail = -net
            max_charge = min(battery_kwh * battery_max_charge_rate, (soc_max - soc[t]) / battery_rte)
            charge[t] = min(excess_avail, max_charge)
            soc[t] += charge[t] * battery_rte
            excess[t] = excess_avail - charge[t]  # curtailment or export
        
        soc[t] = np.clip(soc[t], soc_min, soc_max)
        if t < 23:
            soc[t+1] = soc[t]
    
    # Reliability: fraction of load met
    total_load = np.sum(load_kw)
    total_unmet = np.sum(unmet)
    reliability = 100 * (1 - total_unmet / total_load)
    
    return {
        'solar_gen': solar_gen,
        'charge': charge,
        'discharge': discharge,
        'unmet': unmet,
        'excess': excess,
        'soc': soc,
        'reliability': reliability
    }

def option_solar_battery(load_kw, total_daily_energy, peak_load):
    """Evaluate solar+battery option."""
    solar_kw, battery_kwh = size_solar_battery(load_kw, total_daily_energy, peak_load)
    sim = simulate_solar_battery(load_kw, solar_kw, battery_kwh)
    
    # CAPEX
    capex_solar = solar_kw * solar_capex_per_kw
    capex_battery = battery_kwh * battery_capex_per_kwh
    total_capex = capex_solar + capex_battery
    
    # Annual O&M
    om_solar = capex_solar * solar_opex_percent / 100
    om_battery = capex_battery * battery_opex_percent / 100
    annual_om = om_solar + om_battery
    
    # Battery replacement in year 10
    battery_replacement = battery_kwh * battery_replacement_cost
    
    # Discounted lifecycle cost
    pv = 0
    for year in range(1, analysis_years + 1):
        cost_year = annual_om
        if year == 10:
            cost_year += battery_replacement
        pv += cost_year / ((1 + discount_rate) ** year)
    total_lifecycle = total_capex + pv
    
    # Reliability from simulation
    reliability = sim['reliability']
    
    # CO2: zero if no diesel, but we have unmet load that would need generator
    # For simplicity, we assume unmet is supplied by diesel generator (cost included in LCOE? Not yet)
    # We'll compute diesel backup cost and emissions separately.
    unmet_annual = np.sum(sim['unmet']) * 365
    # Diesel backup cost
    diesel_cost_annual = unmet_annual * gen_lcoe
    diesel_emissions_annual = unmet_annual * gen_emissions_per_kwh / 1000  # tonnes
    
    # Add diesel cost to lifecycle
    pv_diesel = 0
    for year in range(1, analysis_years + 1):
        pv_diesel += diesel_cost_annual / ((1 + discount_rate) ** year)
    total_lifecycle_with_diesel = total_lifecycle + pv_diesel
    
    # Total energy delivered
    annual_energy = total_daily_energy * 365
    # LCOE including diesel backup
    lcoe = total_lifecycle_with_diesel / (annual_energy * analysis_years)
    
    # CO2 total from diesel backup
    total_co2 = diesel_emissions_annual * analysis_years
    
    return {
        'Option': 'Solar + Battery',
        'Solar (kWp)': solar_kw,
        'Battery (kWh)': battery_kwh,
        'CAPEX (₦M)': total_capex / 1e6,
        'Annual OM (₦M)': annual_om / 1e6,
        'Battery Replacement (₦M)': battery_replacement / 1e6,
        'Diesel Backup Annual (₦M)': diesel_cost_annual / 1e6,
        'Total Lifecycle Cost (₦M)': total_lifecycle_with_diesel / 1e6,
        'LCOE (₦/kWh)': lcoe,
        'Reliability (%)': reliability,
        'CO₂ (tonnes/yr)': diesel_emissions_annual,
        'Total CO₂ (tonnes)': total_co2,
        'sim': sim  # for plotting
    }

# ============================================================================
# STEP 5 — OPTION C: SOLAR + PUMPED HYDRO STORAGE (PHS)
# ============================================================================

def size_solar_phs(load_kw, total_daily_energy, peak_load):
    """Size solar PV and PHS for the mini-grid."""
    # Similar logic, but PHS has different efficiencies and rates
    night_energy = np.sum(load_kw[18:]) + np.sum(load_kw[0:6])
    # Assume 70% of night from storage
    phs_night_energy = night_energy * 0.7
    
    # Solar sizing: day energy + extra for storage losses
    extra_generation = phs_night_energy / phs_rte
    day_energy = total_daily_energy - night_energy
    total_needed = day_energy + extra_generation
    
    solar_daily_per_kw = peak_sun_hours * solar_derating
    solar_kw = total_needed / solar_daily_per_kw
    solar_kw = np.ceil(solar_kw / 5) * 5
    
    # PHS storage sizing (electrical equivalent)
    phs_storage_kwh = phs_night_energy / phs_rte  # stored electrical needed
    phs_storage_kwh = np.ceil(phs_storage_kwh / 50) * 50  # round to 50 kWh
    
    # Turbine sizing: need to cover evening peak
    evening_peak = np.max(load_kw[18:22])
    turbine_kw = evening_peak * 1.2  # 20% margin
    turbine_kw = np.ceil(turbine_kw / 10) * 10
    # Pump can be same size or smaller
    pump_kw = turbine_kw
    
    return solar_kw, phs_storage_kwh, turbine_kw, pump_kw

def simulate_solar_phs(load_kw, solar_kw, phs_storage_kwh, turbine_kw, pump_kw):
    """Simulate daily operation with solar+PHS."""
    # Solar generation profile
    solar_shape = np.array([
        0.0,0.0,0.0,0.0,0.0,0.0,
        0.1,0.3,0.6,0.8,0.9,1.0,
        0.95,0.85,0.7,0.5,0.2,0.05,
        0.0,0.0,0.0,0.0,0.0,0.0
    ])
    solar_daily = solar_kw * peak_sun_hours * solar_derating
    solar_gen = solar_shape * (solar_daily / np.sum(solar_shape))
    
    # PHS parameters
    soc = np.zeros(24)
    soc_min = phs_min_soc * phs_storage_kwh
    soc_max = phs_storage_kwh
    soc[0] = soc_max * 0.5  # start at 50%
    
    discharge = np.zeros(24)  # turbine
    charge = np.zeros(24)     # pump
    unmet = np.zeros(24)
    excess = np.zeros(24)
    
    for t in range(24):
        net = load_kw[t] - solar_gen[t]
        
        if net > 0:  # deficit, discharge
            max_discharge = min(turbine_kw, (soc[t] - soc_min) / phs_turbine_efficiency)
            discharge[t] = min(net, max_discharge)
            unmet[t] = net - discharge[t]
            soc[t] -= discharge[t] / phs_turbine_efficiency  # electrical removed
        else:  # excess, charge
            excess_avail = -net
            max_charge = min(pump_kw, (soc_max - soc[t]) / phs_pump_efficiency)
            charge[t] = min(excess_avail, max_charge)
            soc[t] += charge[t] * phs_pump_efficiency
            excess[t] = excess_avail - charge[t]
        
        soc[t] = np.clip(soc[t], soc_min, soc_max)
        if t < 23:
            soc[t+1] = soc[t]
    
    total_load = np.sum(load_kw)
    total_unmet = np.sum(unmet)
    reliability = 100 * (1 - total_unmet / total_load)
    
    return {
        'solar_gen': solar_gen,
        'charge': charge,
        'discharge': discharge,
        'unmet': unmet,
        'excess': excess,
        'soc': soc,
        'reliability': reliability
    }

def option_solar_phs(load_kw, total_daily_energy, peak_load):
    """Evaluate solar+PHS option."""
    solar_kw, phs_storage_kwh, turbine_kw, pump_kw = size_solar_phs(load_kw, total_daily_energy, peak_load)
    sim = simulate_solar_phs(load_kw, solar_kw, phs_storage_kwh, turbine_kw, pump_kw)
    
    # CAPEX
    capex_solar = solar_kw * solar_capex_per_kw
    capex_phs = turbine_kw * phs_turbine_capex_per_kw + phs_storage_kwh * phs_storage_capex_per_kwh
    total_capex = capex_solar + capex_phs
    
    # Annual O&M
    om_solar = capex_solar * solar_opex_percent / 100
    om_phs = capex_phs * phs_opex_percent / 100
    annual_om = om_solar + om_phs
    
    # No replacement within 20 years (PHS lifetime 50+)
    
    # Discounted lifecycle cost
    pv = 0
    for year in range(1, analysis_years + 1):
        pv += annual_om / ((1 + discount_rate) ** year)
    total_lifecycle = total_capex + pv
    
    # Reliability
    reliability = sim['reliability']
    
    # Unmet load backed up by diesel
    unmet_annual = np.sum(sim['unmet']) * 365
    diesel_cost_annual = unmet_annual * gen_lcoe
    diesel_emissions_annual = unmet_annual * gen_emissions_per_kwh / 1000
    
    pv_diesel = 0
    for year in range(1, analysis_years + 1):
        pv_diesel += diesel_cost_annual / ((1 + discount_rate) ** year)
    total_lifecycle_with_diesel = total_lifecycle + pv_diesel
    
    annual_energy = total_daily_energy * 365
    lcoe = total_lifecycle_with_diesel / (annual_energy * analysis_years)
    total_co2 = diesel_emissions_annual * analysis_years
    
    return {
        'Option': 'Solar + PHS',
        'Solar (kWp)': solar_kw,
        'PHS Turbine (kW)': turbine_kw,
        'PHS Storage (kWh)': phs_storage_kwh,
        'CAPEX (₦M)': total_capex / 1e6,
        'Annual OM (₦M)': annual_om / 1e6,
        'Diesel Backup Annual (₦M)': diesel_cost_annual / 1e6,
        'Total Lifecycle Cost (₦M)': total_lifecycle_with_diesel / 1e6,
        'LCOE (₦/kWh)': lcoe,
        'Reliability (%)': reliability,
        'CO₂ (tonnes/yr)': diesel_emissions_annual,
        'Total CO₂ (tonnes)': total_co2,
        'sim': sim
    }

# ============================================================================
# STEP 6 — COMPARE OPTIONS
# ============================================================================

# Run all options
print("\n" + "="*60)
print("OPTION A: GRID EXTENSION")
print("="*60)
res_grid = option_grid(load_kw, total_daily_energy)

print("\n" + "="*60)
print("OPTION B: SOLAR + BATTERY")
print("="*60)
res_battery = option_solar_battery(load_kw, total_daily_energy, peak_load)

print("\n" + "="*60)
print("OPTION C: SOLAR + PHS")
print("="*60)
res_phs = option_solar_phs(load_kw, total_daily_energy, peak_load)

# Create comparison table
comparison = pd.DataFrame([
    res_grid,
    {k: v for k, v in res_battery.items() if k != 'sim'},
    {k: v for k, v in res_phs.items() if k != 'sim'}
])

# Select and order columns for display
display_cols = ['Option', 'CAPEX (₦M)', 'Total Lifecycle Cost (₦M)', 'LCOE (₦/kWh)',
                'Reliability (%)', 'CO₂ (tonnes/yr)']
comparison_display = comparison[display_cols].round({
    'CAPEX (₦M)': 1,
    'Total Lifecycle Cost (₦M)': 1,
    'LCOE (₦/kWh)': 0,
    'Reliability (%)': 1,
    'CO₂ (tonnes/yr)': 1
})

print("\n" + "="*60)
print("COMPARISON TABLE")
print("="*60)
print(comparison_display.to_string(index=False))

# Save comparison to CSV
comparison.to_csv('rural_electrification_comparison.csv', index=False)

# ============================================================================
# STEP 7 — VISUALIZATIONS
# ============================================================================

# Chart 1: Load vs supply for each option (one subplot per option)
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

# Option A: Grid (just load and grid availability? We'll plot load only)
# Option A: Grid (just plot load and note availability)
axes[0].plot(hours, load_kw, 'k-', linewidth=2, label='Load')
axes[0].text(0.5, 0.95, f'Grid availability: {grid_availability*100:.0f}%',
             transform=axes[0].transAxes, ha='center', va='top',
             bbox=dict(facecolor='white', alpha=0.8))
axes[0].set_title('Option A: Grid Extension')
axes[0].set_ylabel('Power (kW)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Option B: Solar+Battery
sim_b = res_battery['sim']
axes[1].plot(hours, load_kw, 'k-', linewidth=2, label='Load')
axes[1].plot(hours, sim_b['solar_gen'], 'y-', linewidth=2, label='Solar generation')
axes[1].bar(hours, -sim_b['charge'], color='green', alpha=0.5, label='Battery charge')
axes[1].bar(hours, sim_b['discharge'], color='blue', alpha=0.5, label='Battery discharge')
axes[1].set_title('Option B: Solar + Battery Mini-Grid')
axes[1].set_ylabel('Power (kW)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Option C: Solar+PHS
sim_c = res_phs['sim']
axes[2].plot(hours, load_kw, 'k-', linewidth=2, label='Load')
axes[2].plot(hours, sim_c['solar_gen'], 'y-', linewidth=2, label='Solar generation')
axes[2].bar(hours, -sim_c['charge'], color='green', alpha=0.5, label='Pump (charge)')
axes[2].bar(hours, sim_c['discharge'], color='blue', alpha=0.5, label='Turbine (discharge)')
axes[2].set_title('Option C: Solar + PHS Mini-Grid')
axes[2].set_xlabel('Hour of day')
axes[2].set_ylabel('Power (kW)')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('rural_electrification_load_supply.png', dpi=150)
plt.show()

# Chart 2: Cost breakdown (CAPEX, O&M, diesel, replacement)
options = ['Grid', 'Solar+Battery', 'Solar+PHS']
capex = [res_grid['CAPEX (₦M)'], res_battery['CAPEX (₦M)'], res_phs['CAPEX (₦M)']]
om_annual = [res_grid['Annual OM (₦M)'], res_battery['Annual OM (₦M)'], res_phs['Annual OM (₦M)']]
diesel_annual = [0, res_battery['Diesel Backup Annual (₦M)'], res_phs['Diesel Backup Annual (₦M)']]
battery_replacement = [0, res_battery.get('Battery Replacement (₦M)', 0), 0]

# Convert to total lifecycle cost components
# For grid, annual energy cost is not in om_annual? We already included in total lifecycle.
# We'll just plot total lifecycle cost per option.
fig, ax = plt.subplots(figsize=(10,6))
x = np.arange(len(options))
width = 0.35
ax.bar(x, capex, width, label='CAPEX', color='navy')
ax.bar(x, [res_grid['Total Lifecycle Cost (₦M)'] - capex[0],
           res_battery['Total Lifecycle Cost (₦M)'] - capex[1],
           res_phs['Total Lifecycle Cost (₦M)'] - capex[2]],
       width, bottom=capex, label='Other (O&M, diesel, replacement)', color='orange')
ax.set_xlabel('Option')
ax.set_ylabel('Cost (₦M)')
ax.set_title('Total Lifecycle Cost Breakdown (20 years)')
ax.set_xticks(x)
ax.set_xticklabels(options)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('rural_electrification_cost_breakdown.png', dpi=150)
plt.show()

# Chart 3: CO2 emissions
fig, ax = plt.subplots(figsize=(8,5))
co2 = [res_grid['CO₂ (tonnes/yr)'], res_battery['CO₂ (tonnes/yr)'], res_phs['CO₂ (tonnes/yr)']]
ax.bar(options, co2, color=['red', 'green', 'blue'])
ax.set_ylabel('CO₂ emissions (tonnes/year)')
ax.set_title('Annual CO₂ Emissions by Option')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('rural_electrification_co2.png', dpi=150)
plt.show()

# ============================================================================
# STEP 8 — RECOMMENDATIONS
# ============================================================================

# Find best in each category
best_reliability = max(comparison.to_dict('records'), key=lambda x: x['Reliability (%)'])
best_lcoe = min(comparison.to_dict('records'), key=lambda x: x['LCOE (₦/kWh)'])
lowest_co2 = min(comparison.to_dict('records'), key=lambda x: x['CO₂ (tonnes/yr)'])

recommendation_text = f"""
RURAL ELECTRIFICATION SCENARIO - RECOMMENDATIONS
================================================

Community: 75 households + school + health center + market
Daily energy demand: {total_daily_energy:.0f} kWh
Peak load: {peak_load:.1f} kW

COMPARISON SUMMARY:
-------------------
{comparison_display.to_string(index=False)}

KEY FINDINGS:
-------------
- Most reliable: {best_reliability['Option']} ({best_reliability['Reliability (%)']:.1f}%)
- Lowest LCOE: {best_lcoe['Option']} (₦{best_lcoe['LCOE (₦/kWh)']:.0f}/kWh)
- Lowest CO₂: {lowest_co2['Option']} ({lowest_co2['CO₂ (tonnes/yr)']:.1f} tonnes/yr)

RECOMMENDATION:
---------------
Based on the analysis, the recommended solution is:

"""

# Decision logic: if grid reliability is very low (<70%) and mini-grids are cost-competitive, recommend mini-grid.
if res_grid['Reliability (%)'] < 70 and res_battery['LCOE (₦/kWh)'] < res_grid['LCOE (₦/kWh)'] * 1.2:
    if res_battery['LCOE (₦/kWh)'] < res_phs['LCOE (₦/kWh)']:
        recommendation_text += "SOLAR + BATTERY MINI-GRID\n\n"
        recommendation_text += "Why: It offers high reliability (≥98%), zero direct emissions, and a competitive LCOE. "
        recommendation_text += "Battery technology is mature, easy to maintain, and scalable. "
        recommendation_text += "The small amount of diesel backup for unmet load keeps emissions low."
    else:
        recommendation_text += "SOLAR + PUMPED HYDRO STORAGE (PHS) MINI-GRID\n\n"
        recommendation_text += "Why: It provides very low LCOE, zero emissions, and long asset life. "
        recommendation_text += "If suitable topography exists, PHS avoids battery replacement costs and offers durable storage."
else:
    recommendation_text += "GRID EXTENSION\n\n"
    recommendation_text += "Why: If the grid is reasonably reliable (>70%) and extension cost is not prohibitive, "
    recommendation_text += "it offers the simplest solution with no on-site generation maintenance. "
    recommendation_text += "However, emissions are high, and long-term tariff escalation may erode savings."

recommendation_text += """
ADDITIONAL INSIGHTS:
--------------------
- **Feasibility:** Solar+battery is easiest to deploy anywhere; PHS requires specific terrain.
- **Scalability:** Both mini-grids can be expanded with additional solar panels.
- **Community acceptance:** Solar+battery is well understood; PHS may need education.
- **Maintenance:** Battery needs replacement every 10 years; PHS has minimal maintenance but civil works monitoring.

NEXT STEPS:
-----------
1. Conduct site survey for PHS feasibility.
2. Perform detailed financial analysis with actual quotes.
3. Engage community for load validation and willingness-to-pay.
4. Apply for rural electrification funding (REA, World Bank).

PORTFOLIO VALUE STATEMENT:
--------------------------
'Simulated rural electrification scenarios for a 75‑household community with community loads,
comparing grid extension, solar+battery mini-grid, and solar+PHS mini-grid. The analysis
incorporated load profiling, system sizing, hourly simulation, lifecycle cost, and CO₂ emissions.
Recommended the optimal solution based on reliability, cost, and sustainability.'
"""

with open('recommendations.txt', 'w', encoding='utf-8') as f:
    f.write(recommendation_text)

print("\nRecommendations saved to recommendations.txt")
print("\n" + "="*60)
print("DAY 15 COMPLETE")
print("="*60)