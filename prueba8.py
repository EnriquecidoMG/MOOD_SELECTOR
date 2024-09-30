import sys
import os
import subprocess
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QListWidget, QLabel, QLineEdit, QHBoxLayout, QMessageBox
)

CONFIG_FILE = "config.json"

class DoomModSelectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.pk3_files = []
        self.presets = {}
        config = self.load_config()
        self.gzdoom_path = config.get("gzdoom_path", "")
        self.init_ui()
        self.load_pk3_files()
        self.load_presets()

    def init_ui(self):
        self.setWindowTitle("Doom Mod Selector")
        self.setGeometry(100, 100, 400, 500)

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

        self.label_presets = QLabel("Presets de Mods:")
        layout.addWidget(self.label_presets)

        self.preset_list = QListWidget()
        layout.addWidget(self.preset_list)

        button_layout = QHBoxLayout()
        
        self.save_preset_button = QPushButton("Guardar Preset")
        self.save_preset_button.clicked.connect(self.save_preset)
        button_layout.addWidget(self.save_preset_button)

        self.show_presets_button = QPushButton("Mostrar Presets")
        self.show_presets_button.clicked.connect(self.show_presets)
        button_layout.addWidget(self.show_presets_button)

        layout.addLayout(button_layout)

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
            self.save_gzdoom_path()

    def save_gzdoom_path(self):
        config = self.load_config()
        config["gzdoom_path"] = self.gzdoom_path
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                return json.load(config_file)
        return {"gzdoom_path": "", "pk3_files": [], "presets": {}}

    def load_pk3_files(self):
        config = self.load_config()
        self.pk3_files = config.get("pk3_files", [])
        self.update_pk3_list()

    def update_pk3_list(self):
        self.list_widget.clear()
        self.list_widget.addItems(self.pk3_files)
        self.save_pk3_files()

    def save_pk3_files(self):
        config = self.load_config()
        config["pk3_files"] = self.pk3_files
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file)

    def save_preset(self):
        preset_name, _ = QFileDialog.getSaveFileName(self, "Guardar Preset", "", "JSON Files (*.json)")
        if preset_name:
            self.presets[preset_name] = self.pk3_files
            with open(preset_name, 'w') as preset_file:
                json.dump(self.pk3_files, preset_file)
            self.preset_list.addItem(os.path.basename(preset_name))

    def load_presets(self):
        # Cargar solo archivos JSON que no sean el archivo de configuración
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                config = json.load(config_file)
                for preset_name in os.listdir("."):
                    if preset_name.endswith(".json") and preset_name != CONFIG_FILE:
                        self.preset_list.addItem(os.path.basename(preset_name))

    def show_presets(self):
        presets_window = PresetWindow(self)
        presets_window.show()

    def run_gzdoom(self):
        if not self.pk3_files or not self.gzdoom_path:
            QMessageBox.warning(self, "Error", "No hay mods o GZDoom no está configurado.")
            return

        command = [self.gzdoom_path] + ["-file"] + self.pk3_files
        subprocess.Popen(command)

class PresetWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Seleccionar Preset")
        self.setGeometry(150, 150, 300, 400)

        layout = QVBoxLayout()

        # Cargar presets guardados
        self.preset_buttons = {}
        for preset_name in os.listdir("."):
            if preset_name.endswith(".json") and preset_name != CONFIG_FILE:
                button = QPushButton(os.path.basename(preset_name))
                button.clicked.connect(lambda checked, name=preset_name: self.load_and_run_preset(name))
                layout.addWidget(button)
                self.preset_buttons[preset_name] = button

        self.setLayout(layout)

    def load_and_run_preset(self, preset_name):
        with open(preset_name, 'r') as preset_file:
            pk3_files = json.load(preset_file)
            self.parent.pk3_files = pk3_files
            self.parent.update_pk3_list()
        self.parent.run_gzdoom()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DoomModSelectorApp()
    window.show()
    sys.exit(app.exec())
