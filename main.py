#!/usr/bin/env python3

import sys
import os
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
from PySide6.QtGui import QFont, QPalette, QColor, QColorConstants, QIcon

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


def import_into_browser():
    """Import the JSON backup into the selected browser."""
    base_path = locations.get_browser_path(bw_sel.currentText().strip()) or ""

    # Construct the full path to Web Data file
    web_data_path = os.path.join(base_path, "Web Data") if base_path else ""

    # If Web Data exists, use it as the pre-selected file; otherwise, use the directory
    start_path = web_data_path if os.path.exists(web_data_path) else base_path

    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select Web Data file",
        start_path,
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

    # Prepare data
    new_rows = {row[0]: row for row in filas}
    ids = list(new_rows.keys())
    existing_ids = utils.db_get_existing_ids(file_path, ids)
    
    to_replace = []
    conflicts = []
    
    for eid in existing_ids:
        if eid in new_rows:
            old_row = utils.get_row_by_id(file_path, eid)
            new_row = new_rows[eid]
            if old_row != tuple(new_row):
                conflicts.append((eid, old_row, new_row))
    
    # Handle each conflict
    for eid, old_row, new_row in conflicts:
        diff = utils.compare_rows(old_row, new_row)
        name_old = old_row[1] if old_row[1] else "Unknown"
        shortcut_old = old_row[2] if old_row[2] else ""
        name_new = new_row[1] if new_row[1] else "Unknown"
        shortcut_new = new_row[2] if new_row[2] else ""
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Conflict Detected")
        msg_box.setText(f"Entry ID {eid}:\n\nExisting: {name_old} ({shortcut_old})\nNew: {name_new} ({shortcut_new})\n\nChanges:\n{diff}")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.button(QMessageBox.StandardButton.Yes).setText("Replace")
        msg_box.button(QMessageBox.StandardButton.No).setText("Keep Existing")
        response = msg_box.exec()
        if response == QMessageBox.StandardButton.Yes:
            to_replace.append(new_row)
    
    # New entries
    to_insert = [row for row in filas if row[0] not in existing_ids]
    
    try:
        if to_insert:
            utils.db_insert_rows(file_path, to_insert, 'ignore')
        if to_replace:
            utils.db_insert_rows(file_path, to_replace, 'replace')
        show_success_import(file_path)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"{e}")


def export_from_browser(bw_sel):
    """Export Search Engines from the selected browser to a JSON file."""
    base_path = locations.get_browser_path(bw_sel.currentText().strip()) or ""

    # Construct the full path to Web Data file
    web_data_path = os.path.join(base_path, "Web Data") if base_path else ""

    # If Web Data exists, use it as the pre-selected file; otherwise, use the directory
    start_path = web_data_path if os.path.exists(web_data_path) else base_path

    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select Web Data file",
        start_path,
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
    """Configure the dark theme using the Fusion style."""
    app.setStyle("Fusion")

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColorConstants.White)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColorConstants.White)
    dark_palette.setColor(QPalette.ColorRole.Text, QColorConstants.White)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColorConstants.White)
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColorConstants.Red)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(35, 35, 35))

    app.setPalette(dark_palette)


app = QApplication(sys.argv)
setup_dark_theme(app)

win = QWidget()
win.setWindowTitle("Browser Search Engines")
win.setWindowIcon(QIcon("images/icon.png"))
win.setMinimumSize(400, 200)

main_layout = QVBoxLayout()
main_layout.setSpacing(10)

frame_layout = QVBoxLayout()
frame_layout.setSpacing(10)

label_warning = QLabel("Close Browser before import or export")
label_warning.setFont(QFont("Arial", 14, QFont.Weight.Bold))
label_warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
frame_layout.addWidget(label_warning)

label_instructions = QLabel(
    "Export from Browser Web Data SQLite to a JSON file\n"
    "Import from a JSON file into a Browser Web Data SQLite"
)
label_instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
frame_layout.addWidget(label_instructions)

bw_sel = QComboBox()
bw_sel.addItems([b.capitalize() for b in locations.LOCATIONS.keys()])
bw_sel.currentTextChanged.connect(select_browser)
bw_sel.setMinimumHeight(35)
frame_layout.addWidget(bw_sel)

main_layout.addLayout(frame_layout)
main_layout.addStretch()

buttons_layout = QHBoxLayout()
buttons_layout.setSpacing(10)

btn_export = QPushButton("Export from Browser")
btn_export.clicked.connect(lambda: export_from_browser(bw_sel))
btn_export.setMinimumHeight(35)
buttons_layout.addWidget(btn_export)

btn_import = QPushButton("Import into Browser")
btn_import.clicked.connect(import_into_browser)
btn_import.setMinimumHeight(35)
buttons_layout.addWidget(btn_import)

main_layout.addLayout(buttons_layout)

win.setLayout(main_layout)

win.show()

sys.exit(app.exec())
