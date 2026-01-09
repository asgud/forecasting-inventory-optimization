import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Supply Chain Dashboard",
    page_icon="📊",
    layout="wide"
)

# ============================================
# CUSTOM CSS FOR STYLING
# ============================================
st.markdown("""
<style>
    .warning-box {
        background: #FEF3C7;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #F59E0B;
    }
    .success-box {
        background: #D1FAE5;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #10B981;
    }
    .critical-box {
        background: #FEE2E2;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #EF4444;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-top: 10px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# LOAD DATA
# ============================================
@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/df_clean_filtered.csv')
    df['order date (DateOrders)'] = pd.to_datetime(df['order date (DateOrders)'])
    inventory_df = pd.read_csv('outputs/inventory_parameters.csv')
    return df, inventory_df

df, inventory_df = load_data()

# ============================================
# HEADER WITH BANNER IMAGE
# ============================================

# Title
st.markdown("""
<div style="text-align: center; margin-bottom: 10px;">
    <h1 style="font-size: 2.5rem; font-weight: 800; color: #1E3A8A;">
        📊 Supply Chain Forecasting & Inventory Planner
    </h1>
    <p style="font-size: 1.2rem; color: #64748B; margin-top: -10px;">
        Demand Forecasting & Inventory Optimization for AX Products
    </p>
</div>
""", unsafe_allow_html=True)

# Banner image (local file)
st.image("banner.jpg", use_container_width=True)

st.markdown("---")

# ============================================
# SIDEBAR - PRODUCT SELECTOR
# ============================================
with st.sidebar:
    st.markdown("## 🔍 Product Selection")
    
    product_list = inventory_df['Product'].tolist()
    selected_product = st.selectbox(
        "Choose a product:",
        product_list,
        index=0
    )
    
    st.markdown("---")
    
    st.markdown("## 📦 Inventory Input")
    current_stock = st.number_input(
        "Current Stock (units):",
        min_value=0,
        max_value=1000,
        value=100,
        step=10
    )
    
    forecast_weeks = st.slider(
        "Forecast Horizon (weeks):",
        min_value=1,
        max_value=12,
        value=4
    )
    
    weeks_of_supply = st.slider(
        "Target Weeks of Supply:",
        min_value=2,
        max_value=8,
        value=4
    )
    
    st.markdown("---")
    st.markdown("### 📋 About")
    st.info("This dashboard helps inventory managers predict demand and optimize stock levels for high-value products.")

# ============================================
# GET SELECTED PRODUCT DATA
# ============================================
product_data = inventory_df[inventory_df['Product'] == selected_product].iloc[0]

# Calculate weekly demand for selected product
product_orders = df[df['Product Name'] == selected_product]
weekly_demand = product_orders.resample('W', on='order date (DateOrders)')['Order Item Quantity'].sum()

# Get key values
avg_demand = product_data['Avg_Weekly_Demand']
unit_price = product_data['Unit_Price']
safety_stock = product_data['Safety_Stock']
reorder_point = product_data['Reorder_Point']

# ============================================
# ORDER CALCULATION (Order Up-To Level)
# ============================================
target_stock = (avg_demand * weeks_of_supply) + safety_stock
order_qty = max(0, int(target_stock - current_stock))
order_cost = order_qty * unit_price

# ============================================
# KEY METRICS ROW
# ============================================
st.markdown('<p class="section-header">📈 Product Overview</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 Unit Price",
        value=f"${unit_price:.2f}"
    )

with col2:
    st.metric(
        label="📦 Avg Weekly Demand",
        value=f"{avg_demand:.0f} units"
    )

with col3:
    cv = product_data['Std_Weekly_Demand'] / product_data['Avg_Weekly_Demand']
    accuracy = (1 - cv) * 100
    st.metric(
        label="🎯 Forecast Accuracy",
        value=f"{accuracy:.1f}%"
    )

with col4:
    st.metric(
        label="🚚 Lead Time",
        value=f"{product_data['Lead_Time_Days']:.1f} days"
    )

st.markdown("---")

# ============================================
# FORECAST SECTION
# ============================================
st.markdown('<p class="section-header">📈 Weekly Demand: Historical & Forecast</p>', unsafe_allow_html=True)

# Train/Test split (80/20)
train_size = int(len(weekly_demand) * 0.8)
train = weekly_demand[:train_size]
test = weekly_demand[train_size:]

# Generate SES forecast for TEST period
alpha = 0.6
test_forecast = []
last_forecast = train.iloc[-1] if len(train) > 0 else avg_demand
for i in range(len(test)):
    if i == 0:
        pred = last_forecast
    else:
        pred = alpha * test.iloc[i-1] + (1 - alpha) * last_forecast
    test_forecast.append(pred)
    last_forecast = pred

# Generate FUTURE forecast
future_forecast = []
last_val = weekly_demand.iloc[-1] if len(weekly_demand) > 0 else avg_demand
for i in range(forecast_weeks):
    pred = alpha * last_val + (1 - alpha) * avg_demand
    future_forecast.append(pred)
    last_val = pred

# Create date labels
train_dates = list(train.index[-20:])
test_dates = list(test.index)
last_date = weekly_demand.index[-1]
future_dates = list(pd.date_range(start=last_date, periods=forecast_weeks + 1, freq='W')[1:])

# Create Plotly chart
fig = go.Figure()

# 1. Training period (Actual)
fig.add_trace(go.Scatter(
    x=train_dates,
    y=train.values[-20:],
    mode='lines',
    name='Historical (Train)',
    line=dict(color='#93C5FD', width=2)
))

# 2. Test period (Actual)
fig.add_trace(go.Scatter(
    x=test_dates,
    y=test.values,
    mode='lines+markers',
    name='Actual (Test Period)',
    line=dict(color='#3B82F6', width=2),
    marker=dict(size=6)
))

# 3. Test period (Forecast)
fig.add_trace(go.Scatter(
    x=test_dates,
    y=test_forecast,
    mode='lines+markers',
    name='Forecast (Test Period)',
    line=dict(color='#10B981', width=2, dash='dash'),
    marker=dict(size=6, symbol='diamond')
))

# 4. Future forecast
fig.add_trace(go.Scatter(
    x=future_dates,
    y=future_forecast,
    mode='lines+markers',
    name='Future Forecast',
    line=dict(color='#F59E0B', width=3, dash='dot'),
    marker=dict(size=8, symbol='star')
))

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Demand (Units)",
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),
    height=450,
    template="plotly_white",
    margin=dict(t=80)
)

st.plotly_chart(fig, use_container_width=True)

# Show model accuracy
if len(test) > 0 and len(test_forecast) > 0:
    test_mape = (abs(test.values - np.array(test_forecast)) / test.values).mean() * 100
    st.markdown(f"**📊 Model Performance (Test Period):** MAPE = {test_mape:.1f}%")

# Show forecast table
st.markdown(f"**📊 Predicted Demand (Next {forecast_weeks} weeks):**")
forecast_df = pd.DataFrame({
    'Week': [f"Week {i+1}" for i in range(forecast_weeks)],
    'Date': [d.strftime('%Y-%m-%d') for d in future_dates],
    'Forecast (units)': [f"{f:.0f}" for f in future_forecast]
})
st.dataframe(forecast_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ============================================
# INVENTORY SIMULATION SECTION
# ============================================
st.markdown('<p class="section-header">📦 Inventory Simulation</p>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    # Project inventory
    inventory_projection = [current_stock]
    for i in range(forecast_weeks):
        new_stock = inventory_projection[-1] - future_forecast[i]
        inventory_projection.append(max(0, new_stock))
    
    # Create inventory chart
    fig2 = go.Figure()
    
    week_labels = [f"Week {i}" for i in range(forecast_weeks + 1)]
    
    fig2.add_trace(go.Scatter(
        x=week_labels,
        y=inventory_projection,
        mode='lines+markers',
        name='Projected Inventory',
        line=dict(color='#3B82F6', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))
    
    # Reorder point line
    fig2.add_hline(y=reorder_point, line_dash="dash", line_color="#F59E0B", 
                   annotation_text=f"Reorder Point ({reorder_point:.0f})")
    
    # Safety stock line
    fig2.add_hline(y=safety_stock, line_dash="dot", line_color="#EF4444",
                   annotation_text=f"Safety Stock ({safety_stock:.0f})")
    
    fig2.update_layout(
        title="Inventory Level Projection",
        xaxis_title="Time",
        yaxis_title="Inventory (Units)",
        height=350,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.markdown("#### 📊 Inventory Parameters")
    
    st.metric("🛡️ Safety Stock", f"{safety_stock:.0f} units")
    st.metric("🔔 Reorder Point", f"{reorder_point:.0f} units")
    
    # Calculate days
    daily_demand = avg_demand / 7
    days_until_stockout = current_stock / daily_demand if daily_demand > 0 else 999
    stock_above_rop = current_stock - reorder_point
    days_until_rop = stock_above_rop / daily_demand if daily_demand > 0 and stock_above_rop > 0 else 0
    
    st.metric("⏱️ Days Until Reorder", f"{max(0, days_until_rop):.1f} days")
    st.metric("⚠️ Days Until Stockout", f"{days_until_stockout:.1f} days")

st.markdown("---")

# ============================================
# RECOMMENDATION SECTION
# ============================================
st.markdown('<p class="section-header">💡 Recommendation</p>', unsafe_allow_html=True)

# Order calculation breakdown
st.markdown("#### 📋 Order Calculation (Order Up-To Level)")

calc_col1, calc_col2, calc_col3 = st.columns(3)

with calc_col1:
    st.markdown(f"""
    **Target Stock Calculation:**
    - Avg Weekly Demand: {avg_demand:.0f} units
    - Weeks of Supply: {weeks_of_supply} weeks
    - Safety Stock: {safety_stock:.0f} units
    - **Target Stock: {target_stock:.0f} units**
    """)

with calc_col2:
    st.markdown(f"""
    **Order Quantity:**
    - Target Stock: {target_stock:.0f} units
    - Current Stock: {current_stock} units
    - **Order Qty: {order_qty} units**
    """)

with calc_col3:
    st.markdown(f"""
    **💰 Cost Impact:**
    - Unit Price: ${unit_price:.2f}
    - Order Qty: {order_qty} units
    - **Order Cost: ${order_cost:,.2f}**
    """)

st.markdown("---")

# Recommendation Box
if current_stock <= safety_stock:
    st.markdown(f"""
    <div class="critical-box">
        <h3>🚨 CRITICAL: Stock Below Safety Level!</h3>
        <p>Current stock (<strong>{current_stock} units</strong>) is at or below safety stock (<strong>{int(safety_stock)} units</strong>).</p>
        <p><strong>Action: Place URGENT order of {order_qty} units immediately!</strong></p>
        <p>💰 <strong>Estimated Order Cost: ${order_cost:,.2f}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
elif current_stock <= reorder_point:
    st.markdown(f"""
    <div class="warning-box">
        <h3>⚠️ REORDER POINT REACHED</h3>
        <p>Current stock (<strong>{current_stock} units</strong>) has reached reorder point (<strong>{int(reorder_point)} units</strong>).</p>
        <p><strong>Action: Order {order_qty} units now ({weeks_of_supply}-week supply)</strong></p>
        <p>💰 <strong>Estimated Order Cost: ${order_cost:,.2f}</strong></p>
        <p>With {product_data['Lead_Time_Days']:.1f} days lead time, stock will arrive before depletion.</p>
    </div>
    """, unsafe_allow_html=True)
    
else:
    st.markdown(f"""
    <div class="success-box">
        <h3>✅ STOCK LEVEL HEALTHY</h3>
        <p>Current stock (<strong>{current_stock} units</strong>) is above reorder point (<strong>{int(reorder_point)} units</strong>).</p>
        <p><strong>Next reorder in approximately {days_until_rop:.1f} days.</strong></p>
        <p>When you reorder: <strong>{order_qty} units</strong> (💰 ${order_cost:,.2f})</p>
        <p>Continue monitoring. No immediate action required.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.9rem;">
    📊 Supply Chain Dashboard | Built with Streamlit | Data: DataCo Supply Chain Dataset
</div>
""", unsafe_allow_html=True)


