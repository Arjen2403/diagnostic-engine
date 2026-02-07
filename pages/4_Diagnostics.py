import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_cleaner import clean_data
from modules.stats_engine import apply_z_score, shift_cause_data, calculate_moving_average

st.set_page_config(layout="wide")

st.title("🔗 Time-Lag Diagnostic Engine")
st.markdown("### Identify Cause (Gob/BTC) & Effect (IR/Rejects) Correlations")

# 1. Sidebar Controls for Data Selection
with st.sidebar:
    st.header("Analysis Settings")
    lag_unit = st.radio("Lag Precision", ["seconds", "minutes"])
    lag_value = st.slider(f"Shift Cause Forward ({lag_unit})", 0, 60, 0)
    
    st.divider()
    show_drift = st.checkbox("Show Trend (Moving Average)", value=True)
    window_size = st.text_input("Rolling Window (e.g., 5min, 100)", value="5min")

# 2. Data Simulation / Loading
# In production, these would be loaded from your SQL/CSV ingestion module
st.info("Upload 'Cause' (Sensors) and 'Effect' (IR/Rejects) datasets to begin.")

col1, col2 = st.columns(2)
with col1:
    cause_file = st.file_uploader("Upload Cause Data (e.g., BTC/Gob)", type="csv")
with col2:
    effect_file = st.file_uploader("Upload Effect Data (e.g., IR/Rejects)", type="csv")

if cause_file and effect_file:
    # REQ 3.1: Load and Clean
    df_cause = pd.read_csv(cause_file)
    df_effect = pd.read_csv(effect_file)
    
    df_cause, _ = clean_data(df_cause)
    df_effect, _ = clean_data(df_effect)

    # REQ 3.2: Apply Time-Shift to the Cause
    df_cause_shifted = shift_cause_data(df_cause, lag_value, unit=lag_unit)

    # 3. Visualization Logic
    st.subheader("Interactive Correlation Plot")
    
    # Apply Z-Score for dual-axis comparison (SRS 3.2)
    # Assuming 'Value' is the generic column name for this example
    cause_col = st.selectbox("Select Cause Variable", df_cause.columns)
    effect_col = st.selectbox("Select Effect Variable", df_effect.columns)
    
    # Process for Visualization
    df_cause_shifted = apply_z_score(df_cause_shifted, [cause_col])
    df_effect = apply_z_score(df_effect, [effect_col])

    # Plotting
    fig = go.Figure()

    # Cause Trace (Standardized)
    fig.add_trace(go.Scatter(
        x=df_cause_shifted['DateTimeID'], 
        y=df_cause_shifted[f'z_{cause_col}'],
        name=f"Cause: {cause_col} (Shifted)",
        line=dict(color='orange', width=1)
    ))

    # Effect Trace (Standardized)
    fig.add_trace(go.Scatter(
        x=df_effect['DateTimeID'], 
        y=df_effect[f'z_{effect_col}'],
        name=f"Effect: {effect_col}",
        line=dict(color='cyan', width=1)
    ))

    # Optional Trend Overlay (Drift Analysis)
    if show_drift:
        df_cause_ma = calculate_moving_average(df_cause_shifted, cause_col, window_size)
        # Re-standardize the MA for the plot
        ma_mu, ma_sigma = df_cause_ma[f'smooth_{cause_col}'].mean(), df_cause_ma[f'smooth_{cause_col}'].std()
        fig.add_trace(go.Scatter(
            x=df_cause_ma['DateTimeID'],
            y=(df_cause_ma[f'smooth_{cause_col}'] - ma_mu) / ma_sigma,
            name="Cause Trend (Drift)",
            line=dict(color='red', width=3, dash='dot')
        ))

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Timeline",
        yaxis_title="Z-Score (Standardized Units)",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # 4. Statistical Insight
    st.success(f"Visualizing {len(df_cause)} rows of data with a {lag_value} {lag_unit} offset.")
