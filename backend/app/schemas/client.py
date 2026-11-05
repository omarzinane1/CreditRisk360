
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator
)

from app.schemas.prediction import CreditFeatures


# Nom utilisé uniquement pour les clients fictifs
NomClient = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=2,
        max_length=80
    )
]


class ClientCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: NomClient
    features: CreditFeatures | None = None


class ClientUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: NomClient | None = None
    features: CreditFeatures | None = None

    @model_validator(mode="after")
    def verifier_modification(self):
        if self.display_name is None and self.features is None:
            raise ValueError(
                "Indiquer un nom ou des caractéristiques à modifier."
            )
        return self


class ClientResponse(BaseModel):
    id: str
    display_name: str
    created_at: str
    updated_at: str
    features: dict[str, int | float | None] | None = None
