import streamlit as st
import pandas as pd
import sqlite3
import os
from databricks import sql
from databricks.sdk.core import Config



# Verifica que la variable de entorno esta definida
assert os.getenv('DATABRICKS_WAREHOUSE_ID'), "DATABRICKS_WAREHOUSE_ID must be set in app.yaml."

# Ejecutar consulta SQL en warehouse y devuleve un dataframe
def sqlQuery(query: str) -> pd.DataFrame:
    cfg = Config() 
    #Conexión a warehouse
    with sql.connect(
        server_hostname=cfg.host,
        http_path=f"/sql/1.0/warehouses/{os.getenv('DATABRICKS_WAREHOUSE_ID')}",
        credentials_provider=lambda: cfg.authenticate
    ) as connection:
        #Cursor para ejecutar consulta
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall_arrow().to_pandas()

@st.cache_data()  
def load_data(query: str):
    return sqlQuery(query)









