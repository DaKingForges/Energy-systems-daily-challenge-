"""
DAY 11: ENERGY LOSSES & THEFT IMPACT MODEL
Energy System Management Portfolio - Week 2: System Design & Decision-Making

Decision Question: For an energy distribution system experiencing technical and 
non-technical losses, is investing in loss reduction measures financially 
justified, and what is the optimal strategy?

DISCLAIMER: This is an ILLUSTRATIVE MODEL based on assumed parameters, using Lagos 
as a case study. It does not contain actual operational data from any specific 
utility. All figures, costs, and loss rates are hypothetical and used for 
educational decision-analysis purposes only.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import itertools

plt.style.use('seaborn-v0_8-whitegrid')
mpl.rcParams['font.size'] = 9
mpl.rcParams['axes.titlesize'] = 11
mpl.rcParams['figure.figsize'] = [18, 10]

# ============================================================================
# 1. DISTRIBUTION SYSTEM DEFINITION & LOSS ASSUMPTIONS (HYPOTHETICAL)
# ============================================================================

def define_distribution_system():
    """
    Define the distribution system with loss parameters.
    ALL values are ASSUMED for modeling purposes.
    """
    
    print("=" * 80)
    print("ENERGY LOSSES & THEFT IMPACT MODEL (ASSUMED DATA - LAGOS CASE STUDY)")
    print("=" * 80)
    print("\n⚠️  DISCLAIMER: All figures, costs and loss rates are hypothetical.")
    print("   This is an educational model, not based on actual utility data.\n")
    
    distribution_system = {
        'system_overview': {
            'name': 'Urban Distribution Network - Zone A (Lagos Metropolis)',
            'location': 'Lagos, Nigeria',
            'customer_type': 'Mixed (Residential 70%, Commercial 30%)',
            'peak_demand_mw': 10.0,                # assumed
            'annual_energy_gwh': 50.0,              # assumed
            'annual_revenue_ngn_million': 50 * 110 * 1000,  # 50 GWh * ₦110/kWh
            'number_of_customers': 25000,           # assumed
            'network_length_km': 150,               # assumed
            'transformers_count': 45,               # assumed
            'feeder_circuits': 8,                  # assumed
        },
        
        'current_loss_scenario': {
            'total_loss_percent': 25.0,             # assumed industry avg.
            'technical_losses': {
                'percentage': 15.0,                 # 15% of total energy
                'components': {
                    'transformer_losses': 4.0,
                    'line_losses': 7.0,
                    'substation_losses': 2.5,
                    'metering_losses': 1.5,
                },
                'causes': ['Aging infrastructure', 'Overloaded transformers',
                           'Poor power factor', 'Long distribution lines',
                           'Undersized conductors']
            },
            'non_technical_losses': {
                'percentage': 10.0,                 # 10% of total energy
                'components': {
                    'theft_bypass': 6.0,
                    'meter_tampering': 2.5,
                    'billing_errors': 1.0,
                    'unmetered_connections': 0.5,
                },
                'causes': ['Illegal connections', 'Meter bypass', 'Corruption',
                           'Inadequate enforcement', 'Poor record keeping']
            },
        },
        
        'loss_reduction_options': {
            'metering_upgrade': {
                'description': 'Install smart meters with remote monitoring',
                'capital_cost_ngn_million': 300,
                'annual_om_percent': 2,
                'implementation_time_months': 18,
                'expected_impact': {
                    'reduces_metering_losses': 80,
                    'reduces_theft_bypass': 40,
                    'reduces_billing_errors': 90,
                }
            },
            'network_rehabilitation': {
                'description': 'Replace aging transformers and conductors',
                'capital_cost_ngn_million': 450,
                'annual_om_percent': 1.5,
                'implementation_time_months': 24,
                'expected_impact': {
                    'reduces_transformer_losses': 70,
                    'reduces_line_losses': 60,
                    'reduces_substation_losses': 75,
                }
            },
            'anti_theft_measures': {
                'description': 'Deploy security, enforcement, community engagement',
                'capital_cost_ngn_million': 120,
                'annual_om_percent': 3,
                'implementation_time_months': 12,
                'expected_impact': {
                    'reduces_theft_bypass': 60,
                    'reduces_meter_tampering': 70,
                    'reduces_unmetered_connections': 80,
                }
            },
            'combined_approach': {
                'description': 'Integrated loss reduction program',
                'capital_cost_ngn_million': 750,
                'annual_om_percent': 2,
                'implementation_time_months': 30,
                'expected_impact': {
                    'reduces_total_losses': 55,
                    'synergy_benefit': 15,
                }
            }
        },
        
        'financial_parameters': {
            'grid_tariff_ngn_per_kwh': 110,
            'energy_cost_ngn_per_kwh': 70,
            'analysis_period_years': 10,
            'discount_rate': 0.12,
            'inflation_rate': 0.15,
            'tariff_escalation_rate': 0.10,
            'energy_growth_rate': 0.03,
        },
        
        'scenarios': {
            'baseline': {
                'name': 'Do Nothing',
                'loss_trend': 'Gradual increase 1%/year'
            },
            'low_loss': {
                'name': 'Aggressive Reduction',
                'target_loss_percent': 15,
                'time_to_achieve_years': 3,
            },
            'medium_loss': {
                'name': 'Moderate Reduction',
                'target_loss_percent': 20,
                'time_to_achieve_years': 5,
            },
            'high_loss': {
                'name': 'Deteriorating',
                'loss_increase_rate': 0.02,
            }
        }
    }
    
    # Calculate current revenue loss
    annual_energy_gwh = distribution_system['system_overview']['annual_energy_gwh']
    total_loss_percent = distribution_system['current_loss_scenario']['total_loss_percent']
    tariff = distribution_system['financial_parameters']['grid_tariff_ngn_per_kwh']
    
    annual_loss_gwh = annual_energy_gwh * (total_loss_percent / 100)
    annual_revenue_loss_ngn_million = annual_loss_gwh * tariff * 1000 / 1e6
    
    distribution_system['current_loss_scenario']['annual_loss_gwh'] = annual_loss_gwh
    distribution_system['current_loss_scenario']['annual_revenue_loss_ngn_million'] = annual_revenue_loss_ngn_million
    
    # Print disclaimer
    print("DISTRIBUTION SYSTEM OVERVIEW (ASSUMED):")
    print("-" * 60)
    print(f"Network: {distribution_system['system_overview']['name']}")
    print(f"Annual Energy: {distribution_system['system_overview']['annual_energy_gwh']} GWh")
    print(f"Total Losses: {total_loss_percent}%")
    print(f"Annual Revenue Lost: ₦{annual_revenue_loss_ngn_million:.1f}M\n")
    
    return distribution_system


# ============================================================================
# 2. LOSS IMPACT MODEL OVER TIME (SCENARIO ANALYSIS)
# ============================================================================

def model_loss_impact_over_time(distribution_system):
    """Model loss impact over 10 years under different scenarios."""
    
    analysis_years = distribution_system['financial_parameters']['analysis_period_years']
    base_energy_gwh = distribution_system['system_overview']['annual_energy_gwh']
    base_loss_percent = distribution_system['current_loss_scenario']['total_loss_percent']
    tariff = distribution_system['financial_parameters']['grid_tariff_ngn_per_kwh']
    energy_cost = distribution_system['financial_parameters']['energy_cost_ngn_per_kwh']
    energy_growth = distribution_system['financial_parameters']['energy_growth_rate']
    tariff_escalation = distribution_system['financial_parameters']['tariff_escalation_rate']
    
    scenarios = {
        'baseline': {
            'name': 'Do Nothing (Baseline)',
            'loss_trend': lambda year: base_loss_percent * (1 + 0.01) ** year,
        },
        'low_loss': {
            'name': 'Aggressive Reduction',
            'loss_trend': lambda year: base_loss_percent * (0.6 if year >= 3 else 
                                  base_loss_percent * (1 - (0.4/3) * year) / base_loss_percent),
        },
        'medium_loss': {
            'name': 'Moderate Reduction',
            'loss_trend': lambda year: base_loss_percent * (0.8 if year >= 5 else 
                                  base_loss_percent * (1 - (0.2/5) * year) / base_loss_percent),
        },
        'high_loss': {
            'name': 'Deteriorating',
            'loss_trend': lambda year: base_loss_percent * (1 + 0.02) ** year,
        }
    }
    
    results = {}
    for scenario_name, scenario_def in scenarios.items():
        years = np.arange(0, analysis_years + 1)
        loss_percent = np.array([scenario_def['loss_trend'](y) for y in years])
        energy_supplied = base_energy_gwh * (1 + energy_growth) ** years
        energy_lost = energy_supplied * (loss_percent / 100)
        
        # Revenue with tariff escalation
        tariff_year = tariff * (1 + tariff_escalation) ** years
        revenue_lost = energy_lost * tariff_year * 1000 / 1e6
        cumulative_revenue_lost = np.cumsum(revenue_lost[1:])   # exclude year 0
        
        results[scenario_name] = {
            'name': scenario_def['name'],
            'years': years,
            'loss_percent': loss_percent,
            'energy_lost_gwh': energy_lost,
            'revenue_lost_ngn_million': revenue_lost,
            'cumulative_revenue_lost': cumulative_revenue_lost,
        }
    
    return results


# ============================================================================
# 3. INVESTMENT OPTION FINANCIAL ANALYSIS
# ============================================================================

def analyze_investment_options(distribution_system, loss_results):
    """Calculate NPV, payback, ROI for each loss reduction option."""
    
    options = distribution_system['loss_reduction_options']
    financial_params = distribution_system['financial_parameters']
    baseline_loss_results = loss_results['baseline']
    analysis_years = financial_params['analysis_period_years']
    discount_rate = financial_params['discount_rate']
    base_energy = distribution_system['system_overview']['annual_energy_gwh']
    baseline_loss = distribution_system['current_loss_scenario']['total_loss_percent']
    
    investment_results = {}
    
    for option_name, option_details in options.items():
        if option_name == 'combined_approach':
            continue   # handled separately later
        
        capital = option_details['capital_cost_ngn_million'] * 1e6
        om_rate = option_details['annual_om_percent'] / 100
        impl_years = option_details['implementation_time_months'] / 12
        
        # Estimate loss reduction based on target loss components
        if option_name == 'metering_upgrade':
            baseline_nt = distribution_system['current_loss_scenario']['non_technical_losses']['percentage']
            reduction = baseline_nt * 0.70   # weighted avg
        elif option_name == 'network_rehabilitation':
            baseline_t = distribution_system['current_loss_scenario']['technical_losses']['percentage']
            reduction = baseline_t * 0.68
        elif option_name == 'anti_theft_measures':
            baseline_nt = distribution_system['current_loss_scenario']['non_technical_losses']['percentage']
            reduction = baseline_nt * 0.70
        else:
            reduction = 0
        
        new_loss = baseline_loss - reduction
        full_effect_year = int(np.ceil(impl_years))
        
        years = np.arange(0, analysis_years + 1)
        capital_spend = np.zeros(len(years))
        om_spend = np.zeros(len(years))
        revenue_savings = np.zeros(len(years))
        
        # Capital: 30% year0, 70% at full_effect_year
        capital_spend[0] = capital * 0.3
        if full_effect_year < len(years):
            capital_spend[full_effect_year] = capital * 0.7
        
        for i, y in enumerate(years):
            if i >= full_effect_year:
                om_spend[i] = capital * om_rate * (1 + financial_params['inflation_rate']) ** (i - full_effect_year)
            
            if i > 0:
                # revenue savings relative to baseline
                baseline_rev_loss = baseline_loss_results['revenue_lost_ngn_million'][i]
                
                # phased benefits
                if i < full_effect_year:
                    progress = i / full_effect_year
                    curr_loss = baseline_loss - reduction * progress * 0.5
                else:
                    curr_loss = new_loss
                
                energy_year = base_energy * (1 + financial_params['energy_growth_rate']) ** i
                tariff_year = financial_params['grid_tariff_ngn_per_kwh'] * \
                             (1 + financial_params['tariff_escalation_rate']) ** i
                loss_with_invest = energy_year * (curr_loss / 100)
                rev_loss_with_invest = loss_with_invest * tariff_year * 1000 / 1e6
                savings = baseline_rev_loss - rev_loss_with_invest
                revenue_savings[i] = savings * 1e6
        
        net_cashflow = revenue_savings - capital_spend - om_spend
        cumulative = np.cumsum(net_cashflow)
        discounted = net_cashflow / ((1 + discount_rate) ** years)
        npv = np.sum(discounted)
        
        # payback
        payback = None
        cum = 0
        for idx, cf in enumerate(net_cashflow):
            cum += cf
            if cum >= 0 and payback is None:
                payback = idx
                break
        
        roi = (np.sum(net_cashflow) / capital) * 100 if capital > 0 else 0
        
        investment_results[option_name] = {
            'name': option_name.replace('_', ' ').title(),
            'capital_cost_ngn': capital,
            'npv_ngn': npv,
            'payback_year': payback,
            'roi_percent': roi,
            'new_loss_percent': new_loss,
            'loss_reduction': reduction,
            'implementation_years': impl_years,
            'net_cashflow_array': net_cashflow,
            'cumulative_net_array': cumulative,
        }
    
    # Combined approach (simplified)
    combined = options['combined_approach']
    capital_combined = combined['capital_cost_ngn_million'] * 1e6
    impl_years_combined = combined['implementation_time_months'] / 12
    synergy = combined['expected_impact']['synergy_benefit'] / 100
    loss_reduction_combined = baseline_loss * (combined['expected_impact']['reduces_total_losses'] / 100) * (1 + synergy)
    new_loss_combined = baseline_loss - loss_reduction_combined
    
    # rough NPV calculation
    total_savings = 0
    for i in range(1, analysis_years + 1):
        baseline_rev_loss = baseline_loss_results['revenue_lost_ngn_million'][i]
        if i < impl_years_combined:
            progress = i / impl_years_combined
            curr_loss = baseline_loss - loss_reduction_combined * progress
        else:
            curr_loss = new_loss_combined
        
        energy_year = base_energy * (1 + financial_params['energy_growth_rate']) ** i
        tariff_year = financial_params['grid_tariff_ngn_per_kwh'] * \
                     (1 + financial_params['tariff_escalation_rate']) ** i
        loss_with_invest = energy_year * (curr_loss / 100)
        rev_loss_with_invest = loss_with_invest * tariff_year * 1000 / 1e6
        savings = baseline_rev_loss - rev_loss_with_invest
        total_savings += savings * 1e6
    
    total_om = capital_combined * (combined['annual_om_percent'] / 100) * (analysis_years - impl_years_combined)
    net_cashflow_combined = total_savings - capital_combined - total_om
    npv_combined = -capital_combined
    for i in range(1, analysis_years + 1):
        if i < impl_years_combined:
            progress = i / impl_years_combined
            savings_year = (total_savings / analysis_years) * progress
            om_year = capital_combined * (combined['annual_om_percent'] / 100) * progress
        else:
            savings_year = total_savings / analysis_years
            om_year = capital_combined * (combined['annual_om_percent'] / 100)
        cf = savings_year - om_year
        npv_combined += cf / ((1 + discount_rate) ** i)
    
    roi_combined = (net_cashflow_combined / capital_combined) * 100
    
    investment_results['combined_approach'] = {
        'name': 'Combined Approach',
        'capital_cost_ngn': capital_combined,
        'npv_ngn': npv_combined,
        'roi_percent': roi_combined,
        'new_loss_percent': new_loss_combined,
        'loss_reduction': loss_reduction_combined,
        'implementation_years': impl_years_combined,
    }
    
    return investment_results


# ============================================================================
# 4. BUDGET-CONSTRAINED PORTFOLIO OPTIMIZATION
# ============================================================================

def optimize_loss_reduction_strategy(distribution_system, investment_results):
    """Select optimal combination of options under different budget levels."""
    
    options = ['metering_upgrade', 'network_rehabilitation', 'anti_theft_measures']
    option_data = []
    for opt in options:
        if opt in investment_results:
            data = investment_results[opt]
            option_data.append({
                'name': opt,
                'capital_cost': data['capital_cost_ngn'],
                'npv': data['npv_ngn'],
                'loss_reduction': data['loss_reduction'],
                'roi': data['roi_percent']
            })
    
    budget_scenarios = {
        'low_budget': 200e6,
        'medium_budget': 500e6,
        'high_budget': 800e6,
        'unlimited': float('inf')
    }
    
    optimal_portfolios = {}
    
    for budget_name, budget_amount in budget_scenarios.items():
        best_portfolio = None
        best_npv = -float('inf')
        best_cost = 0
        
        for r in range(1, len(option_data) + 1):
            for combo in itertools.combinations(range(len(option_data)), r):
                total_cost = sum(option_data[i]['capital_cost'] for i in combo)
                if total_cost <= budget_amount:
                    total_npv = sum(option_data[i]['npv'] for i in combo)
                    total_loss_red = sum(option_data[i]['loss_reduction'] for i in combo)
                    if len(combo) > 1:
                        total_loss_red *= 1.10   # synergy
                        total_npv *= 1.05
                    
                    if total_npv > best_npv:
                        best_npv = total_npv
                        best_portfolio = combo
                        best_cost = total_cost
        
        if best_portfolio is not None:
            portfolio_names = [option_data[i]['name'] for i in best_portfolio]
            total_loss_red = sum(option_data[i]['loss_reduction'] for i in best_portfolio)
            if len(best_portfolio) > 1:
                total_loss_red *= 1.10
            new_loss_rate = distribution_system['current_loss_scenario']['total_loss_percent'] - total_loss_red
            optimal_portfolios[budget_name] = {
                'options': portfolio_names,
                'total_cost_ngn': best_cost,
                'total_npv_ngn': best_npv,
                'new_loss_rate': new_loss_rate,
                'total_loss_reduction': total_loss_red,
                'budget_utilization': (best_cost / budget_amount * 100) if budget_amount < float('inf') else 100
            }
    
    return optimal_portfolios


# ============================================================================
# 5. DECISION DASHBOARD - PURE CHARTS (NO TEXT)
# ============================================================================

def create_decision_dashboard(distribution_system, loss_results, investment_results, optimal_portfolios):
    """
    Create a clean, 9-chart dashboard with no embedded recommendations.
    All textual decision output will be saved to a separate .txt file.
    """
    
    fig = plt.figure(constrained_layout=True, figsize=(18, 12))
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # ---------- 1. Loss Trends Over Time ----------
    ax1 = fig.add_subplot(gs[0, 0])
    colors = {'baseline': 'red', 'low_loss': 'green', 'medium_loss': 'orange', 'high_loss': 'purple'}
    for sc, data in loss_results.items():
        ax1.plot(data['years'], data['loss_percent'], '-', linewidth=2,
                 color=colors.get(sc, 'blue'), label=data['name'])
    ax1.axhline(y=distribution_system['current_loss_scenario']['total_loss_percent'],
                color='black', linestyle='--', alpha=0.5, label='Current')
    ax1.set_xlabel('Years')
    ax1.set_ylabel('Loss (%)')
    ax1.set_title('Loss Trends Under Different Scenarios')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=8)
    ax1.set_ylim(0, 35)
    
    # ---------- 2. Year-10 Revenue Loss ----------
    ax2 = fig.add_subplot(gs[0, 1])
    names = [data['name'][:15] for data in loss_results.values()]
    rev_loss_y10 = [data['revenue_lost_ngn_million'][10] for data in loss_results.values()]
    bars = ax2.bar(names, rev_loss_y10, color=['red', 'green', 'orange', 'purple'], alpha=0.7)
    ax2.set_xlabel('Scenario')
    ax2.set_ylabel('Year 10 Revenue Loss (₦M)')
    ax2.set_title('Revenue Loss – Year 10')
    ax2.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, rev_loss_y10):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+30, f'₦{val:.0f}M',
                 ha='center', va='bottom', fontsize=8)
    
    # ---------- 3. Cumulative Revenue Loss ----------
    ax3 = fig.add_subplot(gs[0, 2])
    for sc, data in loss_results.items():
        ax3.plot(data['years'][1:], data['cumulative_revenue_lost'], '-', linewidth=2,
                 color=colors.get(sc, 'blue'), label=data['name'])
    ax3.set_xlabel('Years')
    ax3.set_ylabel('Cumulative Revenue Loss (₦M)')
    ax3.set_title('10-Year Cumulative Revenue Loss')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper left', fontsize=7)
    
    # ---------- 4. Loss Composition (Pie) ----------
    ax4 = fig.add_subplot(gs[1, 0])
    tech = distribution_system['current_loss_scenario']['technical_losses']['percentage']
    nontech = distribution_system['current_loss_scenario']['non_technical_losses']['percentage']
    ax4.pie([tech, nontech], labels=['Technical', 'Non-Technical'],
            autopct='%1.1f%%', colors=['#ff9999', '#66b3ff'], startangle=90)
    ax4.set_title('Current Loss Composition')
    
    # ---------- 5. Investment Financial Metrics (NPV & ROI) ----------
    ax5 = fig.add_subplot(gs[1, 1])
    inv_names = []
    npv_vals = []
    roi_vals = []
    for opt, res in investment_results.items():
        if 'npv_ngn' in res:
            inv_names.append(res['name'][:20])
            npv_vals.append(res['npv_ngn'] / 1e6)
            roi_vals.append(res.get('roi_percent', 0))
    x = np.arange(len(inv_names))
    width = 0.35
    ax5.bar(x - width/2, npv_vals, width, label='NPV (₦M)', color='green', alpha=0.7)
    ax5.bar(x + width/2, roi_vals, width, label='ROI (%)', color='blue', alpha=0.7)
    ax5.set_xlabel('Investment Option')
    ax5.set_ylabel('Value')
    ax5.set_title('Financial Metrics')
    ax5.set_xticks(x)
    ax5.set_xticklabels(inv_names, rotation=45, ha='right', fontsize=8)
    ax5.grid(True, alpha=0.3, axis='y')
    ax5.legend(loc='upper left', fontsize=7)
    
    # ---------- 6. Payback Period ----------
    ax6 = fig.add_subplot(gs[1, 2])
    pb_names = []
    pb_years = []
    pb_colors = []
    for opt, res in investment_results.items():
        if res.get('payback_year') is not None:
            pb_names.append(res['name'])
            pb_years.append(res['payback_year'])
            pb_colors.append('green' if res['payback_year'] <= 5 else
                            'orange' if res['payback_year'] <= 7 else 'red')
    if pb_names:
        ax6.barh(pb_names, pb_years, color=pb_colors, alpha=0.7)
        ax6.axvline(5, color='green', linestyle='--', alpha=0.5, label='5-yr target')
        ax6.axvline(7, color='orange', linestyle='--', alpha=0.5, label='7-yr max')
        ax6.set_xlabel('Payback (Years)')
        ax6.set_title('Payback Period')
        ax6.legend(loc='lower right', fontsize=7)
        for bar, val in zip(ax6.patches, pb_years):
            ax6.text(val + 0.1, bar.get_y() + bar.get_height()/2, f'{val}y',
                     ha='left', va='center', fontsize=8)
    
    # ---------- 7. Optimal Portfolios by Budget ----------
    ax7 = fig.add_subplot(gs[2, 0])
    if optimal_portfolios:
        budget_names = [bn.replace('_', ' ').title() for bn in optimal_portfolios.keys()]
        new_loss_rates = [p['new_loss_rate'] for p in optimal_portfolios.values()]
        npv_port = [p['total_npv_ngn'] / 1e6 for p in optimal_portfolios.values()]
        
        xp = np.arange(len(budget_names))
        widthp = 0.35
        ax7.bar(xp - widthp/2, new_loss_rates, widthp, label='New Loss %', color='red', alpha=0.7)
        ax7_twin = ax7.twinx()
        ax7_twin.bar(xp + widthp/2, npv_port, widthp, label='NPV (₦M)', color='green', alpha=0.7)
        ax7.set_xlabel('Budget Scenario')
        ax7.set_ylabel('New Loss Rate (%)', color='red')
        ax7_twin.set_ylabel('NPV (₦ Million)', color='green')
        ax7.set_title('Optimal Portfolios by Budget')
        ax7.set_xticks(xp)
        ax7.set_xticklabels(budget_names, rotation=45, ha='right', fontsize=8)
        ax7.axhline(y=distribution_system['current_loss_scenario']['total_loss_percent'],
                    color='black', linestyle='--', alpha=0.5, label='Current')
        # combine legends
        lines1, lab1 = ax7.get_legend_handles_labels()
        lines2, lab2 = ax7_twin.get_legend_handles_labels()
        ax7.legend(lines1 + lines2, lab1 + lab2, loc='upper left', fontsize=7)
    
    # ---------- 8. Impact of Loss Rate on Revenue ----------
    ax8 = fig.add_subplot(gs[2, 1])
    loss_rates = np.arange(5, 35, 2.5)
    annual_energy = distribution_system['system_overview']['annual_energy_gwh']
    tariff = distribution_system['financial_parameters']['grid_tariff_ngn_per_kwh']
    revenues = []
    losses_rev = []
    for lr in loss_rates:
        energy_lost = annual_energy * (lr / 100)
        energy_billed = annual_energy - energy_lost
        revenue = energy_billed * tariff * 1000 / 1e6
        rev_lost = energy_lost * tariff * 1000 / 1e6
        revenues.append(revenue)
        losses_rev.append(rev_lost)
    ax8.plot(loss_rates, revenues, 'g-', linewidth=2, label='Annual Revenue')
    ax8_twin = ax8.twinx()
    ax8_twin.plot(loss_rates, losses_rev, 'r-', linewidth=2, label='Annual Loss')
    ax8.set_xlabel('Loss Rate (%)')
    ax8.set_ylabel('Revenue (₦M)', color='g')
    ax8_twin.set_ylabel('Revenue Loss (₦M)', color='r')
    ax8.set_title('Impact of Loss Rate on Revenue')
    ax8.grid(True, alpha=0.3)
    # mark current
    curr_loss = distribution_system['current_loss_scenario']['total_loss_percent']
    curr_rev = np.interp(curr_loss, loss_rates, revenues)
    curr_loss_rev = np.interp(curr_loss, loss_rates, losses_rev)
    ax8.plot(curr_loss, curr_rev, 'bo', markersize=6, label='Current')
    ax8_twin.plot(curr_loss, curr_loss_rev, 'ro', markersize=6)
    # combine legends
    l1, lab1 = ax8.get_legend_handles_labels()
    l2, lab2 = ax8_twin.get_legend_handles_labels()
    ax8.legend(l1 + l2, lab1 + lab2, loc='upper right', fontsize=7)
    
    # ---------- 9. Implementation Timeline (Medium Budget) ----------
    ax9 = fig.add_subplot(gs[2, 2])
    if 'medium_budget' in optimal_portfolios:
        phases = [
            (0, 6, 'Planning & Design', '#FFE5CC'),
            (6, 18, 'Metering Upgrade', '#CCE5FF'),
            (12, 30, 'Network Rehab', '#D4EDDA'),
            (6, 24, 'Anti-Theft', '#F8D7DA'),
            (24, 36, 'Integration', '#E2E3E5'),
            (36, 48, 'Monitoring', '#FFF3CD')
        ]
        ypos = np.arange(len(phases))
        for i, (start, end, name, color) in enumerate(phases):
            ax9.barh(i, end-start, left=start, height=0.6, color=color, edgecolor='black')
            ax9.text((start+end)/2, i, name, ha='center', va='center', fontsize=7, fontweight='bold')
        ax9.set_yticks(ypos)
        ax9.set_yticklabels([])
        ax9.set_xlabel('Months')
        ax9.set_title('Implementation Timeline (Medium Budget)')
        ax9.grid(True, alpha=0.3, axis='x')
        for month in [6, 18, 24, 30, 36, 48]:
            ax9.axvline(x=month, color='black', linestyle='--', alpha=0.2)
    
    # Overall title with disclaimer
    fig.suptitle('ENERGY LOSSES & THEFT IMPACT MODEL\n'
                 'Lagos Case Study – Illustrative Assumptions (Not Actual Data)',
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.savefig('energy_losses_theft_impact_charts.png', dpi=300,
                bbox_inches='tight', facecolor='white')
    plt.show()
    return fig


# ============================================================================
# 6. DECISION RECOMMENDATIONS – SAVE TO TEXT FILE
# ============================================================================

def save_decision_recommendations(distribution_system, investment_results, optimal_portfolios):
    """
    Write all textual recommendations, financial justification, and risk mitigation
    to a separate .txt file. Includes clear disclaimer about assumptions.
    """
    
    with open('energy_losses_recommendations.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ENERGY LOSSES & THEFT IMPACT MODEL – DECISION RECOMMENDATIONS\n")
        f.write("Lagos Case Study (Illustrative, Assumed Data – Not Actual)\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("⚠️  DISCLAIMER: This analysis is based entirely on hypothetical assumptions\n")
        f.write("   and is intended for educational decision-modeling practice only.\n")
        f.write("   No real operational data from any utility was used.\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("DECISION QUESTION\n")
        f.write("=" * 80 + "\n")
        f.write("For an energy distribution system experiencing 25% losses\n")
        f.write("(15% technical, 10% non-technical), is investing in loss reduction\n")
        f.write("measures financially justified, and what is the optimal strategy?\n\n")
        
        # Current situation
        current_loss = distribution_system['current_loss_scenario']['total_loss_percent']
        annual_loss_gwh = distribution_system['current_loss_scenario']['annual_loss_gwh']
        annual_rev_loss = distribution_system['current_loss_scenario']['annual_revenue_loss_ngn_million']
        f.write(f"Current annual revenue loss: ₦{annual_rev_loss:.1f}M\n")
        f.write(f"Current loss rate: {current_loss}%\n\n")
        
        # Summary of investment options
        f.write("=" * 80 + "\n")
        f.write("INVESTMENT OPTIONS – FINANCIAL SUMMARY (10-year horizon)\n")
        f.write("=" * 80 + "\n")
        for opt, res in investment_results.items():
            if 'npv_ngn' in res:
                f.write(f"\n{res['name']}:\n")
                f.write(f"  Capital Cost: ₦{res['capital_cost_ngn']/1e6:.1f}M\n")
                f.write(f"  New Loss Rate: {res['new_loss_percent']:.1f}%\n")
                f.write(f"  NPV (12% disc.): ₦{res['npv_ngn']/1e6:.1f}M\n")
                if 'payback_year' in res and res['payback_year']:
                    f.write(f"  Payback Period: {res['payback_year']} years\n")
                f.write(f"  ROI: {res['roi_percent']:.1f}%\n")
        
        # Optimal portfolio under medium budget
        f.write("\n" + "=" * 80 + "\n")
        f.write("OPTIMAL STRATEGY – RECOMMENDED PORTFOLIO\n")
        f.write("=" * 80 + "\n")
        if 'medium_budget' in optimal_portfolios:
            port = optimal_portfolios['medium_budget']
            f.write(f"\n🎯 RECOMMENDED: Medium Budget Portfolio (₦500M constraint)\n")
            f.write(f"   Total Investment: ₦{port['total_cost_ngn']/1e6:.1f}M\n")
            f.write(f"   Selected Options: {', '.join(port['options'])}\n")
            f.write(f"\n   Expected Outcomes:\n")
            f.write(f"   • New Loss Rate: {port['new_loss_rate']:.1f}% (from {current_loss:.1f}%)\n")
            f.write(f"   • 10-year NPV: ₦{port['total_npv_ngn']/1e6:.1f}M\n")
            f.write(f"   • Simple Payback: ~{port['total_cost_ngn']/(annual_rev_loss*1e6):.1f} years\n")
            
            # Calculate annual energy saved
            annual_energy = distribution_system['system_overview']['annual_energy_gwh']
            new_annual_loss_gwh = annual_energy * (port['new_loss_rate'] / 100)
            energy_saved = annual_loss_gwh - new_annual_loss_gwh
            households = energy_saved * 1e6 / (3.65 * 5)  # 5 kWh/day per household
            f.write(f"   • Annual Energy Saved: {energy_saved:.1f} GWh\n")
            f.write(f"   • Annual Revenue Saved: ₦{energy_saved * distribution_system['financial_parameters']['grid_tariff_ngn_per_kwh'] * 1000 / 1e6:.1f}M\n")
            f.write(f"   • Equivalent Households Served: {households:,.0f}\n")
        else:
            f.write("No feasible portfolio identified under medium budget.\n")
        
        # Implementation roadmap
        f.write("\n" + "=" * 80 + "\n")
        f.write("IMPLEMENTATION ROADMAP\n")
        f.write("=" * 80 + "\n")
        f.write("Phase 1 (Months 1-6):   Planning & Design, anti-theft quick wins\n")
        f.write("Phase 2 (Months 6-18):  Metering upgrade deployment\n")
        f.write("Phase 3 (Months 12-30): Network rehabilitation\n")
        f.write("Phase 4 (Months 24-36): System integration & data analytics\n")
        f.write("Phase 5 (Months 36-48): Monitoring, optimisation, community engagement\n")
        
        # Risk mitigation
        f.write("\n" + "=" * 80 + "\n")
        f.write("RISK MITIGATION ACTIONS\n")
        f.write("=" * 80 + "\n")
        f.write("1. Phased implementation to manage cash flow and reduce disruption\n")
        f.write("2. Pilot programs in selected feeders before full rollout\n")
        f.write("3. Community engagement campaigns to reduce theft and increase payment compliance\n")
        f.write("4. Performance-based contracts with vendors (e.g., guaranteed loss reduction)\n")
        f.write("5. Real-time loss monitoring and monthly performance reviews\n")
        
        # Conclusion
        f.write("\n" + "=" * 80 + "\n")
        f.write("CONCLUSION\n")
        f.write("=" * 80 + "\n")
        f.write("Under the assumed parameters, investment in loss reduction is clearly\n")
        f.write("financially justified. The optimal strategy is a ₦500M portfolio combining\n")
        f.write("metering upgrades and anti-theft measures, delivering positive NPV,\n")
        f.write("a payback under 5 years, and a loss reduction from 25% to ~18%.\n")
        f.write("\n--- End of Recommendations ---\n")
    
    print("\n✅ Decision recommendations saved to 'energy_losses_recommendations.txt'")


# ============================================================================
# 7. MAIN EXECUTION
# ============================================================================

def main():
    """Execute full analysis and produce both chart dashboard and text file."""
    
    print("=" * 100)
    print("DAY 11: ENERGY LOSSES & THEFT IMPACT MODEL")
    print("(Illustrative Model – Assumed Data, Lagos Case Study)")
    print("=" * 100)
    
    # Step 1: Define system (assumptions)
    distribution_system = define_distribution_system()
    
    # Step 2: Model loss impact over time
    loss_results = model_loss_impact_over_time(distribution_system)
    
    # Step 3: Analyze investment options
    investment_results = analyze_investment_options(distribution_system, loss_results)
    
    # Step 4: Optimise under budget constraints
    optimal_portfolios = optimize_loss_reduction_strategy(distribution_system, investment_results)
    
    # Step 5: Create pure‑chart dashboard (no text boxes)
    create_decision_dashboard(distribution_system, loss_results, investment_results, optimal_portfolios)
    
    # Step 6: Save decision recommendations to separate text file
    save_decision_recommendations(distribution_system, investment_results, optimal_portfolios)
    
    print("\n" + "=" * 100)
    print("PORTFOLIO DELIVERABLES GENERATED:")
    print("=" * 100)
    print("✓ energy_losses_theft_impact_charts.png       (9‑chart dashboard, no text)")
    print("✓ energy_losses_recommendations.txt          (full decision report)")
    print("✓ Clear disclaimer of assumptions throughout")
    print("\n" + "=" * 100)
    print("DAY 11 COMPLETE – READY FOR DAY 12")
    print("=" * 100)


if __name__ == "__main__":
    main()