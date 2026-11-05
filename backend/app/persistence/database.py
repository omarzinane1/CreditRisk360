
import os
import sqlite3
from pathlib import Path
from contextlib import closing

# Chemin de la base de données
RACINE_BACKEND = Path(__file__).resolve().parents[2]

DB_PATH = Path(
    os.environ.get(
        "CREDITRISK360_DB_PATH",
        str(RACINE_BACKEND / "data" / "creditrisk360.sqlite3")
    )
)


def ouvrir_connexion():
    # Création du dossier contenant la base
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connexion = sqlite3.connect(DB_PATH)
    connexion.row_factory = sqlite3.Row

    # Activation des clés étrangères
    connexion.execute("PRAGMA foreign_keys = ON")

    return connexion


def initialiser_base():
    # Création des tables si elles n'existent pas
    with closing(ouvrir_connexion()) as connexion:

        connexion.executescript("""
            CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS client_profiles (
                client_id TEXT PRIMARY KEY,
                features_json TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (client_id)
                    REFERENCES clients(id)
            );

            CREATE TABLE IF NOT EXISTS model_metadata (
                version TEXT PRIMARY KEY,
                trained_at TEXT,
                dataset_hash TEXT,
                feature_schema_hash TEXT,
                metrics_json TEXT,
                threshold_config_json TEXT
            );

            CREATE TABLE IF NOT EXISTS assessments (
                id TEXT PRIMARY KEY,
                client_id TEXT NOT NULL,
                features_json TEXT NOT NULL,
                risk_score REAL NOT NULL
                    CHECK (risk_score BETWEEN 0 AND 1),
                risk_level TEXT NOT NULL
                    CHECK (risk_level IN (
                        'faible', 'modéré', 'élevé'
                    )),
                score_type TEXT NOT NULL,
                model_version TEXT NOT NULL,
                threshold_version TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (client_id)
                    REFERENCES clients(id),
                FOREIGN KEY (model_version)
                    REFERENCES model_metadata(version)
            );

            CREATE INDEX IF NOT EXISTS
                idx_assessments_client_date
                ON assessments(client_id, created_at);
        """)

        connexion.commit()

    return DB_PATH
