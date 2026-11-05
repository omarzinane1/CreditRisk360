
import math

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QGroupBox,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QMessageBox
)

from pages.clients_page import VARIABLES


CLIENTS_PATH = "/api/v1/clients?limit=100&offset=0"
PREVIEW_PATH = "/api/v1/predictions/preview"
SAVE_PATH = "/api/v1/predictions"


class ScoringPage(QWidget):

    def __init__(self, api, parent=None):
        super().__init__(parent)

        self.api = api
        self.clients = {}
        self.champs = {}
        self.valeurs_manquantes = {}

        self.requete_active = None
        self.client_envoye = None
        self.features_envoyees = None

        self.construire_interface()

        self.api.response_received.connect(
            self.recevoir_reponse
        )

        self.api.request_failed.connect(
            self.gerer_erreur
        )

    def construire_interface(self):
        principal = QVBoxLayout(self)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(16)

        description = QLabel(
            "Évaluer le risque de défaut d'un client fictif "
            "avec le modèle E3."
        )
        description.setWordWrap(True)
        principal.addWidget(description)

        # -------------------------
        # SÉLECTION DU CLIENT
        # -------------------------
        selection = QHBoxLayout()

        selection.addWidget(QLabel("Client :"))

        self.combo_clients = QComboBox()
        self.combo_clients.setMinimumWidth(290)

        self.combo_clients.currentIndexChanged.connect(
            self.changer_client
        )

        selection.addWidget(self.combo_clients, 1)

        self.bouton_actualiser = QPushButton(
            "Actualiser les clients"
        )
        self.bouton_actualiser.setObjectName("refreshButton")

        self.bouton_actualiser.clicked.connect(
            self.charger_clients
        )

        selection.addWidget(self.bouton_actualiser)
        principal.addLayout(selection)

        self.info_profil = QLabel(
            "Sélectionne un client pour commencer."
        )
        self.info_profil.setWordWrap(True)
        principal.addWidget(self.info_profil)

        # -------------------------
        # ZONE CENTRALE
        # -------------------------
        colonnes = QHBoxLayout()
        colonnes.setSpacing(18)

        # Formulaire des 10 variables
        self.groupe_formulaire = QGroupBox(
            "Caractéristiques du client"
        )

        disposition_formulaire = QVBoxLayout(
            self.groupe_formulaire
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        contenu = QWidget()
        formulaire = QFormLayout(contenu)
        formulaire.setSpacing(13)

        for libelle, cle, type_variable, nullable in VARIABLES:

            champ = QLineEdit()
            champ.setMinimumWidth(130)

            if type_variable == "int":
                champ.setPlaceholderText(
                    "Entier positif ou nul"
                )
            else:
                champ.setPlaceholderText(
                    "Nombre positif ou nul"
                )

            champ.textEdited.connect(
                self.reinitialiser_resultat
            )

            self.champs[cle] = champ

            if nullable:
                ligne = QWidget()
                horizontal = QHBoxLayout(ligne)
                horizontal.setContentsMargins(0, 0, 0, 0)

                checkbox = QCheckBox("Manquante")

                checkbox.toggled.connect(
                    champ.setDisabled
                )
                checkbox.toggled.connect(
                    self.reinitialiser_resultat
                )

                self.valeurs_manquantes[cle] = checkbox

                horizontal.addWidget(champ, 1)
                horizontal.addWidget(checkbox)

                formulaire.addRow(libelle, ligne)

            else:
                formulaire.addRow(libelle, champ)

        scroll.setWidget(contenu)
        disposition_formulaire.addWidget(scroll)

        colonnes.addWidget(self.groupe_formulaire, 3)

        # -------------------------
        # PANNEAU DES RÉSULTATS
        # -------------------------
        resultats = QGroupBox("Résultat du scoring")
        disposition_resultats = QVBoxLayout(resultats)
        disposition_resultats.setSpacing(15)

        disposition_resultats.addWidget(
            QLabel("Score de risque estimé")
        )

        self.score_label = QLabel("—")
        self.score_label.setStyleSheet(
            "font-size: 34px; "
            "font-weight: bold; "
            "color: #1c3557;"
        )
        disposition_resultats.addWidget(
            self.score_label
        )

        disposition_resultats.addWidget(
            QLabel("Niveau de risque")
        )

        self.niveau_label = QLabel("—")
        self.niveau_label.setStyleSheet(
            "font-size: 21px; "
            "font-weight: bold;"
        )
        disposition_resultats.addWidget(
            self.niveau_label
        )

        self.details_label = QLabel(
            "Aucune prédiction effectuée."
        )
        self.details_label.setWordWrap(True)

        disposition_resultats.addWidget(
            self.details_label
        )

        self.sauvegarde_label = QLabel("")
        self.sauvegarde_label.setWordWrap(True)
        disposition_resultats.addWidget(
            self.sauvegarde_label
        )

        note = QLabel(
            "Score expérimental : il ne constitue pas "
            "une décision d'acceptation ou de refus "
            "d'un crédit."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #65758c;")
        disposition_resultats.addWidget(note)

        disposition_resultats.addStretch()

        colonnes.addWidget(resultats, 2)

        principal.addLayout(colonnes, 1)

        # -------------------------
        # BOUTONS DE SCORING
        # -------------------------
        actions = QHBoxLayout()

        self.bouton_preview = QPushButton(
            "Prévisualiser le score"
        )
        self.bouton_preview.setObjectName("refreshButton")

        self.bouton_enregistrer = QPushButton(
            "Calculer et enregistrer"
        )
        self.bouton_enregistrer.setObjectName(
            "refreshButton"
        )

        self.bouton_preview.clicked.connect(
            lambda: self.envoyer_prediction(False)
        )

        self.bouton_enregistrer.clicked.connect(
            lambda: self.envoyer_prediction(True)
        )

        actions.addWidget(self.bouton_preview)
        actions.addWidget(self.bouton_enregistrer)

        principal.addLayout(actions)

        self.etat = QLabel("")
        self.etat.setWordWrap(True)
        principal.addWidget(self.etat)

        self.changer_client()

    # -------------------------
    # CHARGEMENT DES CLIENTS
    # -------------------------
    def charger_clients(self):
        if self.requete_active is not None:
            return

        self.etat.setText(
            "Chargement des clients depuis FastAPI..."
        )

        self.api.get(CLIENTS_PATH)

    def changer_client(self, *_):
        client_id = self.combo_clients.currentData()
        client = self.clients.get(client_id)

        profil = (
            client.get("features") or {}
            if client else {}
        )

        # Recharger le profil courant du client
        for _, cle, _, nullable in VARIABLES:

            valeur = profil.get(cle)
            champ = self.champs[cle]

            champ.clear()

            if valeur is not None:
                champ.setText(str(valeur))

            if nullable:
                manquante = (
                    cle in profil
                    and valeur is None
                )

                self.valeurs_manquantes[cle].setChecked(
                    manquante
                )

        disponible = client is not None

        self.groupe_formulaire.setEnabled(disponible)
        self.bouton_preview.setEnabled(disponible)
        self.bouton_enregistrer.setEnabled(disponible)

        if disponible:
            if profil:
                self.info_profil.setText(
                    "Profil courant chargé depuis SQLite. "
                    "Tu peux modifier les valeurs pour "
                    "simuler une nouvelle évaluation."
                )
            else:
                self.info_profil.setText(
                    "Ce client n'a pas encore de profil. "
                    "Renseigne les 10 caractéristiques "
                    "avant de calculer un score."
                )
        else:
            self.info_profil.setText(
                "Aucun client sélectionné. "
                "Crée d'abord un client dans la page Clients."
            )

        self.reinitialiser_resultat()

    # -------------------------
    # VALIDATION DES VARIABLES
    # -------------------------
    def lire_caracteristiques(self):
        features = {}

        for libelle, cle, type_variable, nullable in VARIABLES:

            if (
                nullable
                and self.valeurs_manquantes[cle].isChecked()
            ):
                features[cle] = None
                continue

            texte = self.champs[cle].text().strip()

            if not texte:
                raise ValueError(
                    f"Renseigne la variable : {libelle}."
                )

            if type_variable == "int":
                if not texte.isdecimal():
                    raise ValueError(
                        f"{libelle} doit être un entier "
                        "positif ou nul."
                    )

                nombre = int(texte)

            else:
                try:
                    nombre = float(
                        texte.replace(",", ".")
                    )
                except ValueError:
                    raise ValueError(
                        f"{libelle} doit être numérique."
                    )

                if (
                    not math.isfinite(nombre)
                    or nombre < 0
                ):
                    raise ValueError(
                        f"{libelle} doit être un nombre "
                        "fini positif ou nul."
                    )

            if cle == "age" and nombre <= 0:
                raise ValueError(
                    "L'âge doit être strictement positif."
                )

            features[cle] = nombre

        return features

    # -------------------------
    # ENVOI VERS FASTAPI
    # -------------------------
    def envoyer_prediction(self, enregistrer):
        client_id = self.combo_clients.currentData()

        if not client_id:
            QMessageBox.warning(
                self,
                "Client manquant",
                "Sélectionne d'abord un client fictif."
            )
            return

        try:
            features = self.lire_caracteristiques()
        except ValueError as erreur:
            QMessageBox.warning(
                self,
                "Données invalides",
                str(erreur)
            )
            return

        if self.requete_active is not None:
            return

        if enregistrer:
            chemin = SAVE_PATH
            donnees = {
                "client_id": client_id,
                "features": features
            }
        else:
            chemin = PREVIEW_PATH
            donnees = {
                "features": features
            }

        self.requete_active = chemin
        self.client_envoye = client_id
        self.features_envoyees = features

        self.bloquer_actions(True)

        self.etat.setText(
            "Calcul du score E3 en cours..."
        )

        self.api.post(chemin, donnees)

    def bloquer_actions(self, bloque):
        self.combo_clients.setEnabled(not bloque)
        self.bouton_actualiser.setEnabled(not bloque)
        self.groupe_formulaire.setEnabled(not bloque)

        actif = (
            not bloque
            and self.combo_clients.currentData() is not None
        )

        self.bouton_preview.setEnabled(actif)
        self.bouton_enregistrer.setEnabled(actif)

    # -------------------------
    # AFFICHAGE DES RÉSULTATS
    # -------------------------
    def reinitialiser_resultat(self, *_):
        self.score_label.setText("—")
        self.niveau_label.setText("—")

        self.details_label.setText(
            "Aucune prédiction pour les valeurs actuelles."
        )

        self.sauvegarde_label.setText("")

    def afficher_resultat(self, donnees):
        score = float(donnees["risk_score"])
        niveau = donnees["risk_level"]

        self.score_label.setText(
            f"{score * 100:.2f} %"
        )

        couleurs = {
            "faible": "#16856d",
            "modéré": "#b47a14",
            "élevé": "#bf3d46"
        }

        couleur = couleurs.get(niveau, "#243247")

        self.niveau_label.setText(
            niveau.capitalize()
        )

        self.niveau_label.setStyleSheet(
            f"font-size: 21px; "
            f"font-weight: bold; "
            f"color: {couleur};"
        )

        self.details_label.setText(
            f"Modèle : {donnees['model_version']}\n"
            f"Seuils : {donnees['threshold_version']}\n"
            f"Type de score : {donnees['score_type']}"
        )

        if donnees.get("persisted"):
            self.sauvegarde_label.setText(
                "Évaluation enregistrée dans SQLite.\n"
                f"ID : {donnees['assessment_id']}\n"
                f"Date : {donnees['created_at']}"
            )

            self.etat.setText(
                "Prédiction enregistrée avec succès."
            )

        else:
            self.sauvegarde_label.setText(
                "Prévisualisation uniquement : "
                "aucune évaluation enregistrée."
            )

            self.etat.setText(
                "Score calculé sans sauvegarde."
            )

    # -------------------------
    # RÉPONSES HTTP
    # -------------------------
    def recevoir_reponse(self, path, donnees):

        if path == CLIENTS_PATH:

            if not isinstance(donnees, list):
                self.etat.setText(
                    "Format de liste des clients invalide."
                )
                return

            client_precedent = (
                self.combo_clients.currentData()
            )

            self.clients = {
                client["id"]: client
                for client in donnees
            }

            # Éviter des changements de sélection
            # pendant le remplissage du menu
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

                index = self.combo_clients.findData(
                    client_precedent
                )

                if index < 0 and donnees:
                    index = 0

                self.combo_clients.setCurrentIndex(
                    index
                )

            self.changer_client()

            self.etat.setText(
                f"{len(donnees)} client(s) chargé(s)."
            )

        elif (
            path in (PREVIEW_PATH, SAVE_PATH)
            and path == self.requete_active
        ):

            self.requete_active = None
            self.bloquer_actions(False)

            # Après une sauvegarde, le profil courant
            # du client est aussi mis à jour en SQLite
            if path == SAVE_PATH:
                client = self.clients.get(
                    self.client_envoye
                )

                if client is not None:
                    client["features"] = (
                        self.features_envoyees.copy()
                    )

            self.afficher_resultat(donnees)

    def gerer_erreur(self, path, message):

        if path == CLIENTS_PATH:
            self.etat.setText(
                "Impossible de charger les clients."
            )

            QMessageBox.warning(
                self,
                "Erreur API",
                message
            )

        elif path == self.requete_active:
            self.requete_active = None
            self.bloquer_actions(False)

            self.etat.setText(
                "Échec de la prédiction."
            )

            QMessageBox.warning(
                self,
                "Erreur de scoring",
                message
            )
