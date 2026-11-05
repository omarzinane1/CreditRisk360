
import sys
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn


class PredictionService:
    def __init__(self):

        # Chemins du projet CreditRisk360
        self.racine = Path(__file__).resolve().parents[3]
        self.dossier_ml = self.racine / "ml"
        self.dossier_artefacts = self.dossier_ml / "artifacts"

        # Import des classes de prétraitement du modèle
        sys.path.insert(
            0, str(self.dossier_ml / "training")
        )

        # Chargement des métadonnées
        with open(
            self.dossier_artefacts / "metadata.json",
            encoding="utf-8"
        ) as fichier:
            self.metadata = json.load(fichier)

        # Vérification de la version scikit-learn
        version_attendue = self.metadata["libraries"]["scikit-learn"]

        if sklearn.__version__ != version_attendue:
            raise RuntimeError(
                f"Version scikit-learn incompatible : "
                f"{sklearn.__version__} au lieu de "
                f"{version_attendue}"
            )

        # Chargement du pipeline ML approuvé
        self.modele = joblib.load(
            self.dossier_artefacts / "model.joblib"
        )

        # Vérification du pipeline d'inférence
        if "smote" in self.modele.named_steps:
            raise RuntimeError(
                "SMOTE ne doit pas être exécuté pendant l'inférence."
            )

        self.features = self.metadata["features"]
        self.seuils = self.metadata["thresholds"]

        if len(self.features) != 10:
            raise RuntimeError("Le modèle doit accepter 10 variables.")

        print("Modèle E3 chargé avec succès.")

    def predire(self, caracteristiques):

        # Vérification des variables
        if set(caracteristiques) != set(self.features):
            raise ValueError(
                "Les caractéristiques ne correspondent pas "
                "aux 10 variables du modèle."
            )

        # Préparation de l'entrée dans le bon ordre
        X = pd.DataFrame(
            [{nom: caracteristiques[nom]
              for nom in self.features}],
            columns=self.features
        )

        # Prédiction du score corrigé
        # La correction de prévalence est déjà dans model.joblib
        score = float(self.modele.predict_proba(X)[0, 1])

        if not np.isfinite(score) or not (0 <= score <= 1):
            raise ValueError("Score de prédiction invalide.")

        # Détermination du niveau de risque
        if score >= self.seuils["modere_eleve"]:
            niveau = "élevé"
        elif score >= self.seuils["faible_modere"]:
            niveau = "modéré"
        else:
            niveau = "faible"

        return {
            "risk_score": score,
            "risk_level": niveau,
            "score_type": self.metadata["score_type"],
            "model_version": self.metadata["model_version"],
            "threshold_version": self.metadata["threshold_version"]
        }
