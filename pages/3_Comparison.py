import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_ingestion import smart_loader
from modules.data_cleaner import clean_data
from modules.stats_engine import apply_z_score

st.set_page_config(layout="wide", page_title="Machine Comparison | TIP")

st.title("⚖️ Machine Comparison")
st.markdown("### Side-by-Side Performance Analysis")

# 1. Inputs using the smart_loader (SRS 3.1)
col1, col2 = st.columns(2)

with col1:
    st.subheader("Machine A (Baseline)")
    file_a = st.file_uploader("Upload Machine A Data", type="csv", key="file_a")

with col2:
    st.subheader("Machine B (Comparison)")
    file_b = st.file_uploader("Upload Machine B Data", type="csv", key="file_b")

if file_a and file_b:
    with st.spinner("Standardizing datasets..."):
        # Performance fix: Use smart_loader logic
        df_a, _ = clean_data(pd.read_csv(file_a))
        df_b, _ = clean_data(pd.read_csv(file_b))
    
    # 2. Variable Selection
    common_cols = list(set(df_a.columns) & set(df_b.columns))
    if 'DateTimeID' in common_cols: common_cols.remove('DateTimeID')
    
    target_var = st.selectbox("Select Variable to Compare", common_cols)
    
    # 3. Settings Toggle
    c1, c2 = st.columns(2)
    use_zscore = c1.toggle("Use Z-Score Normalization", value=True)
    align_time = c2.toggle("Align Start Times (Relative Analysis)", value=False)
    
    # Process Logic
    plot_df_a = apply_z_score(df_a, [target_var]) if use_zscore else df_a
    plot_df_b = apply_z_score(df_b, [target_var]) if use_zscore else df_b
    plot_col = f"z_{target_var}" if use_zscore else target_var

    # Relative Time Logic
    if align_time:
        plot_df_a['Time_Axis'] = (plot_df_a['DateTimeID'] - plot_df_a['DateTimeID'].min()).dt.total_seconds() / 60
        plot_df_b['Time_Axis'] = (plot_df_b['DateTimeID'] - plot_df_b['DateTimeID'].min()).dt.total_seconds() / 60
        x_label = "Minutes from Start"
    else:
        plot_df_a['Time_Axis'] = plot_df_a['DateTimeID']
        plot_df_b['Time_Axis'] = plot_df_b['DateTimeID']
        x_label = "Actual Timestamp"

    # 4. Visualization
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_df_a['Time_Axis'], y=plot_df_a[plot_col], name="Machine A", line=dict(color='#00d4ff', width=1.5)))
    fig.add_trace(go.Scatter(x=plot_df_b['Time_Axis'], y=plot_df_b[plot_col], name="Machine B", line=dict(color='#ffaa00', width=1.5, opacity=0.8)))
    
    fig.update_layout(template="plotly_dark", xaxis_title=x_label, yaxis_title="Standardized Units" if use_zscore else target_var, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. Benchmarking Table
    st.subheader("Comparative Statistics")
    stats_col1, stats_col2 = st.columns(2)
    stats_col1.dataframe(df_a[target_var].describe().to_frame().T.style.background_gradient(axis=1))
    stats_col2.dataframe(df_b[target_var].describe().to_frame().T.style.background_gradient(axis=1))
else:
    st.info("Awaiting two datasets for comparison.")
