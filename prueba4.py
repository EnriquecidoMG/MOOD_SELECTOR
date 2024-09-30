import sys
import os
import subprocess
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QListWidget, QLabel, QLineEdit
)

CONFIG_FILE = "config.json"

class DoomModSelectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.pk3_files = []
        self.gzdoom_path = self.load_config()  # Carga la ruta antes de crear la UI
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Doom Mod Selector")
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        self.label = QLabel("Mods PK3 seleccionados:")
        layout.addWidget(self.label)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.add_button = QPushButton("Agregar PK3")
        self.add_button.clicked.connect(self.add_pk3_file)
        layout.addWidget(self.add_button)

        self.gzdoom_input = QLineEdit(self.gzdoom_path)
        self.gzdoom_input.setPlaceholderText("Ruta a GZDoom.exe")
        layout.addWidget(self.gzdoom_input)

        self.save_path_button = QPushButton("Guardar Ruta GZDoom")
        self.save_path_button.clicked.connect(self.save_gzdoom_path)
        layout.addWidget(self.save_path_button)

        self.run_button = QPushButton("Ejecutar con GZDoom")
        self.run_button.clicked.connect(self.run_gzdoom)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def add_pk3_file(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar Archivos PK3", "", "PK3 Files (*.pk3);;All Files (*)")
        
        if files:
            self.pk3_files.extend(files)
            self.list_widget.addItems(files)

    def save_gzdoom_path(self):
        self.gzdoom_path = self.gzdoom_input.text()
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump({"gzdoom_path": self.gzdoom_path}, config_file)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                config = json.load(config_file)
                return config.get("gzdoom_path", "")
        return ""

    def run_gzdoom(self):
        if not self.pk3_files or not self.gzdoom_path:
            return

        # Ejecuta GZDoom con los mods seleccionados
        command = [self.gzdoom_path] + ["-file"] + self.pk3_files
        subprocess.Popen(command)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DoomModSelectorApp()
    window.show()
    sys.exit(app.exec())
