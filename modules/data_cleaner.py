import pandas as pd

def clean_data(df):
    """
    Standard Cleaning baseline for XPDS projects.
    """
    initial_rows = len(df)
    # REQ: Auto-remove nulls
    df = df.dropna()
    
    # REQ: Ensure 'Golden Thread' columns are standardized as strings for joining
    golden_thread = ['Line', 'SectionPosition', 'GobPosition', 'Cavity']
    for col in golden_thread:
        if col in df.columns:
            df[col] = df[col].astype(str)
            
    rows_removed = initial_rows - len(df)
    return df, rows_removed
