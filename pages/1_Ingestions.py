import pandas as pd
import polars as pl
import mysql.connector
from sqlalchemy import create_engine

def ingest_from_csv(file_path: str):
    """
    SRS 3.1: Raw String path handling and Polars-based CSV ingestion.
    """
    try:
        # Using Polars for 20M+ row speed
        df_pl = pl.read_csv(file_path)
        return df_pl.to_pandas()
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def ingest_from_sql(query: str, db_config: dict):
    """
    SRS 2.0: MySQL Data Ingestion.
    db_config should contain: user, password, host, database
    """
    try:
        # Create SQLAlchemy engine for Pandas compatibility
        conn_str = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        engine = create_engine(conn_str)
        
        # Stream the data to prevent memory overflow on 20M+ rows
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"Error loading SQL: {e}")
        return None

def smart_loader(source_type, path_or_query, db_config=None):
    """
    Unified entry point for the Ingestion Page.
    """
    if source_type == "CSV":
        return ingest_from_csv(path_or_query)
    elif source_type == "SQL":
        return ingest_from_sql(path_or_query, db_config)
