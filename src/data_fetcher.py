# src/data_fetcher.py
import requests
import pandas as pd
from config.config import Config

def fetch_data_from_api():
    """
    Récupère les données depuis l'API et retourne un DataFrame brut.
    """
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {Config.API_AUTHORIZATION}"
    }
    response = requests.get(Config.API_URL, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        hits = result.get("hits", [])
        df_candidates = pd.json_normalize(hits)
        print("Appel API réussi, nombre total de candidats récupérés :", len(df_candidates))
        return df_candidates
    else:
        print("Erreur lors de l'appel API :", response.status_code)
        return None