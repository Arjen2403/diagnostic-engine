import pandas as pd
import polars as pl
from sqlalchemy import create_engine

def ingest_from_csv(file_path):
    """
    SRS 3.1: High-speed ingestion. 
    Uses Polars to handle 20M+ rows efficiently.
    """
    try:
        # Polars is significantly faster for large CSVs
        df_pl = pl.read_csv(file_path)
        return df_pl.to_pandas()
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def ingest_from_sql(query, db_config):
    """
    SRS 2.0: MySQL Data Ingestion.
    """
    try:
        conn_str = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        engine = create_engine(conn_str)
        # pd.read_sql returns a standard Pandas DataFrame
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"Error loading SQL: {e}")
        return None

def smart_loader(source_type, path_or_query, db_config=None):
    """
    Unified entry point used by 01_Ingestion.py
    """
    if source_type == "CSV":
        return ingest_from_csv(path_or_query)
    elif source_type == "SQL":
        return ingest_from_sql(path_or_query, db_config)
    return None
