
# ==============================================
# CREDITRISK360 — STYLES DES COMPOSANTS
# ==============================================

# Ce style complète le STYLE existant de main.py.
# Il harmonise les formulaires, tableaux, fenêtres,
# onglets, listes et messages sur Windows.

COMPONENT_STYLE = """

/* ==========================================
   TYPOGRAPHIE GÉNÉRALE
   ========================================== */

QWidget {
    font-family: "Segoe UI";
    font-size: 13px;
    color: #243247;
}

/* ==========================================
   FENÊTRES ET DIALOGUES
   ========================================== */

QDialog,
QMessageBox {
    background-color: #f5f7fb;
    color: #243247;
}

QDialog QLabel,
QMessageBox QLabel {
    color: #243247;
    background: transparent;
    font-size: 13px;
}

/* ==========================================
   TITRES ET LABELS
   ========================================== */

QLabel {
    color: #243247;
    background: transparent;
}

QLabel#pageTitle {
    color: #172b49;
    font-size: 25px;
    font-weight: bold;
}

QLabel#cardTitle {
    color: #5f7189;
    font-size: 13px;
}

QLabel#cardValue {
    color: #183657;
    font-size: 20px;
    font-weight: bold;
}

/* ==========================================
   MENU LATÉRAL
   ========================================== */

QFrame#sidebar {
    background-color: #152640;
}

QLabel#brand {
    color: #ffffff;
    font-size: 23px;
    font-weight: bold;
}

QLabel#sidebarCaption {
    color: #b8c5d8;
}

QPushButton#navButton {
    background: transparent;
    color: #d5dfec;
    border: none;
    border-radius: 9px;
    padding: 13px;
    text-align: left;
    font-size: 14px;
}

QPushButton#navButton:hover {
    background-color: #29405f;
}

QPushButton#navButton:checked {
    background-color: #315d91;
    color: white;
    font-weight: bold;
}

/* ==========================================
   CARTES
   ========================================== */

QFrame#card {
    background-color: #ffffff;
    border: 1px solid #dce4ef;
    border-radius: 12px;
}

/* ==========================================
   GROUPES DE FORMULAIRE
   ========================================== */

QGroupBox {
    background-color: #ffffff;
    border: 1px solid #d9e3ee;
    border-radius: 10px;
    margin-top: 18px;
    padding-top: 12px;

    color: #183657;
    font-size: 13px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 7px;

    background-color: #ffffff;
    color: #183657;
    font-weight: bold;
}

/* ==========================================
   CHAMPS DE SAISIE
   ========================================== */

QLineEdit,
QSpinBox,
QDoubleSpinBox,
QComboBox,
QDateEdit {
    background-color: #ffffff;
    color: #1e344f;

    border: 1px solid #cbd7e6;
    border-radius: 7px;

    padding: 7px 9px;
    min-height: 22px;

    selection-background-color: #315d91;
    selection-color: #ffffff;
}

QLineEdit:hover,
QSpinBox:hover,
QDoubleSpinBox:hover,
QComboBox:hover,
QDateEdit:hover {
    border: 1px solid #7c9ac0;
}

QLineEdit:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QComboBox:focus,
QDateEdit:focus {
    border: 2px solid #315d91;
    background-color: #ffffff;
}

QLineEdit:disabled,
QSpinBox:disabled,
QDoubleSpinBox:disabled,
QComboBox:disabled {
    background-color: #edf1f6;
    color: #77869a;
    border: 1px solid #d9e0e9;
}

/* Liste déroulante du QComboBox */

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #243247;
    border: 1px solid #cad8e8;

    selection-background-color: #dce9f8;
    selection-color: #183657;

    outline: none;
}

/* ==========================================
   CASES À COCHER
   ========================================== */

QCheckBox {
    background: transparent;
    color: #243247;
    font-size: 13px;
    spacing: 7px;
}

QCheckBox:disabled {
    color: #8996a8;
}

/* ==========================================
   BOUTONS GÉNÉRAUX
   ========================================== */

QPushButton {
    background-color: #ffffff;
    color: #24466d;

    border: 1px solid #cbd7e6;
    border-radius: 8px;

    padding: 9px 16px;
    min-height: 18px;

    font-weight: 600;
}

QPushButton:hover {
    background-color: #edf3fb;
    border-color: #7c9ac0;
}

QPushButton:pressed {
    background-color: #dbe8f7;
}

QPushButton:disabled {
    background-color: #edf1f6;
    color: #9aa7b5;
    border-color: #e1e6ed;
}

/* Boutons principaux */

QPushButton#refreshButton {
    background-color: #315d91;
    color: #ffffff;
    border: 1px solid #315d91;
    border-radius: 8px;

    padding: 10px 18px;
    font-weight: bold;
}

QPushButton#refreshButton:hover {
    background-color: #244c7c;
    border-color: #244c7c;
}

QPushButton#refreshButton:pressed {
    background-color: #183657;
}

QPushButton#refreshButton:disabled {
    background-color: #b5c4d6;
    color: #ffffff;
    border-color: #b5c4d6;
}

/* Boutons OK / Cancel des dialogues */

QDialogButtonBox QPushButton {
    background-color: #ffffff;
    color: #183657;
    border: 1px solid #cbd7e6;

    min-width: 90px;
    min-height: 24px;
    padding: 7px 14px;
}

QDialogButtonBox QPushButton:hover {
    background-color: #e7eff9;
    border-color: #315d91;
}

QDialogButtonBox QPushButton:default {
    background-color: #315d91;
    color: #ffffff;
    border-color: #315d91;
}

/* ==========================================
   TABLEAUX
   ========================================== */

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f4f7fc;

    color: #243247;
    gridline-color: #e7ecf3;

    border: 1px solid #dce4ef;
    border-radius: 9px;

    selection-background-color: #d9e8fa;
    selection-color: #17385e;
}

QTableWidget::item {
    padding: 6px 9px;
    color: #243247;
}

QTableWidget::item:selected {
    background-color: #d9e8fa;
    color: #17385e;
}

QTableWidget::item:hover {
    background-color: #edf4fc;
}

/* Entêtes des tableaux */

QHeaderView {
    background-color: #edf2f8;
}

QHeaderView::section {
    background-color: #edf2f8;
    color: #294563;

    border: none;
    border-right: 1px solid #dce4ee;
    border-bottom: 1px solid #dce4ee;

    padding: 9px 10px;

    font-weight: bold;
    font-size: 12px;
}

QTableCornerButton::section {
    background-color: #edf2f8;
    border: 1px solid #dce4ee;
}

/* ==========================================
   ZONES DE TEXTE
   ========================================== */

QPlainTextEdit,
QTextEdit {
    background-color: #ffffff;
    color: #243247;

    border: 1px solid #d6e0ec;
    border-radius: 9px;

    padding: 10px;

    selection-background-color: #d9e8fa;
    selection-color: #183657;
}

QPlainTextEdit:focus,
QTextEdit:focus {
    border-color: #315d91;
}

/* ==========================================
   ZONES DÉFILANTES
   ========================================== */

QScrollArea {
    background-color: #ffffff;
    border: none;
}

QScrollArea QWidget {
    background-color: #ffffff;
}

/* ==========================================
   ONGLETS
   ========================================== */

QTabWidget::pane {
    background-color: #ffffff;
    border: 1px solid #dce4ef;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #eaf0f7;
    color: #425a75;

    border: 1px solid #dce4ef;
    padding: 10px 16px;

    min-width: 90px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #24558b;
    font-weight: bold;

    border-bottom: 2px solid #315d91;
}

QTabBar::tab:hover:!selected {
    background-color: #dce8f6;
}

/* ==========================================
   BARRES DE PROGRESSION
   ========================================== */

QProgressBar {
    background-color: #edf2f8;
    color: #243247;

    border: 1px solid #d6e0ec;
    border-radius: 7px;

    text-align: center;
    min-height: 20px;
}

QProgressBar::chunk {
    background-color: #315d91;
    border-radius: 6px;
}

/* ==========================================
   BARRES DE DÉFILEMENT
   ========================================== */

QScrollBar:vertical {
    background-color: #eef2f7;
    width: 11px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #b3c3d6;
    border-radius: 5px;
    min-height: 28px;
}

QScrollBar::handle:vertical:hover {
    background-color: #8aa5c4;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #eef2f7;
    height: 11px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #b3c3d6;
    border-radius: 5px;
    min-width: 28px;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ==========================================
   INFOBULLES
   ========================================== */

QToolTip {
    background-color: #ffffff;
    color: #243247;
    border: 1px solid #cbd7e6;
    padding: 6px;
}

"""
