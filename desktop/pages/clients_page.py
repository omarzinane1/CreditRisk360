
import json

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import (
    QWidget,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QGroupBox,
    QScrollArea,
    QSpinBox,
    QDoubleSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QPlainTextEdit,
    QMessageBox
)


# ==========================================
# CONFIGURATION DE L'API
# ==========================================

CLIENTS_PATH = "/api/v1/clients"
LIST_PATH = "/api/v1/clients?limit=100&offset=0"


# ==========================================
# VARIABLES DU MODÈLE E3
# ==========================================

# Cette liste est également utilisée par
# scoring_page.py et history_page.py.

VARIABLES = [
    (
        "Utilisation du crédit",
        "RevolvingUtilizationOfUnsecuredLines",
        "float",
        False
    ),
    (
        "Âge",
        "age",
        "int",
        False
    ),
    (
        "Retards de 30 à 59 jours",
        "NumberOfTime30-59DaysPastDueNotWorse",
        "int",
        False
    ),
    (
        "Ratio d'endettement",
        "DebtRatio",
        "float",
        False
    ),
    (
        "Revenu mensuel",
        "MonthlyIncome",
        "float",
        True
    ),
    (
        "Lignes de crédit et prêts",
        "NumberOfOpenCreditLinesAndLoans",
        "int",
        False
    ),
    (
        "Retards de 90 jours",
        "NumberOfTimes90DaysLate",
        "int",
        False
    ),
    (
        "Prêts immobiliers",
        "NumberRealEstateLoansOrLines",
        "int",
        False
    ),
    (
        "Retards de 60 à 89 jours",
        "NumberOfTime60-89DaysPastDueNotWorse",
        "int",
        False
    ),
    (
        "Personnes à charge",
        "NumberOfDependents",
        "int",
        True
    )
]


# ==========================================
# FORMULAIRE CLIENT
# ==========================================

class ClientDialog(QDialog):

    def __init__(self, parent=None, client=None):
        super().__init__(parent)

        self.client = client
        self.payload = None

        self.champs = {}
        self.valeurs_manquantes = {}

        if client is None:
            self.setWindowTitle("Nouveau client fictif")
        else:
            self.setWindowTitle("Modifier un client fictif")

        self.resize(650, 590)
        self.setMinimumWidth(540)

        # ----------------------------------
        # LAYOUT PRINCIPAL
        # ----------------------------------

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        information = QLabel(
            "Gestion des clients de démonstration. "
            "Utiliser uniquement des données fictives."
        )
        information.setWordWrap(True)

        layout.addWidget(information)

        # ----------------------------------
        # NOM DU CLIENT
        # ----------------------------------

        layout.addWidget(QLabel("Nom du client"))

        self.nom = QLineEdit()
        self.nom.setFixedHeight(38)

        self.nom.setPlaceholderText(
            "Exemple : Client fictif CR-002"
        )

        if client is not None:
            self.nom.setText(
                client.get("display_name", "")
            )

        layout.addWidget(self.nom)

        # ----------------------------------
        # ACTIVER LE FORMULAIRE FINANCIER
        # ----------------------------------

        self.modifier_profil = QCheckBox(
            "Saisir ou modifier les 10 caractéristiques"
        )

        layout.addWidget(self.modifier_profil)

        # ----------------------------------
        # GROUPE DES CARACTÉRISTIQUES
        # ----------------------------------

        groupe = QGroupBox(
            "Profil de crédit fictif"
        )

        groupe_layout = QVBoxLayout(groupe)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(300)

        contenu = QWidget()
        formulaire = QFormLayout(contenu)
        formulaire.setSpacing(12)

        profil = (
            client.get("features") or {}
            if client is not None
            else {}
        )

        # ----------------------------------
        # CONSTRUCTION DES 10 CHAMPS
        # ----------------------------------

        for (
            libelle,
            cle,
            type_variable,
            nullable
        ) in VARIABLES:

            if type_variable == "int":

                champ = QSpinBox()

                minimum = (
                    1 if cle == "age" else 0
                )

                champ.setRange(
                    minimum,
                    999999
                )

            else:

                champ = QDoubleSpinBox()

                champ.setRange(
                    0,
                    1000000000
                )

                champ.setDecimals(6)
                champ.setSingleStep(0.01)

            # Valeur précédemment enregistrée
            valeur = profil.get(cle)

            if valeur is not None:
                champ.setValue(valeur)

            elif cle == "age":
                champ.setValue(35)

            self.champs[cle] = champ

            # ----------------------------------
            # VARIABLES POUVANT ÊTRE MANQUANTES
            # ----------------------------------

            if nullable:

                ligne = QWidget()

                horizontal = QHBoxLayout(ligne)

                horizontal.setContentsMargins(
                    0, 0, 0, 0
                )

                manquante = QCheckBox(
                    "Manquante"
                )

                manquante.setChecked(
                    valeur is None
                )

                champ.setDisabled(
                    manquante.isChecked()
                )

                manquante.toggled.connect(
                    champ.setDisabled
                )

                self.valeurs_manquantes[
                    cle
                ] = manquante

                horizontal.addWidget(
                    champ, 1
                )

                horizontal.addWidget(
                    manquante
                )

                formulaire.addRow(
                    libelle,
                    ligne
                )

            else:

                formulaire.addRow(
                    libelle,
                    champ
                )

        scroll.setWidget(contenu)

        groupe_layout.addWidget(scroll)

        layout.addWidget(groupe)

        # Les éléments restent en haut du formulaire.
        # L'espace disponible est placé avant les boutons.
        layout.addStretch(1)

        # Profil masqué par défaut
        groupe.setVisible(False)

        self.modifier_profil.toggled.connect(
            groupe.setVisible
        )

        # ----------------------------------
        # BOUTONS DE VALIDATION
        # ----------------------------------

        boutons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        boutons.accepted.connect(
            self.valider
        )

        boutons.rejected.connect(
            self.reject
        )

        layout.addWidget(boutons)

    # ======================================
    # VALIDATION DU FORMULAIRE
    # ======================================

    def valider(self):

        nom = self.nom.text().strip()

        if not 2 <= len(nom) <= 80:

            QMessageBox.warning(
                self,
                "Nom invalide",
                "Le nom doit contenir entre "
                "2 et 80 caractères."
            )

            return

        payload = {
            "display_name": nom
        }

        # Ajouter les variables seulement
        # si l'utilisateur le demande.

        if self.modifier_profil.isChecked():

            features = {}

            for (
                libelle,
                cle,
                type_variable,
                nullable
            ) in VARIABLES:

                if (
                    nullable
                    and self.valeurs_manquantes[
                        cle
                    ].isChecked()
                ):

                    features[cle] = None

                else:

                    features[cle] = (
                        self.champs[cle].value()
                    )

            payload["features"] = features

        self.payload = payload

        self.accept()


