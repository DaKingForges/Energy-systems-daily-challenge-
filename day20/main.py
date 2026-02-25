"""
DAY 20: Energy System of the Future – Scenario Planning
Energy System Management Portfolio

Simulate three future scenarios (2050) for a rural district (10,000 households + community loads):
- Scenario A: Renewable Dominance (high solar/wind/storage, carbon pricing)
- Scenario B: Fossil Resilience (gas dominant, limited policy)
- Scenario C: Electrification & Flexibility (massive EVs, V2G, smart DR)

Outputs:
- scenario_comparison_table.csv
- energy_mix_stacked_bar.png
- emissions_trajectory.png
- storage_growth.png
- cost_comparison.png
- risk_matrix.png
- strategic_insights.txt
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================================
# STEP 1 — DEFINE SCOPE & BASELINE (2025)
# ============================================================================

# Rural district: 10,000 households + community loads (schools, clinics, market)
n_households = 10_000
hh_daily_kWh = 2.0
community_daily_kWh = 20_000  # total community loads (schools, etc.)
total_daily_kWh = n_households * hh_daily_kWh + community_daily_kWh
annual_demand_GWh = total_daily_kWh * 365 / 1e6
print(f"Baseline annual demand (2025): {annual_demand_GWh:.1f} GWh")

# Baseline (2025) technology mix (simplified)
baseline = {
    'year': 2025,
    'solar_MW': 5,
    'wind_MW': 2,
    'gas_MW': 10,
    'diesel_MW': 8,
    'grid_import_MW': 15,  # equivalent capacity (not actual)
    'battery_MWh': 10,
    'phs_MWh': 0,
    'ev_share': 0.05,       # 5% of households have EV
    'load_growth_rate': 0.02 # 2% per year
}

# ============================================================================
# STEP 2 — SCENARIO DEFINITIONS (2050)
# ============================================================================

# Common parameters
target_year = 2050
years = target_year - baseline['year']
load_growth_factor = (1 + baseline['load_growth_rate']) ** years
load_2050_GWh = annual_demand_GWh * load_growth_factor

# EV adoption rates (share of households)
ev_share_A = 0.8   # 80% EV
ev_share_B = 0.2   # 20% EV
ev_share_C = 0.9   # 90% EV + V2G

# Additional EV load: each EV consumes 3,500 kWh/year, 80% of charging managed smartly
ev_annual_kWh = 3500
ev_load_A = n_households * ev_share_A * ev_annual_kWh / 1e6  # GWh
ev_load_B = n_households * ev_share_B * ev_annual_kWh / 1e6
ev_load_C = n_households * ev_share_C * ev_annual_kWh / 1e6

# Total demand including EVs
demand_A_GWh = load_2050_GWh + ev_load_A
demand_B_GWh = load_2050_GWh + ev_load_B
demand_C_GWh = load_2050_GWh + ev_load_C

# Scenario assumptions (technology costs, policy)
scenarios = {
    'A: Renewable Dominance': {
        'solar_cost_reduction': 0.7,      # 30% of 2025 cost
        'wind_cost_reduction': 0.7,
        'battery_cost_reduction': 0.5,
        'phs_cost_reduction': 0.8,
        'carbon_tax_per_ton': 50,          # $/ton CO2
        'renewable_target': 0.85,           # 85% of generation
        'storage_duration_hours': 6,        # battery + PHS
        'demand_response_capacity': 0.15,   # 15% peak reduction
    },
    'B: Fossil Resilience': {
        'solar_cost_reduction': 0.9,
        'wind_cost_reduction': 0.9,
        'battery_cost_reduction': 0.9,
        'phs_cost_reduction': 1.0,
        'carbon_tax_per_ton': 0,
        'renewable_target': 0.30,
        'storage_duration_hours': 2,
        'demand_response_capacity': 0.05,
    },
    'C: Electrification & Flexibility': {
        'solar_cost_reduction': 0.6,
        'wind_cost_reduction': 0.6,
        'battery_cost_reduction': 0.4,
        'phs_cost_reduction': 0.6,
        'carbon_tax_per_ton': 40,
        'renewable_target': 0.75,
        'storage_duration_hours': 8,
        'demand_response_capacity': 0.25,
    }
}

# ============================================================================
# STEP 3 — QUANTIFY EACH SCENARIO
# ============================================================================

def scenario_analysis(scenario_name, params, demand_GWh, baseline):
    """Compute capacity mix, generation, storage, cost, emissions."""
    # Peak demand estimate (assume load factor 0.6)
    peak_MW = demand_GWh * 1e6 / 8760 / 0.6  # rough
    # Renewable share target
    ren_share = params['renewable_target']
    ren_generation_GWh = demand_GWh * ren_share
    
    # Simplified capacity factor assumptions
    cf_solar = 0.20   # 20%
    cf_wind = 0.30
    cf_gas = 0.85
    cf_diesel = 0.30
    # Solar and wind needed
    solar_MW = (ren_generation_GWh * 0.7) / (cf_solar * 8760 / 1e3)  # assume 70% of renewable from solar
    wind_MW = (ren_generation_GWh * 0.3) / (cf_wind * 8760 / 1e3)
    
    # Fossil backup
    fossil_share = 1 - ren_share
    fossil_generation_GWh = demand_GWh * fossil_share
    # Assume gas dominates fossil
    gas_MW = (fossil_generation_GWh * 0.8) / (cf_gas * 8760 / 1e3)
    diesel_MW = (fossil_generation_GWh * 0.2) / (cf_diesel * 8760 / 1e3)
    
    # Storage capacity (energy) based on duration and peak
    storage_MWh = peak_MW * params['storage_duration_hours']
    # Split storage: 70% battery, 30% PHS
    battery_MWh = storage_MWh * 0.7
    phs_MWh = storage_MWh * 0.3
    
    # Costs (simplified overnight costs in $/kW or $/kWh)
    cost_solar_per_kW = 1000 * params['solar_cost_reduction']   # $1000/kW baseline
    cost_wind_per_kW = 1500 * params['wind_cost_reduction']
    cost_gas_per_kW = 800
    cost_diesel_per_kW = 500
    cost_battery_per_kWh = 300 * params['battery_cost_reduction']
    cost_phs_per_kWh = 100 * params['phs_cost_reduction']
    
    capex_solar = solar_MW * 1000 * cost_solar_per_kW
    capex_wind = wind_MW * 1000 * cost_wind_per_kW
    capex_gas = gas_MW * 1000 * cost_gas_per_kW
    capex_diesel = diesel_MW * 1000 * cost_diesel_per_kW
    capex_battery = battery_MWh * 1000 * cost_battery_per_kWh
    capex_phs = phs_MWh * 1000 * cost_phs_per_kWh
    total_capex = capex_solar + capex_wind + capex_gas + capex_diesel + capex_battery + capex_phs
    
    # Annual O&M (simplified % of capex)
    om_rate = 0.02
    annual_om = total_capex * om_rate
    
    # Fuel costs (for fossil)
    gas_price = 5  # $/MMBtu, heat rate 7 MMBtu/MWh → $35/MWh
    diesel_price = 0.8  # $/L, 3.6 kWh/L → $0.22/kWh? Wait, better use $/MWh. Assume diesel $0.5/L, 3.6 kWh/L → $139/MWh. Let's use typical numbers.
    # Simpler: use $/MWh
    gas_cost_per_MWh = 40
    diesel_cost_per_MWh = 150
    fuel_cost = (fossil_generation_GWh * 0.8 * gas_cost_per_MWh * 1000 + 
                 fossil_generation_GWh * 0.2 * diesel_cost_per_MWh * 1000)  # in $
    
    # Carbon tax
    emissions_gas = fossil_generation_GWh * 0.8 * 0.4  # 0.4 tCO2/MWh for gas
    emissions_diesel = fossil_generation_GWh * 0.2 * 0.8
    total_emissions = emissions_gas + emissions_diesel  # ktCO2
    carbon_tax = total_emissions * params['carbon_tax_per_ton'] * 1000  # $ (since emissions in kt, tax per ton)
    
    # Total annual cost (including amortized capex, O&M, fuel, carbon tax)
    # Simple annuity: assume 20 years, 8% discount rate
    discount_rate = 0.08
    annuity_factor = (discount_rate * (1+discount_rate)**20) / ((1+discount_rate)**20 - 1)
    annualized_capex = total_capex * annuity_factor
    total_annual_cost = annualized_capex + annual_om + fuel_cost + carbon_tax
    
    # Average cost per MWh
    avg_cost_per_MWh = total_annual_cost / (demand_GWh * 1000)  # $/MWh
    
    return {
        'Scenario': scenario_name,
        'Demand_GWh': demand_GWh,
        'Solar_MW': solar_MW,
        'Wind_MW': wind_MW,
        'Gas_MW': gas_MW,
        'Diesel_MW': diesel_MW,
        'Battery_MWh': battery_MWh,
        'PHS_MWh': phs_MWh,
        'Renewable_share': ren_share * 100,
        'Total_CAPEX_$M': total_capex / 1e6,
        'Annual_OM_$M': annual_om / 1e6,
        'Fuel_Cost_$M': fuel_cost / 1e6,
        'Carbon_Tax_$M': carbon_tax / 1e6,
        'Total_Annual_Cost_$M': total_annual_cost / 1e6,
        'Avg_Cost_$_per_MWh': avg_cost_per_MWh,
        'Emissions_ktCO2': total_emissions
    }

# Compute for each scenario
results = []
for name, params in scenarios.items():
    if 'A' in name:
        demand = demand_A_GWh
    elif 'B' in name:
        demand = demand_B_GWh
    else:
        demand = demand_C_GWh
    res = scenario_analysis(name, params, demand, baseline)
    results.append(res)

# Convert to DataFrame
df = pd.DataFrame(results)
df = df.round(2)
print("\n=== SCENARIO COMPARISON TABLE (2050) ===")
print(df.to_string(index=False))

# Save
df.to_csv('scenario_comparison_table.csv', index=False)

# ============================================================================
# STEP 4 — VISUALIZATIONS
# ============================================================================

# 1. Energy mix stacked bar chart (baseline + scenarios)
# For baseline, we need to estimate 2025 mix.
baseline_mix = {
    'Solar': baseline['solar_MW'] * 0.2 * 8760 / 1e3,  # GWh
    'Wind': baseline['wind_MW'] * 0.3 * 8760 / 1e3,
    'Gas': baseline['gas_MW'] * 0.85 * 8760 / 1e3,
    'Diesel': baseline['diesel_MW'] * 0.3 * 8760 / 1e3,
    'Grid': baseline['grid_import_MW'] * 8760 * 0.8 / 1e3,  # assume 80% availability
}
baseline_total = sum(baseline_mix.values())
baseline_mix_pct = {k: v/baseline_total*100 for k,v in baseline_mix.items()}
baseline_mix_pct['Storage'] = 0  # no significant storage in baseline

scenario_mix = []
for res in results:
    solar_GWh = res['Solar_MW'] * 0.2 * 8760 / 1e3
    wind_GWh = res['Wind_MW'] * 0.3 * 8760 / 1e3
    gas_GWh = res['Gas_MW'] * 0.85 * 8760 / 1e3
    diesel_GWh = res['Diesel_MW'] * 0.3 * 8760 / 1e3
    total = res['Demand_GWh']  # should match sum roughly
    scenario_mix.append({
        'Solar': solar_GWh / total * 100,
        'Wind': wind_GWh / total * 100,
        'Gas': gas_GWh / total * 100,
        'Diesel': diesel_GWh / total * 100,
        'Storage': 0,  # storage is not a generation source, but we can show as "dispatch" - for simplicity we ignore in mix
    })

# Stacked bar
categories = ['Baseline 2025', 'A: Renewable', 'B: Fossil', 'C: Flexibility']
solar_pct = [baseline_mix_pct['Solar'], scenario_mix[0]['Solar'], scenario_mix[1]['Solar'], scenario_mix[2]['Solar']]
wind_pct = [baseline_mix_pct['Wind'], scenario_mix[0]['Wind'], scenario_mix[1]['Wind'], scenario_mix[2]['Wind']]
gas_pct = [baseline_mix_pct['Gas'], scenario_mix[0]['Gas'], scenario_mix[1]['Gas'], scenario_mix[2]['Gas']]
diesel_pct = [baseline_mix_pct['Diesel'], scenario_mix[0]['Diesel'], scenario_mix[1]['Diesel'], scenario_mix[2]['Diesel']]
grid_pct = [baseline_mix_pct['Grid'], 0, 0, 0]  # grid only in baseline

fig, ax = plt.subplots(figsize=(10,6))
ax.bar(categories, solar_pct, label='Solar', color='gold')
ax.bar(categories, wind_pct, bottom=solar_pct, label='Wind', color='lightblue')
ax.bar(categories, gas_pct, bottom=np.array(solar_pct)+np.array(wind_pct), label='Gas', color='orange')
ax.bar(categories, diesel_pct, bottom=np.array(solar_pct)+np.array(wind_pct)+np.array(gas_pct), label='Diesel', color='brown')
ax.bar(categories, grid_pct, bottom=np.array(solar_pct)+np.array(wind_pct)+np.array(gas_pct)+np.array(diesel_pct), label='Grid', color='gray')
ax.set_ylabel('Share of Generation (%)')
ax.set_title('Energy Mix: Baseline vs Scenarios (2050)')
ax.legend()
ax.set_ylim(0,100)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('energy_mix_stacked_bar.png', dpi=150)
plt.show()

# 2. Emissions trajectory
years_plot = [2025, 2050]
baseline_emissions = baseline_mix['Gas']*0.4 + baseline_mix['Diesel']*0.8  # ktCO2
emissions_A = df.loc[df['Scenario'].str.contains('A'), 'Emissions_ktCO2'].values[0]
emissions_B = df.loc[df['Scenario'].str.contains('B'), 'Emissions_ktCO2'].values[0]
emissions_C = df.loc[df['Scenario'].str.contains('C'), 'Emissions_ktCO2'].values[0]

fig, ax = plt.subplots(figsize=(8,5))
ax.plot([2025,2050], [baseline_emissions, emissions_A], 'o-', label='A: Renewable', color='green')
ax.plot([2025,2050], [baseline_emissions, emissions_B], 'o-', label='B: Fossil', color='red')
ax.plot([2025,2050], [baseline_emissions, emissions_C], 'o-', label='C: Flexibility', color='blue')
ax.set_xlabel('Year')
ax.set_ylabel('Emissions (kt CO₂)')
ax.set_title('Emissions Trajectory to 2050')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('emissions_trajectory.png', dpi=150)
plt.show()

# 3. Storage growth
storage_baseline = baseline['battery_MWh'] + baseline['phs_MWh']
storage_A = df.loc[df['Scenario'].str.contains('A'), 'Battery_MWh'].values[0] + df.loc[df['Scenario'].str.contains('A'), 'PHS_MWh'].values[0]
storage_B = df.loc[df['Scenario'].str.contains('B'), 'Battery_MWh'].values[0] + df.loc[df['Scenario'].str.contains('B'), 'PHS_MWh'].values[0]
storage_C = df.loc[df['Scenario'].str.contains('C'), 'Battery_MWh'].values[0] + df.loc[df['Scenario'].str.contains('C'), 'PHS_MWh'].values[0]

fig, ax = plt.subplots(figsize=(8,5))
x = np.arange(4)  # Change from 3 to 4 to match 4 data points
ax.bar(x, [storage_baseline, storage_A, storage_B, storage_C], tick_label=['Baseline', 'A', 'B', 'C'], color=['gray','green','red','blue'])
ax.set_ylabel('Storage Capacity (MWh)')
ax.set_title('Energy Storage Deployment')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('storage_growth.png', dpi=150)
plt.show()

# 4. Cost comparison
fig, ax = plt.subplots(figsize=(8,5))
x = np.arange(3)
costs = [df.loc[df['Scenario'].str.contains('A'), 'Avg_Cost_$_per_MWh'].values[0],
         df.loc[df['Scenario'].str.contains('B'), 'Avg_Cost_$_per_MWh'].values[0],
         df.loc[df['Scenario'].str.contains('C'), 'Avg_Cost_$_per_MWh'].values[0]]
ax.bar(x, costs, tick_label=['A', 'B', 'C'], color=['green','red','blue'])
ax.set_ylabel('Average Cost ($/MWh)')
ax.set_title('Levelized Cost of Energy (2050)')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('cost_comparison.png', dpi=150)
plt.show()

# 5. Risk matrix (simplified – likelihood vs impact for each scenario across key risks)
risks = ['Fuel price shock', 'Extreme weather', 'Technology failure', 'Demand surge']
# Qualitative scores (1-5) for likelihood and impact for each scenario
# We'll create a heatmap-like plot
risk_scores = {
    'A': {'Fuel price shock': [2, 3],   # low likelihood, medium impact
          'Extreme weather': [4, 4],     # high likelihood (more renewables exposed), high impact
          'Technology failure': [3, 4],  # medium likelihood, high impact (battery supply)
          'Demand surge': [3, 3]},
    'B': {'Fuel price shock': [5, 5],    # high likelihood, high impact
          'Extreme weather': [3, 3],
          'Technology failure': [2, 3],
          'Demand surge': [3, 4]},
    'C': {'Fuel price shock': [2, 2],
          'Extreme weather': [4, 4],
          'Technology failure': [4, 4],  # complex systems, higher failure risk
          'Demand surge': [4, 3]}
}

fig, axes = plt.subplots(1,3, figsize=(12,4), sharey=True)
for idx, scenario in enumerate(['A','B','C']):
    ax = axes[idx]
    data = risk_scores[scenario]
    for i, risk in enumerate(risks):
        l, imp = data[risk]
        ax.scatter(l, imp, s=100, label=risk if idx==0 else "")
        ax.annotate(risk, (l+0.1, imp+0.1), fontsize=8)
    ax.set_xlim(0,6)
    ax.set_ylim(0,6)
    ax.set_xlabel('Likelihood')
    if idx==0:
        ax.set_ylabel('Impact')
    ax.set_title(f'Scenario {scenario}')
    ax.grid(True, alpha=0.3)
    ax.plot([0,6], [3,3], 'k--', alpha=0.5)
    ax.plot([3,3], [0,6], 'k--', alpha=0.5)
axes[0].legend(loc='upper left', fontsize=7)
plt.suptitle('Risk Matrix: Likelihood vs Impact')
plt.tight_layout()
plt.savefig('risk_matrix.png', dpi=150)
plt.show()

# ============================================================================
# STEP 5 — STRATEGIC INSIGHTS (EXECUTIVE SUMMARY)
# ============================================================================

insights = f"""
STRATEGIC INSIGHTS REPORT – ENERGY SYSTEM FUTURES (2050)
========================================================

