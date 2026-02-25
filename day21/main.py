"""
DAY 21: Small Hydropower Potential Analysis
Energy System Management Portfolio

Conduct a feasibility study for a small hydropower site:
- Use realistic flow and head data (with assumptions)
- Calculate theoretical and practical power
- Select turbine type
- Estimate annual energy with seasonal variation
- Estimate CAPEX and LCOE
- Compare with diesel and solar+storage
- Discuss environmental and practical constraints

Outputs:
- hydropower_summary.csv
- seasonal_generation.png
- recommendations.txt
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================================
# STEP 1 — SITE SELECTION & PARAMETERS
# ============================================================================

# We choose a hypothetical but realistic site: a river in a rural region
# with moderate head and flow.

# River name (for context)
river_name = "Ogbomosho River Tributary"
location = "Oyo State, Nigeria"

# Head (H) in meters – from topographic survey or Google Earth estimation
head_m = 25  # meters (suitable for Francis turbine)

# Average flow rate (Q) in m³/s – from regional hydrological data
# Assume wet season (June–October) flow = 8 m³/s, dry season (Nov–May) = 2 m³/s
# For annual average, we compute weighted average.
wet_flow = 8.0      # m³/s
dry_flow = 2.0      # m³/s
wet_months = 5      # June to October
dry_months = 7
avg_flow = (wet_flow * wet_months + dry_flow * dry_months) / 12

# Seasonal flow array for monthly analysis
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
# Dry: Jan–May, Wet: Jun–Oct, Dry: Nov–Dec
monthly_flow = np.array([dry_flow]*5 + [wet_flow]*5 + [dry_flow]*2)

print("=== SITE DESCRIPTION ===")
print(f"River: {river_name}")
print(f"Location: {location}")
print(f"Head: {head_m} m")
print(f"Average annual flow: {avg_flow:.2f} m³/s")
print(f"Seasonal flow: Wet season ({wet_months} months) = {wet_flow} m³/s, Dry = {dry_flow} m³/s")

# ============================================================================
# STEP 2 — PHYSICAL CONSTANTS & EFFICIENCY
# ============================================================================

rho = 1000      # kg/m³ (water density)
g = 9.81        # m/s² (gravity)

# Efficiency chain
turbine_efficiency = 0.87      # Francis turbine typical
generator_efficiency = 0.95
system_losses = 0.03            # 3% losses in transformer/controls
overall_efficiency = turbine_efficiency * generator_efficiency * (1 - system_losses)

# ============================================================================
# STEP 3 — POWER CALCULATION
# ============================================================================

# Theoretical power (gross)
P_theoretical_kW = (rho * g * head_m * avg_flow) / 1000  # kW

# Actual power (net)
P_actual_kW = P_theoretical_kW * overall_efficiency

print("\n=== POWER CALCULATION ===")
print(f"Theoretical power: {P_theoretical_kW:.1f} kW")
print(f"Overall efficiency: {overall_efficiency*100:.1f}%")
print(f"Actual (net) power: {P_actual_kW:.1f} kW")

# ============================================================================
# STEP 4 — TURBINE SELECTION
# ============================================================================

# Based on head and flow, select turbine type
if head_m < 10:
    turbine_type = "Kaplan / Propeller"
elif head_m < 50:
    turbine_type = "Francis"
else:
    turbine_type = "Pelton"

turbine_justification = f"""
Head: {head_m} m → {turbine_type} turbine is appropriate.
- Francis turbines cover 10–50 m head efficiently.
- Expected efficiency: 85–90% at design flow.
- Suitable for medium-head sites with moderate flow variation.
"""

print("\n=== TURBINE SELECTION ===")
print(f"Selected turbine type: {turbine_type}")
print(turbine_justification)

# ============================================================================
# STEP 5 — ANNUAL ENERGY ESTIMATION
# ============================================================================

# Monthly power output based on flow (linear scaling with flow)
monthly_power_kW = monthly_flow / avg_flow * P_actual_kW

# Monthly energy (kWh) = power (kW) * hours in month
days_in_month = [31,28,31,30,31,30,31,31,30,31,30,31]
monthly_energy_kWh = monthly_power_kW * np.array(days_in_month) * 24

annual_energy_kWh = np.sum(monthly_energy_kWh)
annual_energy_GWh = annual_energy_kWh / 1e6

# Capacity factor
capacity_factor = annual_energy_kWh / (P_actual_kW * 8760)

print("\n=== ANNUAL ENERGY ESTIMATE ===")
print(f"Annual energy production: {annual_energy_kWh:.0f} kWh ({annual_energy_GWh:.2f} GWh)")
print(f"Capacity factor: {capacity_factor:.3f}")

# Create monthly energy table
monthly_df = pd.DataFrame({
    'Month': months,
    'Flow (m³/s)': monthly_flow,
    'Power (kW)': monthly_power_kW,
    'Days': days_in_month,
    'Energy (kWh)': monthly_energy_kWh
})
print("\nMonthly breakdown:")
print(monthly_df.round(1).to_string(index=False))

# Save monthly table
monthly_df.to_csv('hydropower_monthly.csv', index=False)

# Plot seasonal generation
plt.figure(figsize=(10,5))
plt.bar(months, monthly_energy_kWh/1000, color='skyblue', edgecolor='black')
plt.axhline(y=annual_energy_kWh/12/1000, color='red', linestyle='--', label='Monthly average')
plt.xlabel('Month')
plt.ylabel('Energy (MWh)')
plt.title(f'{river_name} – Monthly Hydropower Generation')
plt.legend()
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('seasonal_generation.png', dpi=150)
plt.show()

# ============================================================================
# STEP 6 — ECONOMIC ESTIMATION
# ============================================================================

# Installed cost per kW (typical small hydro range: $1500–$4000/kW)
# We'll use $2500/kW for a medium estimate.
cost_per_kW_usd = 2500  # USD
exchange_rate_ngn_usd = 1500  # ₦ per USD (approximate)

installed_capacity_kW = P_actual_kW  # we size to net power
capex_usd = installed_capacity_kW * cost_per_kW_usd
capex_ngn = capex_usd * exchange_rate_ngn_usd

# Annual O&M (typically 1–2% of CAPEX)
om_rate = 0.015
annual_om_usd = capex_usd * om_rate

# No fuel cost
fuel_cost_usd = 0

# Discount rate (real, for LCOE calculation)
discount_rate = 0.08
lifetime = 30  # years

# Simple LCOE calculation
# LCOE = (CAPEX + sum(OM/(1+r)^t)) / sum(Energy/(1+r)^t)
# We'll use annuity factor for simplicity: annualized cost / annual energy
annuity_factor = (discount_rate * (1+discount_rate)**lifetime) / ((1+discount_rate)**lifetime - 1)
annualized_capex_usd = capex_usd * annuity_factor
total_annual_cost_usd = annualized_capex_usd + annual_om_usd
lcoe_usd_per_kWh = total_annual_cost_usd / annual_energy_kWh
lcoe_ngn_per_kWh = lcoe_usd_per_kWh * exchange_rate_ngn_usd

print("\n=== ECONOMIC ESTIMATION ===")
print(f"Installed capacity: {installed_capacity_kW:.1f} kW")
print(f"CAPEX: ${capex_usd:,.0f} (₦{capex_ngn:,.0f})")
print(f"Annual O&M: ${annual_om_usd:,.0f}")
print(f"LCOE: ${lcoe_usd_per_kWh:.3f}/kWh (₦{lcoe_ngn_per_kWh:.0f}/kWh)")

# Comparison with diesel (from Day 2: ₦485/kWh) and solar+storage (from Day 3: ₦187/kWh)
diesel_lcoe_ngn = 485
solar_battery_lcoe_ngn = 187

print("\n=== COMPARISON WITH ALTERNATIVES ===")
print(f"Small Hydro LCOE: ₦{lcoe_ngn_per_kWh:.0f}/kWh")
print(f"Diesel Generator LCOE: ₦{diesel_lcoe_ngn}/kWh")
print(f"Solar + Battery LCOE: ₦{solar_battery_lcoe_ngn}/kWh")

if lcoe_ngn_per_kWh < diesel_lcoe_ngn:
    print("✓ Small hydro cheaper than diesel.")
else:
    print("✗ Small hydro more expensive than diesel.")

if lcoe_ngn_per_kWh < solar_battery_lcoe_ngn:
    print("✓ Small hydro cheaper than solar+battery.")
else:
    print("✗ Small hydro more expensive than solar+battery.")

# ============================================================================
# STEP 7 — ENVIRONMENTAL & PRACTICAL CONSTRAINTS
# ============================================================================

constraints = f"""
ENVIRONMENTAL & PRACTICAL CONSTRAINTS
======================================

