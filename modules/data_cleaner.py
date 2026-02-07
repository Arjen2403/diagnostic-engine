import pandas as pd

def clean_data(df):
    """
    Standard Cleaning baseline for XPDS projects.
    Adheres to SRS v1.4: Optimized for memory and join integrity.
    """
    initial_rows = len(df)

    # 1. REQ 3.1: DateTimeID Standardization (Binary format for RAM efficiency)
    if 'DateTimeID' in df.columns:
        # pd.to_datetime is vectorized and memory-efficient
        df['DateTimeID'] = pd.to_datetime(df['DateTimeID'])

    # 2. REQ 3.1: Selective Null Removal (The Golden Thread Guard)
    # Optimization: Only drop if critical join keys are missing
    golden_thread = ['Line', 'SectionPosition', 'GobPosition', 'Cavity']
    critical_keys = [col for col in golden_thread if col in df.columns]
    
    if 'DateTimeID' in df.columns:
        critical_keys.append('DateTimeID')
        
    # Fixed: Only drops rows missing the "Thread", preserving other sensor data
    df = df.dropna(subset=critical_keys)
    
    # 3. REQ: Ensure 'Golden Thread' columns are standardized as strings
    for col in golden_thread:
        if col in df.columns:
            df[col] = df[col].astype(str)
            
    rows_removed = initial_rows - len(df)
    
    # Audit Trail (SRS Section 5)
    print(f"Cleaning Complete. Rows Processed: {initial_rows} | Rows Removed: {rows_removed}")
    
    return df, rows_removed
