#!/usr/bin/env python3

import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor

import locations
import utils


def show_file_error():
    QMessageBox.critical(None, "Error", "File not found.")


def show_empty_alert():
    QMessageBox.critical(
        None, "Error", f"No data found in the backup file {utils.BACKUP_FILE}"
    )


def show_success_export():
    QMessageBox.information(
        None,
        "Success",
        f"Search Engines exported successfully in {utils.BACKUP_FILE}",
    )


def show_success_import(path):
    QMessageBox.information(
        None, "Success", f"Search Engines imported successfully in {path}"
    )


def importar():
    """Importa el JSON backup en el navegador seleccionado"""
    path = locations.get_browser_path(bw_sel.currentText().strip())
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select Web Data file",
        path,
        "Web Data SQLite (Web Data);;All Files (*)",
    )
    if not file_path:
        show_file_error()
        return

    print(f"Importing from {file_path}")
    filas = utils.json_read(utils.BACKUP_FILE)
    if len(filas) == 0:
        show_empty_alert()
        return

    try:
        utils.db_insertar_filas(file_path, filas)
        show_success_import(file_path)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"{e}")


def exportar(bw_sel):
    """Exporta Search Engines del navegador seleccionado en un archivo JSON"""
    path = locations.get_browser_path(bw_sel.currentText().strip())
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select Web Data file",
        path,
        "Web Data SQLite (Web Data);;All Files (*)",
    )
    if not file_path:
        show_file_error()
        return

    filas = utils.db_read_keywords(file_path)
    utils.json_write(filas)
    show_success_export()


def select_browser():
    print(f"Browser: {bw_sel.currentText()}")


def setup_dark_theme(app):
    """Configura el tema oscuro usando Fusion style"""
    app.setStyle("Fusion")

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))

    app.setPalette(dark_palette)


app = QApplication(sys.argv)
setup_dark_theme(app)

win = QWidget()
win.setWindowTitle("Browser Search Engines")
win.setMinimumSize(400, 200)

main_layout = QVBoxLayout()
main_layout.setSpacing(10)

frame_layout = QVBoxLayout()
frame_layout.setSpacing(10)

label_warning = QLabel("Close Browser before import or export")
label_warning.setFont(QFont("Arial", 14, QFont.Bold))
label_warning.setAlignment(Qt.AlignCenter)
frame_layout.addWidget(label_warning)

label_instructions = QLabel(
    "Export from Browser Web Data SQLite to a JSON file\n"
    "Import from a JSON file into a Browser Web Data SQLite"
)
label_instructions.setAlignment(Qt.AlignCenter)
frame_layout.addWidget(label_instructions)

bw_sel = QComboBox()
bw_sel.addItems(list(locations.LOCATIONS.keys()))
bw_sel.currentTextChanged.connect(select_browser)
bw_sel.setMinimumHeight(35)
frame_layout.addWidget(bw_sel)

main_layout.addLayout(frame_layout)
main_layout.addStretch()

buttons_layout = QHBoxLayout()
buttons_layout.setSpacing(10)

btn_export = QPushButton("Export from Browser")
btn_export.clicked.connect(lambda: exportar(bw_sel))
btn_export.setMinimumHeight(35)
buttons_layout.addWidget(btn_export)

btn_import = QPushButton("Import into Browser")
btn_import.clicked.connect(importar)
btn_import.setMinimumHeight(35)
buttons_layout.addWidget(btn_import)

main_layout.addLayout(buttons_layout)

win.setLayout(main_layout)

win.show()

sys.exit(app.exec())
