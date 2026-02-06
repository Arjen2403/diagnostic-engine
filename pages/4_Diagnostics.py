import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_cleaner import clean_data
from modules.stats_engine import calculate_zscore

st.title("🔗 Cause & Effect: Time-Lag Diagnostics")

# 1. DATA INGESTION (Session State assumed from Ingestion Page)
if 'datasets' not in st.session_state:
    st.warning("Please upload at least two datasets in the Ingestion page first.")
    st.stop()

datasets = st.session_state.datasets # Dictionary of DataFrames

# 2. SELECT CORRELATION PAIR
st.sidebar.header("Correlation Settings")
primary_key = st.sidebar.selectbox("Select Primary Dataset (The Effect)", options=datasets.keys())
secondary_key = st.sidebar.selectbox("Select Secondary Dataset (The Potential Cause)", 
                                     options=[k for k in datasets.keys() if k != primary_key])

# Select columns to compare
p_col = st.sidebar.selectbox(f"Value from {primary_key}", options=datasets[primary_key].select_dtypes(include='number').columns)
s_col = st.sidebar.selectbox(f"Value from {secondary_key}", options=datasets[secondary_key].select_dtypes(include='number').columns)

# 3. TIME-LAG SLIDER
st.sidebar.divider()
lag_minutes = st.sidebar.slider("Time-Lag Shift (Minutes)", 0, 30, 0)
st.sidebar.info("Shifts the 'Cause' dataset forward in time to match the 'Effect'.")

# 4. PROCESSING THE JOIN
# We use the Golden Thread columns established in the SRS
golden_thread = ['DateTimeID', 'Line', 'SectionPosition', 'GobPosition', 'Cavity']

df_p = datasets[primary_key][golden_thread + [p_col]].copy()
df_s = datasets[secondary_key][golden_thread + [s_col]].copy()

# Apply the Time-Lag to the Secondary Dataset
if lag_minutes > 0:
    df_s['DateTimeID'] = df_s['DateTimeID'] + pd.Timedelta(minutes=lag_minutes)

# Merge datasets on the Golden Thread
# Note: For 20M+ rows, ensure DateTimeID is rounded to nearest minute/interval
merged_df = pd.merge(df_p, df_s, on=golden_thread, how='inner', suffixes=('_p', '_s'))

if merged_df.empty:
    st.error("No overlapping data found for the selected Golden Thread criteria and Time-Lag.")
else:
    # 5. VISUALIZATION: DUAL AXIS TREND
    st.subheader(f"Cross-Dataset Correlation: {primary_key} vs {secondary_key}")
    
    # Calculate Z-Scores for fair comparison (Standard Baseline)
    merged_df['Z_p'] = calculate_zscore(merged_df[f"{p_col}_p"])
    merged_df['Z_s'] = calculate_zscore(merged_df[f"{s_col}_s"])
    
    fig = go.Figure()
    
    # Primary Trend
    fig.add_trace(go.Scatter(x=merged_df['DateTimeID'], y=merged_df['Z_p'],
                             name=f"{primary_key} (Z-Score)", line=dict(color='firebrick')))
    
    # Secondary Trend
    fig.add_trace(go.Scatter(x=merged_df['DateTimeID'], y=merged_df['Z_s'],
                             name=f"{secondary_key} (Shifted Z-Score)", line=dict(color='royalblue', dash='dot')))
    
    fig.update_layout(title=f"Time-Shifted Overlay (Lag: {lag_minutes} min)",
                      xaxis_title="Timeline", yaxis_title="Normalized Value (Z-Score)",
                      template="plotly_white", hovermode="x unified")
    
    st.plotly_chart(fig, use_container_width=True)

    # 6. STATISTICAL INSIGHT
    correlation = merged_df['Z_p'].corr(merged_df['Z_s'])
    st.metric("Correlation Coefficient (R)", f"{correlation:.3f}")
    
    if abs(correlation) > 0.7:
        st.success("Strong Correlation detected! This suggest a direct cause-and-effect relationship.")
    elif abs(correlation) > 0.4:
        st.info("Moderate Correlation. Potential relationship found.")
    else:
        st.warning("Low Correlation. Try adjusting the Time-Lag slider or selecting different variables.")

# 7. EXPORT SNAPSHOT
if st.button("📸 Add to PDF Report"):
    # Logic to send current fig to st.session_state.report_snapshots
    st.toast("Snapshot added to Report Center!")
