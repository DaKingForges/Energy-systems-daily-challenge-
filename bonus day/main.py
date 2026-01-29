"""
DAY 9: Model Scenario Analysis - Restaurant Energy Efficiency Investments
This is a MODEL SCENARIO based on industry benchmarks and typical Lagos restaurant operations.
All numbers are illustrative examples for educational purposes.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')
mpl.rcParams['font.size'] = 9
mpl.rcParams['axes.titlesize'] = 11
mpl.rcParams['figure.figsize'] = [15, 9]

# ============================================================================
# 1. MODEL SCENARIO SETUP - "TYPICAL MEDIUM-SIZED LAGOS RESTAURANT"
# ============================================================================

def create_model_scenario():
    """
    Create a realistic but illustrative model scenario
    Based on industry benchmarks for 80-120 seat restaurants in urban Nigeria
    """
    
    print("=" * 100)
    print("MODEL SCENARIO: TYPICAL MEDIUM-SIZED LAGOS RESTAURANT")
    print("=" * 100)
    
    print("\n📊 THIS IS A MODEL SCENARIO - Illustrative Example for Educational Purposes")
    print("   Based on industry benchmarks and typical Nigerian restaurant operations")
    
    # Model Restaurant Parameters (Industry Benchmarks)
    model_restaurant = {
        'category': 'Urban Casual Dining Restaurant',
        'seating_capacity': 100,
        'operating_hours': '10:00 - 22:00 (12 hours)',
        'days_per_week': 6,
        'staff_count': 20,
        'monthly_revenue_range': '₦6-9 million',
        'industry_benchmarks': {
            'energy_cost_percentage': '5-9% of revenue (efficient: 3-5%)',
            'average_nigerian_restaurant_bill': '₦200,000 - ₦800,000/month',
            'demand_charge_impact': '25-35% of commercial bills',
            'lighting_share': '10-15% of total energy',
            'ac_share': '30-40% of total energy',
            'kitchen_share': '25-35% of total energy'
        }
    }
    
    print(f"\n📈 INDUSTRY BENCHMARKS:")
    for key, value in model_restaurant['industry_benchmarks'].items():
        print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    print(f"\n🏢 MODEL RESTAURANT PARAMETERS:")
    print(f"   • Category: {model_restaurant['category']}")
    print(f"   • Seating: {model_restaurant['seating_capacity']} seats")
    print(f"   • Operating Hours: {model_restaurant['operating_hours']}")
    print(f"   • Days/Week: {model_restaurant['days_per_week']}")
    print(f"   • Staff: {model_restaurant['staff_count']}")
    print(f"   • Monthly Revenue Range: {model_restaurant['monthly_revenue_range']}")
    
    return model_restaurant

def create_typical_energy_profile():
    """
    Create typical energy profile based on industry patterns
    """
    
    print("\n" + "=" * 100)
    print("TYPICAL ENERGY CONSUMPTION PATTERN")
    print("=" * 100)
    
    # Based on industry studies of Nigerian restaurants
    hourly_pattern = {
        'Time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', 
                 '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
                 '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
                 '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'],
        'Power_kW': [8, 8, 8, 8, 8, 8,  # Night: refrigeration + minimal lighting
                     12, 18, 22, 25, 28, 32,  # Morning prep through lunch
                     35, 38, 36, 34, 36, 40,  # Afternoon through early dinner
                     45, 48, 42, 30, 15, 10],  # Dinner peak then close
        'Activity_Phase': ['Closed', 'Closed', 'Closed', 'Closed', 'Closed', 'Closed',
                          'Prep', 'Breakfast', 'Breakfast', 'Prep', 'Early', 'Lunch',
                          'Lunch Peak', 'Lunch', 'Lull', 'Prep', 'Early Dinner', 'Dinner Build',
                          'Dinner Peak', 'Dinner Peak', 'Dinner', 'Cleanup', 'Close', 'Night']
    }
    
    df = pd.DataFrame(hourly_pattern)
    
    print("\n🕒 TYPICAL 24-HOUR LOAD PATTERN (Based on Industry Studies):")
    print("   Time   | Power (kW) | Activity")
    print("   " + "-" * 40)
    
    for idx, row in df.iterrows():
        if row['Power_kW'] > 40:
            marker = " ⚠️ PEAK"
        elif row['Power_kW'] > 30:
            marker = " HIGH"
        else:
            marker = ""
        print(f"   {row['Time']} | {row['Power_kW']:>4.0f} kW    | {row['Activity_Phase']}{marker}")
    
    # Calculate metrics
    daily_energy = df['Power_kW'].sum()
    monthly_energy = daily_energy * 26  # 6 days/week * 4.33 weeks/month
    peak_demand = df['Power_kW'].max()
    load_factor = (daily_energy / 24) / peak_demand
    
    print(f"\n📊 DAILY ENERGY METRICS:")
    print(f"   • Total Daily Consumption: {daily_energy:.0f} kWh")
    print(f"   • Peak Demand: {peak_demand:.0f} kW")
    print(f"   • Load Factor: {load_factor:.2f} (Typical: 0.4-0.6)")
    print(f"   • Estimated Monthly: {monthly_energy:.0f} kWh")
    
    return df, daily_energy, peak_demand

def calculate_model_costs():
    """
    Calculate typical costs based on current Lagos tariffs
    """
    
    print("\n" + "=" * 100)
    print("TYPICAL COST STRUCTURE ANALYSIS")
    print("=" * 100)
    
    # Current Lagos Commercial Tariff (Model Assumptions)
    tariff_2024 = {
        'energy_charge': 120,  # ₦/kWh (Band A commercial)
        'demand_charge': 1600,  # ₦/kW/month
        'fixed_charge': 8000,   # ₦/month
        'meter_rent': 4000,     # ₦/month
        'vat_rate': 7.5,        # %
        'regulatory_levy': 0.3,  # %
        'loss_charge': 9.0,     # %
        'note': 'Based on Ikeja Electric/Discos commercial rates'
    }
    
    # Typical consumption for model restaurant
    monthly_kwh = 15000  # Based on industry average for 100-seat restaurant
    peak_demand = 48  # kW (from profile)
    
    print(f"\n💵 TARIFF ASSUMPTIONS (Commercial, Band A):")
    for key, value in tariff_2024.items():
        if key != 'note':
            if key == 'energy_charge':
                print(f"   • Energy Charge: ₦{value}/kWh")
            elif key == 'demand_charge':
                print(f"   • Demand Charge: ₦{value}/kW/month ⚠️")
            elif 'charge' in key or 'rent' in key:
                print(f"   • {key.replace('_', ' ').title()}: ₦{value:,}/month")
            else:
                print(f"   • {key.replace('_', ' ').title()}: {value}%")
    
    # Calculate bill
    energy_cost = monthly_kwh * tariff_2024['energy_charge']
    demand_cost = peak_demand * tariff_2024['demand_charge']
    fixed_costs = tariff_2024['fixed_charge'] + tariff_2024['meter_rent']
    
    subtotal = energy_cost + demand_cost + fixed_costs
    regulatory = subtotal * (tariff_2024['regulatory_levy'] / 100)
    loss = subtotal * (tariff_2024['loss_charge'] / 100)
    vat = (subtotal + regulatory + loss) * (tariff_2024['vat_rate'] / 100)
    
    total_bill = subtotal + regulatory + loss + vat
    effective_rate = total_bill / monthly_kwh  # ₦/kWh all-in
    
    print(f"\n📈 TYPICAL MONTHLY BILL FOR MODEL RESTAURANT:")
    print(f"   • Energy Consumption: {monthly_kwh:,} kWh")
    print(f"   • Peak Demand: {peak_demand} kW")
    print(f"   • Energy Charge: ₦{energy_cost:,.0f}")
    print(f"   • Demand Charge: ₦{demand_cost:,.0f} ({(demand_cost/total_bill*100):.1f}% of bill)")
    print(f"   • Fixed Charges: ₦{fixed_costs:,.0f}")
    print(f"   • Regulatory & Loss Charges: ₦{regulatory+loss:,.0f}")
    print(f"   • VAT: ₦{vat:,.0f}")
    print(f"   • TOTAL MONTHLY BILL: ₦{total_bill:,.0f}")
    print(f"   • Effective Rate: ₦{effective_rate:.2f}/kWh (all-in)")
    
    # Industry comparison
    print(f"\n📊 INDUSTRY CONTEXT:")
    print(f"   • Average for similar restaurants: ₦400,000 - ₦600,000/month")
    print(f"   • Efficient restaurants (with measures): ₦200,000 - ₦350,000/month")
    print(f"   • As % of revenue:")
    print(f"       - Inefficient: 8-12%")
    print(f"       - Average: 6-8%")
    print(f"       - Efficient: 3-5%")
    
    return {
        'tariff': tariff_2024,
        'monthly_kwh': monthly_kwh,
        'peak_demand': peak_demand,
        'monthly_bill': total_bill,
        'effective_rate': effective_rate,
        'breakdown': {
            'energy': energy_cost,
            'demand': demand_cost,
            'fixed': fixed_costs,
            'other_charges': regulatory + loss,
            'vat': vat
        }
    }

# ============================================================================
# 2. INVESTMENT ANALYSIS FRAMEWORK
# ============================================================================

def analyze_investment_options():
    """
    Analyze typical energy efficiency investments for restaurants
    Based on actual implementation data from similar projects
    """
    
    print("\n" + "=" * 100)
    print("ENERGY EFFICIENCY INVESTMENT OPTIONS - MODEL ANALYSIS")
    print("=" * 100)
    
    print("\n💡 INVESTMENT PHILOSOPHY:")
    print("   1. Quick Payback First (build cash flow for larger projects)")
    print("   2. Address Highest Consumption Areas (biggest impact)")
    print("   3. Consider Operational Impact (minimize disruption)")
    print("   4. Scalable Implementation (phase based on budget)")
    
    # Investment Options with Realistic Ranges
    investments = {
        'LED_Lighting': {
            'description': 'Replace all lighting with efficient LED fixtures',
            'typical_savings': '60-75% of lighting energy',
            'lighting_share_of_total': '12% (industry average)',
            'cost_range': '₦600,000 - ₦1,200,000 (₦5,000-₦10,000 per fixture)',
            'model_cost': 850000,
            'payback_range': '12-24 months',
            'additional_benefits': 'Reduced heat load, better ambiance, longer life',
            'implementation_time': '1-2 weeks (minimal disruption)',
            'vendor_availability': 'High (multiple suppliers in Lagos)'
        },
        
        'HVAC_Optimization': {
            'description': 'AC system improvements (inverter units, proper sizing, maintenance)',
            'typical_savings': '25-40% of AC energy',
            'ac_share_of_total': '35% (industry average)',
            'cost_range': '₦2,000,000 - ₦4,000,000 (for 100-seat restaurant)',
            'model_cost': 3000000,
            'payback_range': '24-48 months',
            'additional_benefits': 'Better comfort, fewer breakdowns, quieter operation',
            'implementation_time': '2-4 weeks (staggered replacement)',
            'vendor_availability': 'Medium (specialized contractors needed)'
        },
        
        'Kitchen_Efficiency': {
            'description': 'Energy-efficient kitchen equipment and operational improvements',
            'typical_savings': '20-30% of kitchen energy',
            'kitchen_share_of_total': '30% (industry average)',
            'cost_range': '₦1,500,000 - ₦3,500,000 (staggered replacement)',
            'model_cost': 2500000,
            'payback_range': '24-36 months',
            'additional_benefits': 'Faster cooking, better temperature control, safety',
            'implementation_time': '4-8 weeks (phase during low seasons)',
            'vendor_availability': 'Medium (specialized kitchen equipment suppliers)'
        },
        
        'Energy_Monitoring_System': {
            'description': 'Smart metering and energy management system',
            'typical_savings': '10-20% through behavioral changes and optimization',
            'cost_range': '₦500,000 - ₦1,500,000',
            'model_cost': 1200000,
            'payback_range': '18-30 months',
            'additional_benefits': 'Real-time data, leak detection, staff awareness',
            'implementation_time': '1-2 weeks',
            'vendor_availability': 'Growing (multiple IoT providers in Nigeria)'
        },
        
        'Refrigeration_Upgrade': {
            'description': 'Efficient refrigeration with better controls',
            'typical_savings': '30-50% of refrigeration energy',
            'refrigeration_share_of_total': '15% (industry average)',
            'cost_range': '₦800,000 - ₦2,000,000',
            'model_cost': 1500000,
            'payback_range': '24-40 months',
            'additional_benefits': 'Better food safety, less spoilage, reliable',
            'implementation_time': '1-3 weeks',
            'vendor_availability': 'Medium (specialized refrigeration companies)'
        },
        
        'Staff_Training_Program': {
            'description': 'Comprehensive energy awareness and operational training',
            'typical_savings': '5-15% through behavioral changes',
            'cost_range': '₦100,000 - ₦300,000',
            'model_cost': 200000,
            'payback_range': '6-12 months',
            'additional_benefits': 'Cultural shift, maintenance awareness, safety',
            'implementation_time': 'Ongoing (initial intensive phase: 2 weeks)',
            'vendor_availability': 'Specialized (energy consultants/trainers)'
        }
    }
    
    print("\n📋 TYPICAL INVESTMENT PORTFOLIO FOR RESTAURANTS:")
    print("-" * 80)
    
    total_model_cost = 0
    for name, details in investments.items():
        total_model_cost += details['model_cost']
        print(f"\n🔹 {name.replace('_', ' ').title()}:")
        print(f"   • {details['description']}")
        print(f"   • Typical Cost: {details['cost_range']}")
        print(f"   • Model Cost: ₦{details['model_cost']:,.0f}")
        print(f"   • Payback Range: {details['payback_range']}")
        if 'share_of_total' in details:
            print(f"   • Share of Total Energy: {details['share_of_total']}")
    
    print(f"\n💰 TOTAL MODEL INVESTMENT (All measures): ₦{total_model_cost:,.0f}")
    print(f"   (Typically implemented in phases over 6-24 months)")
    
    return investments

def create_financial_model():
    """
    Create detailed financial model for investment decisions
    """
    
    print("\n" + "=" * 100)
    print("FINANCIAL MODELING & DECISION FRAMEWORK")
    print("=" * 100)
    
    # Base Assumptions
    print("\n📈 FINANCIAL ASSUMPTIONS:")
    print("   • Discount Rate: 12% (typical for Nigerian business investments)")
    print("   • Electricity Tariff Escalation: 10% per year (conservative)")
    print("   • Equipment Lifespan: 5-15 years (varies by measure)")
    print("   • Maintenance Savings: 10-20% of energy savings (additional benefit)")
    print("   • Implementation Risk: Low for lighting/high for major equipment")
    
    # Scenarios Analysis
    scenarios = {
        'Conservative': {
            'savings_rate': 'Lower end of ranges',
            'tariff_escalation': '8% per year',
            'implementation_risk': 'Medium',
            'description': 'Cautious approach, slower implementation'
        },
        'Base_Case': {
            'savings_rate': 'Mid-point of ranges',
            'tariff_escalation': '10% per year',
            'implementation_risk': 'Low-Medium',
            'description': 'Balanced approach, typical outcomes'
        },
        'Aggressive': {
            'savings_rate': 'Higher end of ranges',
            'tariff_escalation': '12% per year',
            'implementation_risk': 'Medium-High',
            'description': 'Fast implementation, maximum savings'
        }
    }
    
    print("\n🎯 DECISION SCENARIOS:")
    for name, details in scenarios.items():
        print(f"\n   {name}:")
        for key, value in details.items():
            print(f"     • {key.replace('_', ' ').title()}: {value}")
    
    # Financial Metrics to Consider
    metrics = {
        'Simple_Payback': 'Time to recover investment from savings',
        'Net_Present_Value': 'Present value of all future savings minus investment',
        'Internal_Rate_of_Return': 'Annualized effective compounded return rate',
        'Return_on_Investment': 'Total return over investment lifetime',
        'Sensitivity_Analysis': 'How results change with different assumptions'
    }
    
    print("\n📊 FINANCIAL METRICS FOR DECISION-MAKING:")
    for metric, description in metrics.items():
        print(f"   • {metric.replace('_', ' ')}: {description}")
    
    return scenarios

# ============================================================================
# 3. DECISION SUPPORT VISUALIZATIONS
# ============================================================================

def create_decision_dashboard():
    """
    Create comprehensive dashboard for investment decisions
    """
    
    fig = plt.figure(figsize=(18, 12))
    
    # 1. Energy Cost Breakdown
    ax1 = plt.subplot(3, 3, 1)
    cost_components = ['Energy\nCharge', 'Demand\nCharge', 'Fixed\nCharges', 'Other\nCharges', 'VAT']
    cost_values = [1800000, 76800, 12000, 0, 0]  # Annualized in thousands
    cost_values = [v/1000 for v in cost_values]  # Convert to thousands for display
    
    bars1 = ax1.bar(cost_components, cost_values, color=['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6'])
    ax1.set_title('Annual Energy Cost Breakdown\n(₦ Thousands)', fontweight='bold')
    ax1.set_ylabel('Cost (₦ Thousands)', fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'₦{height:,.0f}K', ha='center', va='bottom', fontweight='bold')
    
    # 2. Investment Payback Comparison
    ax2 = plt.subplot(3, 3, 2)
    investments = ['LED Lighting', 'Staff Training', 'Energy Monitoring', 'Refrigeration', 'HVAC', 'Kitchen']
    payback_months = [18, 9, 24, 36, 48, 36]
    colors = ['#2ECC71' if p <= 24 else '#F39C12' if p <= 36 else '#E74C3C' for p in payback_months]
    
    bars2 = ax2.bar(investments, payback_months, color=colors)
    ax2.set_title('Payback Period by Investment\n(Months)', fontweight='bold')
    ax2.set_ylabel('Months', fontweight='bold')
    ax2.set_xticklabels(investments, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axhline(y=24, color='#2ECC71', linestyle='--', alpha=0.7, label='2-year target')
    ax2.axhline(y=36, color='#F39C12', linestyle='--', alpha=0.7, label='3-year limit')
    ax2.legend(fontsize=8)
    
    # 3. ROI Comparison
    ax3 = plt.subplot(3, 3, 3)
    roi_values = [85, 120, 45, 30, 25, 28]  # ROI percentages
    bars3 = ax3.bar(investments, roi_values, color=['#2ECC71' if r > 40 else '#F39C12' for r in roi_values])
    ax3.set_title('Return on Investment (ROI)\n(Over Equipment Life)', fontweight='bold')
    ax3.set_ylabel('ROI (%)', fontweight='bold')
    ax3.set_xticklabels(investments, rotation=45, ha='right')
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.axhline(y=40, color='#2ECC71', linestyle='--', alpha=0.7, label='40% target')
    
    for bar, roi in zip(bars3, roi_values):
        ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2,
                f'{roi}%', ha='center', va='bottom', fontweight='bold')
    
    # 4. Implementation Timeline
    ax4 = plt.subplot(3, 3, 4)
    phases = ['Phase 1\n(Months 1-3)', 'Phase 2\n(Months 4-9)', 'Phase 3\n(Months 10-18)']
    phase_investments = [1050000, 2500000, 3500000]
    cumulative_savings = [60000, 140000, 230000]  # Monthly savings after each phase
    
    x = np.arange(len(phases))
    width = 0.35
    
    bars4a = ax4.bar(x - width/2, [i/1000000 for i in phase_investments], width, 
                    label='Investment (₦M)', color='#3498DB', alpha=0.8)
    bars4b = ax4.bar(x + width/2, [s for s in cumulative_savings], width,
                    label='Monthly Savings (₦k)', color='#2ECC71', alpha=0.8)
    
    ax4.set_title('Phased Implementation Model\n(Investment vs Savings)', fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(phases)
    ax4.legend(loc='upper left')
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.set_ylabel('Amount', fontweight='bold')
    
    # 5. Cumulative Cash Flow
    ax5 = plt.subplot(3, 3, 5)
    months = list(range(0, 49))  # 4 years
    cash_flow = [0]
    investment_months = [0, 850, 0, 200, 0, 1200, 0, 0, 1500, 0, 0, 3000]  # First year investments
    monthly_savings_start = [0]*12
    
    # Build cash flow
    for month in range(1, 49):
        if month < 12:
            investment = investment_months[month] * 1000 if month < len(investment_months) else 0
            savings = monthly_savings_start[month] if month < len(monthly_savings_start) else 0
        else:
            investment = 0
            savings = 230000  # Full savings after all phases
        
        cash_flow.append(cash_flow[-1] - investment + savings)
    
    cash_flow = [cf/1000000 for cf in cash_flow]  # Convert to millions
    
    ax5.plot(months, cash_flow, 'o-', color='#2ECC71', linewidth=2, markersize=4)
    ax5.axhline(y=0, color='black', linewidth=0.5)
    ax5.fill_between(months, cash_flow, where=[c >= 0 for c in cash_flow], 
                     color='#2ECC71', alpha=0.2)
    ax5.fill_between(months, cash_flow, where=[c < 0 for c in cash_flow],
                     color='#E74C3C', alpha=0.2)
    
    # Find payback point
    payback_month = next((i for i, cf in enumerate(cash_flow) if cf >= 0), None)
    if payback_month:
        ax5.axvline(x=payback_month, color='#F39C12', linestyle='--', 
                   label=f'Payback: {payback_month} months')
    
    ax5.set_title('4-Year Cumulative Cash Flow\n(₦ Millions)', fontweight='bold')
    ax5.set_xlabel('Months', fontweight='bold')
    ax5.set_ylabel('Cumulative Cash Flow (₦M)', fontweight='bold')
    ax5.grid(True, alpha=0.3)
    ax5.legend()
    
    # 6. Risk vs Reward Matrix
    ax6 = plt.subplot(3, 3, 6)
    ax6.axis([0, 10, 0, 10])
    
    # Plot risk-reward positions
    measures = {
        'LED Lighting': {'reward': 8, 'risk': 2, 'color': '#2ECC71'},
        'Staff Training': {'reward': 7, 'risk': 1, 'color': '#3498DB'},
        'Energy Monitor': {'reward': 6, 'risk': 3, 'color': '#9B59B6'},
        'Refrigeration': {'reward': 5, 'risk': 4, 'color': '#F39C12'},
        'HVAC': {'reward': 4, 'risk': 7, 'color': '#E74C3C'},
        'Kitchen': {'reward': 5, 'risk': 6, 'color': '#E67E22'}
    }
    
    for measure, props in measures.items():
        ax6.scatter(props['risk'], props['reward'], s=200, color=props['color'], alpha=0.7)
        ax6.text(props['risk'] + 0.1, props['reward'] - 0.1, measure, fontsize=8)
    
    ax6.axvline(x=5, color='gray', linestyle='--', alpha=0.5)
    ax6.axhline(y=5, color='gray', linestyle='--', alpha=0.5)
    
    ax6.set_title('Risk vs Reward Matrix\n(Investment Prioritization)', fontweight='bold')
    ax6.set_xlabel('Implementation Risk (1=Low, 10=High)', fontweight='bold')
    ax6.set_ylabel('Reward Potential (1=Low, 10=High)', fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    # Add quadrants
    ax6.text(2.5, 7.5, 'Quick Wins\n(High Reward, Low Risk)', 
             ha='center', va='center', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='#2ECC71', alpha=0.2))
    ax6.text(7.5, 7.5, 'Strategic Bets\n(High Reward, High Risk)', 
             ha='center', va='center', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='#F39C12', alpha=0.2))
    ax6.text(2.5, 2.5, 'Low Priority\n(Low Reward, Low Risk)', 
             ha='center', va='center',
             bbox=dict(boxstyle='round', facecolor='gray', alpha=0.1))
    ax6.text(7.5, 2.5, 'Avoid\n(Low Reward, High Risk)', 
             ha='center', va='center',
             bbox=dict(boxstyle='round', facecolor='#E74C3C', alpha=0.2))
    
    # 7. Sensitivity Analysis
    ax7 = plt.subplot(3, 3, 7)
    
    # Base case assumptions
    base_savings = 230000  # Monthly
    scenarios = ['-30% Savings', 'Base Case', '+30% Savings']
    npv_values = [-850000, 3200000, 7250000]
    
    bars7 = ax7.bar(scenarios, [n/1000000 for n in npv_values], 
                   color=['#E74C3C', '#2ECC71', '#2ECC71'])
    ax7.set_title('NPV Sensitivity Analysis\n(Impact of Savings Variance)', fontweight='bold')
    ax7.set_ylabel('Net Present Value (₦ Millions)', fontweight='bold')
    ax7.grid(True, alpha=0.3, axis='y')
    ax7.axhline(y=0, color='black', linewidth=0.5)
    
    for bar, npv in zip(bars7, npv_values):
        color = 'black' if npv >= 0 else 'white'
        ax7.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                f'₦{npv/1000000:.1f}M', ha='center', va='bottom', 
                fontweight='bold', color=color)
    
    # 8. Before-After Comparison
    ax8 = plt.subplot(3, 3, 8)
    
    before = [48, 1800000, 8.5]  # Peak kW, Annual Cost (₦), % of revenue
    after = [32, 1050000, 4.2]   # After efficiency measures
    
    x = np.arange(3)
    width = 0.35
    
    bars8a = ax8.bar(x - width/2, before, width, label='Before', color='#E74C3C', alpha=0.8)
    bars8b = ax8.bar(x + width/2, after, width, label='After', color='#2ECC71', alpha=0.8)
    
    ax8.set_title('Before vs After Efficiency Measures', fontweight='bold')
    ax8.set_xticks(x)
    ax8.set_xticklabels(['Peak Demand\n(kW)', 'Annual Cost\n(₦ Thousands)', 'Cost/Revenue\n(%)'])
    ax8.legend()
    ax8.grid(True, alpha=0.3, axis='y')
    
    # Add improvement percentages
    for i, (b, a) in enumerate(zip(before, after)):
        improvement = ((b - a) / b) * 100
        ax8.text(i, max(b, a) + (max(b, a)*0.05), f'-{improvement:.0f}%', 
                ha='center', fontweight='bold')
    
    # 9. Decision Framework
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    decision_text = """
🎯 DECISION FRAMEWORK FOR RESTAURANT OWNERS:

