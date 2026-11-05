
from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QProgressBar,
    QScrollArea,
)


# ==========================================
# CONFIGURATION API
# ==========================================

METRICS_PATH = "/api/v1/model/metrics"
MODEL_PATH = "/api/v1/model"


# ==========================================
# MÉTRIQUES À AFFICHER
# ==========================================

METRIQUES = [
    ("Accuracy", "Accuracy"),
    ("Recall", "Recall (classe 1)"),
    ("Precision", "Precision (classe 1)"),
    ("F1-score", "F1 (classe 1)"),
    ("ROC-AUC", "ROC-AUC"),
    ("Average Precision", "Average Precision"),
]


# ==========================================
# FONCTIONS DE FORMATAGE
# ==========================================

def pourcentage(valeur):
    if valeur is None:
        return "—"
    return f"{float(valeur) * 100:.2f} %"


def decimal(valeur):
    if valeur is None:
        return "—"
    return f"{float(valeur):.4f}"


def entier(valeur):
    if valeur is None:
        return "—"
    return f"{int(valeur):,}".replace(",", " ")


# ==========================================
# PAGE MODEL PERFORMANCE
# ==========================================

class PerformancePage(QWidget):

    def __init__(self, api, parent=None):
        super().__init__(parent)

        self.api = api

        self.metrics = {}
        self.metadata = {}

        # Construire l'interface
        self.construire_interface()

        # Connexion aux réponses HTTP
        self.api.response_received.connect(
            self.recevoir_reponse
        )

        self.api.request_failed.connect(
            self.gerer_erreur
        )

    # ======================================
    # CONSTRUCTION DE L'INTERFACE
    # ======================================

    def construire_interface(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # ----------------------------------
        # EN-TÊTE
        # ----------------------------------

        entete = QHBoxLayout()

        explication = QLabel(
            "Résultats scientifiques exportés depuis "
            "le notebook E3. Les mesures sont historiques "
            "et ne sont pas recalculées sur les clients fictifs."
        )

        explication.setWordWrap(True)

        entete.addWidget(explication, 1)

        bouton = QPushButton("Actualiser")
        bouton.setObjectName("refreshButton")

        bouton.clicked.connect(
            self.charger_donnees
        )

        entete.addWidget(bouton)

        layout.addLayout(entete)

        # ----------------------------------
        # VERSION DU MODÈLE
        # ----------------------------------

        self.versions = QLabel(
            "Modèle : —   |   Seuils : —"
        )

        self.versions.setStyleSheet(
            "font-weight: bold; color: #315d91;"
        )

        layout.addWidget(self.versions)

        self.seuils = QLabel(
            "Seuils de risque : —"
        )

        self.seuils.setWordWrap(True)

        layout.addWidget(self.seuils)

        # ==================================
        # ONGLETS
        # ==================================

        self.onglets = QTabWidget()
        layout.addWidget(self.onglets, 1)

        # ==================================
        # ONGLET 1 : VALIDATION / TEST
        # ==================================

        page_mesures = QWidget()

        mesures_layout = QVBoxLayout(
            page_mesures
        )

        mesures_layout.setSpacing(13)

        # Choix Validation ou Test
        choix = QHBoxLayout()

        choix.addWidget(
            QLabel("Jeu évalué :")
        )

        self.jeu = QComboBox()

        self.jeu.addItem(
            "Validation",
            "validation"
        )

        self.jeu.addItem(
            "Test",
            "test"
        )

        self.jeu.currentIndexChanged.connect(
            self.actualiser_mesures
        )

        choix.addWidget(self.jeu)
        choix.addStretch()

        mesures_layout.addLayout(choix)

        # ----------------------------------
        # CARTES DES MÉTRIQUES
        # ----------------------------------

        cartes = QGridLayout()
        cartes.setSpacing(10)

        self.cartes = {}

        for i, (titre, cle) in enumerate(
            METRIQUES
        ):

            carte = QFrame()
            carte.setObjectName("card")

            contenu = QVBoxLayout(carte)

            nom = QLabel(titre)
            nom.setObjectName("cardTitle")

            valeur = QLabel("—")
            valeur.setObjectName("cardValue")

            contenu.addWidget(nom)
            contenu.addWidget(valeur)

            self.cartes[cle] = valeur

            cartes.addWidget(
                carte,
                i // 3,
                i % 3
            )

        mesures_layout.addLayout(cartes)

        # ----------------------------------
        # SCORE DE BRIER
        # ----------------------------------

        self.brier = QLabel(
            "Score de Brier : —"
        )

        mesures_layout.addWidget(self.brier)

        # ----------------------------------
        # MATRICE DE CONFUSION
        # ----------------------------------

        titre_confusion = QLabel(
            "Matrice de confusion — "
            "lignes réelles, colonnes prédites"
        )

        mesures_layout.addWidget(titre_confusion)

        self.confusion = self.creer_tableau(
            [
                "Prédit 0 (sans défaut)",
                "Prédit 1 (défaut)"
            ],
            [
                "Réel 0",
                "Réel 1"
            ]
        )

        self.confusion.setFixedHeight(115)

        mesures_layout.addWidget(
            self.confusion
        )

        # ----------------------------------
        # RÉPARTITION PAR NIVEAU DE RISQUE
        # ----------------------------------

        mesures_layout.addWidget(
            QLabel(
                "Répartition par niveau de risque"
            )
        )

        self.repartition = self.creer_tableau([
            "Niveau",
            "Clients",
            "Défauts",
            "Taux de défaut",
            "% des clients"
        ])

        self.repartition.setFixedHeight(145)

        mesures_layout.addWidget(
            self.repartition
        )

        note = QLabel(
            "Un rappel élevé permet de détecter "
            "davantage de défauts, mais peut entraîner "
            "plus de fausses alertes."
        )

        note.setWordWrap(True)

        mesures_layout.addWidget(note)
        mesures_layout.addStretch()

        self.onglets.addTab(
            self.defilable(page_mesures),
            "Validation / Test"
        )

        # ==================================
        # ONGLET 2 : COMPARAISON E1 E2 E3
        # ==================================

        comparaison_page = QWidget()

        comparaison_layout = QVBoxLayout(
            comparaison_page
        )

        comparaison_layout.setSpacing(13)

        note_comparaison = QLabel(
            "Comparaison des expériences au seuil "
            "commun 0,5. Ces résultats ne représentent "
            "pas les performances du seuil final thresholds-v2."
        )

        note_comparaison.setWordWrap(True)

        comparaison_layout.addWidget(
            note_comparaison
        )

        # Tableau de comparaison
        self.comparaison = self.creer_tableau([
            "Expérience",
            "Recall",
            "Precision",
            "F1",
            "AP",
            "ROC-AUC",
            "Accuracy"
        ])

        self.comparaison.setFixedHeight(160)

        comparaison_layout.addWidget(
            self.comparaison
        )

        comparaison_layout.addWidget(
            QLabel(
                "Recall des expériences (seuil 0,5)"
            )
        )

        # Barres comparatives
        self.barres = {}

        experiences = [
            "E1 - Baseline",
            "E2 - class_weight",
            "E3 - SMOTE"
        ]

        for nom in experiences:

            ligne = QHBoxLayout()

            titre = QLabel(nom)
            titre.setMinimumWidth(145)

            barre = QProgressBar()
            barre.setRange(0, 1000)
            barre.setValue(0)
            barre.setFormat("—")

            ligne.addWidget(titre)
            ligne.addWidget(barre, 1)

            comparaison_layout.addLayout(
                ligne
            )

            self.barres[nom] = barre

        comparaison_layout.addStretch()

        self.onglets.addTab(
            comparaison_page,
            "E1 / E2 / E3"
        )

        # ==================================
        # ONGLET 3 : CALIBRATION
        # ==================================

        calibration_page = QWidget()

        calibration_layout = QVBoxLayout(
            calibration_page
        )

        calibration_layout.setSpacing(13)

        calibration_layout.addWidget(
            QLabel(
                "Calibration sur la validation"
            )
        )

        self.calibration = self.creer_tableau([
            "Méthode",
            "Score moyen prédit",
            "Taux observé",
            "Brier"
        ])

        self.calibration.setMinimumHeight(180)

        calibration_layout.addWidget(
            self.calibration
        )

        # Intervalles de confiance
        calibration_layout.addWidget(
            QLabel(
                "Intervalles de confiance "
                "exportés sur le test"
            )
        )

        self.intervalles = self.creer_tableau([
            "Métrique",
            "Borne basse",
            "Borne haute"
        ])

        self.intervalles.setMinimumHeight(130)

        calibration_layout.addWidget(
            self.intervalles
        )

        avertissement = QLabel(
            "Le score corrigé reste une estimation "
            "approximative : la correction de prévalence "
            "ne garantit pas une calibration parfaite. "
            "Le jeu de test ayant déjà été consulté "
            "pendant le projet, ses résultats sont "
            "descriptifs et ne constituent pas une "
            "nouvelle évaluation indépendante."
        )

        avertissement.setWordWrap(True)

        calibration_layout.addWidget(
            avertissement
        )

        calibration_layout.addStretch()

        self.onglets.addTab(
            calibration_page,
            "Calibration et incertitude"
        )

        # ==================================
        # MESSAGE D'ÉTAT
        # ==================================

        # IMPORTANT : ce label était absent
        # dans ton code précédent.

        self.etat = QLabel(
            "Ouvre la page pour charger les métriques."
        )

        self.etat.setWordWrap(True)

        layout.addWidget(self.etat)

    # ======================================
    # OUTILS POUR LES TABLEAUX
    # ======================================

    @staticmethod
    def defilable(widget):

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        scroll.setWidget(widget)

        return scroll

    @staticmethod
    def creer_tableau(entetes, lignes=None):

        table = QTableWidget()

        table.setColumnCount(
            len(entetes)
        )

        table.setHorizontalHeaderLabels(
            entetes
        )

        if lignes:

            table.setRowCount(
                len(lignes)
            )

            table.setVerticalHeaderLabels(
                lignes
            )

        else:

            table.verticalHeader().setVisible(
                False
            )

        table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        table.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )

        table.setAlternatingRowColors(True)
        table.setSortingEnabled(False)

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        return table

    @staticmethod
    def remplir(table, lignes):

        table.setRowCount(
            len(lignes)
        )

        for i, valeurs in enumerate(lignes):

            for j, valeur in enumerate(valeurs):

                item = QTableWidgetItem(
                    str(valeur)
                )

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                table.setItem(
                    i,
                    j,
                    item
                )

    # ======================================
    # CHARGEMENT DEPUIS FASTAPI
    # ======================================

    def charger_donnees(self):

        self.etat.setText(
            "Chargement des performances "
            "depuis FastAPI..."
        )

        self.api.get(MODEL_PATH)
        self.api.get(METRICS_PATH)

    # ======================================
    # RÉPONSES HTTP
    # ======================================

    def recevoir_reponse(self, path, donnees):

        # Informations du modèle
        if path == MODEL_PATH:

            if isinstance(donnees, dict):

                self.metadata = donnees

                self.actualiser_seuils()

        # Métriques scientifiques
        elif path == METRICS_PATH:

            if (
                not isinstance(donnees, dict)
                or not isinstance(
                    donnees.get("metrics"),
                    dict
                )
            ):

                self.etat.setText(
                    "Réponse des métriques invalide."
                )

                return

            self.metrics = donnees["metrics"]

            self.versions.setText(
                f"Modèle : "
                f"{donnees.get('model_version', '—')}"
                "   |   "
                f"Seuils : "
                f"{donnees.get('threshold_version', '—')}"
            )

            # Actualiser les trois onglets
            self.actualiser_mesures()
            self.actualiser_comparaison()
            self.actualiser_calibration()

            self.etat.setText(
                "Métriques E3 chargées depuis Docker."
            )

    # ======================================
    # ERREURS API
    # ======================================

    def gerer_erreur(self, path, message):

        if path in (MODEL_PATH, METRICS_PATH):

            self.etat.setText(
                f"Erreur API ({path}) : {message}"
            )

    # ======================================
    # AFFICHER LES SEUILS
    # ======================================

    def actualiser_seuils(self):

        seuils = self.metadata.get(
            "thresholds",
            {}
        )

        if not isinstance(seuils, dict):
            return

        self.seuils.setText(
            "Faible / modéré : "
            + pourcentage(
                seuils.get("faible_modere")
            )
            + "   |   Modéré / élevé : "
            + pourcentage(
                seuils.get("modere_eleve")
            )
            + "   |   Seuil de décision : "
            + pourcentage(
                seuils.get("decision")
            )
        )

    # ======================================
    # AFFICHER VALIDATION / TEST
    # ======================================

    def actualiser_mesures(self, *_):

        jeu = self.jeu.currentData()

        valeurs = self.metrics.get(
            jeu,
            {}
        )

        if not isinstance(valeurs, dict):
            valeurs = {}

        # Cartes des métriques
        for titre, cle in METRIQUES:

            valeur = valeurs.get(cle)

            if cle in (
                "ROC-AUC",
                "Average Precision"
            ):

                resultat = decimal(valeur)

            else:

                resultat = pourcentage(valeur)

            self.cartes[cle].setText(
                resultat
            )

        # Score de Brier
        self.brier.setText(
            "Score de Brier : "
            + decimal(
                valeurs.get("Score de Brier")
            )
        )

        # ----------------------------------
        # MATRICE DE CONFUSION
        # ----------------------------------

        self.remplir(
            self.confusion,
            [
                [
                    entier(valeurs.get("VN")),
                    entier(valeurs.get("FP"))
                ],
                [
                    entier(valeurs.get("FN")),
                    entier(valeurs.get("VP"))
                ]
            ]
        )

        # ----------------------------------
        # NIVEAUX DE RISQUE
        # ----------------------------------

        niveaux = self.metrics.get(
            "niveaux_risque_" + jeu,
            {}
        )

        if not isinstance(niveaux, dict):
            niveaux = {}

        lignes = []

        for nom in (
            "faible",
            "modéré",
            "élevé"
        ):

            info = niveaux.get(
                nom,
                {}
            )

            if not isinstance(info, dict):
                info = {}

            taux = info.get(
                "Taux_de_défaut"
            )

            proportion = info.get(
                "% des clients"
            )

            lignes.append([
                nom.capitalize(),

                entier(
                    info.get("Clients")
                ),

                entier(
                    info.get("Défauts")
                ),

                (
                    f"{float(taux):.2f} %"
                    if taux is not None
                    else "—"
                ),

                (
                    f"{float(proportion):.2f} %"
                    if proportion is not None
                    else "—"
                )
            ])

        self.remplir(
            self.repartition,
            lignes
        )

    # ======================================
    # COMPARAISON E1 / E2 / E3
    # ======================================

    def actualiser_comparaison(self):

        experiences = self.metrics.get(
            "comparaison_experiences_validation_seuil_0_5",
            {}
        )

        if not isinstance(experiences, dict):
            experiences = {}

        lignes = []

        for nom in (
            "E1 - Baseline",
            "E2 - class_weight",
            "E3 - SMOTE"
        ):

            info = experiences.get(
                nom,
                {}
            )

            if not isinstance(info, dict):
                info = {}

            lignes.append([
                nom,
                pourcentage(
                    info.get("Recall (classe 1)")
                ),
                pourcentage(
                    info.get("Precision (classe 1)")
                ),
                pourcentage(
                    info.get("F1 (classe 1)")
                ),
                decimal(
                    info.get("Average Precision")
                ),
                decimal(
                    info.get("ROC-AUC")
                ),
                pourcentage(
                    info.get("Accuracy")
                )
            ])

            # Barre de Recall
            barre = self.barres[nom]

            rappel = info.get(
                "Recall (classe 1)"
            )

            if rappel is not None:

                valeur = float(rappel)

                barre.setValue(
                    round(valeur * 1000)
                )

                barre.setFormat(
                    pourcentage(valeur)
                )

            else:

                barre.setValue(0)
                barre.setFormat("—")

        self.remplir(
            self.comparaison,
            lignes
        )

    # ======================================
    # CALIBRATION ET INCERTITUDE
    # ======================================

    def actualiser_calibration(self):

        donnees = self.metrics.get(
            "calibration_validation",
            {}
        )

        if not isinstance(donnees, dict):
            donnees = {}

        lignes = []

        for nom, info in donnees.items():

            if not isinstance(info, dict):
                continue

            lignes.append([
                nom,

                pourcentage(
                    info.get(
                        "Probabilité moyenne prédite"
                    )
                ),

                pourcentage(
                    info.get(
                        "Taux de défaut observé"
                    )
                ),

                decimal(
                    info.get(
                        "Score de Brier"
                    )
                )
            ])

        self.remplir(
            self.calibration,
            lignes
        )

        # ----------------------------------
        # INTERVALLES DE CONFIANCE
        # ----------------------------------

        intervalles = self.metrics.get(
            "intervalles_confiance_test",
            {}
        )

        if not isinstance(intervalles, dict):
            intervalles = {}

        lignes = []

        for nom, bornes in intervalles.items():

            if (
                not isinstance(bornes, list)
                or len(bornes) != 2
            ):
                continue

            format_valeur = (
                decimal
                if nom == "Average Precision"
                else pourcentage
            )

            lignes.append([
                nom,
                format_valeur(bornes[0]),
                format_valeur(bornes[1])
            ])

        self.remplir(
            self.intervalles,
            lignes
        )
