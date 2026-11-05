
from pathlib import Path
import sys
import json
import joblib
import numpy as np
import pandas as pd

# Chemins du projet
RACINE = Path(__file__).resolve().parent
DOSSIER_ML = RACINE / "ml"

sys.path.insert(0, str(DOSSIER_ML / "training"))

DOSSIER_ARTEFACTS = DOSSIER_ML / "artifacts"

# Vérification des fichiers
fichiers = [
    "model.joblib",
    "metadata.json",
    "metrics.json",
    "exemples_reference.json"
]

for fichier in fichiers:
    chemin = DOSSIER_ARTEFACTS / fichier
    assert chemin.is_file(), f"Fichier manquant : {fichier}"

print("1. Les quatre artefacts sont présents.")

# Chargement des métadonnées
with open(DOSSIER_ARTEFACTS / "metadata.json",
          encoding="utf-8") as f:
    metadata = json.load(f)

with open(DOSSIER_ARTEFACTS / "metrics.json",
          encoding="utf-8") as f:
    metrics = json.load(f)

with open(DOSSIER_ARTEFACTS / "exemples_reference.json",
          encoding="utf-8") as f:
    reference = json.load(f)

print("2. Métadonnées chargées.")
print("Version :", metadata["model_version"])
print("Seuils :", metadata["threshold_version"])

# Vérification des versions
assert metadata["threshold_version"] == "thresholds-v2"
assert metadata["model_version"] == reference["model_version"]
assert metadata["threshold_version"] == reference["threshold_version"]

# Vérification des variables
features = metadata["features"]
assert len(features) == 10
assert len(set(features)) == 10

print("3. Les 10 variables sont présentes.")

# Chargement du pipeline exporté
# Charger uniquement un modèle provenant du projet fiable.
modele = joblib.load(
    DOSSIER_ARTEFACTS / "model.joblib"
)

assert "smote" not in modele.named_steps
assert "modele" in modele.named_steps

print("4. Modèle chargé sans SMOTE à l'inférence.")

# Vérification des seuils
seuils = metadata["thresholds"]

seuil_faible = seuils["faible_modere"]
seuil_eleve = seuils["modere_eleve"]
seuil_decision = seuils["decision"]

assert 0 < seuil_faible < seuil_eleve < 1
assert np.isclose(seuil_decision, seuil_eleve)
assert np.isclose(
    metrics["seuil_decision"],
    seuil_decision
)

print("5. Les seuils sont cohérents.")

# Vérification des cinq exemples
exemples = reference["exemples"]
assert len(exemples) == 5

for exemple in exemples:
    assert set(exemple["features"]) == set(features)

X = pd.DataFrame(
    [e["features"] for e in exemples],
    columns=features
)

scores = modele.predict_proba(X)[:, 1]
scores_attendus = np.array([
    e["risk_score"] for e in exemples
])

ecart = np.max(np.abs(scores - scores_attendus))

assert np.isfinite(scores).all()
assert ((scores >= 0) & (scores <= 1)).all()
assert ecart < 1e-10

# Comparaison des niveaux de risque
niveaux = np.where(
    scores >= seuil_eleve, "élevé",
    np.where(scores >= seuil_faible, "modéré", "faible")
)

niveaux_attendus = [
    e["risk_level"] for e in exemples
]

assert niveaux.tolist() == niveaux_attendus

print("6. Les cinq prédictions sont cohérentes.")
print("Écart maximal :", ecart)

# Affichage des résultats
resultats = pd.DataFrame({
    "Profil": [e["description"] for e in exemples],
    "Score": scores,
    "Niveau": niveaux
})

print("\nRésultats des profils de référence :")
print(resultats.to_string(index=False))

print("\nAccuracy Test :", round(
    metrics["test"]["Accuracy"] * 100, 2
), "%")

print("Recall Test :", round(
    metrics["test"]["Recall (classe 1)"] * 100, 2
), "%")

print("\nValidation des artefacts réussie.")
