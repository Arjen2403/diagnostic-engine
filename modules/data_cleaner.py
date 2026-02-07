import pandas as pd

def clean_data(df):
    """
    Standard Cleaning baseline for XPDS projects.
    Adheres to SRS v1.4: 20M+ row performance & Golden Thread Standardization.
    """
    initial_rows = len(df)

    # 1. REQ 3.1: DateTimeID Standardization (YYYY-MM-DD HH:MM:SS)
    if 'DateTimeID' in df.columns:
        df['DateTimeID'] = pd.to_datetime(df['DateTimeID']).dt.strftime('%Y-%m-%d %H:%M:%S')

    # 2. REQ 3.1: Auto-remove nulls
    df = df.dropna()
    
    # 3. REQ: Ensure 'Golden Thread' columns are standardized as strings for joining
    # Vectorized casting is faster for high-volume datasets
    golden_thread = ['Line', 'SectionPosition', 'GobPosition', 'Cavity']
    for col in golden_thread:
        if col in df.columns:
            df[col] = df[col].astype(str)
            
    rows_removed = initial_rows - len(df)
    
    # Audit Trail (SRS Section 5)
    print(f"Cleaning Complete. Rows Processed: {initial_rows} | Rows Removed: {rows_removed}")
    
    return df, rows_removed
