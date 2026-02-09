import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Set page configuration
st.set_page_config(layout="wide", page_title="TIP | Universal Diagnostic Engine")

st.title("🎯 Universal Diagnostic Engine")
st.markdown("### Performance Monitoring & Dataset Inspection")

# --- 1. MULTI-DATASET LOADING LOGIC ---
if 'datasets' not in st.session_state:
    st.session_state['datasets'] = {}

# Ingestion Section (If no data exists yet)
if not st.session_state['datasets']:
    st.info("👋 No data found. Please upload a dataset to begin.")
    uploaded_file = st.file_uploader("Upload CSV (Intensity, Loading, etc.)", type="csv")
    if uploaded_file:
        file_label = st.text_input("Label this dataset (e.g., 'Intensity' or 'Loading')", value="MainData")
        if st.button("Initialize Dataset"):
            df_new = pd.read_csv(uploaded_file)
            df_new['DateTimeID'] = pd.to_datetime(df_new['DateTimeID'])
            st.session_state['datasets'][file_label] = df_new
            st.rerun()
    st.stop()

# --- 2. DATASET SELECTOR ---
# This allows the user to switch between loaded files (Intensity vs Loading)
all_loaded = list(st.session_state['datasets'].keys())
active_label = st.selectbox("📁 Select Dataset to Visualize", all_loaded)
df = st.session_state['datasets'][active_label]

# --- 3. SIDEBAR FILTERS ---
with st.sidebar:
    st.header(f"🔍 Filtering: {active_label}")
    
    # Standard TIP Hierarchy
    all_lines = sorted(df['Line'].unique())
    selected_lines = st.multiselect("1. Select Line(s)", options=all_lines, default=all_lines[:1])
    
    if not selected_lines:
        st.stop()

    temp_df = df[df['Line'].isin(selected_lines)]
    selected_secs = st.multiselect("2. Select Section(s) [Optional]", options=sorted(temp_df['SectionPosition'].unique()))
    
    if selected_secs:
        temp_df = temp_df[temp_df['SectionPosition'].isin(selected_secs)]
    
    selected_cavs = st.multiselect("3. Select Cavity/Cavities [Optional]", options=sorted(temp_df['Cavity'].unique()))

    st.divider()
    
    # 4. Dynamic Variable Selector
    # Exclude metadata to show only the measurements
    meta_cols = ['DateTimeID', 'Line', 'SectionPosition', 'GobPosition', 'Cavity', 'NumberOfMeasurements']
    value_options = [c for c in df.columns if c not in meta_cols and "_xsq" not in c and "Setpoint" not in c]
    selected_vars = st.multiselect("Select Variable(s) to Analyze", options=value_options)
    
    st.divider()
    alarm_limit = st.slider("Critical Deviation Limit (%)", 1.0, 10.0, 5.0)

# --- FILTERING EXECUTION ---
filtered_df = df[df['Line'].isin(selected_lines)].copy()
if selected_secs: filtered_df = filtered_df[filtered_df['SectionPosition'].isin(selected_secs)]
if selected_cavs: filtered_df = filtered_df[filtered_df['Cavity'].isin(selected_cavs)]

if not selected_vars:
    st.info("👈 Please select variables in the sidebar to generate graphs.")
else:
    # --- SECTION 1: NORMALIZED DEVIATION ---
    st.subheader("📈 Normalized Deviation Tracking (%)")
    
    dev_cols = []
    for var in selected_vars:
        # Handling the Intensity naming convention vs Standard naming
        if "IntensityZone" in var:
            sp_col = var.replace('IntensityZone', 'IntensitySetpointZone')
        else:
            sp_col = var.replace('_avg', 'Setpoint_avg')
            
        if sp_col in filtered_df.columns:
            dev_name = f"{var} Dev%"
            filtered_df[dev_name] = ((filtered_df[var] - filtered_df[sp_col]) / filtered_df[sp_col]) * 100
            dev_cols.append(dev_name)

    if dev_cols:
        plot_dev_df = filtered_df.melt(id_vars=['DateTimeID', 'Cavity'], value_vars=dev_cols)
        fig_dev = px.line(plot_dev_df, x='DateTimeID', y='value', color='Cavity', line_dash='variable',
                          title=f"Deviation Analysis: {active_label}", template="plotly_dark")
        fig_dev.add_hline(y=alarm_limit, line_dash="dash", line_color="red")
        fig_dev.add_hline(y=-alarm_limit, line_dash="dash", line_color="red")
        fig_dev.add_hline(y=0, line_color="white", line_width=2)
        st.plotly_chart(fig_dev, use_container_width=True)
        
        st.info(f"**📊 Logic: Normalized Deviation ({active_label})**\n"
                f"Calculated as: $((Measured - Setpoint) / Setpoint) \\times 100$.\n"
                f"This removes spatial bias (like conveyor cooling) and highlights true process anomalies.")
    else:
        st.warning(f"No Setpoints found in '{active_label}'. Deviation tracking is unavailable.")

    st.divider()

    # --- SECTION 2: ACTUAL VALUES ---
    st.subheader(f"🔥 Actual {active_label} Trends")
    plot_actual_df = filtered_df.melt(id_vars=['DateTimeID', 'Cavity'], value_vars=selected_vars)
    fig_actual = px.line(plot_actual_df, x='DateTimeID', y='value', color='Cavity', line_dash='variable',
                         title=f"Raw Measurements: {active_label}", template="plotly_dark")
    st.plotly_chart(fig_actual, use_container_width=True)
    
    st.info(f"**📊 Logic: Actual Values**\n"
            f"Shows the direct raw measurements for the selected {active_label} variables.")

    st.divider()

    # --- SECTION 3: BASELINE DRIFT ---
    st.subheader("📉 Adaptive Baseline Drift Monitor")
    drift_scope = st.radio("Baseline Scope:", ["Machine Total", "By Section", "By Cavity"], horizontal=True)
    
    drift_vars = [v.replace('IntensityZone', 'IntensitySetpointZone').replace('_avg', 'Setpoint_avg') for v in selected_vars]
    valid_drift = [v for v in drift_vars if v in filtered_df.columns]

    if valid_drift:
        group_cols = ['DateTimeID']
        if drift_scope == "By Section": group_cols.append('SectionPosition')
        elif drift_scope == "By Cavity": group_cols.append('Cavity')

        drift_data = filtered_df.groupby(group_cols)[valid_drift].mean().reset_index()
        drift_plot_df = drift_data.melt(id_vars=group_cols, value_vars=valid_drift)

        fig_drift = px.line(drift_plot_df, x='DateTimeID', y='value', 
                            color='SectionPosition' if drift_scope == "By Section" else ('Cavity' if drift_scope == "By Cavity" else 'variable'),
                            line_dash='variable' if drift_scope != "Machine Total" else None,
                            title="Reference Standard Drift Trend", template="plotly_dark")
        st.plotly_chart(fig_drift, use_container_width=True)
        
        st.info("**📊 Logic: Baseline Drift**\n"
                "Tracks the average of the Setpoints. If this trends up or down, the whole machine is shifting.")