1. Ecological flow: Minimum flow must be maintained downstream to preserve aquatic life.
   Typically 10–30% of average flow. This reduces available power during dry months.
   For this site, ecological flow requirement might be {0.2*avg_flow:.2f} m³/s, which is
   close to dry season flow ({dry_flow} m³/s). Potential conflict in dry months.

2. Sedimentation: Rivers carry sediment, especially in wet season. This can erode turbine
   blades and reduce reservoir capacity if a dam is built. Regular desilting or
   run-of-river design may be needed.

3. Community displacement: If a dam and reservoir are required, local communities may
   need relocation. Run-of-river schemes minimize this impact.

4. Access roads: Site may be remote; building access roads adds cost and environmental
   disturbance.

5. Grid interconnection: Distance to existing lines affects transmission cost.
   If >5 km, additional investment is needed.

6. Seasonal variability: Dry season output drops to {monthly_power_kW[4]:.1f} kW, only
   {monthly_power_kW[4]/P_actual_kW*100:.1f}% of wet season peak. This may require
   backup (diesel, battery) or hybridisation.

7. Permitting and water rights: Lengthy approval processes can delay projects.
"""

print("\n=== CONSTRAINTS ===")
print(constraints)

# ============================================================================
# STEP 8 — RECOMMENDATIONS (save to .txt)
# ============================================================================

recommendations = f"""
SMALL HYDROPOWER FEASIBILITY SUMMARY – {river_name}
======================================================

