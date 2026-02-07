import pandas as pd
import numpy as np

def apply_z_score(df, columns):
    """
    SRS 3.2: Z-Score Normalization.
    Allows direct comparison of different units (e.g., Celsius vs. Reject Count).
    Formula: z = (x - μ) / σ
    """
    df_z = df.copy()
    for col in columns:
        if col in df.columns:
            mu = df[col].mean()
            sigma = df[col].std()
            # Prevent division by zero if std is 0
            if sigma > 0:
                df_z[f'z_{col}'] = (df[col] - mu) / sigma
            else:
                df_z[f'z_{col}'] = 0.0
    return df_z

def shift_cause_data(df, minutes_lag, timestamp_col='DateTimeID'):
    """
    SRS 3.2: Time-Lag Correlation Engine.
    Shifts the 'Cause' dataset forward in time to align with 'Effect'.
    """
    # Ensure datetime format for calculation
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    
    # Calculate the offset
    # Positive lag means the cause happened X minutes BEFORE the effect
    df_shifted = df.copy()
    df_shifted[timestamp_col] = df_shifted[timestamp_col] + pd.Timedelta(minutes=minutes_lag)
    
    return df_shifted

def calculate_cpk(df, column, lsl, usl):
    """
    SRS 3.3: Statistical Benchmarking.
    Calculates Process Capability (Cpk).
    """
    mean = df[column].mean()
    sigma = df[column].std()
    
    if sigma == 0:
        return 0
        
    cpu = (usl - mean) / (3 * sigma)
    cpl = (mean - lsl) / (3 * sigma)
    
    return min(cpu, cpl)
