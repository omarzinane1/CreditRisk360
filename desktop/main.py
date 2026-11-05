
"""
CreditRisk360 — Application Desktop PySide6

Interface Windows connectée au Backend FastAPI dans Docker.

Pages :
1. Dashboard
2. Clients
3. Credit Scoring
4. Historique
5. Model Performance
"""

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from api_client import ApiClient

from pages.clients_page import ClientsPage
from pages.scoring_page import ScoringPage
from pages.history_page import HistoryPage
from pages.performance_page import PerformancePage
from styles import COMPONENT_STYLE


# ==========================================
# NAVIGATION
# ==========================================

PAGES = [
    "Dashboard",
    "Clients",
    "Credit Scoring",
    "Historique",
    "Model Performance",
]


# ==========================================
# STYLE DE L'APPLICATION
# ==========================================

STYLE = """
QMainWindow,
QWidget#root,
QWidget#content {
    background: #f5f7fb;
}

QLabel {
    font-family: "Segoe UI";
    color: #243247;
    font-size: 13px;
}

QFrame#sidebar {
    background: #152640;
}

QLabel#brand {
    color: white;
    font-size: 23px;
    font-weight: bold;
}

QLabel#sidebarCaption {
    color: #b8c5d8;
}

QPushButton#navButton {
    background: transparent;
    color: #c9d4e5;
    border: none;
    border-radius: 9px;
    padding: 13px;
    text-align: left;
    font-size: 14px;
}

QPushButton#navButton:hover {
    background: #29405f;
}

QPushButton#navButton:checked {
    background: #315d91;
    color: white;
    font-weight: bold;
}

QPushButton#refreshButton {
    background: #315d91;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 11px 20px;
    font-weight: bold;
}

QPushButton#refreshButton:hover {
    background: #244c7c;
}

QFrame#card {
    background: white;
    border: 1px solid #dfe6f0;
    border-radius: 12px;
}

QLabel#cardTitle {
    color: #65758c;
    font-size: 13px;
}

QLabel#cardValue {
    color: #1c3557;
    font-size: 19px;
    font-weight: bold;
}

QLabel#pageTitle {
    font-size: 25px;
    font-weight: bold;
}
"""


# ==========================================
# FENÊTRE PRINCIPALE
# ==========================================

