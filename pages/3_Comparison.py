import streamlit as st
import plotly.graph_objects as go
from modules.stats_engine import apply_z_score

st.set_page_config(layout="wide")

st.title("⚖️ Machine Comparison")
st.markdown("### Side-by-Side Performance Analysis")

# SRS Requirement: Compare two independent datasets
col1, col2 = st.columns(2)

with col1:
    st.subheader("Machine A (Baseline)")
    file_a = st.file_uploader("Upload Machine A Data", type="csv", key="file_a")

with col2:
    st.subheader("Machine B (Comparison)")
    file_b = st.file_uploader("Upload Machine B Data", type="csv", key="file_b")

if file_a and file_b:
    import pandas as pd
    df_a = pd.read_csv(file_a)
    df_b = pd.read_csv(file_b)
    
    # Feature Selection
    common_cols = list(set(df_a.columns) & set(df_b.columns))
    target_var = st.selectbox("Select Variable to Compare", common_cols)
    
    # SRS 3.2: Z-Score Normalization for Comparison
    # This allows comparing two machines even if their raw sensor offsets differ
    use_zscore = st.toggle("Use Z-Score Normalization", value=True)
    
    if use_zscore:
        df_a = apply_z_score(df_a, [target_var])
        df_b = apply_z_score(df_b, [target_var])
        plot_col = f"z_{target_var}"
    else:
        plot_col = target_var

    # Visualization
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=df_a['DateTimeID'], y=df_a[plot_col], name="Machine A", line=dict(color='#00d4ff')))
    fig.add_trace(go.Scatter(x=df_b['DateTimeID'], y=df_b[plot_col], name="Machine B", line=dict(color='#ffaa00')))
    
    fig.update_layout(template="plotly_dark", title=f"Comparison: {target_var}", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    
    # SRS 3.3: Statistical Benchmarking
    st.subheader("Comparative Statistics")
    stats_col1, stats_col2 = st.columns(2)
    stats_col1.write("**Machine A Metrics**")
    stats_col1.dataframe(df_a[target_var].describe().to_frame().T)
    
    stats_col2.write("**Machine B Metrics**")
    stats_col2.dataframe(df_b[target_var].describe().to_frame().T)
else:
    st.info("Please upload two datasets to enable comparison mode.")