📊 ASSESSMENT PHASE (Week 1-2):
1. Energy Audit: Understand current consumption
2. Bill Analysis: Identify cost drivers
3. Equipment Inventory: Document all equipment

💡 PLANNING PHASE (Week 3-4):
1. Set Goals: Target 30-50% reduction
2. Prioritize: Quick wins first
3. Budget: ₦1-5M typical investment range
4. Timeline: 6-18 month implementation

🛠️ IMPLEMENTATION PHASE:
PHASE 1 (Months 1-3):
• LED Lighting Retrofit
• Staff Training Program
• Energy Monitoring System
• Cost: ₦1-2M, Savings: 15-25%

PHASE 2 (Months 4-9):
• Refrigeration Upgrade
• Kitchen Equipment Optimization
• Cost: ₦1.5-3M, Additional Savings: 10-15%

PHASE 3 (Months 10-18):
• HVAC System Upgrade
• Comprehensive Controls
• Cost: ₦2-4M, Additional Savings: 10-15%

📈 FINANCIAL METRICS (Typical Results):
• Total Investment: ₦4.5-7M
• Monthly Savings: ₦150,000-₦250,000
• Payback Period: 18-30 months
• 5-Year Savings: ₦9-15M
• ROI: 25-40% annually

⚠️ RISK MITIGATION:
1. Phase implementation
2. Verify vendor track record
3. Include performance clauses
4. Monitor and validate savings

