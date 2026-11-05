
import os
import sys
import tempfile
import unittest

from pathlib import Path


# Ajouter backend au chemin d'import Python
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))


# Profil fictif de référence
FEATURES = {
    "RevolvingUtilizationOfUnsecuredLines": 0.42,
    "age": 35,
    "NumberOfTime30-59DaysPastDueNotWorse": 1,
    "DebtRatio": 0.35,
    "MonthlyIncome": 8000,
    "NumberOfOpenCreditLinesAndLoans": 5,
    "NumberOfTimes90DaysLate": 0,
    "NumberRealEstateLoansOrLines": 1,
    "NumberOfTime60-89DaysPastDueNotWorse": 0,
    "NumberOfDependents": 2
}


class TestCreditRisk360API(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # Utiliser une base temporaire distincte
        cls.temp_dir = tempfile.TemporaryDirectory()

        cls.old_db_path = os.environ.get(
            "CREDITRISK360_DB_PATH"
        )

        os.environ["CREDITRISK360_DB_PATH"] = str(
            Path(cls.temp_dir.name) / "test.sqlite3"
        )

        # Importer l'application après la configuration
        from fastapi.testclient import TestClient
        from app.main import app

        cls.client = TestClient(app)

        # Déclenche le lifespan :
        # initialisation SQLite et chargement de E3
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):

        cls.client.__exit__(None, None, None)

        if cls.old_db_path is None:
            os.environ.pop(
                "CREDITRISK360_DB_PATH", None
            )
        else:
            os.environ["CREDITRISK360_DB_PATH"] = (
                cls.old_db_path
            )

        cls.temp_dir.cleanup()

    def test_01_health(self):

        reponse = self.client.get("/health")

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.json()["status"], "ok")
        self.assertTrue(reponse.json()["model_loaded"])
        self.assertTrue(reponse.json()["db_ok"])

    def test_02_metrics(self):

        reponse = self.client.get(
            "/api/v1/model/metrics"
        )

        self.assertEqual(reponse.status_code, 200)

        contenu = reponse.json()

        self.assertIn("model_version", contenu)
        self.assertIn("threshold_version", contenu)
        self.assertIn("metrics", contenu)

    def test_03_validation(self):

        features_invalides = {
            **FEATURES,
            "age": -5
        }

        reponse = self.client.post(
            "/api/v1/predictions/preview",
            json={"features": features_invalides}
        )

        self.assertEqual(reponse.status_code, 422)

    def test_04_client_inexistant(self):

        reponse = self.client.get(
            "/api/v1/clients/"
            "00000000-0000-4000-8000-000000000001"
        )

        self.assertEqual(reponse.status_code, 404)

    def test_05_scoring_et_historique(self):

        # Création du client fictif
        reponse = self.client.post(
            "/api/v1/clients",
            json={
                "display_name": "Client fictif test API"
            }
        )

        self.assertEqual(reponse.status_code, 201)

        client_id = reponse.json()["id"]

        # Prédiction sans sauvegarde
        preview = self.client.post(
            "/api/v1/predictions/preview",
            json={"features": FEATURES}
        )

        self.assertEqual(preview.status_code, 200)

        # Première évaluation A1
        reponse_a1 = self.client.post(
            "/api/v1/predictions",
            json={
                "client_id": client_id,
                "features": FEATURES
            }
        )

        self.assertEqual(reponse_a1.status_code, 201)

        a1 = reponse_a1.json()

        self.assertTrue(a1["persisted"])
        self.assertEqual(
            a1["risk_score"],
            preview.json()["risk_score"]
        )

        # Deuxième évaluation A2
        features_a2 = {
            **FEATURES,
            "RevolvingUtilizationOfUnsecuredLines": 0.80,
            "NumberOfTime30-59DaysPastDueNotWorse": 3,
            "NumberOfTimes90DaysLate": 1
        }

        reponse_a2 = self.client.post(
            "/api/v1/predictions",
            json={
                "client_id": client_id,
                "features": features_a2
            }
        )

        self.assertEqual(reponse_a2.status_code, 201)

        a2 = reponse_a2.json()

        # Chaque évaluation possède son identifiant
        self.assertNotEqual(
            a1["assessment_id"],
            a2["assessment_id"]
        )

        # Vérifier l'historique SQLite
        historique_response = self.client.get(
            f"/api/v1/clients/{client_id}/assessments"
        )

        self.assertEqual(
            historique_response.status_code,
            200
        )

        historique = historique_response.json()

        self.assertEqual(len(historique), 2)

        evaluations = {
            item["assessment_id"]: item
            for item in historique
        }

        # A1 n'a pas été modifiée
        a1_rechargee = evaluations[a1["assessment_id"]]

        self.assertEqual(
            a1_rechargee["features"],
            FEATURES
        )

        self.assertEqual(
            a1_rechargee["risk_score"],
            a1["risk_score"]
        )

        # A2 possède ses propres caractéristiques
        a2_rechargee = evaluations[a2["assessment_id"]]

        self.assertEqual(
            a2_rechargee["features"],
            features_a2
        )

        # Le profil courant correspond à A2
        client_response = self.client.get(
            f"/api/v1/clients/{client_id}"
        )

        self.assertEqual(
            client_response.status_code,
            200
        )

        self.assertEqual(
            client_response.json()["features"],
            features_a2
        )


if __name__ == "__main__":
    unittest.main()
