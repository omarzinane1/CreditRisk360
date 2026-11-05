
import json

from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QPlainTextEdit,
    QTabWidget
)

from pages.clients_page import VARIABLES


CLIENTS_PATH = "/api/v1/clients?limit=100&offset=0"


def afficher_valeur(valeur):
    if valeur is None:
        return "Manquante"

    if isinstance(valeur, float):
        return f"{valeur:g}"

    return str(valeur)


def afficher_date(date_iso):
    # Les dates enregistrées par notre Backend sont en UTC
    return date_iso[:19].replace("T", " ") + " UTC"


class HistoryPage(QWidget):

    def __init__(self, api, parent=None):
        super().__init__(parent)

        self.api = api
        self.clients = {}
        self.evaluations = []
        self.chemin_historique = None

        self.construire_interface()

        self.api.response_received.connect(
            self.recevoir_reponse
        )
        self.api.request_failed.connect(
            self.gerer_erreur
        )

    def construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        description = QLabel(
            "Consulter les évaluations enregistrées "
            "et comparer l'évolution du profil d'un "
            "client fictif."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # -----------------------
        # SÉLECTION DU CLIENT
        # -----------------------
        barre = QHBoxLayout()

        barre.addWidget(QLabel("Client :"))

        self.combo_clients = QComboBox()
        self.combo_clients.setMinimumWidth(250)

        self.combo_clients.currentIndexChanged.connect(
            self.changer_client
        )

        barre.addWidget(self.combo_clients, 1)

        bouton = QPushButton("Actualiser")
        bouton.setObjectName("refreshButton")
        bouton.clicked.connect(self.charger_clients)

        barre.addWidget(bouton)
        layout.addLayout(barre)

        # -----------------------
        # RÉSUMÉ DE L'HISTORIQUE
        # -----------------------
        resume = QHBoxLayout()

        self.nombre_label = QLabel("Évaluations : —")
        self.dernier_score_label = QLabel(
            "Dernier score : —"
        )

        resume.addWidget(self.nombre_label)
        resume.addSpacing(25)
        resume.addWidget(self.dernier_score_label)
        resume.addStretch()

        layout.addLayout(resume)

        # -----------------------
        # TABLEAU DES ÉVALUATIONS
        # -----------------------
        self.table = QTableWidget()
        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels([
            "N°",
            "Date (UTC)",
            "Score",
            "Niveau",
            "Modèle",
            "Identifiant"
        ])

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().setVisible(False)

        entete = self.table.horizontalHeader()
        entete.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table.itemSelectionChanged.connect(
            self.afficher_evaluation
        )

        layout.addWidget(self.table, 2)

        # -----------------------
        # ONGLETS DÉTAILS / COMPARAISON
        # -----------------------
        self.onglets = QTabWidget()

        # Détails complets de l'évaluation
        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText(
            "Sélectionne une évaluation."
        )

        self.onglets.addTab(
            self.details,
            "Détails de l'évaluation"
        )

        # Comparaison avec l'évaluation précédente
        comparaison = QWidget()
        comparaison_layout = QVBoxLayout(comparaison)

        self.comparaison_label = QLabel(
            "Sélectionne une évaluation."
        )
        self.comparaison_label.setWordWrap(True)
        comparaison_layout.addWidget(
            self.comparaison_label
        )

        self.table_comparaison = QTableWidget()
        self.table_comparaison.setColumnCount(4)

        self.table_comparaison.setHorizontalHeaderLabels([
            "Caractéristique",
            "Précédente",
            "Sélectionnée",
            "Écart"
        ])

        self.table_comparaison.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table_comparaison.setAlternatingRowColors(
            True
        )
        self.table_comparaison.verticalHeader().setVisible(
            False
        )

        self.table_comparaison.horizontalHeader(
        ).setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        comparaison_layout.addWidget(
            self.table_comparaison
        )

        note = QLabel(
            "L'écart correspond à la différence entre "
            "les valeurs des deux évaluations. "
            "Il ne mesure pas l'effet causal d'une "
            "variable sur le score."
        )
        note.setWordWrap(True)
        comparaison_layout.addWidget(note)

        self.onglets.addTab(
            comparaison,
            "Comparaison avec la précédente"
        )

        layout.addWidget(self.onglets, 2)

        # Messages d'état
        self.etat = QLabel(
            "Choisis un client pour consulter son historique."
        )
        self.etat.setWordWrap(True)
        layout.addWidget(self.etat)

    # -----------------------
    # CHARGEMENT DES CLIENTS
    # -----------------------
    def charger_clients(self):
        self.etat.setText(
            "Chargement des clients..."
        )
        self.api.get(CLIENTS_PATH)

    def changer_client(self, *_):
        client_id = self.combo_clients.currentData()

        # Réinitialiser l'affichage
        self.evaluations = []
        self.chemin_historique = None

        self.table.setRowCount(0)
        self.details.clear()
        self.table_comparaison.setRowCount(0)

        self.nombre_label.setText(
            "Évaluations : —"
        )
        self.dernier_score_label.setText(
            "Dernier score : —"
        )

        if not client_id:
            self.etat.setText(
                "Aucun client sélectionné."
            )
            return

        # Route d'historique du client courant
        self.chemin_historique = (
            f"/api/v1/clients/{client_id}/assessments"
        )

        self.etat.setText(
            "Chargement de l'historique..."
        )

        self.api.get(self.chemin_historique)

    # -----------------------
    # REMPLISSAGE DU TABLEAU
    # -----------------------
    def remplir_tableau(self):
        self.table.setRowCount(0)
        self.table.setRowCount(
            len(self.evaluations)
        )

        total = len(self.evaluations)

        for ligne, evaluation in enumerate(
            self.evaluations
        ):
            # Le Backend renvoie les plus récentes
            # en premier : A3, A2, A1...
            numero = f"A{total - ligne}"

            score = (
                float(evaluation["risk_score"]) * 100
            )

            valeurs = [
                numero,
                afficher_date(evaluation["created_at"]),
                f"{score:.2f} %",
                evaluation["risk_level"].capitalize(),
                evaluation["model_version"],
                evaluation["assessment_id"][:8] + "..."
            ]

            for colonne, valeur in enumerate(valeurs):
                cellule = QTableWidgetItem(
                    str(valeur)
                )

                cellule.setToolTip(
                    evaluation["assessment_id"]
                )

                if colonne == 3:
                    couleur = {
                        "faible": "#16856d",
                        "modéré": "#b47a14",
                        "élevé": "#bf3d46"
                    }.get(
                        evaluation["risk_level"],
                        "#243247"
                    )

                    cellule.setForeground(
                        QColor(couleur)
                    )

                self.table.setItem(
                    ligne,
                    colonne,
                    cellule
                )

        self.nombre_label.setText(
            f"Évaluations : {total}"
        )

        if self.evaluations:
            derniere = self.evaluations[0]

            score = (
                float(derniere["risk_score"]) * 100
            )

            self.dernier_score_label.setText(
                f"Dernier score : {score:.2f} % "
                f"({derniere['risk_level']})"
            )

            self.table.selectRow(0)

        else:
            self.dernier_score_label.setText(
                "Dernier score : —"
            )
            self.details.setPlainText(
                "Ce client n'a pas encore d'évaluation."
            )

    # -----------------------
    # DÉTAILS D'UNE ÉVALUATION
    # -----------------------
    def afficher_evaluation(self):
        ligne = self.table.currentRow()

        if not 0 <= ligne < len(self.evaluations):
            return

        evaluation = self.evaluations[ligne]
        numero = (
            f"A{len(self.evaluations) - ligne}"
        )

        texte = (
            f"Évaluation : {numero}\n"
            f"ID : {evaluation['assessment_id']}\n"
            f"Client : {evaluation['client_id']}\n"
            f"Date : {afficher_date(evaluation['created_at'])}\n"
            f"Score : {evaluation['risk_score'] * 100:.2f} %\n"
            f"Niveau : {evaluation['risk_level']}\n"
            f"Modèle : {evaluation['model_version']}\n"
            f"Seuils : {evaluation['threshold_version']}\n"
            f"Type : {evaluation['score_type']}\n\n"
            "CARACTÉRISTIQUES ENREGISTRÉES\n"
            + json.dumps(
                evaluation["features"],
                indent=2,
                ensure_ascii=False
            )
        )

        self.details.setPlainText(texte)
        self.comparer_evaluations(ligne)

    # -----------------------
    # COMPARAISON AVEC A(N-1)
    # -----------------------
    def comparer_evaluations(self, ligne):
        actuelle = self.evaluations[ligne]

        # Le tableau est ordonné du plus récent
        # au plus ancien.
        index_precedent = ligne + 1

        precedente = (
            self.evaluations[index_precedent]
            if index_precedent < len(self.evaluations)
            else None
        )

        numero_actuel = (
            len(self.evaluations) - ligne
        )

        if precedente is None:
            self.comparaison_label.setText(
                f"A{numero_actuel} : aucune évaluation "
                "précédente."
            )
        else:
            self.comparaison_label.setText(
                f"Comparaison A{numero_actuel - 1} "
                f"→ A{numero_actuel}"
            )

        self.table_comparaison.setRowCount(
            len(VARIABLES)
        )

        for index, (libelle, cle, _, _) in enumerate(
            VARIABLES
        ):
            nouvelle = actuelle["features"].get(
                cle
            )

            ancienne = (
                precedente["features"].get(cle)
                if precedente is not None
                else None
            )

            # Écart seulement si les deux
            # évaluations possèdent une valeur
            if (
                precedente is not None
                and ancienne is not None
                and nouvelle is not None
            ):
                ecart = nouvelle - ancienne
                ecart_texte = f"{ecart:+.4g}"
            else:
                ecart_texte = "—"

            valeurs = [
                libelle,
                (
                    afficher_valeur(ancienne)
                    if precedente is not None
                    else "—"
                ),
                afficher_valeur(nouvelle),
                ecart_texte
            ]

            for colonne, valeur in enumerate(valeurs):
                self.table_comparaison.setItem(
                    index,
                    colonne,
                    QTableWidgetItem(str(valeur))
                )

    # -----------------------
    # RÉPONSES DE FASTAPI
    # -----------------------
    def recevoir_reponse(self, path, donnees):

        if path == CLIENTS_PATH:

            if not isinstance(donnees, list):
                self.etat.setText(
                    "Liste des clients invalide."
                )
                return

            client_precedent = (
                self.combo_clients.currentData()
            )

            self.clients = {
                client["id"]: client
                for client in donnees
            }

            with QSignalBlocker(self.combo_clients):
                self.combo_clients.clear()

                for client in donnees:
                    libelle = (
                        f"{client['display_name']} "
                        f"({client['id'][:8]})"
                    )

                    self.combo_clients.addItem(
                        libelle,
                        client["id"]
                    )

                position = (
                    self.combo_clients.findData(
                        client_precedent
                    )
                )

                if position < 0 and donnees:
                    position = 0

                self.combo_clients.setCurrentIndex(
                    position
                )

            self.changer_client()

        elif (
            self.chemin_historique is not None
            and path == self.chemin_historique
        ):

            if not isinstance(donnees, list):
                self.etat.setText(
                    "Format d'historique invalide."
                )
                return

            self.evaluations = donnees
            self.remplir_tableau()

            self.etat.setText(
                f"{len(donnees)} évaluation(s) "
                "récupérée(s) depuis SQLite."
            )

    def gerer_erreur(self, path, message):

        if path == CLIENTS_PATH:
            self.etat.setText(
                "Impossible de charger les clients : "
                + message
            )

        elif (
            self.chemin_historique is not None
            and path == self.chemin_historique
        ):
            self.etat.setText(
                "Impossible de charger l'historique : "
                + message
            )
