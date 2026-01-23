# Day 3: Solar PV Sizing Analysis - Grid Offset Model

## Project Overview

This project designs an optimal solar PV system to offset 60% of daily energy consumption for a typical Nigerian household. The analysis considers Nigeria-specific solar conditions, system losses, roof space constraints, and provides comprehensive financial and environmental benefits assessment.

## Professional Context

Solar PV system sizing is a critical skill for energy system managers, requiring understanding of local solar resources, load patterns, financial analysis, and technical constraints. This project demonstrates the complete process from load analysis to system design and economic justification.

## Technical Approach

The analysis follows industry-standard methodology:

1. **Load Profile Analysis**: Uses consistent household demand from Day 1
2. **Solar Resource Assessment**: Nigeria-specific solar parameters (5.5 peak sun hours average)
3. **System Sizing**: Calculates required PV capacity for 60% offset target
4. **Performance Modeling**: Creates realistic hourly generation profile
5. **Energy Balance Analysis**: Compares generation vs consumption
6. **Financial Analysis**: ROI, payback period, lifetime savings
7. **Environmental Assessment**: CO2 reduction and equivalent benefits

## Key Deliverables

- **Load vs Solar Generation Profile**: Hourly comparison visualization
- **PV System Specifications**: Size, panel count, roof space requirements
- **Energy Balance Analysis**: Self-consumption, export, import metrics
- **Financial Analysis**: Cost, savings, ROI, payback period
- **Environmental Benefits**: CO2 reduction, equivalent trees/cars
- **System Recommendations**: Optimization and risk mitigation strategies

## Technical Specifications

- **Target Offset**: 60% of daily energy consumption
- **Solar Resource**: Nigeria average (5.5 peak sun hours)
- **System Losses**: 20% (wiring, inverter, temperature, etc.)
- **Panel Technology**: 550W monocrystalline (20.5% efficiency)
- **Inverter Efficiency**: 96% (grid-tied)
- **Roof Space**: 50 m² available with 20% spacing factor

## Key Findings

1. **Optimal System Size**: 4.2 kW PV system (8 × 550W panels)
2. **Daily Generation**: 18.5 kWh (62% actual offset)
3. **Financial Metrics**: 4.2-year payback, 24% ROI in Year 1
4. **Environmental Impact**: 3.8 tons CO2 reduction annually
5. **Roof Utilization**: 26.1 m² required (52% of available space)

## Files Included

- `solar_pv_sizing_analysis.py` - Main analysis script
- `solar_pv_sizing_analysis.png` - Main visualization dashboard
- `monthly_solar_generation.png` - Monthly generation profile
- `solar_hourly_analysis.csv` - Detailed hourly data
- `solar_system_sizing_summary.csv` - System specifications
- `solar_financial_summary.csv` - Financial analysis
- `requirements.txt` - Python dependencies

## How to Reproduce

```bash
# Install dependencies
pip install -r requirements.txt

# Run analysis
python solar_pv_sizing_analysis.py
```
