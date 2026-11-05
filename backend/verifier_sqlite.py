
from contextlib import closing

from app.persistence.database import (
    initialiser_base,
    ouvrir_connexion
)

# Initialisation de la base SQLite
chemin = initialiser_base()

print("Base SQLite initialisée.")
print("Chemin :", chemin)

# Vérification des tables
with closing(ouvrir_connexion()) as connexion:

    lignes = connexion.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """).fetchall()

    tables = {ligne["name"] for ligne in lignes}

    attendues = {
        "clients",
        "client_profiles",
        "assessments",
        "model_metadata"
    }

    assert attendues.issubset(tables)

    # Vérification des clés étrangères
    foreign_keys = connexion.execute(
        "PRAGMA foreign_keys"
    ).fetchone()[0]

    assert foreign_keys == 1

    # Vérification de l'intégrité SQLite
    integrite = connexion.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

    assert integrite == "ok"

print("\nTables créées :")

for table in sorted(attendues):
    print("-", table)

print("\nClés étrangères : activées")
print("Intégrité SQLite : OK")
print("\nValidation SQLite réussie.")
