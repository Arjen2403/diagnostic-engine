import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import tempfile
import os
from modules.data_cleaner import clean_data
from modules.stats_engine import apply_z_score, shift_cause_data, calculate_moving_average
from modules.pdf_generator import generate_diagnostic_report

st.set_page_config(layout="wide", page_title="Diagnostic Engine | TIP")

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
    
    st.divider()
    st.info("💡 Use the slider to align sensor 'drifts' with production 'rejects'.")

# 2. Data Loading
st.info("Upload 'Cause' (Sensors) and 'Effect' (IR/Rejects) datasets to begin.")
col1, col2 = st.columns(2)

with col1:
    cause_file = st.file_uploader("Upload Cause Data (e.g., BTC/Gob)", type="csv")
with col2:
    effect_file = st.file_uploader("Upload Effect Data (e.g., IR/Rejects)", type="csv")

if cause_file and effect_file:
    # REQ 3.1: Load and Clean
    with st.spinner("Standardizing datasets..."):
        df_cause = pd.read_csv(cause_file)
        df_effect = pd.read_csv(effect_file)
        
        df_cause, _ = clean_data(df_cause)
        df_effect, _ = clean_data(df_effect)

    # REQ 3.2: Apply Time-Shift to the Cause
    df_cause_shifted = shift_cause_data(df_cause, lag_value, unit=lag_unit)

    # 3. Visualization Setup
    st.subheader("Interactive Correlation Plot")
    
    # Column Selection
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        cause_col = st.selectbox("Select Cause Variable (Sensor)", df_cause.columns)
    with v_col2:
        effect_col = st.selectbox("Select Effect Variable (Outcome)", df_effect.columns)
    
    # Process Z-Scores for dual-axis comparison
    df_plot_cause = apply_z_score(df_cause_shifted, [cause_col])
    df_plot_effect = apply_z_score(df_effect, [effect_col])

    # Plotting
    fig = go.Figure()

    # Cause Trace
    fig.add_trace(go.Scatter(
        x=df_plot_cause['DateTimeID'], 
        y=df_plot_cause[f'z_{cause_col}'],
        name=f"Cause: {cause_col} (Shifted)",
        line=dict(color='orange', width=1.5)
    ))

    # Effect Trace
    fig.add_trace(go.Scatter(
        x=df_plot_effect['DateTimeID'], 
        y=df_plot_effect[f'z_{effect_col}'],
        name=f"Effect: {effect_col}",
        line=dict(color='cyan', width=1.5, opacity=0.7)
    ))

    # Optional Trend Overlay (Drift Analysis)
    if show_drift:
        df_cause_ma = calculate_moving_average(df_cause_shifted, cause_col, window_size)
        ma_mu, ma_sigma = df_cause_ma[f'smooth_{cause_col}'].mean(), df_cause_ma[f'smooth_{cause_col}'].std()
        
        fig.add_trace(go.Scatter(
            x=df_cause_ma['DateTimeID'],
            y=(df_cause_ma[f'smooth_{cause_col}'] - ma_mu) / ma_sigma,
            name="Trend (Moving Avg)",
            line=dict(color='red', width=3, dash='dot')
        ))

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Timeline (Standardized)",
        yaxis_title="Z-Score (Standard Deviations)",
        hovermode="x unified",
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 4. Snapshot & Reporting Logic (SRS Section 5)
    st.divider()
    st.subheader("📄 Reporting & Audit Trail")
    
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        user_name = st.text_input("Operator/Analyst Name")
        machine_id = st.text_input("Machine/Line Reference")
    with r_col2:
        report_notes = st.text_area("Analysis Remarks", placeholder="e.g. Correlation confirmed between BTC drift and reject spike.")

    if st.button("🚀 Generate PDF Diagnostic Report"):
        if not user_name or not machine_id:
            st.error("⚠️ Analyst Name and Machine Reference are required for audit compliance.")
        else:
            with st.spinner("Capturing state and building PDF..."):
                # Use a temp file for the plot snapshot
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                    fig.write_image(tmp_img.name, engine="kaleido")
                    img_path = tmp_img.name

                pdf_filename = f"Diagnostic_{machine_id}_{lag_value}{lag_unit}.pdf"
                generate_diagnostic_report(pdf_filename, user_name, machine_id, img_path)

                # Provide Download
                with open(pdf_filename, "rb") as f:
                    st.download_button(
                        label="📥 Download Diagnostic PDF",
                        data=f,
                        file_name=pdf_filename,
                        mime="application/pdf"
                    )
                
                # Cleanup
                if os.path.exists(img_path): os.remove(img_path)
                st.success(f"Report '{pdf_filename}' is ready.")

else:
    st.warning("Awaiting data upload. Please provide both Cause and Effect CSV files.")