class CreditRisk360Window(QMainWindow):

    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre
        self.setWindowTitle(
            "CreditRisk360 — Credit Scoring Desktop"
        )

        self.resize(1200, 760)
        self.setMinimumSize(900, 580)

        # ----------------------------------
        # COMMUNICATION AVEC FASTAPI
        # ----------------------------------

        self.api = ApiClient(self)

        self.api.response_received.connect(
            self.recevoir_reponse
        )

        self.api.request_failed.connect(
            self.gerer_erreur
        )

        # ----------------------------------
        # CONSTRUCTION DE L'INTERFACE
        # ----------------------------------

        self.construire_interface()

        # Vérification automatique au démarrage
        QTimer.singleShot(
            100,
            self.actualiser
        )

    # ======================================
    # CONSTRUIRE L'INTERFACE
    # ======================================

    def construire_interface(self):

        root = QWidget()
        root.setObjectName("root")

        self.setCentralWidget(root)

        principal = QHBoxLayout(root)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        # ==================================
        # MENU LATÉRAL
        # ==================================

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)

        menu = QVBoxLayout(sidebar)
        menu.setContentsMargins(18, 30, 18, 22)
        menu.setSpacing(9)

        # Logo / titre
        brand = QLabel("CreditRisk360")
        brand.setObjectName("brand")

        menu.addWidget(brand)

        caption = QLabel("Credit Scoring Platform")
        caption.setObjectName("sidebarCaption")

        menu.addWidget(caption)
        menu.addSpacing(35)

        # Groupe des boutons de navigation
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.nav_buttons = []

        for index, nom in enumerate(PAGES):

            bouton = QPushButton(nom)

            bouton.setObjectName("navButton")
            bouton.setCheckable(True)

            bouton.clicked.connect(
                lambda checked=False, i=index:
                    self.afficher_page(i)
            )

            self.nav_group.addButton(bouton)
            self.nav_buttons.append(bouton)

            menu.addWidget(bouton)

        # Dashboard sélectionné au démarrage
        self.nav_buttons[0].setChecked(True)

        menu.addStretch()

        footer = QLabel(
            "Prototype académique\n"
            "Données fictives uniquement"
        )

        footer.setObjectName("sidebarCaption")
        menu.addWidget(footer)

        principal.addWidget(sidebar)

        # ==================================
        # CONTENU PRINCIPAL
        # ==================================

        content = QWidget()
        content.setObjectName("content")

        zone = QVBoxLayout(content)
        zone.setContentsMargins(30, 25, 30, 25)
        zone.setSpacing(22)

        # ----------------------------------
        # BARRE SUPÉRIEURE
        # ----------------------------------

        header = QHBoxLayout()

        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("pageTitle")

        self.status_label = QLabel(
            "● Vérification API..."
        )

        self.status_label.setStyleSheet(
            "color: #7b8797; font-weight: bold;"
        )

        refresh_button = QPushButton("Actualiser")
        refresh_button.setObjectName("refreshButton")

        refresh_button.clicked.connect(
            self.actualiser
        )

        header.addWidget(self.page_title)
        header.addStretch()
        header.addWidget(self.status_label)
        header.addSpacing(15)
        header.addWidget(refresh_button)

        zone.addLayout(header)

        # ==================================
        # CRÉATION DES CINQ PAGES
        # ==================================

        self.stack = QStackedWidget()

        # PAGE 0 : Dashboard
        self.stack.addWidget(
            self.construire_dashboard()
        )

        # PAGE 1 : Clients
        self.clients_page = ClientsPage(
            self.api,
            self
        )

        self.stack.addWidget(
            self.clients_page
        )

        # PAGE 2 : Credit Scoring
        self.scoring_page = ScoringPage(
            self.api,
            self
        )

        self.stack.addWidget(
            self.scoring_page
        )

        # PAGE 3 : Historique
        self.history_page = HistoryPage(
            self.api,
            self
        )

        self.stack.addWidget(
            self.history_page
        )

        # PAGE 4 : Model Performance
        self.performance_page = PerformancePage(
            self.api,
            self
        )

        self.stack.addWidget(
            self.performance_page
        )

        # Ajout des pages dans la fenêtre
        zone.addWidget(self.stack)

        principal.addWidget(
            content,
            1
        )

    # ======================================
    # CRÉER UNE CARTE DU DASHBOARD
    # ======================================

    def creer_carte(self, titre):

        frame = QFrame()
        frame.setObjectName("card")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        titre_label = QLabel(titre)
        titre_label.setObjectName("cardTitle")

        valeur_label = QLabel("En attente...")
        valeur_label.setObjectName("cardValue")
        valeur_label.setWordWrap(True)

        layout.addWidget(titre_label)
        layout.addWidget(valeur_label)

        return frame, valeur_label

    # ======================================
    # PAGE DASHBOARD
    # ======================================

    def construire_dashboard(self):

        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        intro = QLabel(
            "Vue générale de la plateforme CreditRisk360"
        )

        layout.addWidget(intro)

        # ----------------------------------
        # CARTES D'ÉTAT DU BACKEND
        # ----------------------------------

        cartes = QHBoxLayout()
        cartes.setSpacing(16)

        self.valeurs_dashboard = {}

        definitions = [
            ("api", "Backend FastAPI"),
            ("model", "Modèle E3"),
            ("db", "Base SQLite"),
        ]

        for identifiant, titre in definitions:

            carte, valeur = self.creer_carte(titre)

            self.valeurs_dashboard[
                identifiant
            ] = valeur

            cartes.addWidget(carte)

        layout.addLayout(cartes)

        # ----------------------------------
        # AVERTISSEMENT ACADÉMIQUE
        # ----------------------------------

        note = QLabel(
            "Les scores sont des estimations expérimentales "
            "destinées à la démonstration académique, "
            "et non à une décision réelle d'octroi de crédit."
        )

        note.setWordWrap(True)

        layout.addWidget(note)
        layout.addStretch()

        return page

    # ======================================
    # NAVIGATION ENTRE LES PAGES
    # ======================================

    def afficher_page(self, index):

        self.stack.setCurrentIndex(index)
        self.page_title.setText(PAGES[index])

        # PAGE CLIENTS
        if index == 1:

            self.clients_page.charger_clients()

        # PAGE CREDIT SCORING
        elif index == 2:

            self.scoring_page.charger_clients()

        # PAGE HISTORIQUE
        elif index == 3:

            self.history_page.charger_clients()

        # PAGE MODEL PERFORMANCE
        elif index == 4:

            self.performance_page.charger_donnees()

    # ======================================
    # BOUTON ACTUALISER
    # ======================================

    def actualiser(self):

        self.status_label.setText(
            "● Vérification API..."
        )

        self.status_label.setStyleSheet(
            "color: #7b8797; font-weight: bold;"
        )

        # Vérification de FastAPI et SQLite
        self.api.get("/health")

        # Récupération de la version E3
        self.api.get("/api/v1/model")

        # Actualiser également la page courante
        index = self.stack.currentIndex()

        if index == 1:

            self.clients_page.charger_clients()

        elif index == 2:

            self.scoring_page.charger_clients()

        elif index == 3:

            self.history_page.charger_clients()

        elif index == 4:

            self.performance_page.charger_donnees()

    # ======================================
    # RÉPONSES HTTP
    # ======================================

    def recevoir_reponse(self, path, donnees):

        # ----------------------------------
        # GET /health
        # ----------------------------------

        if path == "/health":

            pret = (
                isinstance(donnees, dict)
                and donnees.get("status") == "ok"
                and donnees.get("model_loaded") is True
                and donnees.get("db_ok") is True
            )

            if pret:

                self.status_label.setText(
                    "● API connectée"
                )

                self.status_label.setStyleSheet(
                    "color: #16856d; font-weight: bold;"
                )

                self.valeurs_dashboard["api"].setText(
                    "En ligne"
                )

                self.valeurs_dashboard["db"].setText(
                    "Opérationnelle"
                )

            else:

                self.status_label.setText(
                    "● API non prête"
                )

                self.status_label.setStyleSheet(
                    "color: #c77719; font-weight: bold;"
                )

                self.valeurs_dashboard["api"].setText(
                    "Non prête"
                )

                self.valeurs_dashboard["db"].setText(
                    "À vérifier"
                )

        # ----------------------------------
        # GET /api/v1/model
        # ----------------------------------

        elif (
            path == "/api/v1/model"
            and isinstance(donnees, dict)
        ):

            version = donnees.get(
                "model_version",
                "Inconnue"
            )

            self.valeurs_dashboard["model"].setText(
                str(version)
            )

        # Les métriques sont maintenant traitées
        # directement par PerformancePage.
        #
        # Aucune utilisation de self.metrics_box.

    # ======================================
    # GESTION DES ERREURS
    # ======================================

    def gerer_erreur(self, path, message):

        # ----------------------------------
        # BACKEND INDISPONIBLE
        # ----------------------------------

        if path == "/health":

            self.status_label.setText(
                "● API déconnectée"
            )

            self.status_label.setStyleSheet(
                "color: #bf3d46; font-weight: bold;"
            )

            self.valeurs_dashboard["api"].setText(
                "Indisponible"
            )

            self.valeurs_dashboard["model"].setText(
                "Non vérifié"
            )

            self.valeurs_dashboard["db"].setText(
                "Non vérifiée"
            )

        # ----------------------------------
        # INFORMATIONS DU MODÈLE INDISPONIBLES
        # ----------------------------------

        elif path == "/api/v1/model":

            self.valeurs_dashboard["model"].setText(
                "Indisponible"
            )


# ==========================================
# DÉMARRAGE DE L'APPLICATION
# ==========================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    # Style principal + style commun des composants
    app.setStyleSheet(STYLE + "\n" + COMPONENT_STYLE)

    fenetre = CreditRisk360Window()
    fenetre.show()

    sys.exit(app.exec())
