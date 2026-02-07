import pandas as pd

def find_best_lag(df_cause, df_effect, column_cause, column_effect, max_lag_min=15):
    """
    SRS 3.2: Automated Cause-and-Effect Discovery.
    Tests various time-lags to find where the correlation is strongest.
    """
    lags = []
    correlations = []
    
    # 1. Ensure we are looking at 'Drift' (Moving Averages)
    cause_series = df_cause[column_cause].rolling(window='1min').mean()
    effect_series = df_effect[column_effect].rolling(window='1min').mean()
    
    # 2. Iteratively shift and test correlation
    for lag in range(max_lag_min + 1):
        shifted_cause = cause_series.shift(lag, freq='min')
        # Re-aligning the data for comparison
        combined = pd.concat([shifted_cause, effect_series], axis=1).dropna()
        if not combined.empty:
            corr = combined.corr().iloc[0, 1]
            lags.append(lag)
            correlations.append(corr)
            
    # Find the lag with the highest absolute correlation
    best_lag = lags[correlations.index(max(correlations, key=abs))]
    return best_lag, max(correlations)
