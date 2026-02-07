import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from modules.stats_engine import calculate_moving_average, calculate_cpk

st.set_page_config(layout="wide", page_title="Visualization | TIP")

st.title("📈 Data Visualization")
st.markdown("### Single-Dataset Deep Dive & Statistical Benchmarking")

if 'raw_data' not in st.session_state:
    st.warning("No data found. Please go to the 📥 Ingestion page first.")
    st.stop()

df = st.session_state['raw_data']

# 1. Sidebar Configuration
with st.sidebar:
    st.header("Visualization Settings")
    target_col = st.selectbox("Select Variable to Analyze", df.columns)
    
    st.divider()
    st.subheader("Process Capability (Cpk)")
    enable_cpk = st.checkbox("Calculate Cpk")
    lsl, usl = None, None
    if enable_cpk:
        lsl = st.number_input("Lower Specification Limit (LSL)", value=df[target_col].min())
        usl = st.number_input("Upper Specification Limit (USL)", value=df[target_col].max())

# 2. Statistics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Mean", round(df[target_col].mean(), 2))
col2.metric("Std Dev", round(df[target_col].std(), 2))
col3.metric("Min / Max", f"{round(df[target_col].min(), 1)} / {round(df[target_col].max(), 1)}")

if enable_cpk:
    cpk_val = calculate_cpk(df, target_col, lsl, usl)
    # Color coding the metric for better visibility
    delta_color = "normal" if cpk_val >= 1.33 else "inverse"
    col4.metric("Process Capability (Cpk)", round(cpk_val, 2), delta="Target > 1.33", delta_color=delta_color)

# 3. Main Time-Series Plot
st.subheader(f"Timeline: {target_col}")

smooth_data = st.checkbox("Apply Moving Average (Smoothing)")
if smooth_data:
    window = st.text_input("Window Size (e.g., 5min, 100)", value="5min")
    try:
        df_plot = calculate_moving_average(df, target_col, window)
        plot_col = f'smooth_{target_col}'
    except:
        st.error("Invalid Window Format. Reverting to raw data.")
        df_plot, plot_col = df, target_col
else:
    df_plot, plot_col = df, target_col

fig = px.line(df_plot, x='DateTimeID', y=plot_col, 
              template="plotly_dark",
              color_discrete_sequence=['#00d4ff'])

# Add LSL/USL lines if Cpk is enabled
if enable_cpk:
    fig.add_hline(y=lsl, line_dash="dash", line_color="red", annotation_text="LSL")
    fig.add_hline(y=usl, line_dash="dash", line_color="red", annotation_text="USL")

fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# 4. Distribution Analysis
st.subheader("Distribution Analysis")
hist_fig = px.histogram(df, x=target_col, nbins=50, 
                        marginal="box", 
                        template="plotly_dark",
                        color_discrete_sequence=['#ffaa00'])
st.plotly_chart(hist_fig, use_container_width=True)
