#!/usr/bin/env python3
"""
HwGDReqs - Geometry Dash Level Request Manager for Streamers
Made by MalikHw47
"""

import sys
import os
import json
import requests
import random
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QTextEdit, QLabel, QDialog, QLineEdit,
    QComboBox, QCheckBox, QMessageBox, QSplashScreen, QGridLayout,
    QGroupBox, QScrollArea, QDialogButtonBox, QInputDialog, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon, QColor


class HwGDReqs(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_dir = self.get_app_dir()
        self.config_file = self.app_dir / "config.json"
        self.queue_file = self.app_dir / "queue.json"
        self.history_file = self.app_dir / "history.json"
        
        self.config = self.load_config()
        self.queue = self.load_queue()
        self.history = self.load_history()
        
        self.api_base = "https://hwgdreqs.rf.gd"
        self.gd_api = "https://gdbrowser.com/api/level"
        self.blacklist_url = "https://raw.githubusercontent.com/malikhw/hwgdbot-db/main/fuck-out.json"
        
        self.init_ui()
        self.load_queue_to_list()
        
        # Auto-refresh timer (every 5 seconds)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.fetch_queue_from_server)
        self.refresh_timer.start(5000)
        
        # Show donation popup on first run
        if not self.config.get("donation_dismissed", False):
            QTimer.singleShot(500, self.show_donation_popup)
    
    def get_app_dir(self):
        """Get application data directory"""
        if sys.platform == "win32":
            app_dir = Path(os.getenv("APPDATA")) / "HwGDReqs"
        else:
            app_dir = Path.home() / ".hwgdreqs"
        
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir
    
    def load_config(self):
        """Load configuration file"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "app_id": "",
            "streamer_name": "",
            "filters": {
                "length": ["Tiny", "Short", "Medium", "Long", "XL"],
                "difficulty": ["NA", "Easy", "Normal", "Hard", "Harder", "Insane", 
                              "Easy Demon", "Medium Demon", "Hard Demon", "Insane Demon", "Extreme Demon"],
                "rated": "both"
            },
            "bg_type": "gradient",
            "bg_color1": "#ff6b6b",
            "bg_color2": "#4ecdc4",
            "bg_image": "",
            "custom_message": "Okay! {levelname} submitted to {streamername}!",
            "donation_dismissed": False
        }
    
    def save_config(self):
        """Save configuration file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    def load_queue(self):
        """Load queue file"""
        if self.queue_file.exists():
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_queue(self):
        """Save queue file"""
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(self.queue, f, indent=2)
    
    def load_history(self):
        """Load history file"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_history(self):
        """Save history file"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("HwGDReqs - GD Level Request Manager")
        self.setGeometry(100, 100, 1000, 600)
        
        # Set window icon
        icon_path = self.get_resource_path("icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel - Queue
        left_panel = QVBoxLayout()
        
        # Queue label
        queue_label = QLabel("Request Queue")
        queue_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        left_panel.addWidget(queue_label)
        
        # Queue list
        self.queue_list = QListWidget()
        self.queue_list.itemClicked.connect(self.show_level_details)
        left_panel.addWidget(self.queue_list)
        
        # Action buttons
        button_layout = QGridLayout()
        
        self.copy_btn = QPushButton("Copy ID")
        self.copy_btn.clicked.connect(self.copy_level_id)
        button_layout.addWidget(self.copy_btn, 0, 0)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_level)
        button_layout.addWidget(self.delete_btn, 0, 1)
        
        self.random_btn = QPushButton("Choose Random")
        self.random_btn.clicked.connect(self.choose_random)
        button_layout.addWidget(self.random_btn, 1, 0)
        
        self.report_btn = QPushButton("Report")
        self.report_btn.clicked.connect(self.report_level)
        button_layout.addWidget(self.report_btn, 1, 1)
        
        self.clear_btn = QPushButton("Clear Queue")
        self.clear_btn.clicked.connect(self.clear_queue)
        button_layout.addWidget(self.clear_btn, 2, 0)
        
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_btn, 2, 1)
        
        self.export_btn = QPushButton("Export Queue")
        self.export_btn.clicked.connect(self.export_queue)
        button_layout.addWidget(self.export_btn, 3, 0)
        
        self.donate_btn = QPushButton("Donate to MHw47")
        self.donate_btn.clicked.connect(self.open_donation)
        button_layout.addWidget(self.donate_btn, 3, 1)
        
        left_panel.addLayout(button_layout)
        
        # Right panel - Level details
        right_panel = QVBoxLayout()
        
        details_label = QLabel("Level Details")
        details_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        right_panel.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        right_panel.addWidget(self.details_text)
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 60)
        main_layout.addLayout(right_panel, 40)
        
        # Menu bar
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
    
    def get_resource_path(self, relative_path):
        """Get absolute path to resource (for bundled apps)"""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.dirname(__file__), relative_path)
    
    def get_difficulty_icon(self, difficulty):
        """Get the difficulty icon path"""
        diff_map = {
            "NA": "na.png",
            "Easy": "easy.png",
            "Normal": "normal.png",
            "Hard": "hard.png",
            "Harder": "harder.png",
            "Insane": "insane.png",
            "Easy Demon": "demon.png",
            "Medium Demon": "demon.png",
            "Hard Demon": "demon.png",
            "Insane Demon": "demon.png",
            "Extreme Demon": "demon.png"
        }
        
        icon_name = diff_map.get(difficulty, "na.png")
        icon_path = self.get_resource_path(f"icons/{icon_name}")
        return icon_path if os.path.exists(icon_path) else None
    
    def load_queue_to_list(self):
        """Load queue items to the list widget"""
        self.queue_list.clear()
        for level in self.queue:
            item_text = f"{level['name']} by {level['author']}"
            
            # Add warning symbol if blacklisted
            if level.get('blacklisted', False):
                item_text = f"⚠️ {item_text}"
            
            item = QListWidgetItem(item_text)
            
            # Set icon
            icon_path = self.get_difficulty_icon(level.get('difficulty', 'NA'))
            if icon_path:
                item.setIcon(QIcon(icon_path))
            
            # Store level data
            item.setData(Qt.ItemDataRole.UserRole, level)
            
            self.queue_list.addItem(item)
    
    def show_level_details(self, item):
        """Show level details in the right panel"""
        level = item.data(Qt.ItemDataRole.UserRole)
        
        details = f"""
<h2>{level['name']}</h2>
<p><b>Author:</b> {level['author']}</p>
<p><b>Level ID:</b> {level['id']}</p>
<p><b>Difficulty:</b> {level.get('difficulty', 'NA')}</p>
<p><b>Length:</b> {level.get('length', 'Unknown')}</p>
<p><b>Stars:</b> {level.get('stars', 0)}</p>
<p><b>Downloads:</b> {level.get('downloads', 0)}</p>
<p><b>Likes:</b> {level.get('likes', 0)}</p>
<p><b>Description:</b> {level.get('description', 'No description')}</p>
"""
        
        if level.get('blacklisted', False):
            details += f"""
<p style='color: red; font-weight: bold;'>⚠️ WARNING: This level is blacklisted!</p>
<p><b>Reason:</b> {level.get('blacklist_reason', 'Unknown')}</p>
<p><b>DO NOT PLAY IF STREAMING!</b></p>
"""
        
        self.details_text.setHtml(details)
    
    def copy_level_id(self):
        """Copy selected level ID to clipboard"""
        current_item = self.queue_list.currentItem()
        if current_item:
            level = current_item.data(Qt.ItemDataRole.UserRole)
            clipboard = QApplication.clipboard()
            clipboard.setText(level['id'])
            QMessageBox.information(self, "Copied", f"Level ID {level['id']} copied to clipboard!")
    
    def delete_level(self):
        """Delete selected level from queue"""
        current_row = self.queue_list.currentRow()
        if current_row >= 0:
            level = self.queue[current_row]
            
            # Move to history
            self.history.append(level)
            self.save_history()
            
            # Remove from queue
            self.queue.pop(current_row)
            self.save_queue()
            self.load_queue_to_list()
            self.details_text.clear()
            
            # Sync with server
            self.sync_queue_to_server()
    
    def choose_random(self):
        """Choose a random level from queue"""
        if self.queue:
            random_level = random.choice(self.queue)
            QMessageBox.information(
                self, 
                "Random Level", 
                f"Random pick:\n\n{random_level['name']} by {random_level['author']}\nID: {random_level['id']}"
            )
            
            # Find and select the item
            for i in range(self.queue_list.count()):
                item = self.queue_list.item(i)
                level = item.data(Qt.ItemDataRole.UserRole)
                if level['id'] == random_level['id']:
                    self.queue_list.setCurrentRow(i)
                    self.show_level_details(item)
                    break
        else:
            QMessageBox.warning(self, "Empty Queue", "The queue is empty!")
    
    def report_level(self):
        """Report a level"""
        current_item = self.queue_list.currentItem()
        if current_item:
            level = current_item.data(Qt.ItemDataRole.UserRole)
            reason, ok = QInputDialog.getText(
                self, 
                "Report Level", 
                f"Report reason for '{level['name']}':"
            )
            
            if ok and reason:
                try:
                    response = requests.post(
                        f"{self.api_base}/fuck-it.php",
                        json={
                            "level_id": level['id'],
                            "level_name": level['name'],
                            "reason": reason
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        QMessageBox.information(self, "Reported", "Level reported successfully!")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to report level.")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to report: {str(e)}")
    
    def clear_queue(self):
        """Clear all levels from queue"""
        reply = QMessageBox.question(
            self,
            "Clear Queue",
            "Are you sure you want to clear the entire queue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Move all to history
            self.history.extend(self.queue)
            self.save_history()
            
            # Clear queue
            self.queue = []
            self.save_queue()
            self.load_queue_to_list()
            self.details_text.clear()
            
            # Sync with server
            self.sync_queue_to_server()
    
    def export_queue(self):
        """Export queue to text file"""
        if not self.queue:
            QMessageBox.warning(self, "Empty Queue", "The queue is empty!")
            return
        
        export_path = self.app_dir / "queue_export.txt"
        
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write("HwGDReqs Queue Export\n")
            f.write("=" * 50 + "\n\n")
            for i, level in enumerate(self.queue, 1):
                f.write(f"{i}. {level['name']} by {level['author']}\n")
                f.write(f"   ID: {level['id']}\n")
                f.write(f"   Difficulty: {level.get('difficulty', 'NA')}\n")
                f.write(f"   Length: {level.get('length', 'Unknown')}\n\n")
        
        QMessageBox.information(self, "Exported", f"Queue exported to:\n{export_path}")
    
    def open_donation(self):
        """Open donation page"""
        import webbrowser
        webbrowser.open("https://malikhw.github.io/donate")
    
    def show_donation_popup(self):
        """Show donation popup on first run"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Support the Developer")
        dialog.setModal(True)
        
        layout = QVBoxLayout()
        
        label = QLabel(
            "Hi! I'm MalikHw47, the creator of HwGDReqs.\n\n"
            "If you find this tool useful, please consider supporting me!\n"
            "Your donations help me create more awesome tools."
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        
        button_layout = QHBoxLayout()
        
        donate_btn = QPushButton("Donate")
        donate_btn.clicked.connect(lambda: [self.open_donation(), dialog.accept()])
        button_layout.addWidget(donate_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(close_btn)
        
        dont_show_btn = QPushButton("Don't show again")
        dont_show_btn.clicked.connect(lambda: [self.dismiss_donation(), dialog.accept()])
        button_layout.addWidget(dont_show_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()
    
    def dismiss_donation(self):
        """Dismiss donation popup permanently"""
        self.config["donation_dismissed"] = True
        self.save_config()
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self, self.config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.config = dialog.get_config()
            self.save_config()
            self.sync_settings_to_server()
    
    def show_about(self):
        """Show about dialog"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def fetch_queue_from_server(self):
        """Fetch queue from server"""
        if not self.config.get("app_id"):
            return
        
        try:
            response = requests.get(
                f"{self.api_base}/api.php",
                params={"id": self.config["app_id"], "action": "fetch"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    server_queue = data.get("queue", [])
                    
                    # Check for new levels
                    if len(server_queue) > len(self.queue):
                        # New level(s) submitted
                        pass  # Could add sound notification here if implemented
                    
                    self.queue = server_queue
                    self.save_queue()
                    self.load_queue_to_list()
        except Exception:
            pass  # Silently fail for auto-refresh
    
    def sync_queue_to_server(self):
        """Sync queue to server"""
        if not self.config.get("app_id"):
            return
        
        try:
            requests.post(
                f"{self.api_base}/api.php",
                json={
                    "id": self.config["app_id"],
                    "action": "update_queue",
                    "queue": self.queue
                },
                timeout=10
            )
        except Exception:
            pass
    
    def sync_settings_to_server(self):
        """Sync settings to server"""
        if not self.config.get("app_id"):
            return
        
        try:
            requests.post(
                f"{self.api_base}/api.php",
                json={
                    "id": self.config["app_id"],
                    "action": "update_config",
                    "config": self.config
                },
                timeout=10
            )
        except Exception:
            pass


class SettingsDialog(QDialog):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config.copy()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # APP-ID section
        app_id_group = QGroupBox("Authentication")
        app_id_layout = QVBoxLayout()
        
        app_id_label = QLabel("APP-ID (from hwgdreqs.rf.gd):")
        app_id_layout.addWidget(app_id_label)
        
        self.app_id_input = QLineEdit()
        self.app_id_input.setText(self.config.get("app_id", ""))
        self.app_id_input.setPlaceholderText("Enter your APP-ID here")
        app_id_layout.addWidget(self.app_id_input)
        
        app_id_group.setLayout(app_id_layout)
        scroll_layout.addWidget(app_id_group)
        
        # Streamer name
        name_group = QGroupBox("Streamer Information")
        name_layout = QVBoxLayout()
        
        name_label = QLabel("Streamer Name:")
        name_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setText(self.config.get("streamer_name", ""))
        self.name_input.setPlaceholderText("Your name for viewers to see")
        name_layout.addWidget(self.name_input)
        
        name_group.setLayout(name_layout)
        scroll_layout.addWidget(name_group)
        
        # Filters section
        filters_group = QGroupBox("Level Filters")
        filters_layout = QVBoxLayout()
        
        # Length filter
        length_label = QLabel("Allowed Lengths:")
        filters_layout.addWidget(length_label)
        
        self.length_checks = {}
        length_layout = QHBoxLayout()
        for length in ["Tiny", "Short", "Medium", "Long", "XL"]:
            cb = QCheckBox(length)
            cb.setChecked(length in self.config["filters"]["length"])
            self.length_checks[length] = cb
            length_layout.addWidget(cb)
        filters_layout.addLayout(length_layout)
        
        # Difficulty filter
        diff_label = QLabel("Allowed Difficulties:")
        filters_layout.addWidget(diff_label)
        
        self.diff_checks = {}
        diff_layout1 = QHBoxLayout()
        for diff in ["NA", "Easy", "Normal", "Hard", "Harder", "Insane"]:
            cb = QCheckBox(diff)
            cb.setChecked(diff in self.config["filters"]["difficulty"])
            self.diff_checks[diff] = cb
            diff_layout1.addWidget(cb)
        filters_layout.addLayout(diff_layout1)
        
        diff_layout2 = QHBoxLayout()
        for diff in ["Easy Demon", "Medium Demon", "Hard Demon", "Insane Demon", "Extreme Demon"]:
            cb = QCheckBox(diff)
            cb.setChecked(diff in self.config["filters"]["difficulty"])
            self.diff_checks[diff] = cb
            diff_layout2.addWidget(cb)
        filters_layout.addLayout(diff_layout2)
        
        # Rated filter
        rated_label = QLabel("Rated Filter:")
        filters_layout.addWidget(rated_label)
        
        self.rated_combo = QComboBox()
        self.rated_combo.addItems(["Both", "Rated Only", "Unrated Only"])
        current_rated = self.config["filters"].get("rated", "both")
        if current_rated == "rated":
            self.rated_combo.setCurrentText("Rated Only")
        elif current_rated == "unrated":
            self.rated_combo.setCurrentText("Unrated Only")
        else:
            self.rated_combo.setCurrentText("Both")
        filters_layout.addWidget(self.rated_combo)
        
        filters_group.setLayout(filters_layout)
        scroll_layout.addWidget(filters_group)
        
        # Website customization
        web_group = QGroupBox("Website Customization")
        web_layout = QVBoxLayout()
        
        # Background type
        bg_type_label = QLabel("Background Type:")
        web_layout.addWidget(bg_type_label)
        
        self.bg_type_combo = QComboBox()
        self.bg_type_combo.addItems(["Gradient", "Solid Color", "Image"])
        self.bg_type_combo.setCurrentText(self.config.get("bg_type", "gradient").title())
        web_layout.addWidget(self.bg_type_combo)
        
        # Colors
        color_layout = QHBoxLayout()
        
        color1_label = QLabel("Color 1:")
        color_layout.addWidget(color1_label)
        
        self.color1_input = QLineEdit()
        self.color1_input.setText(self.config.get("bg_color1", "#ff6b6b"))
        color_layout.addWidget(self.color1_input)
        
        color2_label = QLabel("Color 2:")
        color_layout.addWidget(color2_label)
        
        self.color2_input = QLineEdit()
        self.color2_input.setText(self.config.get("bg_color2", "#4ecdc4"))
        color_layout.addWidget(self.color2_input)
        
        web_layout.addLayout(color_layout)
        
        # Custom message
        msg_label = QLabel("Success Message (variables: {levelname}, {streamername}, {author}):")
        web_layout.addWidget(msg_label)
        
        self.msg_input = QLineEdit()
        self.msg_input.setText(self.config.get("custom_message", "Okay! {levelname} submitted to {streamername}!"))
        web_layout.addWidget(self.msg_input)
        
        web_group.setLayout(web_layout)
        scroll_layout.addWidget(web_group)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_config(self):
        """Get updated config"""
        self.config["app_id"] = self.app_id_input.text()
        self.config["streamer_name"] = self.name_input.text()
        
        # Filters
        self.config["filters"]["length"] = [
            length for length, cb in self.length_checks.items() if cb.isChecked()
        ]
        self.config["filters"]["difficulty"] = [
            diff for diff, cb in self.diff_checks.items() if cb.isChecked()
        ]
        
        rated_text = self.rated_combo.currentText()
        if rated_text == "Rated Only":
            self.config["filters"]["rated"] = "rated"
        elif rated_text == "Unrated Only":
            self.config["filters"]["rated"] = "unrated"
        else:
            self.config["filters"]["rated"] = "both"
        
        # Website customization
        self.config["bg_type"] = self.bg_type_combo.currentText().lower()
        self.config["bg_color1"] = self.color1_input.text()
        self.config["bg_color2"] = self.color2_input.text()
        self.config["custom_message"] = self.msg_input.text()
        
        return self.config


class AboutDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("About HwGDReqs")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("HwGDReqs")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Geometry Dash Level Request Manager for Streamers")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Made by
        made_by = QLabel("Made by MalikHw47")
        made_by.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        made_by.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(made_by)
        
        # Social buttons
        button_layout = QVBoxLayout()
        
        youtube_btn = QPushButton("YouTube: @MalikHw47")
        youtube_btn.clicked.connect(lambda: self.open_url("https://youtube.com/@MalikHw47"))
        button_layout.addWidget(youtube_btn)
        
        twitch_btn = QPushButton("Twitch: MalikHw47")
        twitch_btn.clicked.connect(lambda: self.open_url("https://twitch.tv/MalikHw47"))
        button_layout.addWidget(twitch_btn)
        
        github_btn = QPushButton("GitHub: MalikHw47")
        github_btn.clicked.connect(lambda: self.open_url("https://github.com/MalikHw47"))
        button_layout.addWidget(github_btn)
        
        layout.addLayout(button_layout)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)


def show_splash():
    """Show splash screen"""
    app = QApplication.instance()
    
    splash_path = os.path.join(os.path.dirname(__file__), "icon.png")
    if os.path.exists(splash_path):
        pixmap = QPixmap(splash_path)
        splash = QSplashScreen(pixmap)
        splash.show()
        app.processEvents()
        
        # Show for 1 second
        QTimer.singleShot(1000, splash.close)
        
        return splash
    return None


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HwGDReqs")
    app.setOrganizationName("MalikHw47")
    
    # Show splash screen
    splash = show_splash()
    if splash:
        import time
        time.sleep(1)
    
    # Create main window
    window = HwGDReqs()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
