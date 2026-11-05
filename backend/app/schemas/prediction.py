
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


# Types numériques utilisés par le modèle
EntierPositifOuNul = Annotated[
    int, Field(strict=True, ge=0)
]

NombrePositifOuNul = Annotated[
    float, Field(strict=True, ge=0, allow_inf_nan=False)
]


class CreditFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Utilisation du crédit
    RevolvingUtilizationOfUnsecuredLines: NombrePositifOuNul

    # Informations générales
    age: Annotated[int, Field(strict=True, gt=0)]

    # Retards de paiement
    NumberOfTime30_59DaysPastDueNotWorse: EntierPositifOuNul = Field(
        alias="NumberOfTime30-59DaysPastDueNotWorse"
    )

    # Endettement et revenus
    DebtRatio: NombrePositifOuNul
    MonthlyIncome: NombrePositifOuNul | None

    # Crédits et prêts
    NumberOfOpenCreditLinesAndLoans: EntierPositifOuNul
    NumberOfTimes90DaysLate: EntierPositifOuNul
    NumberRealEstateLoansOrLines: EntierPositifOuNul

    NumberOfTime60_89DaysPastDueNotWorse: EntierPositifOuNul = Field(
        alias="NumberOfTime60-89DaysPastDueNotWorse"
    )

    NumberOfDependents: EntierPositifOuNul | None


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    features: CreditFeatures


class PredictionResponse(BaseModel):
    risk_score: float
    risk_level: Literal["faible", "modéré", "élevé"]
    score_type: str
    model_version: str
    threshold_version: str
    persisted: bool = False


from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_id: UUID
    features: CreditFeatures


class AssessmentResponse(PredictionResponse):
    assessment_id: UUID
    client_id: UUID
    created_at: datetime
    features: dict[str, int | float | None]
    persisted: bool = True