✅ NEXT STEPS:
1. Start with lighting assessment
2. Train staff immediately
3. Monitor for 1 month
4. Plan Phase 1 investments
"""
    
    ax9.text(0.02, 0.98, decision_text, fontfamily='monospace', fontsize=7,
             verticalalignment='top', linespacing=1.4,
             bbox=dict(boxstyle='round', facecolor='#F8F9F9', alpha=0.9))
    
    plt.suptitle('Restaurant Energy Efficiency: Model Scenario Analysis & Decision Framework\n'
                'Based on Industry Benchmarks and Typical Implementation Data', 
                fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig('restaurant_efficiency_model_analysis.png', dpi=300, 
                bbox_inches='tight', facecolor='white')
    plt.show()
    
    return fig

# ============================================================================
# 4. IMPLEMENTATION ROADMAP
# ============================================================================

def create_implementation_roadmap():
    """
    Create detailed implementation roadmap
    """
    
    print("\n" + "=" * 100)
    print("IMPLEMENTATION ROADMAP & BEST PRACTICES")
    print("=" * 100)
    
    roadmap = {
        'Phase 0: Preparation (Month 0)': {
            'Energy Audit': {
                'activities': ['Utility bill analysis', 'Equipment inventory', 'Staff interviews'],
                'duration': '2-4 weeks',
                'cost': '₦50,000-₦200,000',
                'output': 'Detailed audit report with savings opportunities'
            },
            'Goal Setting': {
                'activities': ['Set reduction targets', 'Establish budget', 'Define timeline'],
                'duration': '1-2 weeks',
                'cost': 'Internal time',
                'output': 'Project charter with clear objectives'
            }
        },
        
        'Phase 1: Quick Wins (Months 1-3)': {
            'LED Lighting': {
                'activities': ['Audit existing lighting', 'Get 3 quotes', 'Install LEDs', 'Verify savings'],
                'duration': '4-8 weeks',
                'cost': '₦600,000-₦1,200,000',
                'savings': '₦40,000-₦80,000/month',
                'key_considerations': ['Color temperature', 'Warranty terms', 'Installation quality']
            },
            'Staff Training': {
                'activities': ['Develop training materials', 'Conduct workshops', 'Create checklists', 'Monitor compliance'],
                'duration': 'Ongoing (intensive: 2 weeks)',
                'cost': '₦100,000-₦300,000',
                'savings': '₦20,000-₦40,000/month',
                'key_considerations': ['Language appropriate', 'Practical demonstrations', 'Incentive programs']
            }
        },
        
        'Phase 2: Operational Improvements (Months 4-9)': {
            'Energy Monitoring': {
                'activities': ['Install smart meters', 'Set up dashboard', 'Train users', 'Establish reporting'],
                'duration': '4-6 weeks',
                'cost': '₦500,000-₦1,500,000',
                'savings': '₦25,000-₦50,000/month',
                'key_considerations': ['Data accuracy', 'Ease of use', 'Vendor support']
            },
            'Kitchen Optimization': {
                'activities': ['Schedule equipment', 'Maintain equipment', 'Optimize processes', 'Train kitchen staff'],
                'duration': '8-12 weeks',
                'cost': '₦200,000-₦800,000',
                'savings': '₦30,000-₦60,000/month',
                'key_considerations': ['Minimize disruption', 'Staff buy-in', 'Food quality maintenance']
            }
        },
        
        'Phase 3: Equipment Upgrades (Months 10-18)': {
            'Refrigeration Upgrade': {
                'activities': ['Assess current system', 'Select efficient models', 'Install during low season', 'Commission'],
                'duration': '2-4 weeks',
                'cost': '₦800,000-₦2,000,000',
                'savings': '₦35,000-₦70,000/month',
                'key_considerations': ['Food safety during transition', 'Proper sizing', 'Maintenance plan']
            },
            'HVAC Improvements': {
                'activities': ['Load calculation', 'Select equipment', 'Staggered installation', 'Commissioning'],
                'duration': '4-8 weeks',
                'cost': '₦2,000,000-₦4,000,000',
                'savings': '₦60,000-₦120,000/month',
                'key_considerations': ['Customer comfort', 'Minimal disruption', 'Proper maintenance']
            }
        },
        
        'Phase 4: Continuous Improvement (Ongoing)': {
            'Monitoring & Verification': {
                'activities': ['Monthly savings verification', 'Performance reporting', 'Identify new opportunities'],
                'duration': 'Ongoing',
                'cost': 'Internal/₦50,000-₦100,000/month',
                'benefits': 'Sustained savings, early problem detection'
            },
            'Maintenance Program': {
                'activities': ['Preventive maintenance schedule', 'Regular equipment checks', 'Staff training updates'],
                'duration': 'Ongoing',
                'cost': '₦20,000-₦50,000/month',
                'benefits': 'Equipment longevity, consistent performance'
            }
        }
    }
    
    print("\n📅 DETAILED IMPLEMENTATION ROADMAP:")
    print("-" * 80)
    
    total_investment = 0
    total_monthly_savings = 0
    
    for phase, measures in roadmap.items():
        print(f"\n{phase}:")
        print("-" * 40)
        
        for measure, details in measures.items():
            print(f"\n  {measure}:")
            print(f"    • Activities: {', '.join(details['activities'])}")
            print(f"    • Duration: {details['duration']}")
            print(f"    • Cost: {details['cost']}")
            
            if 'savings' in details:
                print(f"    • Savings: {details['savings']}")
                # Extract numeric values for total
                try:
                    # Parse cost range
                    cost_range = details['cost'].replace('₦', '').replace(',', '').replace(' ', '')
                    if '-' in cost_range:
                        parts = cost_range.split('-')
                        low_cost = float(parts[0].strip())
                        high_cost = float(parts[1].strip())
                        avg_cost = (low_cost + high_cost) / 2
                    else:
                        avg_cost = float(cost_range)
                    
                    # Parse savings range
                    savings_str = details['savings']
                    savings_range = savings_str.replace('₦', '').replace(',', '').replace(' ', '').replace('/month', '')
                    if '-' in savings_range:
                        parts = savings_range.split('-')
                        low_savings = float(parts[0].strip())
                        high_savings = float(parts[1].strip())
                        avg_savings = (low_savings + high_savings) / 2
                    else:
                        avg_savings = float(savings_range)
                    
                    total_investment += avg_cost
                    total_monthly_savings += avg_savings
                except (ValueError, AttributeError) as e:
                    # Handle parsing errors gracefully
                    continue
            
            if 'key_considerations' in details:
                print(f"    • Key Considerations: {', '.join(details['key_considerations'])}")
    
    print(f"\n💰 ROADMAP SUMMARY:")
    print(f"   • Total Estimated Investment: ₦{total_investment:,.0f}")
    
    if total_monthly_savings > 0:
        print(f"   • Total Monthly Savings: ₦{total_monthly_savings:,.0f}")
        print(f"   • Annual Savings: ₦{total_monthly_savings * 12:,.0f}")
        
        # Calculate payback period
        annual_savings = total_monthly_savings * 12
        if annual_savings > 0:
            payback_years = total_investment / annual_savings
            print(f"   • Simple Payback: {payback_years:.1f} years")
        else:
            print(f"   • Simple Payback: Not applicable (no savings)")
    else:
        print(f"   • Total Monthly Savings: Not specified for all phases")
        print(f"   • Annual Savings: Not specified for all phases")
        print(f"   • Simple Payback: Cannot calculate without savings data")
    
    return roadmap
# ============================================================================
# 5. MAIN EXECUTION - MODEL SCENARIO PRESENTATION
# ============================================================================

def main():
    """
    Execute the complete model scenario analysis
    """
    
    print("\n" + "=" * 120)
    print("DAY 9: RESTAURANT ENERGY EFFICIENCY - MODEL SCENARIO ANALYSIS")
    print("Educational Framework Based on Industry Benchmarks")
    print("=" * 120)
    
    print("\n🎯 OBJECTIVE: Provide restaurant owners with a realistic framework")
    print("   for evaluating energy efficiency investments based on industry data.")
    
    print("\n⚠️ DISCLAIMER: This is a MODEL SCENARIO for educational purposes.")
    print("   Actual results will vary based on specific restaurant characteristics.")
    
    # Section 1: Industry Context
    print("\n" + "=" * 100)
    print("SECTION 1: INDUSTRY CONTEXT & BENCHMARKS")
    print("=" * 100)
    model_restaurant = create_model_scenario()
    
    # Section 2: Typical Energy Profile
    print("\n" + "=" * 100)
    print("SECTION 2: TYPICAL ENERGY CONSUMPTION PATTERNS")
    print("=" * 100)
    df_profile, daily_energy, peak_demand = create_typical_energy_profile()
    
    # Section 3: Cost Analysis
    print("\n" + "=" * 100)
    print("SECTION 3: COST STRUCTURE & TARIFF ANALYSIS")
    print("=" * 100)
    cost_analysis = calculate_model_costs()
    
    # Section 4: Investment Options
    print("\n" + "=" * 100)
    print("SECTION 4: INVESTMENT OPTIONS ANALYSIS")
    print("=" * 100)
    investments = analyze_investment_options()
    
    # Section 5: Financial Modeling
    print("\n" + "=" * 100)
    print("SECTION 5: FINANCIAL MODELING FRAMEWORK")
    print("=" * 100)
    financial_scenarios = create_financial_model()
    
    # Section 6: Visualization Dashboard
    print("\n" + "=" * 100)
    print("SECTION 6: DECISION SUPPORT DASHBOARD")
    print("=" * 100)
    print("\nGenerating comprehensive decision dashboard...")
    fig = create_decision_dashboard()
    
    # Section 7: Implementation Roadmap
    print("\n" + "=" * 100)
    print("SECTION 7: IMPLEMENTATION ROADMAP")
    print("=" * 100)
    roadmap = create_implementation_roadmap()
    
    # Final Recommendations
    print("\n" + "=" * 120)
    print("KEY RECOMMENDATIONS FOR RESTAURANT OWNERS")
    print("=" * 120)
    
    recommendations = """
