
import json
from uuid import uuid4
from datetime import datetime, timezone
from contextlib import closing

from app.persistence.database import ouvrir_connexion


def date_utc():
    return datetime.now(timezone.utc).isoformat()


def convertir_client(ligne):
    if ligne is None:
        return None

    return {
        "id": ligne["id"],
        "display_name": ligne["display_name"],
        "created_at": ligne["created_at"],
        "updated_at": ligne["updated_at"],
        "features": (
            json.loads(ligne["features_json"])
            if ligne["features_json"] is not None
            else None
        )
    }


def obtenir_client(client_id):
    with closing(ouvrir_connexion()) as connexion:
        ligne = connexion.execute("""
            SELECT c.id, c.display_name,
                   c.created_at, c.updated_at,
                   p.features_json
            FROM clients AS c
            LEFT JOIN client_profiles AS p
                ON c.id = p.client_id
            WHERE c.id = ?
        """, (client_id,)).fetchone()

    return convertir_client(ligne)


def enregistrer_profil(connexion, client_id, features, date):
    # Conservation du dernier profil courant
    contenu = json.dumps(
        features,
        ensure_ascii=False,
        allow_nan=False
    )

    connexion.execute("""
        INSERT INTO client_profiles (
            client_id, features_json, updated_at
        )
        VALUES (?, ?, ?)
        ON CONFLICT(client_id)
        DO UPDATE SET
            features_json = excluded.features_json,
            updated_at = excluded.updated_at
    """, (client_id, contenu, date))


def creer_client(display_name, features=None):
    client_id = str(uuid4())
    maintenant = date_utc()

    with closing(ouvrir_connexion()) as connexion:
        with connexion:
            connexion.execute("""
                INSERT INTO clients (
                    id, display_name,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?)
            """, (
                client_id,
                display_name,
                maintenant,
                maintenant
            ))

            if features is not None:
                enregistrer_profil(
                    connexion, client_id,
                    features, maintenant
                )

    return obtenir_client(client_id)


def lister_clients(limit=20, offset=0):
    with closing(ouvrir_connexion()) as connexion:
        lignes = connexion.execute("""
            SELECT c.id, c.display_name,
                   c.created_at, c.updated_at,
                   p.features_json
            FROM clients AS c
            LEFT JOIN client_profiles AS p
                ON c.id = p.client_id
            ORDER BY c.created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()

    return [convertir_client(ligne) for ligne in lignes]


def modifier_client(client_id, display_name=None, features=None):
    maintenant = date_utc()

    with closing(ouvrir_connexion()) as connexion:
        with connexion:
            existe = connexion.execute(
                "SELECT 1 FROM clients WHERE id = ?",
                (client_id,)
            ).fetchone()

            if existe is None:
                return None

            if display_name is not None:
                connexion.execute("""
                    UPDATE clients
                    SET display_name = ?, updated_at = ?
                    WHERE id = ?
                """, (display_name, maintenant, client_id))

            if features is not None:
                enregistrer_profil(
                    connexion, client_id,
                    features, maintenant
                )

                connexion.execute("""
                    UPDATE clients
                    SET updated_at = ?
                    WHERE id = ?
                """, (maintenant, client_id))

    return obtenir_client(client_id)
