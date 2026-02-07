import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import tempfile
import os
from modules.data_ingestion import smart_loader
from modules.data_cleaner import clean_data
from modules.stats_engine import apply_z_score, shift_cause_data, calculate_moving_average, find_best_lag
from modules.pdf_generator import generate_diagnostic_report

st.set_page_config(layout="wide", page_title="Diagnostic Engine | TIP")

st.title("🔗 Time-Lag Diagnostic Engine")

# 1. Sidebar Controls
with st.sidebar:
    st.header("Analysis Settings")
    lag_unit = st.radio("Lag Precision", ["seconds", "minutes"])
    
    # Session state for lag to allow auto-update
    if 'current_lag' not in st.session_state: st.session_state['current_lag'] = 0
    
    lag_value = st.slider(f"Shift Cause Forward ({lag_unit})", 0, 60, st.session_state['current_lag'])
    
    st.divider()
    show_drift = st.checkbox("Show Trend (Moving Average)", value=True)
    window_size = st.text_input("Rolling Window (e.g., 5min, 100)", value="5min")

# 2. Data Loading (Optimized)
st.info("Upload 'Cause' and 'Effect' datasets.")
col1, col2 = st.columns(2)
with col1:
    cause_file = st.file_uploader("Upload Cause Data", type="csv")
with col2:
    effect_file = st.file_uploader("Upload Effect Data", type="csv")

if cause_file and effect_file:
    with st.spinner("Processing High-Volume Data..."):
        # Use pandas here for the file buffer, but cleaning handles the optimization
        df_cause, _ = clean_data(pd.read_csv(cause_file))
        df_effect, _ = clean_data(pd.read_csv(effect_file))

    # 3. Correlation Selection & Auto-Discovery
    st.subheader("Interactive Correlation Plot")
    v_col1, v_col2, v_col3 = st.columns([2, 2, 1])
    
    cause_col = v_col1.selectbox("Select Cause Variable", df_cause.columns)
    effect_col = v_col2.selectbox("Select Effect Variable", df_effect.columns)
    
    if v_col3.button("✨ Suggest Lag"):
        best_lag, corr = find_best_lag(df_cause, df_effect, cause_col, effect_col)
        st.session_state['current_lag'] = best_lag
        st.rerun()

    # Apply Shift & Z-Score
    df_cause_shifted = shift_cause_data(df_cause, lag_value, unit=lag_unit)
    df_plot_cause = apply_z_score(df_cause_shifted, [cause_col])
    df_plot_effect = apply_z_score(df_effect, [effect_col])

    # Plotting
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot_cause['DateTimeID'], y=df_plot_cause[f'z_{cause_col}'], name="Cause (Shifted)", line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df_plot_effect['DateTimeID'], y=df_plot_effect[f'z_{effect_col}'], name="Effect", line=dict(color='cyan', opacity=0.7)))

    if show_drift:
        df_cause_ma = calculate_moving_average(df_cause_shifted, cause_col, window_size)
        ma_mu, ma_sigma = df_cause_ma[f'smooth_{cause_col}'].mean(), df_cause_ma[f'smooth_{cause_col}'].std()
        fig.add_trace(go.Scatter(x=df_cause_ma['DateTimeID'], y=(df_cause_ma[f'smooth_{cause_col}'] - ma_mu) / ma_sigma, 
                                 name="Trend", line=dict(color='red', width=3, dash='dot')))

    fig.update_layout(template="plotly_dark", hovermode="x unified", height=500)
    st.plotly_chart(fig, use_container_width=True)

    # 4. Reporting (Fixed Notes Integration)
    st.divider()
    st.subheader("📄 Reporting & Audit Trail")
    r_col1, r_col2 = st.columns(2)
    user_name = r_col1.text_input("Analyst Name")
    machine_id = r_col1.text_input("Machine Reference")
    report_notes = r_col2.text_area("Analysis Remarks")

    if st.button("🚀 Generate PDF Diagnostic Report"):
        if not user_name or not machine_id:
            st.error("Audit metadata required.")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                fig.write_image(tmp_img.name, engine="kaleido")
                pdf_filename = f"Diagnostic_{machine_id}.pdf"
                # Updated to pass the notes to the generator
                generate_diagnostic_report(pdf_filename, user_name, machine_id, tmp_img.name, notes=report_notes)
                
                with open(pdf_filename, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=pdf_filename)
                os.remove(tmp_img.name)
