# src/data_loader.py
from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder
from urllib.parse import quote_plus
from config.config import Config
from sqlalchemy import text

def load_data_to_db(df_candidates, df_placements):
    """
    Charge les données transformées dans PostgreSQL.
    """
    encoded_pg_password = quote_plus(Config.PG_PASSWORD)
    
    with SSHTunnelForwarder(
        (Config.SSH_HOST, Config.SSH_PORT),
        ssh_username=Config.SSH_USER,
        ssh_password=Config.SSH_PASSWORD,
        remote_bind_address=(Config.PG_HOST, Config.PG_PORT)
    ) as tunnel:
        
        local_port = tunnel.local_bind_port
        db_url = f"postgresql+psycopg2://{Config.PG_USER}:{encoded_pg_password}@localhost:{local_port}/{Config.PG_DB}"
        engine = create_engine(db_url)
        
        try:
            with engine.connect() as conn:
                conn.execute(text("ROLLBACK"))
                
                tables = {
                    "candidates": df_candidates,
                    "placements": df_placements
                }
                
                for table_name, df in tables.items():
                    print(f"Insertion de {table_name} dans mstudio.{table_name}...")
                    df.to_sql(
                        name=table_name,
                        con=engine,
                        schema="mstudio",
                        if_exists="replace",
                        index=False
                    )
                    print(f"✅ Insertion réussie pour {table_name} !")
        
        except Exception as e:
            print(f"⚠️ Erreur pendant l'insertion : {e}")