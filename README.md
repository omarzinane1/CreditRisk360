# CreditRisk360

## Présentation

CreditRisk360 est un projet académique de Data Mining et Machine Learning consacré à l'analyse du risque de défaut de paiement.

Le projet repose sur le dataset **Give Me Some Credit** et utilise la Régression Logistique pour comparer trois stratégies :

- E1 : Régression Logistique classique.
- E2 : Régression Logistique avec pondération des classes.
- E3 : Régression Logistique avec SMOTE.

Le modèle E3 est retenu pour la démonstration, avec un seuil de décision sélectionné sur la validation.

## Technologies

- Python 3.11
- Scikit-learn 1.6.1
- Imbalanced-learn 0.13.0
- Pandas, NumPy, SciPy
- Matplotlib et Seaborn
- Jupyter Notebook
- Joblib

## Installation

Créer un environnement virtuel :

```powershell
python -m venv .venv
```

Installer les dépendances :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Machine Learning

Le notebook principal se trouve dans `notebooks/`.

Les artefacts du modèle sont enregistrés dans `ml/artifacts/` :

- `model.joblib`
- `metadata.json`
- `metrics.json`
- `exemples_reference.json`

## Vérification des artefacts

Depuis la racine du projet :

```powershell
.\.venv\Scripts\python.exe verifier_artefacts.py
```

Ce script permet de vérifier la cohérence des métadonnées, des seuils et des prédictions du modèle exporté.

## Architecture prévue

La version finale comprendra :

- Une API FastAPI conteneurisée avec Docker.
- Une base de données SQLite.
- Une application Desktop développée avec PySide6.
- Un système de scoring dynamique et d'historique des évaluations.

Le système utilisera uniquement des données publiques anonymisées et des profils fictifs pour la démonstration. Il ne devra pas servir à des décisions automatiques d'octroi de crédit.