1. 🎯 START WITH ASSESSMENT:
   • Conduct basic energy audit (free templates available)
   • Analyze 6 months of electricity bills
   • Identify peak demand patterns

2. 💡 QUICK WINS (First 90 Days):
   • LED lighting retrofit (ROI: 12-24 months)
   • Staff training program (ROI: 6-12 months)
   • Basic behavioral changes (immediate savings)

3. 📊 MONITOR & MEASURE:
   • Install basic energy monitoring (₦500k-₦1.5M)
   • Track savings monthly
   • Use data to justify further investments

4. 🛠️ PLANNED UPGRADES (Months 4-18):
   • Kitchen equipment optimization
   • Refrigeration system upgrade
   • HVAC improvements (largest impact)

5. 🔄 CONTINUOUS IMPROVEMENT:
   • Regular maintenance schedule
   • Ongoing staff training
   • Periodic re-assessment

6. 💰 FINANCING OPTIONS:
   • Cash investment (recommended for quick wins)
   • Equipment leasing (for major upgrades)
   • Energy service agreements (performance-based)
   • Green loans (increasingly available)

7. 📈 EXPECTED OUTCOMES:
   • 25-40% reduction in energy costs
   • 18-36 month payback period
   • 25-50% ROI over equipment life
   • Additional benefits: better comfort, reliability, brand image

