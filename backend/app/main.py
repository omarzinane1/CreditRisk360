
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    API_PREFIX
)

from app.api.routers import health, model, predictions, clients
from app.services.prediction_service import PredictionService
from app.persistence.database import initialiser_base
from app.persistence.assessments_repository import (
    enregistrer_version_modele
)

# Chargement du modèle au démarrage de l'API

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Initialisation de la base SQLite
    initialiser_base()

    # Chargement du modèle E3
    service = PredictionService()

    # Enregistrement de la version du modèle
    enregistrer_version_modele(
        service.metadata,
        service.dossier_artefacts / "metrics.json"
    )

    app.state.prediction_service = service

    yield


# Création de l'application
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    lifespan=lifespan
)

# Enregistrement des routes
app.include_router(health.router)
app.include_router(model.router, prefix=API_PREFIX)
# Route de prédiction du modèle E3
app.include_router(
    predictions.router,
    prefix=API_PREFIX
)
# Routes de gestion des clients fictifs
app.include_router(
    clients.router,
    prefix=API_PREFIX
)


@app.get("/", tags=["General"])
def accueil():
    return {
        "application": "CreditRisk360",
        "message": "API initialisée avec succès",
        "version": APP_VERSION
    }

