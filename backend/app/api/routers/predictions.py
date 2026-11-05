
from fastapi import APIRouter, HTTPException, Request

from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse
)


router = APIRouter(tags=["Predictions"])


@router.post(
    "/predictions/preview",
    response_model=PredictionResponse,
    status_code=200,
    summary="Calculer un score de risque"
)
def predire_risque(
    donnees: PredictionRequest,
    request: Request
):

    # Récupération du service ML déjà chargé
    service = getattr(
        request.app.state,
        "prediction_service",
        None
    )

    if service is None:
        raise HTTPException(
            status_code=503,
            detail="Le modèle E3 est indisponible."
        )

    # Conservation des noms exacts des 10 variables
    caracteristiques = donnees.features.model_dump(
        by_alias=True
    )

    # Calcul du score avec le modèle E3
    resultat = service.predire(caracteristiques)

    # Résultat non enregistré dans SQLite
    return PredictionResponse(
        **resultat,
        persisted=False
    )

from app.schemas.prediction import (
    AssessmentRequest,
    AssessmentResponse
)

from app.persistence.assessments_repository import (
    creer_evaluation
)

from app.persistence.clients_repository import obtenir_client


@router.post(
    "/predictions",
    response_model=AssessmentResponse,
    status_code=201,
    summary="Calculer et enregistrer une évaluation"
)
def enregistrer_prediction(
    donnees: AssessmentRequest,
    request: Request
):

    # Vérification du client fictif
    client_id = str(donnees.client_id)

    if obtenir_client(client_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable."
        )

    # Récupération du modèle E3
    service = getattr(
        request.app.state,
        "prediction_service",
        None
    )

    if service is None:
        raise HTTPException(
            status_code=503,
            detail="Le modèle E3 est indisponible."
        )

    # Conservation des noms exacts des variables
    features = donnees.features.model_dump(
        by_alias=True
    )

    # Calcul du score
    resultat = service.predire(features)

    # Enregistrement dans SQLite
    evaluation = creer_evaluation(
        client_id=client_id,
        features=features,
        resultat=resultat
    )

    if evaluation is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable."
        )

    return evaluation