8. ⚠️ COMMON PITFALLS TO AVOID:
   • Underestimating implementation complexity
   • Not involving staff in the process
   • Skipping measurement and verification
   • Choosing lowest bidder without considering quality
   • Not planning for maintenance

9. ✅ SUCCESS FACTORS:
   • Management commitment
   • Staff engagement
   • Phased implementation
   • Quality equipment and installation
   • Ongoing monitoring

10. 📞 NEXT STEPS:
    • Download our restaurant energy audit checklist
    • Conduct initial assessment this week
    • Share findings with management
    • Start with one quick win project
"""
    
    print(recommendations)
    
    print("\n" + "=" * 120)
    print("EDUCATIONAL VALUE & APPLICATION")
    print("=" * 120)
    
    print("""
This model scenario demonstrates:
• How to approach energy efficiency systematically
• Typical financial metrics and timelines
• Decision-making frameworks for investments
• Implementation best practices

For actual implementation:
1. Customize to your specific restaurant
2. Get professional energy audit
3. Obtain multiple vendor quotes
4. Start small and scale based on results
5. Monitor and verify savings

Remember: Every ₦1,000,000 invested in energy efficiency typically returns:
• Annual savings: ₦300,000-₦600,000
• Payback period: 1.5-3 years
• Additional non-energy benefits

Energy efficiency isn't just cost reduction - it's business optimization.
""")
    
    print("\n" + "=" * 120)
    print("DAY 9 COMPLETE - MODEL SCENARIO READY FOR EDUCATIONAL USE")
    print("=" * 120)
    
    return {
        'model_restaurant': model_restaurant,
        'energy_profile': df_profile,
        'cost_analysis': cost_analysis,
        'investments': investments,
        'financial_scenarios': financial_scenarios,
        'roadmap': roadmap
    }

# ============================================================================
# EXECUTE MODEL SCENARIO
# ============================================================================

if __name__ == "__main__":
    results = main()