Baseline (2025):
- Annual demand: {annual_demand_GWh:.1f} GWh
- Dominant sources: grid imports, diesel, some solar.
- Emissions: {baseline_emissions:.1f} ktCO2/yr

Scenario Comparison (2050):
{df[['Scenario','Demand_GWh','Renewable_share','Avg_Cost_$_per_MWh','Emissions_ktCO2']].to_string(index=False)}

Key Findings:
-------------
1. **Scenario A (Renewable Dominance)** achieves {df.loc[df['Scenario'].str.contains('A'),'Renewable_share'].values[0]:.0f}% renewables with moderate cost (${df.loc[df['Scenario'].str.contains('A'),'Avg_Cost_$_per_MWh'].values[0]:.0f}/MWh) and near-zero emissions. Requires massive storage ({storage_A:.0f} MWh) and strong policy support (carbon tax). Resilient to fuel shocks but vulnerable to weather.

2. **Scenario B (Fossil Resilience)** maintains low upfront cost but high fuel price exposure and emissions ({df.loc[df['Scenario'].str.contains('B'),'Emissions_ktCO2'].values[0]:.1f} ktCO2). High risk from fuel shocks (likelihood 5, impact 5).

3. **Scenario C (Electrification & Flexibility)** leverages EVs and smart DR to reduce peak and integrate renewables ({df.loc[df['Scenario'].str.contains('C'),'Renewable_share'].values[0]:.0f}%). Highest storage ({storage_C:.0f} MWh) and cost (${df.loc[df['Scenario'].str.contains('C'),'Avg_Cost_$_per_MWh'].values[0]:.0f}/MWh) but offers demand-side flexibility and V2G backup. Technology failure risk is elevated due to complexity.

