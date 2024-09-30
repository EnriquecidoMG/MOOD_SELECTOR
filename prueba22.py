import sys
import os
import subprocess
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QGridLayout, QLabel, QLineEdit, QMessageBox, QListWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFontDatabase, QFont

CONFIG_FILE = "config.json"

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel()
        pixmap = QPixmap("./resources/moodselectorlogo.png")
        self.label.setPixmap(pixmap)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setFixedSize(pixmap.width(), pixmap.height())
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
        self.load_custom_font()
        self.init_ui()
        self.load_presets()
        self.center_window()

    def load_custom_font(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/doomed.ttf")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            self.custom_font = QFont(font_families[0], 12)
            self.setFont(self.custom_font)

    def init_ui(self):
        self.setWindowTitle("Seleccionar Preset")
        self.setFixedSize(400, 500)

        background_label = QLabel(self)
        background_label.setPixmap(QPixmap("./resources/background.jpg"))
        background_label.setScaledContents(True)
        background_label.setGeometry(0, 0, 400, 500)

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)  # Margen de 50 píxeles

        self.label_presets = QLabel("Select Game")
        self.label_presets.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_presets)

        self.grid_layout = QGridLayout()
        layout.addLayout(self.grid_layout)

        layout.addSpacing(20)

        options_layout = QHBoxLayout()
        self.options_button = QPushButton("Opciones")
        self.options_button.clicked.connect(self.show_options)
        options_layout.addStretch()
        options_layout.addWidget(self.options_button)
        options_layout.addStretch()

        layout.addLayout(options_layout)
        self.setLayout(layout)

        self.setStyleSheet(self.style_sheet())

    def style_sheet(self):
        return """
            QLabel {
                font-size: 20px;
                color: white;
                margin-bottom: 10px;
                text-align: center;
            }
            QPushButton {
                background-color: rgba(160, 160, 160, 0.8);
                border: none;
                border-radius: 15px;
                padding: 10px;
                font-size: 16px;
                margin: 5px;
                max-width: 300px;  /* Limitar el ancho máximo de los botones */
                max-height: 60px;  /* Limitar la altura máxima de los botones */
            }
            QPushButton:hover {
                background-color: rgba(176, 176, 176, 0.8);
            }
            #optionsButton {
                font-size: 15px;
                padding: 12px;
                min-width: 125px;
                max-width: 125px;
            }
        """

    def load_presets(self):
        self.clear_grid_layout()
        preset_buttons = self.create_preset_buttons()
        self.add_buttons_to_grid(preset_buttons)

    def clear_grid_layout(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def create_preset_buttons(self):
        preset_buttons = []
        for preset_name in os.listdir("."):
            if preset_name.endswith(".json") and preset_name != CONFIG_FILE:
                button_text = os.path.splitext(os.path.basename(preset_name))[0]
                button = QPushButton(button_text)
                button.clicked.connect(lambda checked, name=preset_name: self.run_selected_preset(name))
                preset_buttons.append(button)
        return preset_buttons

    def add_buttons_to_grid(self, buttons):
        for index, button in enumerate(buttons):
            self.grid_layout.addWidget(button, index // 3, index % 3)

    def run_selected_preset(self, preset_name):
        try:
            with open(preset_name, 'r') as preset_file:
                self.pk3_files = json.load(preset_file)
                self.run_gzdoom()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar el preset: {str(e)}")

    def run_gzdoom(self):
        if not self.pk3_files:
            QMessageBox.warning(self, "Error", "No hay mods en este preset.")
            return

        config = self.load_config()
        gzdoom_path = config.get("gzdoom_path", "")
        if not os.path.exists(gzdoom_path):
            QMessageBox.warning(self, "Error", "La ruta a GZDoom no es válida.")
            return

        command = [gzdoom_path] + ["-file"] + self.pk3_files
        subprocess.Popen(command)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                return json.load(config_file)
        return self.default_config()

    def default_config(self):
        return {
            "gzdoom_path": "",
            "pk3_files": [],
            "presets": {},
            "preset_window_position": (100, 100),
            "options_window_position": (100, 100)
        }

    def center_window(self):
        screen = self.screen()
        screen_rect = screen.availableGeometry()
        self.move(
            (screen_rect.width() - self.width()) // 2,
            (screen_rect.height() - self.height()) // 2
        )

    def show_options(self):
        self.save_position()
        self.options_window = DoomModSelectorApp()
        self.options_window.show()
        self.close()

    def save_position(self):
        config = self.load_config()
        config["preset_window_position"] = (self.x(), self.y())
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file, indent=4)

class DoomModSelectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.pk3_files = []
        self.load_custom_font()
        self.init_ui()
        self.load_pk3_files()
        self.center_window()

    def load_custom_font(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/doomed.ttf")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            self.custom_font = QFont(font_families[0], 12)
            self.setFont(self.custom_font)

    def init_ui(self):
        self.setWindowTitle("Doom Mod Selector")
        self.setFixedSize(400, 500)

        background_label = QLabel(self)
        background_label.setPixmap(QPixmap("./resources/background.jpg"))
        background_label.setScaledContents(True)
        background_label.setGeometry(0, 0, 400, 500)

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)  # Margen de 50 píxeles

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
        self.setFont(self.custom_font)

        self.setStyleSheet(self.style_sheet())

    def style_sheet(self):
        return """
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: rgba(160, 160, 160, 0.8);
                border: none;
                border-radius: 15px;
                padding: 10px;
                font-size: 16px;
                margin: 5px;
                max-width: 300px;  /* Limitar el ancho máximo de los botones */
                max-height: 60px;  /* Limitar la altura máxima de los botones */
            }
            QPushButton:hover {
                background-color: rgba(176, 176, 176, 0.8);
            }
        """

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
            json.dump(config, config_file, indent=4)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                return json.load(config_file)
        return self.default_config()

    def default_config(self):
        return {
            "gzdoom_path": "",
            "pk3_files": [],
            "presets": {},
            "preset_window_position": (100, 100),
            "options_window_position": (100, 100)
        }

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
                json.dump(self.pk3_files, preset_file, indent=4)

    def run_gzdoom(self):
        if not self.pk3_files:
            QMessageBox.warning(self, "Error", "No hay mods seleccionados.")
            return
        
        config = self.load_config()
        gzdoom_path = config.get("gzdoom_path", "")
        if not os.path.exists(gzdoom_path):
            QMessageBox.warning(self, "Error", "La ruta a GZDoom no es válida.")
            return

        command = [gzdoom_path] + ["-file"] + self.pk3_files
        subprocess.Popen(command)

    def back_to_presets(self):
        self.save_position()
        self.preset_window = PresetWindow()
        self.preset_window.show()
        self.close()

    def save_position(self):
        config = self.load_config()
        config["options_window_position"] = (self.x(), self.y())
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file, indent=4)

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
    
    QTimer.singleShot(2000, lambda: [splash.close(), PresetWindow().show()])

    sys.exit(app.exec())
