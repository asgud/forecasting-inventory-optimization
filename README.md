# 📊 Supply Chain Forecasting & Inventory Optimization

A data-driven approach to demand forecasting and inventory management for a global retail supply chain.


### 🛠️ Skills & Tools
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)

`ABC-XYZ Analysis` `Time Series Forecasting` `Inventory Optimization` `Safety Stock Calculation` `Data Visualization` `Interactive Dashboards`

---

## 📋 Business Case

> *This project uses a publicly available supply chain dataset to simulate a real-world inventory optimization scenario.*

### The Problem

A global retail company manages **87 products** across multiple markets. The supply chain team faces two critical challenges:

1. **Stockouts** — Lost sales due to insufficient inventory
2. **Overstocking** — Cash tied up in excess inventory

Currently, inventory decisions are based on intuition and historical averages, leading to inconsistent service levels and suboptimal inventory investment.

### The Goal

Build a **data-driven inventory planning system** that:
- Predicts future demand using time series forecasting
- Identifies high-priority products for focused management
- Calculates optimal safety stock and reorder points
- Provides actionable recommendations to prevent stockouts

### Business Impact

| Metric | Before | After |
|--------|--------|-------|
| Demand Visibility | Reactive | 4-week forecast |
| Product Focus | All 87 equally | Top 6 products (74% revenue) |
| Reorder Decisions | Gut feeling | Data-driven triggers |
| Stockout Risk | Unknown | Predicted days in advance |

---

## 🎯 Approach

### Scope
- **Data:** 75,564 orders over 145 weeks (2015-2017)
- **Products:** Focus on AX segment (high-value, stable demand)
- **Forecast Horizon:** 4-12 weeks ahead
- **Output:** Interactive dashboard for inventory planning

### Methodology

1. **Data Cleaning** — Validate and prepare 75,564 orders
2. **ABC-XYZ Segmentation** — Identify high-priority products
3. **Demand Forecasting** — Predict future demand using time series model
4. **Inventory Optimization** — Calculate safety stock & reorder points

---

## 🔍 Key Techniques

### 1. ABC-XYZ Analysis
Segmented 87 products based on **revenue contribution (ABC)** and **demand variability (XYZ)**.

| Segment | Products | Revenue Share | Strategy |
|---------|----------|---------------|----------|
| **AX** | 6 | 74% | Lean/JIT — High priority, tight control |
| BX | 3 | 21% | Automated reorder — Moderate monitoring |
| CY/CZ | 78 | 5% | Minimal stock — Low investment |

**Insight:** Focus resources on 6 AX products that drive 74% of revenue.

### 2. Time Series Forecasting

#### Why Time Series Over ML Models?

| Factor | Our Data | Implication |
|--------|----------|-------------|
| Variability (CV) | 11.1% | Low — Simple models work well |
| Trend | Flat (slope = -0.61) | No trend models needed |
| Seasonality | 9.8% variation | Weak — No seasonal models needed |
| Features Available | Demand only | No external features for ML |

**Conclusion:** With stable demand and no external features (price, promotions, weather), simple time series models outperform complex ML models which would overfit the data.

#### Model Comparison

| Model | MAPE | Result |
|-------|------|--------|
| Naive | 19.06% | Baseline |
| Moving Average (4) | 19.39% | Too slow |
| **SES (α=0.6)** | **18.75%** | ✅ Winner |

**Why Simple Exponential Smoothing (SES)?**  
SES balances reactivity (responds to recent changes) with stability (doesn't overreact to noise).

### 3. Safety Stock & Reorder Point
Calculated inventory parameters for each AX product:

```
Safety Stock = Z × σ × √(Lead Time)
Reorder Point = (Avg Demand × Lead Time) + Safety Stock
```

| Product | Safety Stock | Reorder Point |
|---------|--------------|---------------|
| Field & Stream Gun Safe | 14 units | 40 units |
| Perfect Fitness Rip Deck | 57 units | 167 units |
| Nike Running Shoe | 41 units | 97 units |

**Service Level:** 99% for all AX products (Z = 2.33)

---

## 📱 Interactive Dashboard

Built a Streamlit app that allows users to:

✅ Select any AX product  
✅ View demand forecast (historical + future)  
✅ Simulate inventory depletion  
✅ Get reorder recommendations with cost impact  

**Try it:** `streamlit run app.py`

---

## 📁 Project Structure

```
├── 01_Data_Cleaning.ipynb        # Data validation & cleaning
├── 02_EDA_ABC_XYZ.ipynb          # Exploratory analysis & segmentation
├── 03_Forecasting_Models.ipynb   # Model comparison & selection
├── 04_Inventory_Optimization.ipynb # Safety stock & reorder calculations
├── app.py                        # Streamlit dashboard
├── data/                         # Raw and processed data
├── outputs/                      # Analysis results (CSV)
├── banner.jpg                    # Dashboard banner image
└── requirements.txt              # Python dependencies
```

---

## ⚠️ Limitations

| Limitation | Impact | Future Improvement |
|------------|--------|-------------------|
| **Single variable model** | Doesn't account for price, promotions, seasonality | Add external features with ML models |
| **Static lead time** | Uses average LT, not dynamic | Incorporate supplier variability |
| **Historical data only** | No real-time inventory tracking | Connect to live inventory system |
| **AX products only** | 6 of 87 products covered | Extend to BX, CY segments |

---

## 🚀 Getting Started

```bash
# Clone repository
git clone https://github.com/yourusername/supply-chain-forecasting.git

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run app.py
```

---

## 📈 Results Summary

| Deliverable | Outcome |
|-------------|---------|
| Product Segmentation | 6 AX products identified (74% revenue) |
| Forecast Accuracy | 12-19% MAPE across AX products |
| Inventory Parameters | Safety stock & reorder points calculated |
| Decision Tool | Interactive dashboard for inventory planning |

---

## 👤 About

Supply chain professional developing data science skills to bridge the gap between business operations and analytics. This project demonstrates how data-driven approaches can improve inventory management decisions.

---

## 📄 License

This project uses the [DataCo Supply Chain Dataset](https://data.mendeley.com/) for educational purposes.