Site: {location}
Head: {head_m} m
Average flow: {avg_flow:.2f} m³/s

TECHNICAL SUMMARY
-----------------
- Installed capacity (net): {P_actual_kW:.1f} kW
- Annual energy: {annual_energy_GWh:.2f} GWh
- Capacity factor: {capacity_factor:.3f}
- Turbine type: {turbine_type} (justified by head range)

ECONOMIC SUMMARY
----------------
- CAPEX: ₦{capex_ngn:,.0f} (${capex_usd:,.0f})
- LCOE: ₦{lcoe_ngn_per_kWh:.0f}/kWh
- Comparison:
  • Diesel: ₦{diesel_lcoe_ngn}/kWh
  • Solar+battery: ₦{solar_battery_lcoe_ngn}/kWh
  • Small hydro is {'cheaper' if lcoe_ngn_per_kWh < diesel_lcoe_ngn else 'more expensive'} than diesel,
    and {'cheaper' if lcoe_ngn_per_kWh < solar_battery_lcoe_ngn else 'more expensive'} than solar+battery.

SEASONALITY
-----------
- Wet season (Jun–Oct): power up to {monthly_power_kW[5]:.1f} kW
- Dry season (Nov–May): power as low as {monthly_power_kW[4]:.1f} kW
- This variability suggests either:
  (a) Accept lower dry season output and use backup,
  (b) Add storage (small reservoir or battery) to shift wet season excess,
  (c) Hybridise with solar PV to complement dry season (sunny) periods.

RECOMMENDATION
--------------
1. **Immediate next step**: Conduct detailed flow measurements for at least one full year
   to confirm seasonal pattern. If actual dry season flow is significantly lower,
   project economics may worsen.

2. **Design choice**: A run-of-river scheme with a small weir (no large reservoir) is
   recommended to minimise environmental impact and cost. This will limit dry season output
   but avoids displacement.

3. **Hybridisation**: Pair with solar PV (e.g., 50 kWp) to supplement dry season generation.
   The solar profile complements hydro: solar produces more in dry (sunny) season when
   hydro is low. This could improve reliability and reduce battery needs.

4. **Grid connection**: Assess distance to nearest distribution line. If >5 km, factor in
   transmission cost (approx. $20,000/km) into CAPEX.

5. **Community engagement**: Early consultation with downstream communities regarding
   water access and ecological flow is essential.

6. **Funding**: Explore rural electrification grants (e.g., REA in Nigeria) that may cover
   part of the capital cost, improving LCOE.

CONCLUSION
----------
The site shows promising technical potential with competitive LCOE compared to diesel.
Seasonal variation is the main challenge, but hybridisation with solar can mitigate this.
A detailed feasibility study (hydrological, geotechnical, environmental) is warranted.

PORTFOLIO STATEMENT
-------------------
'Conducted a small hydropower resource assessment using realistic hydrological data,
calculated technical generation potential, selected appropriate turbine technology,
and evaluated economic and environmental feasibility, recommending hybridisation with
solar to address seasonal variability.'
"""

with open('recommendations.txt', 'w', encoding='utf-8') as f:
    f.write(recommendations)

print("\nRecommendations saved to recommendations.txt")

# Save summary CSV
summary = pd.DataFrame({
    'Parameter': ['Head (m)', 'Avg Flow (m³/s)', 'Installed Capacity (kW)', 'Annual Energy (GWh)',
                  'Capacity Factor', 'CAPEX (₦M)', 'LCOE (₦/kWh)', 'Turbine Type'],
    'Value': [head_m, avg_flow, P_actual_kW, annual_energy_GWh,
              capacity_factor, capex_ngn/1e6, lcoe_ngn_per_kWh, turbine_type]
})
summary.to_csv('hydropower_summary.csv', index=False)
print("\nSummary saved to hydropower_summary.csv")

print("\n=== DAY 21 COMPLETE ===")