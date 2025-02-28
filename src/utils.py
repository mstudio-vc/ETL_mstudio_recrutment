# src/utils.py
import re

def list_to_string(x):
    """
    Convertit une liste en une chaîne de caractères.
    """
    if isinstance(x, list):
        return ", ".join([str(item) for item in x])
    return x

def format_sources(x):
    """
    Formate la colonne 'sources'.
    """
    if isinstance(x, list):
        if len(x) > 0 and isinstance(x[0], dict) and 'name' in x[0]:
            return ", ".join([str(item.get('name', '')) for item in x])
        else:
            return list_to_string(x)
    return x

def extract_tag_name(tag_string):
    """
    Extrait le nom du tag à partir d'une chaîne de caractères.
    """
    match = re.search(r"'name': '([^']+)'", tag_string)
    if match:
        return match.group(1)
    return None

def transformer_persona(valeur):
    """
    Transforme la valeur de la colonne 'persona'.
    """
    valeurs_conservees = ["2nd Line Founder", "Bon élève", "Repeat entrepreneur", "Top"]
    return valeur if valeur in valeurs_conservees else "Autre/NA"