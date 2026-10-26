"""
CreditRisk 360 - Prétraitement partagé entre le notebook et l'API.
Fichier généré depuis le notebook credit_scoring.ipynb.
"""
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Ordre officiel des 10 variables (mêmes noms que le CSV)
FEATURES = [
    "RevolvingUtilizationOfUnsecuredLines",
    "age",
    "NumberOfTime30-59DaysPastDueNotWorse",
    "DebtRatio",
    "MonthlyIncome",
    "NumberOfOpenCreditLinesAndLoans",
    "NumberOfTimes90DaysLate",
    "NumberRealEstateLoansOrLines",
    "NumberOfTime60-89DaysPastDueNotWorse",
    "NumberOfDependents",
]

COLONNES_RETARDS = [
    "NumberOfTime30-59DaysPastDueNotWorse",
    "NumberOfTime60-89DaysPastDueNotWorse",
    "NumberOfTimes90DaysLate",
]

# Indicateurs de valeurs manquantes ajoutés par le pipeline
INDICATEURS = ["Retards_manquants", "Revenu_manquant", "Dependants_manquant"]

# Bornes d'écrêtage (quantiles APPRIS sur le train uniquement)
QUANTILES_ECRETAGE = {
    "RevolvingUtilizationOfUnsecuredLines": 0.99,
    "DebtRatio": 0.99,
    "MonthlyIncome": 0.99,
    "NumberOfOpenCreditLinesAndLoans": 0.999,
    "NumberRealEstateLoansOrLines": 0.999,
    "NumberOfDependents": 0.999,
    "NumberOfTime30-59DaysPastDueNotWorse": 0.999,
    "NumberOfTime60-89DaysPastDueNotWorse": 0.999,
    "NumberOfTimes90DaysLate": 0.999,
}


class NettoyageAnomalies(BaseEstimator, TransformerMixin):
    """Remplace les valeurs invalides par NaN et ajoute les indicateurs.

    - age hors de [18, 120]      -> NaN
    - retards égaux à 96 ou 98   -> NaN
    - ajoute 3 indicateurs 0/1 : retards, revenu et personnes à charge manquants

    Aucun paramètre à apprendre. Idempotent : peut être appliqué à des données
    brutes (API) ou déjà nettoyées (notebook) avec le même résultat.
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X[FEATURES].copy()
        X["age"] = X["age"].mask(~X["age"].between(18, 120), np.nan)
        for colonne in COLONNES_RETARDS:
            X[colonne] = X[colonne].replace({96: np.nan, 98: np.nan})
        X["Retards_manquants"] = X[COLONNES_RETARDS].isnull().any(axis=1).astype(int)
        X["Revenu_manquant"] = X["MonthlyIncome"].isnull().astype(int)
        X["Dependants_manquant"] = X["NumberOfDependents"].isnull().astype(int)
        return X


class EcretageQuantiles(BaseEstimator, TransformerMixin):
    """Écrête les valeurs supérieures à un quantile appris sur le train."""

    def __init__(self, quantiles=None):
        self.quantiles = quantiles

    def fit(self, X, y=None):
        self.bornes_ = {c: float(X[c].quantile(q)) for c, q in self.quantiles.items()}
        return self

    def transform(self, X):
        X = X.copy()
        for colonne, borne in self.bornes_.items():
            X[colonne] = X[colonne].clip(upper=borne)
        return X


class LogColonnes(BaseEstimator, TransformerMixin):
    """Applique log(1 + x) aux colonnes indiquées."""

    def __init__(self, colonnes=None):
        self.colonnes = colonnes

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        for colonne in self.colonnes:
            X[colonne] = np.log1p(X[colonne])
        return X


def construire_preprocesseur():
    """Pipeline de prétraitement complet (non ajusté).

    Étapes : nettoyage + indicateurs -> écrêtage -> log(DebtRatio)
             -> imputation médiane + standardisation (10 variables)
             -> indicateurs conservés tels quels (0/1).
    Toutes les valeurs apprises le sont sur les données passées à fit().
    """
    transformation = ColumnTransformer(
        [
            (
                "numeriques",
                Pipeline(
                    [
                        ("imputation", SimpleImputer(strategy="median")),
                        ("standardisation", StandardScaler()),
                    ]
                ),
                FEATURES,
            ),
            ("indicateurs", "passthrough", INDICATEURS),
        ],
        verbose_feature_names_out=False,
    )
    transformation.set_output(transform="pandas")

    return Pipeline(
        [
            ("nettoyage", NettoyageAnomalies()),
            ("ecretage", EcretageQuantiles(QUANTILES_ECRETAGE)),
            ("log_debtratio", LogColonnes(["DebtRatio"])),
            ("transformation", transformation),
        ]
    )