# ==========================================
# PAGE CLIENTS
# ==========================================

class ClientsPage(QWidget):

    def __init__(self, api, parent=None):
        super().__init__(parent)

        self.api = api

        # Clients chargés depuis SQLite
        self.clients = []

        # CORRECTION :
        # mémoriser uniquement la requête PATCH
        # réellement envoyée par cette page.
        self.pending_patch_path = None

        self.construire_interface()

        # Signaux HTTP partagés avec les autres pages
        self.api.response_received.connect(
            self.recevoir_reponse
        )

        self.api.request_failed.connect(
            self.gerer_erreur
        )

    # ======================================
    # INTERFACE GRAPHIQUE
    # ======================================

    def construire_interface(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0, 0, 0, 0
        )

        layout.setSpacing(15)

        description = QLabel(
            "Gérer les clients fictifs et "
            "leurs caractéristiques de crédit."
        )

        description.setWordWrap(True)

        layout.addWidget(description)

        # ----------------------------------
        # BARRE DES ACTIONS
        # ----------------------------------

        actions = QHBoxLayout()

        self.nombre_clients = QLabel(
            "Clients : —"
        )

        bouton_ajouter = QPushButton(
            "Ajouter un client"
        )

        bouton_modifier = QPushButton(
            "Modifier le client"
        )

        bouton_actualiser = QPushButton(
            "Actualiser"
        )

        for bouton in (
            bouton_ajouter,
            bouton_modifier,
            bouton_actualiser
        ):
            bouton.setObjectName(
                "refreshButton"
            )

        bouton_ajouter.clicked.connect(
            self.ajouter_client
        )

        bouton_modifier.clicked.connect(
            self.modifier_client
        )

        bouton_actualiser.clicked.connect(
            self.charger_clients
        )

        actions.addWidget(
            self.nombre_clients
        )

        actions.addStretch()

        actions.addWidget(
            bouton_ajouter
        )

        actions.addWidget(
            bouton_modifier
        )

        actions.addWidget(
            bouton_actualiser
        )

        layout.addLayout(actions)

        # ----------------------------------
        # TABLEAU DES CLIENTS
        # ----------------------------------

        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "Nom fictif",
            "Identifiant",
            "Profil",
            "Créé le",
            "Mis à jour"
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

        self.table.setAlternatingRowColors(
            True
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch
        )

        self.table.itemSelectionChanged.connect(
            self.afficher_details
        )

        layout.addWidget(
            self.table, 2
        )

        # ----------------------------------
        # DÉTAILS DU CLIENT
        # ----------------------------------

        layout.addWidget(
            QLabel(
                "Détails du client sélectionné"
            )
        )

        self.details = QPlainTextEdit()

        self.details.setReadOnly(True)

        self.details.setMaximumHeight(210)

        self.details.setPlaceholderText(
            "Sélectionne un client dans le tableau."
        )

        layout.addWidget(
            self.details, 1
        )

        # ----------------------------------
        # MESSAGE D'ÉTAT
        # ----------------------------------

        self.etat = QLabel("")

        self.etat.setWordWrap(True)

        layout.addWidget(
            self.etat
        )

    # ======================================
    # CHARGEMENT DES CLIENTS
    # ======================================

    def charger_clients(self):

        self.etat.setText(
            "Chargement des clients..."
        )

        self.api.get(
            LIST_PATH
        )

    # ======================================
    # CLIENT SÉLECTIONNÉ
    # ======================================

    def client_selectionne(self):

        ligne = self.table.currentRow()

        if 0 <= ligne < len(self.clients):
            return self.clients[ligne]

        return None

    # ======================================
    # AFFICHER LES DÉTAILS
    # ======================================

    def afficher_details(self):

        client = self.client_selectionne()

        if client is None:
            self.details.clear()
            return

        self.details.setPlainText(
            json.dumps(
                client,
                indent=2,
                ensure_ascii=False
            )
        )

    # ======================================
    # AJOUTER UN CLIENT
    # ======================================

    def ajouter_client(self):

        dialogue = ClientDialog(self)

        if (
            dialogue.exec()
            == QDialog.DialogCode.Accepted
        ):

            self.etat.setText(
                "Création du client en cours..."
            )

            self.api.post(
                CLIENTS_PATH,
                dialogue.payload
            )

    # ======================================
    # MODIFIER UN CLIENT
    # ======================================

    def modifier_client(self):

        client = self.client_selectionne()

        if client is None:

            QMessageBox.information(
                self,
                "Sélection requise",
                "Sélectionne d'abord un client."
            )

            return

        dialogue = ClientDialog(
            self,
            client=client
        )

        if (
            dialogue.exec()
            == QDialog.DialogCode.Accepted
        ):

            # CORRECTION :
            # on conserve le chemin exact du PATCH.
            chemin = (
                f"{CLIENTS_PATH}/{client['id']}"
            )

            self.pending_patch_path = chemin

            self.etat.setText(
                "Modification du client en cours..."
            )

            self.api.patch(
                chemin,
                dialogue.payload
            )

    # ======================================
    # GESTION DES RÉPONSES HTTP
    # ======================================

    def recevoir_reponse(self, path, donnees):

        # ----------------------------------
        # GET /api/v1/clients
        # ----------------------------------

        if path == LIST_PATH:

            if not isinstance(donnees, list):
                self.etat.setText(
                    "Réponse invalide : liste attendue."
                )
                return

            self.clients = donnees

            # Empêcher les signaux de sélection
            # pendant le remplissage du tableau.
            with QSignalBlocker(self.table):

                self.table.setRowCount(0)

                self.table.setRowCount(
                    len(self.clients)
                )

                for ligne, client in enumerate(
                    self.clients
                ):

                    profil = client.get("features")

                    colonnes = [
                        client["display_name"],
                        client["id"][:8] + "...",
                        (
                            "Complet"
                            if profil is not None
                            else "Non renseigné"
                        ),
                        client["created_at"][:19],
                        client["updated_at"][:19]
                    ]

                    for colonne, valeur in enumerate(
                        colonnes
                    ):

                        cellule = QTableWidgetItem(
                            str(valeur)
                        )

                        self.table.setItem(
                            ligne,
                            colonne,
                            cellule
                        )

                if self.clients:
                    self.table.selectRow(0)

            self.nombre_clients.setText(
                f"Clients : {len(self.clients)}"
            )

            self.etat.setText(
                "Liste des clients actualisée."
            )

            # Mise à jour des détails après
            # le remplissage du tableau.
            self.afficher_details()

        # ----------------------------------
        # POST /api/v1/clients
        # ----------------------------------

        elif path == CLIENTS_PATH:

            QMessageBox.information(
                self,
                "Client créé",
                "Le client fictif a été "
                "enregistré dans SQLite."
            )

            self.charger_clients()

        # ----------------------------------
        # PATCH /api/v1/clients/{id}
        # ----------------------------------

        elif (
            self.pending_patch_path is not None
            and path == self.pending_patch_path
        ):

            # CORRECTION :
            # seul le PATCH lancé par cette page
            # déclenche le message de modification.

            self.pending_patch_path = None

            QMessageBox.information(
                self,
                "Client modifié",
                "Les modifications du client "
                "ont été enregistrées."
            )

            self.charger_clients()

        # Toutes les autres réponses sont ignorées.
        #
        # Par exemple :
        # GET /api/v1/clients/{id}/assessments
        #
        # Cette requête appartient à HistoryPage
        # et ne doit pas afficher "Client modifié".

    # ======================================
    # GESTION DES ERREURS HTTP
    # ======================================

    def gerer_erreur(self, path, message):

        # La page ne traite que les erreurs de :
        # - GET liste des clients
        # - POST création de client
        # - PATCH réellement lancé par cette page

        chemins_autorises = (
            LIST_PATH,
            CLIENTS_PATH,
            self.pending_patch_path
        )

        if path not in chemins_autorises:
            return

        # Réinitialisation si le PATCH a échoué
        if (
            self.pending_patch_path is not None
            and path == self.pending_patch_path
        ):
            self.pending_patch_path = None

        self.etat.setText(
            "Erreur de communication avec FastAPI."
        )

        QMessageBox.warning(
            self,
            "Erreur API",
            message
        )
