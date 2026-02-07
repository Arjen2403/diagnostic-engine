import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from modules.stats_engine import calculate_moving_average, calculate_cpk

st.set_page_config(layout="wide")

st.title("📈 Data Explorer")
st.markdown("### Single-Dataset Deep Dive & Statistical Benchmarking")

# Ensure data has been loaded via the Ingestion page
if 'raw_data' not in st.session_state:
    st.warning("No data found. Please go to the 📥 Ingestion page first.")
    st.stop()

df = st.session_state['raw_data']

# 1. Sidebar Configuration
with st.sidebar:
    st.header("Explorer Settings")
    target_col = st.selectbox("Select Variable to Analyze", df.columns)
    
    st.divider()
    st.subheader("Process Capability (Cpk)")
    enable_cpk = st.checkbox("Calculate Cpk")
    if enable_cpk:
        lsl = st.number_input("Lower Specification Limit (LSL)", value=0.0)
        usl = st.number_input("Upper Specification Limit (USL)", value=100.0)

# 2. Key Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Mean", round(df[target_col].mean(), 2))
col2.metric("Std Dev", round(df[target_col].std(), 2))
col3.metric("Min / Max", f"{round(df[target_col].min(), 1)} / {round(df[target_col].max(), 1)}")

if enable_cpk:
    cpk_val = calculate_cpk(df, target_col, lsl, usl)
    col4.metric("Process Capability (Cpk)", round(cpk_val, 2))

# 3. Main Visualization
st.subheader(f"Time-Series Analysis: {target_col}")

# Options for smoothing
smooth_data = st.checkbox("Apply Moving Average (Smoothing)")
if smooth_data:
    window = st.text_input("Window Size (e.g., 10min, 50)", value="5min")
    df_plot = calculate_moving_average(df, target_col, window)
    plot_col = f'smooth_{target_col}'
else:
    df_plot = df
    plot_col = target_col

fig = px.line(df_plot, x='DateTimeID', y=plot_col, 
              title=f"{target_col} Over Time",
              template="plotly_dark")

fig.update_traces(line=dict(width=1, color='#00d4ff'))
st.plotly_chart(fig, use_container_width=True)

# 4. Distribution Analysis (SRS Section 3.3)
st.subheader("Statistical Distribution")
hist_fig = px.histogram(df, x=target_col, nbins=50, 
                        marginal="box", 
                        template="plotly_dark",
                        color_discrete_sequence=['#00d4ff'])
st.plotly_chart(hist_fig, use_container_width=True)
