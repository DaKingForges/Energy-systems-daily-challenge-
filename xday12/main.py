import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Load Day 1 household profile (representative 24h in kW) ---
# This is the profile from Day 1 (hourly averages)
household_base = np.array([
    0.8, 0.7, 0.6, 0.5, 0.6, 1.2, 2.5, 3.8, 4.2, 3.5, 2.8, 2.2,
    2.0, 1.8, 1.9, 2.3, 3.5, 4.8, 5.5, 5.2, 4.5, 3.2, 2.0, 1.2
])  # kW, hour 0 to 23

# Create 30 households with realistic variation
np.random.seed(42)
n_households = 30
hourly_loads = []
for i in range(n_households):
    variation = np.random.normal(1.0, 0.15, size=24)  # ±15% variation
    load = household_base * variation
    # Ensure no negative values
    load = np.maximum(load, 0.1)
    hourly_loads.append(load)

community_load_original = np.sum(hourly_loads, axis=0)  # total kW per hour

# --- Define shiftable load per household (fraction of total) ---
# Assume 20% of each hour is shiftable, but concentrated in appliances
# For simplicity, we create a shiftable mask: higher during peaks
shiftable_fraction = np.zeros(24)
shiftable_fraction[6:10] = 0.3    # morning peak
shiftable_fraction[17:22] = 0.4   # evening peak
shiftable_fraction[10:17] = 0.1   # day
shiftable_fraction[22:24] = 0.05  # night
shiftable_fraction[0:6] = 0.02    # early morning

# Total shiftable energy per household
shiftable_energy_original = community_load_original * shiftable_fraction

# --- Target hours for shifting (off-peak + solar) ---
target_hours = list(range(22,24)) + list(range(0,5)) + list(range(9,17))  # 22-23,0-4,9-16
# Map each peak hour to the nearest target hour (simple logic: shift to earliest available)
shift_map = {}
for h in range(24):
    if shiftable_fraction[h] > 0.1 and h not in target_hours:
        # find nearest target hour (circular)
        candidates = target_hours
        distances = [min(abs(h-t), 24-abs(h-t)) for t in candidates]
        nearest = candidates[np.argmin(distances)]
        shift_map[h] = nearest
    else:
        shift_map[h] = h  # no shift

# Build shifted load profile
community_load_shifted = community_load_original.copy()
shifted_energy = np.zeros(24)

for h_from, h_to in shift_map.items():
    if h_from != h_to:
        energy_to_move = shiftable_energy_original[h_from] * 0.8  # move 80% of shiftable
        community_load_shifted[h_from] -= energy_to_move
        community_load_shifted[h_to] += energy_to_move
        shifted_energy[h_from] = energy_to_move

# --- Tariff and cost calculation ---
def tou_tariff(hour):
    if 22 <= hour or hour < 5:
        return 50   # off-peak
    elif 5 <= hour < 17 or (21 <= hour < 22):
        return 80   # mid-peak
    else:  # 17-21
        return 150  # on-peak

tariff = np.array([tou_tariff(h) for h in range(24)])
demand_charge_rate = 5000  # ₦ per kW of monthly peak

# Daily energy cost (excluding demand charge for now)
cost_original = np.sum(community_load_original * tariff)
cost_shifted = np.sum(community_load_shifted * tariff)

# Peak demand (kW)
peak_original = np.max(community_load_original)
peak_shifted = np.max(community_load_shifted)

# Demand charge (monthly, but we can show daily equivalent)
demand_charge_original = peak_original * demand_charge_rate / 30  # daily approx
demand_charge_shifted = peak_shifted * demand_charge_rate / 30

total_daily_cost_original = cost_original + demand_charge_original
total_daily_cost_shifted = cost_shifted + demand_charge_shifted

# --- Results ---
print("Original peak: {:.2f} kW".format(peak_original))
print("Shifted peak: {:.2f} kW".format(peak_shifted))
print("Peak reduction: {:.2f} kW ({:.1f}%)".format(
    peak_original - peak_shifted, 100*(peak_original - peak_shifted)/peak_original))
print("\nDaily energy cost (excluding demand):")
print("  Original: ₦{:.0f}".format(cost_original))
print("  Shifted:  ₦{:.0f}".format(cost_shifted))
print("  Savings:  ₦{:.0f} ({:.1f}%)".format(
    cost_original - cost_shifted, 100*(cost_original - cost_shifted)/cost_original))
print("\nDaily demand charge (pro-rated):")
print("  Original: ₦{:.0f}".format(demand_charge_original))
print("  Shifted:  ₦{:.0f}".format(demand_charge_shifted))
print("  Savings:  ₦{:.0f}".format(demand_charge_original - demand_charge_shifted))
print("\nTotal daily cost (energy + demand):")
print("  Original: ₦{:.0f}".format(total_daily_cost_original))
print("  Shifted:  ₦{:.0f}".format(total_daily_cost_shifted))
print("  Savings:  ₦{:.0f} ({:.1f}%)".format(
    total_daily_cost_original - total_daily_cost_shifted,
    100*(total_daily_cost_original - total_daily_cost_shifted)/total_daily_cost_original))

# Annual savings
annual_savings = (total_daily_cost_original - total_daily_cost_shifted) * 365
print("\nAnnual savings: ₦{:.0f}".format(annual_savings))

# --- Plot ---
hours = np.arange(24)
plt.figure(figsize=(12,5))
plt.plot(hours, community_load_original, 'o-', label='Original load', linewidth=2)
plt.plot(hours, community_load_shifted, 's-', label='Shifted load', linewidth=2)
plt.axvspan(17, 21, alpha=0.2, color='red', label='On-peak')
plt.axvspan(6, 9, alpha=0.2, color='orange', label='Morning peak')
plt.axvspan(22, 24, alpha=0.1, color='green', label='Off-peak')
plt.axvspan(0, 5, alpha=0.1, color='green')
plt.axvspan(9, 16, alpha=0.1, color='yellow', label='Solar hours')
plt.xlabel('Hour of day')
plt.ylabel('Load (kW)')
plt.title('Community Load Shifting for Peak Reduction (30 households)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('load_shifting_community_peak_reduction.png', dpi=150)
plt.show()