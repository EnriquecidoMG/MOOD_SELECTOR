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
        config = self.load_config()  # Carga la configuración
        self.gzdoom_path = config.get("gzdoom_path", "")  # Obtiene solo la ruta
        self.init_ui()
        self.load_pk3_files()  # Carga los archivos PK3 recordados

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

        self.browse_button = QPushButton("Buscar GZDoom")
        self.browse_button.clicked.connect(self.browse_gzdoom_path)
        layout.addWidget(self.browse_button)

        self.run_button = QPushButton("Ejecutar con GZDoom")
        self.run_button.clicked.connect(self.run_gzdoom)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def add_pk3_file(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar Archivos PK3", "", "PK3 Files (*.pk3);;All Files (*)")
        
        if files:
            self.pk3_files.extend(files)
            self.update_pk3_list()

    def browse_gzdoom_path(self):
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar GZDoom.exe", "", "Executable Files (*.exe);;All Files (*)")
        if file:
            self.gzdoom_input.setText(file)
            self.gzdoom_path = file
            self.save_gzdoom_path()  # Guarda automáticamente la ruta seleccionada

    def save_gzdoom_path(self):
        config = self.load_config()
        config["gzdoom_path"] = self.gzdoom_path
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                return json.load(config_file)
        return {"gzdoom_path": "", "pk3_files": []}

    def load_pk3_files(self):
        config = self.load_config()
        self.pk3_files = config.get("pk3_files", [])
        self.update_pk3_list()

    def update_pk3_list(self):
        self.list_widget.clear()
        self.list_widget.addItems(self.pk3_files)
        self.save_pk3_files()  # Guarda la lista actualizada de PK3

    def save_pk3_files(self):
        config = self.load_config()
        config["pk3_files"] = self.pk3_files
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file)

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
