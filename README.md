# -*- coding: utf-8 -*-
"""
Created on Sat Feb  7 15:21:00 2026

@author: Gebruiker
"""

# 🔗 XPDS Diagnostic Engine (TIP)
### Technology Implementation Program: Factory Data Correlation & Benchmarking

The **XPDS Diagnostic Engine** is a high-performance analytical suite designed for glass manufacturing. It streamlines the identification of cause-and-effect relationships between process sensors (e.g., BTC, Gob weights) and production outcomes (e.g., IR rejects, quality defects).



## 🚀 Key Features
* **High-Volume Processing:** Optimized via `Polars` and `Pandas` vectorization to handle 20M+ rows of sensor data.
* **The Golden Thread:** Automatic standardization of Line, Section, Gob, and Cavity identifiers to ensure seamless data joins.
* **Time-Lag Discovery:** Automated statistical engine to find lead/lag correlations between independent data sources.
* **Process Capability:** Built-in Cpk benchmarking with visual specification limits (LSL/USL).
* **Audit-Ready Reporting:** One-click PDF generation including analysis snapshots and operator metadata.

## 📁 Project Structure
```text
Technology_Implementation_Program/
├── app.py                     # Main dashboard entry point
├── auth.py                    # Security and access control
├── requirements.txt           # Environment dependencies
├── modules/
│   ├── data_ingestion.py      # CSV/SQL high-speed loaders
│   ├── data_cleaner.py        # Memory-optimized standardization
│   ├── stats_engine.py        # Z-Score, Lag-Discovery, & Cpk logic
│   └── pdf_generator.py       # Automated PDF report builder
└── pages/
    ├── 01_Ingestion.py        # Data source selection & verification
    ├── 02_Visualization.py    # Deep-dive analysis & benchmarking
    ├── 03_Comparison.py       # Machine A/B relative performance
    └── 05_Diagnostics.py      # Flagship Time-Lag correlation tool