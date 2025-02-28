# src/data_transformer.py
import pandas as pd
import re
from src.utils import list_to_string, format_sources, extract_tag_name, transformer_persona

def transform_candidates_data(df_candidates):
    """
    Nettoie et transforme les données des candidats.
    """
    # Liste des colonnes à garder pour les candidats
    cols_candidates = [
        "initials", "id", "phones", "created_at", "tags", "admin_id", 
        "new", "last_activity_at", "name", "updated_at", "source", "sources", "positive_ratings", "emails"
    ]

    # Extraction des colonnes désirées
    df_candidates_clean = df_candidates[cols_candidates].copy()

    # Exploser la colonne "placements" pour obtenir une ligne par placement par candidat
    df_placements = df_candidates[['id', 'placements']].explode('placements')
    # Conserver uniquement les lignes où 'placements' n'est pas vide
    df_placements = df_placements[df_placements['placements'].notna()]

    # Aplatir la colonne 'placements' (contenant un dictionnaire) en colonnes séparées
    df_placements_flat = pd.json_normalize(df_placements['placements'])
    # Préfixer les colonnes avec "placement." pour distinguer ces données
    df_placements_flat = df_placements_flat.add_prefix("placement.")

    # Ajouter l'identifiant du candidat (issu du DataFrame d'origine)
    df_placements_flat["candidate_id"] = df_placements["id"].values

    # Sélectionner les colonnes d'intérêt pour les placements
    cols_placements = [
        "placement.id", "placement.candidate_id", "placement.is_hired", 
        "placement.disqualified_at", "placement.disqualified_by", "placement.disqualify_reason", 
        "placement.hired_at", "placement.job_starts_at", "placement.overdue_at", 
        "placement.stage.id", "placement.stage.name",
        "placement.offer.id", "placement.offer.status", "placement.offer.title", "candidate_id"
    ]
    df_placements_clean = df_placements_flat[cols_placements].copy()

    # Vérifier la redondance des colonnes candidate_id
    if "placement.candidate_id" in df_placements_clean.columns and "candidate_id" in df_placements_clean.columns:
        diff = (df_placements_clean["placement.candidate_id"] != df_placements_clean["candidate_id"]).sum()
        if diff > 0:
            print(f"ATTENTION : Il y a {diff} lignes où 'placement.candidate_id' diffère de 'candidate_id'.")
        else:
            # Si identiques, supprimer la redondance et renommer
            df_placements_clean.drop(columns=["candidate_id"], inplace=True)
            df_placements_clean.rename(columns={"placement.candidate_id": "candidate_id"}, inplace=True)

    # Liste des offres ciblées
    offres_visees = [
        'Call For Founders - Energy',
        'Call For Founders - Artificial Intelligence',
        'Call For Founders - Marketplace',
        'Call For Founders - Agritech',
        'Call For Founders - Fintech'
    ]

    # Filtrer les placements pour ne conserver que ceux dont l'offre correspond aux nouvelles offres
    df_placements_filtre = df_placements_clean[
        df_placements_clean["placement.offer.title"].isin(offres_visees)
    ].copy()

    # Récupérer la liste des IDs candidats présents dans les placements filtrés
    candidate_ids_filtered = df_placements_filtre["candidate_id"].unique()

    # Filtrer le DataFrame candidats pour ne conserver que les candidats présents dans candidate_ids_filtered
    df_candidates_filtre = df_candidates_clean[
        df_candidates_clean["id"].isin(candidate_ids_filtered)
    ].copy()

    # Conversion des colonnes de dates en datetime
    df_candidates_filtre['created_at'] = pd.to_datetime(df_candidates_filtre['created_at'], errors='coerce')
    df_candidates_filtre['updated_at'] = pd.to_datetime(df_candidates_filtre['updated_at'], errors='coerce')
    df_candidates_filtre['last_activity_at'] = pd.to_datetime(df_candidates_filtre['last_activity_at'], errors='coerce')

    # Transformation sur les colonnes concernées
    df_candidates_filtre['phones'] = df_candidates_filtre['phones'].apply(list_to_string)
    df_candidates_filtre['tags'] = df_candidates_filtre['tags'].apply(list_to_string)
    df_candidates_filtre['emails'] = df_candidates_filtre['emails'].apply(list_to_string)

    # Traitement de la colonne 'sources'
    df_candidates_filtre['sources'] = df_candidates_filtre['sources'].apply(format_sources)

    # Extraction du nom du tag via une expression régulière
    df_candidates_filtre['persona'] = df_candidates_filtre['tags'].apply(extract_tag_name)

    # Transformation de la colonne 'persona'
    df_candidates_filtre['persona'] = df_candidates_filtre['persona'].apply(transformer_persona)

    # Dictionnaire de renommage pour df_candidates_filtre
    noms_colonnes_candidates = {
        'id': 'id',
        'name': 'nom',
        'initials': 'initiales',
        'phones': 'contacts',
        'emails': 'emails',
        'created_at': 'date_de_creation',
        'last_activity_at': 'date_Derniere_activite',
        'updated_at': 'date_mis_a_jour',
        'persona': 'persona',
        'source': 'source',
        'sources': 'sources',
        'admin_id': 'id_admin',
        'new': 'new',
        'positive_ratings': 'evaluations_positives'
    }
    df_candidates_transforme = df_candidates_filtre.rename(columns=noms_colonnes_candidates)

    # Réorganiser les colonnes
    colonnes_ordonnee_candidates = [
        'id', 'nom', 'initiales', 'contacts', 'emails', 
        'date_de_creation', 'date_Derniere_activite', 'date_mis_a_jour', 
        'persona', 'source', 'sources', 
        'id_admin', 'new', 'evaluations_positives'
    ]
    df_candidates_transforme = df_candidates_transforme[colonnes_ordonnee_candidates]

    # Mapping des sources
    mapping_source = {
        "career_site": "Inbound",
        "manual": "Outbound"
    }
    df_candidates_transforme["source"] = df_candidates_transforme["source"].replace(mapping_source)

    # Dictionnaire de renommage pour df_placements_filtre
    noms_colonnes_placements = {
        'placement.id': 'id_placement',
        'candidate_id': 'id_candidat',
        'placement.is_hired': 'embauche',
        'placement.disqualified_at': 'date_disqualification',
        'placement.disqualified_by': 'disqualifie_par',
        'placement.disqualify_reason': 'raison_disqualification',
        'placement.hired_at': "date_embauche",
        'placement.job_starts_at': 'date_debut',
        'placement.overdue_at': 'date_depassage',
        'placement.stage.id': "id_etape",
        'placement.stage.name': "etape",
        'placement.offer.id': "id_jobs",
        'placement.offer.status': "statut_jobs",
        'placement.offer.title': "jobs"
    }
    df_placements_transforme = df_placements_filtre.rename(columns=noms_colonnes_placements)

    # Réorganiser les colonnes
    colonnes_ordonnee_placements = [
        'id_placement', 'id_candidat', 'id_jobs', 'jobs', 'statut_jobs',
        'id_etape', 'etape', 
        'embauche', "date_embauche", 'date_debut',
        'date_disqualification', 'disqualifie_par', 'raison_disqualification',
        'date_depassage'
    ]
    df_placements_transforme = df_placements_transforme[colonnes_ordonnee_placements]

    # Mapping des offres
    mapping_offres = {
        "Call For Founders - Energy": "Energy",
        "Call For Founders - Artificial Intelligence": "AI",
        "Call For Founders - Marketplace": "Marketplace",
        "Call For Founders - Agritech": "Agritech",
        "Call For Founders - Fintech": "Fintech"
    }
    df_placements_transforme["jobs"] = df_placements_transforme["jobs"].replace(mapping_offres)

    # Conversion des colonnes de dates en datetime
    date_cols = ["date_embauche", "date_debut", "date_disqualification", "date_depassage"]
    for col in date_cols:
        df_placements_transforme[col] = pd.to_datetime(df_placements_transforme[col], errors='coerce')

    return df_candidates_transforme, df_placements_transforme