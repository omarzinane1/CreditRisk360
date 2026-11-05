
from fastapi import APIRouter, Request, HTTPException
import json

router = APIRouter(tags=["Machine Learning"])


@router.get("/model")
def informations_modele(request: Request):

    service = request.app.state.prediction_service

    return {
        "model_name": service.metadata["model_name"],
        "model_version": service.metadata["model_version"],
        "threshold_version": service.metadata["threshold_version"],
        "score_type": service.metadata["score_type"],
        "features": service.features,
        "thresholds": service.seuils
    }


@router.get(
    "/model/metrics",
    summary="Consulter les métriques du modèle E3"
)
def consulter_metriques(request: Request):

    # Récupérer le modèle chargé
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

    # Chemin du fichier des métriques
    chemin = (
        service.dossier_artefacts / "metrics.json"
    )

    try:
        with open(chemin, encoding="utf-8") as fichier:
            metrics = json.load(fichier)

    except (OSError, json.JSONDecodeError):
        raise HTTPException(
            status_code=503,
            detail="Les métriques du modèle sont indisponibles."
        )

    return {
        "model_version": service.metadata["model_version"],
        "threshold_version": service.metadata["threshold_version"],
        "metrics": metrics
    }

