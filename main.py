import sys
import os
import subprocess
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QGridLayout, QLabel, QLineEdit, QMessageBox, QListWidget, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFontDatabase, QFont, QIcon

class ConfigManager:
    def __init__(self):
        self.config = {
            "gzdoom_path": "",
            "pk3_files": [],
            "presets": {},
            "preset_window_position": (100, 100),
            "options_window_position": (100, 100)
        }

    def save_config(self):
        with open("config.json", 'w') as file:
            json.dump(self.config, file, indent=4)

    def update_gzdoom_path(self, path):
        self.config["gzdoom_path"] = path
        self.save_config()

class BaseWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("./resources/icon.ico"))
        self.config_manager = ConfigManager()
        self.load_custom_font()
        self.setStyleSheet(open("styles.css").read())  # Load CSS file

    def load_custom_font(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/doomed.ttf")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            self.setFont(QFont(font_families[0], 12))

    def center_window(self):
        screen = self.screen()
        screen_rect = screen.availableGeometry()
        self.move(
            (screen_rect.width() - self.width()) // 2,
            (screen_rect.height() - self.height()) // 2
        )

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

class PresetWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        self.pk3_files = []
        self.init_ui()
        self.load_presets()
        self.center_window()

    def init_ui(self):
        self.setWindowTitle("Select Preset")
        self.setFixedSize(400, 500)
        layout = self.create_main_layout()
        self.setLayout(layout)

    def create_main_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)

        self.label_presets = QLabel("Select Game")
        self.label_presets.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_presets.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        layout.addWidget(self.label_presets, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.grid_layout = QGridLayout()
        layout.addLayout(self.grid_layout)
        layout.addSpacing(20)
        layout.addLayout(self.create_options_layout())
        return layout

    def create_options_layout(self):
        options_layout = QHBoxLayout()
        
        self.options_button = QPushButton("Options")
        self.options_button.setObjectName("optionsButton")  # Set object name for styling
        self.options_button.clicked.connect(self.show_options)
        
        options_layout.addStretch()
        options_layout.addWidget(self.options_button)
        options_layout.addStretch()
        return options_layout

    def load_presets(self):
        self.clear_grid_layout()
        preset_buttons = self.create_preset_buttons()
        self.add_buttons_to_layout(preset_buttons)

    def clear_grid_layout(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def create_preset_buttons(self):
        preset_buttons = []
        for preset_name in os.listdir("."):
            if preset_name.endswith(".json") and preset_name != "config.json":
                button_text = os.path.splitext(os.path.basename(preset_name))[0]
                button = QPushButton(button_text)
                button.clicked.connect(lambda checked, name=preset_name: self.run_selected_preset(name))
                preset_buttons.append(button)
        return preset_buttons

    def add_buttons_to_layout(self, preset_buttons):
        for index, button in enumerate(preset_buttons):
            self.grid_layout.addWidget(button, index // 3, index % 3)

    def run_selected_preset(self, preset_name):
        try:
            with open(preset_name, 'r') as preset_file:
                self.pk3_files = json.load(preset_file)
                self.run_gzdoom()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load the preset: {str(e)}")

    def run_gzdoom(self):
        if not self.pk3_files:
            QMessageBox.warning(self, "Error", "No mods in this preset.")
            return
        
        gzdoom_path = self.config_manager.config.get("gzdoom_path", "")
        if not gzdoom_path:
            QMessageBox.warning(self, "Error", "GZDoom is not configured.")
            return

        command = [gzdoom_path] + ["-file"] + self.pk3_files
        subprocess.Popen(command)

    def show_options(self):
        self.save_position()
        self.options_window = DoomModSelectorApp()
        self.options_window.show()
        self.close()

    def save_position(self):
        self.config_manager.config["preset_window_position"] = (self.x(), self.y())
        self.config_manager.save_config()

class DoomModSelectorApp(BaseWindow):
    def __init__(self):
        super().__init__()
        self.pk3_files = []
        self.init_ui()
        self.load_pk3_files()
        self.center_window()

    def init_ui(self):
        self.setWindowTitle("Doom Mod Selector")
        self.setFixedSize(400, 500)

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)

        self.label = QLabel("Selected PK3 Mods:")
        layout.addWidget(self.label)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.add_button = QPushButton("Add PK3")
        self.add_button.clicked.connect(self.add_pk3_file)
        layout.addWidget(self.add_button)

        self.gzdoom_input = QLineEdit("")
        self.gzdoom_input.setPlaceholderText("Path to GZDoom.exe")
        layout.addWidget(self.gzdoom_input)

        self.browse_button = QPushButton("Browse GZDoom")
        self.browse_button.clicked.connect(self.browse_gzdoom_path)
        layout.addWidget(self.browse_button)

        self.save_preset_button = QPushButton("Save Preset")
        self.save_preset_button.clicked.connect(self.save_preset)
        layout.addWidget(self.save_preset_button)

        self.run_button = QPushButton("Run GZDoom")
        self.run_button.clicked.connect(self.run_gzdoom)
        layout.addWidget(self.run_button)

        self.back_button = QPushButton("Back to Presets")
        self.back_button.clicked.connect(self.back_to_presets)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def add_pk3_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PK3 Files", "", "PK3 Files (*.pk3);;All Files (*)")
        
        if files:
            self.pk3_files.extend(files)
            self.update_pk3_list()

    def browse_gzdoom_path(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select GZDoom.exe", "", "Executable Files (*.exe);;All Files (*)")
        if file:
            self.gzdoom_input.setText(file)
            self.save_gzdoom_path()

    def save_gzdoom_path(self):
        self.config_manager.update_gzdoom_path(self.gzdoom_input.text())

    def load_pk3_files(self):
        self.pk3_files = self.config_manager.config.get("pk3_files", [])
        self.update_pk3_list()

    def update_pk3_list(self):
        self.list_widget.clear()
        self.list_widget.addItems(self.pk3_files)

    def save_preset(self):
        preset_name, _ = QFileDialog.getSaveFileName(self, "Save Preset", "", "JSON Files (*.json)")
        if preset_name:
            with open(preset_name, 'w') as preset_file:
                json.dump(self.pk3_files, preset_file)

    def run_gzdoom(self):
        if not self.pk3_files:
            QMessageBox.warning(self, "Error", "No mods selected.")
            return
        
        gzdoom_path = self.config_manager.config.get("gzdoom_path", "")
        if not gzdoom_path:
            QMessageBox.warning(self, "Error", "GZDoom is not configured.")
            return

        command = [gzdoom_path] + ["-file"] + self.pk3_files
        subprocess.Popen(command)

    def back_to_presets(self):
        self.save_position()
        self.preset_window = PresetWindow()
        self.preset_window.show()
        self.close()

    def save_position(self):
        self.config_manager.config["options_window_position"] = (self.x(), self.y())
        self.config_manager.save_config()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()
    
    QTimer.singleShot(2000, lambda: [splash.close(), PresetWindow().show()])  # 2000 ms = 2 seconds

    sys.exit(app.exec())
