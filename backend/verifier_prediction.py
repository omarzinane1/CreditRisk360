
import json
from pathlib import Path

from app.services.prediction_service import PredictionService


# Initialisation du modèle
service = PredictionService()

racine = Path(__file__).resolve().parents[1]

# Chargement des cinq profils de référence
with open(
    racine / "ml/artifacts/exemples_reference.json",
    encoding="utf-8"
) as fichier:
    reference = json.load(fichier)

assert (
    reference["threshold_version"]
    == service.metadata["threshold_version"]
)

# Comparaison des prédictions
for exemple in reference["exemples"]:

    resultat = service.predire(exemple["features"])

    score_attendu = exemple["risk_score"]
    score_obtenu = resultat["risk_score"]

    ecart = abs(score_attendu - score_obtenu)

    assert ecart < 1e-10
    assert resultat["risk_level"] == exemple["risk_level"]

    print(
        exemple["description"],
        "| Score :", round(score_obtenu, 6),
        "| Niveau :", resultat["risk_level"]
    )

print("\nToutes les prédictions sont cohérentes.")
