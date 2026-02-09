# -*- coding: utf-8 -*-
"""
Created on Sat Feb  7 15:12:32 2026

@author: Gebruiker
"""

import time
import pandas as pd
import numpy as np
from modules.data_cleaner import clean_data
from modules.stats_engine import find_best_lag, apply_z_score

# --- PHASE 1: GENERATE 2M ROWS (STRESS SAMPLE) ---
print("🚀 Generating stress-test data...")
rows = 2_000_000 
dates = pd.date_range('2026-01-01', periods=rows, freq='s')

# Create a sine wave 'Cause' and a shifted 'Effect'
cause_val = np.sin(np.linspace(0, 100, rows))
# Shift effect by 300 seconds (5 minutes)
effect_val = np.roll(cause_val, 300) + np.random.normal(0, 0.1, rows)

df_test = pd.DataFrame({
    'DateTimeID': dates,
    'Line': 'Line_1',
    'SectionPosition': 1,
    'GobPosition': 1,
    'Cavity': 1,
    'BTC_Temp': cause_val,
    'Rejects': effect_val
})

# --- PHASE 2: BENCHMARK CLEANING ---
start_time = time.time()
print("🧹 Testing data_cleaner module...")
df_clean, loss = clean_data(df_test)
clean_time = time.time() - start_time
print(f"✅ Cleaning took: {clean_time:.2f} seconds")

# --- PHASE 3: BENCHMARK CORRELATION (THE LAG TEST) ---
print("🔍 Testing Auto-Lag Discovery...")
start_time = time.time()
# We look for the 5-minute shift we hardcoded
best_lag, correlation = find_best_lag(df_clean, df_clean, 'BTC_Temp', 'Rejects', max_lag_min=10)
lag_time = time.time() - start_time

print(f"✅ Correlation Logic took: {lag_time:.2f} seconds")
print(f"📈 Result: Found Lag of {best_lag} mins with {correlation:.2f} correlation.")