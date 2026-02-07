import pandas as pd
import numpy as np

def apply_z_score(df, columns):
    """SRS 3.2: Z-Score Normalization for dual-axis comparison."""
    df_z = df.copy()
    for col in columns:
        if col in df.columns:
            mu, sigma = df[col].mean(), df[col].std()
            df_z[f'z_{col}'] = (df[col] - mu) / sigma if sigma > 0 else 0.0
    return df_z

def shift_cause_data(df, shift_value, unit='minutes', timestamp_col='DateTimeID'):
    """SRS 3.2: High-Precision Time-Lag Engine."""
    df_shifted = df.copy()
    delta = pd.Timedelta(seconds=shift_value) if unit == 'seconds' else pd.Timedelta(minutes=shift_value)
    df_shifted[timestamp_col] = df_shifted[timestamp_col] + delta
    return df_shifted

def calculate_moving_average(df, column, window_size='5min'):
    """SRS 3.3: Moving Average for Drift Analysis."""
    df_temp = df.copy().set_index('DateTimeID')
    df_temp[f'smooth_{column}'] = df_temp[column].rolling(window=window_size).mean()
    return df_temp.reset_index()

def find_best_lag(df_cause, df_effect, column_cause, column_effect, max_lag_min=15):
    """SRS 3.2: Automated Cause-and-Effect Discovery."""
    # Ensure time-based indexing for shifting
    c = df_cause[['DateTimeID', column_cause]].set_index('DateTimeID').resample('1min').mean()
    e = df_effect[['DateTimeID', column_effect]].set_index('DateTimeID').resample('1min').mean()
    
    lags, correlations = [], []
    
    for lag in range(max_lag_min + 1):
        # Shift the cause series
        shifted_c = c[column_cause].shift(lag)
        combined = pd.concat([shifted_c, e[column_effect]], axis=1).dropna()
        
        if len(combined) > 1:
            corr = combined.corr().iloc[0, 1]
            lags.append(lag)
            correlations.append(corr if not np.isnan(corr) else 0)
            
    if not correlations: return 0, 0
    best_idx = correlations.index(max(correlations, key=abs))
    return lags[best_idx], correlations[best_idx]

def calculate_cpk(df, column, lsl, usl):
    """SRS 3.3: Process Capability Index."""
    mu, sigma = df[column].mean(), df[column].std()
    if sigma == 0: return 0
    return min((usl - mu) / (3 * sigma), (mu - lsl) / (3 * sigma))
