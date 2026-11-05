
import json
from uuid import uuid4
from pathlib import Path
from datetime import datetime, timezone
from contextlib import closing

from app.persistence.database import ouvrir_connexion
from app.persistence.clients_repository import enregistrer_profil


def date_utc():
    return datetime.now(timezone.utc).isoformat()


def enregistrer_version_modele(metadata, chemin_metrics):
    # Chargement des résultats scientifiques
    with open(chemin_metrics, encoding="utf-8") as fichier:
        metrics = json.load(fichier)

    # Version des seuils utilisée avec ce modèle
    configuration = {
        "threshold_version": metadata["threshold_version"],
        "thresholds": metadata["thresholds"]
    }

    configuration_json = json.dumps(
        configuration, sort_keys=True
    )

    with closing(ouvrir_connexion()) as connexion:
        with connexion:
            ligne = connexion.execute("""
                SELECT threshold_config_json
                FROM model_metadata
                WHERE version = ?
            """, (metadata["model_version"],)).fetchone()

            if ligne is not None:
                # Une version ne doit pas désigner deux
                # configurations de seuils différentes
                if ligne["threshold_config_json"] != configuration_json:
                    raise RuntimeError(
                        "La version du modèle existe déjà "
                        "avec des seuils différents."
                    )
                return

            connexion.execute("""
                INSERT INTO model_metadata (
                    version, trained_at, dataset_hash,
                    feature_schema_hash, metrics_json,
                    threshold_config_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                metadata["model_version"],
                metadata.get("trained_at"),
                metadata.get("dataset_hash"),
                metadata.get("feature_schema_hash"),
                json.dumps(metrics, ensure_ascii=False),
                configuration_json
            ))


def creer_evaluation(client_id, features, resultat):
    # Identifiant et date de la nouvelle évaluation
    assessment_id = str(uuid4())
    maintenant = date_utc()

    contenu = json.dumps(
        features,
        ensure_ascii=False,
        allow_nan=False
    )

    with closing(ouvrir_connexion()) as connexion:
        with connexion:

            # Vérification du client
            client = connexion.execute("""
                SELECT id FROM clients WHERE id = ?
            """, (client_id,)).fetchone()

            if client is None:
                return None

            # Sauvegarde du profil courant
            enregistrer_profil(
                connexion, client_id,
                features, maintenant
            )

            connexion.execute("""
                UPDATE clients
                SET updated_at = ?
                WHERE id = ?
            """, (maintenant, client_id))

            # Nouvelle évaluation immuable
            connexion.execute("""
                INSERT INTO assessments (
                    id, client_id, features_json,
                    risk_score, risk_level, score_type,
                    model_version, threshold_version,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assessment_id,
                client_id,
                contenu,
                resultat["risk_score"],
                resultat["risk_level"],
                resultat["score_type"],
                resultat["model_version"],
                resultat["threshold_version"],
                maintenant
            ))

    return {
        "assessment_id": assessment_id,
        "client_id": client_id,
        "created_at": maintenant,
        "features": features,
        **resultat,
        "persisted": True
    }


def lister_evaluations(client_id):
    with closing(ouvrir_connexion()) as connexion:
        lignes = connexion.execute("""
            SELECT *
            FROM assessments
            WHERE client_id = ?
            ORDER BY created_at DESC, id DESC
        """, (client_id,)).fetchall()

    evaluations = []

    for ligne in lignes:
        evaluations.append({
            "assessment_id": ligne["id"],
            "client_id": ligne["client_id"],
            "created_at": ligne["created_at"],
            "features": json.loads(ligne["features_json"]),
            "risk_score": ligne["risk_score"],
            "risk_level": ligne["risk_level"],
            "score_type": ligne["score_type"],
            "model_version": ligne["model_version"],
            "threshold_version": ligne["threshold_version"],
            "persisted": True
        })

    return evaluations
