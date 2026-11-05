
from fastapi import APIRouter, HTTPException, Query

from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse
)

from app.persistence.clients_repository import (
    creer_client,
    obtenir_client,
    lister_clients,
    modifier_client
)


router = APIRouter(tags=["Clients"])


@router.post(
    "/clients",
    response_model=ClientResponse,
    status_code=201
)
def ajouter_client(donnees: ClientCreate):

    features = (
        donnees.features.model_dump(by_alias=True)
        if donnees.features is not None
        else None
    )

    return creer_client(
        display_name=donnees.display_name,
        features=features
    )


@router.get(
    "/clients",
    response_model=list[ClientResponse]
)
def consulter_clients(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):

    return lister_clients(limit, offset)


@router.get(
    "/clients/{client_id}",
    response_model=ClientResponse
)
def consulter_client(client_id: str):

    client = obtenir_client(client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable."
        )

    return client


@router.patch(
    "/clients/{client_id}",
    response_model=ClientResponse
)
def actualiser_client(
    client_id: str,
    donnees: ClientUpdate
):

    features = (
        donnees.features.model_dump(by_alias=True)
        if donnees.features is not None
        else None
    )

    client = modifier_client(
        client_id=client_id,
        display_name=donnees.display_name,
        features=features
    )

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable."
        )

    return client


from uuid import UUID

from app.schemas.prediction import AssessmentResponse

from app.persistence.assessments_repository import (
    lister_evaluations
)


@router.get(
    "/clients/{client_id}/assessments",
    response_model=list[AssessmentResponse],
    summary="Historique des évaluations d'un client"
)
def consulter_historique(client_id: UUID):

    identifiant = str(client_id)

    # Vérification de l'existence du client
    if obtenir_client(identifiant) is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable."
        )

    # Récupération des évaluations enregistrées
    return lister_evaluations(identifiant)
