from src.data_fetcher import fetch_data_from_api
from src.data_transformer import transform_candidates_data
from src.data_loader import load_data_to_db

def main():
    # Récupération des données
    df_candidates = fetch_data_from_api()
    
    if df_candidates is not None:
        # Transformation des données
        df_candidates_clean, df_placements_clean = transform_candidates_data(df_candidates)
        
        # Chargement des données
        load_data_to_db(df_candidates_clean, df_placements_clean)

if __name__ == "__main__":
    main()
