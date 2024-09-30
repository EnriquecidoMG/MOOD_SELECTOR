import sys
import os
import subprocess
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QGridLayout, QLabel, QLineEdit, QMessageBox, QListWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFontDatabase, QFont

CONFIG_FILE = "config.json"

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)  # Sin marco
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Fondo transparente
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel()
        pixmap = QPixmap("./resources/moodselectorlogo.png")  # Cambia esta ruta a tu logo PNG
        self.label.setPixmap(pixmap)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setGeometry(100, 100, pixmap.width(), pixmap.height())
        self.center_window()

    def center_window(self):
        screen = self.screen()
        screen_rect = screen.availableGeometry()
        self.move(
            (screen_rect.width() - self.width()) // 2,
            (screen_rect.height() - self.height()) // 2
        )

class PresetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.pk3_files = []
        self.load_custom_font()  # Cargar la fuente personalizada
        self.init_ui()
        self.load_presets()
        self.center_window()  # Centrar la ventana

    def load_custom_font(self):
        font_id = QFontDatabase.addApplicationFont("ruta/a/tu/fuente.ttf")  # Cambia esta ruta
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            self.custom_font = QFont(font_families[0], 12)  # Cambia el tamaño si es necesario
            self.setFont(self.custom_font)  # Aplicar la fuente personalizada aquí

    def init_ui(self):
        self.setWindowTitle("Seleccionar Preset")
        self.setGeometry(100, 100, 400, 500)
        self.setStyleSheet(""" 
            QWidget {
                background-color: #808080;  /* Gris oscuro */
                border-radius: 15px;
            }
            QLabel {
                font-size: 20px;  /* Aumentar tamaño de fuente */
                color: white;  /* Color de texto blanco */
                margin-bottom: 10px;  /* Espacio debajo del label */
                text-align: center;  /* Centrar texto */
            }
            QPushButton {
                background-color: #A0A0A0;  /* Gris claro para botones */
                border: none;
                border-radius: 15px;  /* Bordes más redondeados */
                padding: 10px;  /* Espaciado interno */
                font-size: 16px;  /* Aumentar tamaño de fuente */
                margin: 5px;  /* Espacio entre botones */
            }
            QPushButton:hover {
                background-color: #B0B0B0;  /* Resaltado más claro */
            }
            #optionsButton {
                font-size: 12px;  /* Tamaño de fuente más pequeño */
                padding: 5px;  /* Menor espaciado interno */
                min-width: 100px;  /* Ancho mínimo */
                max-width: 100px;  /* Ancho máximo */
            }
        """)

        layout = QVBoxLayout()
        self.label_presets = QLabel("Select Game")
        self.label_presets.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_presets)

        self.grid_layout = QGridLayout()
        layout.addLayout(self.grid_layout)

        layout.addSpacing(20)  # Espacio de 20 píxeles

        options_layout = QHBoxLayout()
        self.options_button = QPushButton("Opciones")
        self.options_button.setObjectName("optionsButton")
        self.options_button.clicked.connect(self.show_options)
        options_layout.addStretch()
        options_layout.addWidget(self.options_button)
        options_layout.addStretch()

        layout.addLayout(options_layout)

        self.setLayout(layout)

    def load_presets(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        preset_buttons = []
        for preset_name in os.listdir("."):
            if preset_name.endswith(".json") and preset_name != CONFIG_FILE:
                button_text = os.path.splitext(os.path.basename(preset_name))[0]
                button = QPushButton(button_text)
                button.clicked.connect(lambda checked, name=preset_name: self.run_selected_preset(name))
                preset_buttons.append(button)

        for index, button in enumerate(preset_buttons):
            self.grid_layout.addWidget(button, index // 3, index % 3)

    def run_selected_preset(self, preset_name):
        with open(preset_name, 'r') as preset_file:
            self.pk3_files = json.load(preset_file)
            self.run_gzdoom()

    def run_gzdoom(self):
        if not self.pk3_files:
            QMessageBox.warning(self, "Error", "No hay mods en este preset.")
            return
        
        config = self.load_config()
        gzdoom_path = config.get("gzdoom_path", "")
        if not gzdoom_path:
            QMessageBox.warning(self, "Error", "GZDoom no está configurado.")
            return

        command = [gzdoom_path] + ["-file"] + self.pk3_files
        subprocess.Popen(command)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                return json.load(config_file)
        return {"gzdoom_path": "", "pk3_files": [], "presets": {}, "preset_window_position": (100, 100), "options_window_position": (100, 100)}

    def center_window(self):
        screen = self.screen()
        screen_rect = screen.availableGeometry()
        self.move(
            (screen_rect.width() - self.width()) // 2,
            (screen_rect.height() - self.height()) // 2
        )

    def show_options(self):
        self.save_position()  # Guardar posición actual
        self.options_window = DoomModSelectorApp()
        self.options_window.show()
        self.close()

    def save_position(self):
        config = self.load_config()
        config["preset_window_position"] = (self.x(), self.y())
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file)

class DoomModSelectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.pk3_files = []
        self.load_custom_font()  # Cargar la fuente personalizada
        self.init_ui()
        self.load_pk3_files()
        self.center_window()  # Centrar la ventana

    def load_custom_font(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/doomed.ttf")  # Cambia esta ruta
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            self.custom_font = QFont(font_families[0], 12)  # Cambia el tamaño si es necesario
            self.setFont(self.custom_font)  # Aplicar la fuente personalizada aquí

    def init_ui(self):
        self.setWindowTitle("Doom Mod Selector")
        self.setGeometry(100, 100, 400, 500)
        self.setStyleSheet(""" 
            QWidget {
                background-color: #808080;  /* Gris oscuro */
                border-radius: 15px;
            }
            QPushButton {
                background-color: #A0A0A0;  /* Gris claro para botones */
                border: none;
                border-radius: 15px;  /* Bordes más redondeados */
                padding: 10px;  /* Espaciado interno */
                font-size: 16px;  /* Aumentar tamaño de fuente */
            }
            QPushButton:hover {
                background-color: #B0B0B0;  /* Resaltado más claro */
            }
        """)

        layout = QVBoxLayout()

        self.label = QLabel("Mods PK3 seleccionados:")
        layout.addWidget(self.label)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.add_button = QPushButton("Agregar PK3")
        self.add_button.clicked.connect(self.add_pk3_file)
        layout.addWidget(self.add_button)

        self.gzdoom_input = QLineEdit("")
        self.gzdoom_input.setPlaceholderText("Ruta a GZDoom.exe")
        layout.addWidget(self.gzdoom_input)

        self.browse_button = QPushButton("Buscar GZDoom")
        self.browse_button.clicked.connect(self.browse_gzdoom_path)
        layout.addWidget(self.browse_button)

        self.save_preset_button = QPushButton("Guardar Preset")
        self.save_preset_button.clicked.connect(self.save_preset)
        layout.addWidget(self.save_preset_button)

        self.run_button = QPushButton("Ejecutar con GZDoom")
        self.run_button.clicked.connect(self.run_gzdoom)
        layout.addWidget(self.run_button)

        self.back_button = QPushButton("Volver a Presets")
        self.back_button.clicked.connect(self.back_to_presets)
        layout.addWidget(self.back_button)

        self.setLayout(layout)
        self.setFont(self.custom_font)  # Aplicar la fuente personalizada aquí también

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
            self.save_gzdoom_path()

    def save_gzdoom_path(self):
        config = self.load_config()
        config["gzdoom_path"] = self.gzdoom_input.text()
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                return json.load(config_file)
        return {"gzdoom_path": "", "pk3_files": [], "presets": {}, "preset_window_position": (100, 100), "options_window_position": (100, 100)}

    def load_pk3_files(self):
        config = self.load_config()
        self.pk3_files = config.get("pk3_files", [])
        self.update_pk3_list()

    def update_pk3_list(self):
        self.list_widget.clear()
        self.list_widget.addItems(self.pk3_files)

    def save_preset(self):
        preset_name, _ = QFileDialog.getSaveFileName(self, "Guardar Preset", "", "JSON Files (*.json)")
        if preset_name:
            with open(preset_name, 'w') as preset_file:
                json.dump(self.pk3_files, preset_file)

    def run_gzdoom(self):
        if not self.pk3_files:
            QMessageBox.warning(self, "Error", "No hay mods seleccionados.")
            return
        
        config = self.load_config()
        gzdoom_path = config.get("gzdoom_path", "")
        if not gzdoom_path:
            QMessageBox.warning(self, "Error", "GZDoom no está configurado.")
            return

        command = [gzdoom_path] + ["-file"] + self.pk3_files
        subprocess.Popen(command)

    def back_to_presets(self):
        self.save_position()  # Guardar posición actual
        self.preset_window = PresetWindow()
        self.preset_window.show()
        self.close()

    def save_position(self):
        config = self.load_config()
        config["options_window_position"] = (self.x(), self.y())
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file)

    def center_window(self):
        screen = self.screen()
        screen_rect = screen.availableGeometry()
        self.move(
            (screen_rect.width() - self.width()) // 2,
            (screen_rect.height() - self.height()) // 2
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()
    
    # Temporizador para mostrar la pantalla de presentación por un tiempo
    QTimer.singleShot(2000, lambda: [splash.close(), PresetWindow().show()])  # 2000 ms = 2 segundos

    sys.exit(app.exec())
