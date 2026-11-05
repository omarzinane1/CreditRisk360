
import sqlite3
from contextlib import closing

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.persistence.database import ouvrir_connexion


router = APIRouter(tags=["Health"])


@router.get("/health", summary="État de CreditRisk360")
def verifier_sante(request: Request):

    # Vérification du modèle ML
    service = getattr(
        request.app.state,
        "prediction_service",
        None
    )

    model_loaded = (
        service is not None
        and hasattr(service, "modele")
    )

    # Vérification de SQLite et des tables
    db_ok = False

    try:
        with closing(ouvrir_connexion()) as connexion:
            connexion.execute(
                "SELECT id FROM clients LIMIT 1"
            ).fetchone()

            connexion.execute(
                "SELECT client_id FROM client_profiles LIMIT 1"
            ).fetchone()

            connexion.execute(
                "SELECT id FROM assessments LIMIT 1"
            ).fetchone()

            connexion.execute(
                "SELECT version FROM model_metadata LIMIT 1"
            ).fetchone()

        db_ok = True

    except (sqlite3.Error, OSError):
        db_ok = False

    # État global
    pret = model_loaded and db_ok

    return JSONResponse(
        status_code=200 if pret else 503,
        content={
            "status": "ok" if pret else "not_ready",
            "model_loaded": model_loaded,
            "db_ok": db_ok
        }
    )
