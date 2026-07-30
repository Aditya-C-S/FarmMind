from .treatments import TREATMENTS

DISEASE_MAP = {
    # Rice
    "sheath_blight": "Sheath_Blight",
    "rice_blast": "Rice_Blast",

    # Tomato
    "early_blight": "Early_Blight",
    "tomato_leaf_curl_virus": "Tomato_Leaf_Curl_Virus",

    # Alias
    "tylcv": "Tomato_Leaf_Curl_Virus",
}

def get_preventive_treatment(disease_id):
    key = DISEASE_MAP.get(disease_id)
    if not key:
        return None

    # Since these are stage-based preventive alerts,
    # return the mild/preventive recommendation.
    return TREATMENTS.get(key, {}).get("Mild")