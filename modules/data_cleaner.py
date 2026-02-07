import pandas as pd

def clean_data(df):
    """
    Enhanced Cleaning baseline for XPDS projects.
    Adheres to SRS v1.4: Optimized for memory and join integrity.
    """
    initial_rows = len(df)

    # 1. REQ 3.1: DateTimeID Standardization (Keep as datetime64 for calculation efficiency)
    if 'DateTimeID' in df.columns:
        # Convert to datetime object but NOT to string yet to save RAM
        df['DateTimeID'] = pd.to_datetime(df['DateTimeID'])

    # 2. REQ 3.1: Selective Null Removal (The Golden Thread Guard)
    # We only drop rows if they are missing critical join keys
    golden_thread = ['Line', 'SectionPosition', 'GobPosition', 'Cavity']
    
    # Check which of the golden thread columns exist in this specific DF
    existing_keys = [col for col in golden_thread if col in df.columns]
    
    # Also include DateTimeID in the survival check if it exists
    if 'DateTimeID' in df.columns:
        existing_keys.append('DateTimeID')
        
    df = df.dropna(subset=existing_keys)
    
    # 3. REQ: Standardize identifiers as strings for joining
    for col in golden_thread:
        if col in df.columns:
            df[col] = df[col].astype(str)
            
    rows_removed = initial_rows - len(df)
    
    # Audit Trail (SRS Section 5)
    print(f"Cleaning Complete. Rows Processed: {initial_rows} | Rows Removed: {rows_removed}")
    
    return df, rows_removed