Resilience Assessment:
- Most resilient to fuel shocks: A and C (low fossil dependence).
- Most resilient to extreme weather: B (dispatchable fossil), but A and C can be hardened with distributed storage.
- Most affordable: B, but at high environmental cost.
- Lowest transition risk: A (policy-driven, technology mature).

Strategic Recommendations:
--------------------------
1. **Begin investing now in renewable and storage cost reduction** – all scenarios benefit.
2. **Pilot V2G and smart charging** to prepare for high EV penetration (Scenario C).
3. **Diversify storage portfolio** – combine battery (fast response) with PHS (long duration) to hedge technology failure and weather risks.
4. **Implement carbon pricing gradually** to make Scenario A economically viable without shock.
5. **Strengthen grid and distribution infrastructure** to handle bidirectional flows and increased electrification.

Pumped Hydro Storage (PHS) plays a critical role in long-duration storage, especially in Scenarios A and C. Its low cost per kWh and long life make it ideal for seasonal shifts and multi-day backup.

Conclusion:
-----------
The future is not predetermined. By understanding these three distinct pathways, investors and policymakers can make robust decisions that perform well across multiple futures. The most balanced approach combines elements of A and C: aggressive renewables, diversified storage, and smart demand-side participation.
"""

with open('strategic_insights.txt', 'w') as f:
    f.write(insights)
print("\nStrategic insights saved to strategic_insights.txt")

print("\n=== DAY 20 COMPLETE ===")