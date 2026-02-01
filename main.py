#!/usr/bin/env python3
"""
HwGDReqs - Geometry Dash Level Request Manager for Streamers
Made by MalikHw47
"""

import sys
import json
import os
import random
import time
import requests
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QLabel, QTextEdit, QDialog, QLineEdit,
    QCheckBox, QComboBox, QGroupBox, QSplashScreen, QMessageBox,
    QInputDialog, QFileDialog, QGridLayout
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPixmap, QIcon, QFont


class ConfigManager:
    """Handles all configuration and data persistence"""
    
    def __init__(self):
        if sys.platform == "win32":
            self.config_dir = Path(os.getenv('APPDATA')) / 'HwGDReqs'
        else:
            self.config_dir = Path.home() / '.hwgdreqs'
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'config.json'
        self.queue_file = self.config_dir / 'queue.json'
        self.history_file = self.config_dir / 'history.json'
        
        self.config = self.load_config()
        self.queue = self.load_queue()
        self.history = self.load_history()
    
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            'app_id': '',
            'streamer_name': '',
            'filters': {
                'length': ['Tiny', 'Short', 'Medium', 'Long', 'XL'],
                'difficulty': ['NA', 'Easy', 'Normal', 'Hard', 'Harder', 'Insane', 
                              'Easy Demon', 'Medium Demon', 'Hard Demon', 'Insane Demon', 'Extreme Demon'],
                'rated': 'both'  # 'rated', 'unrated', 'both'
            },
            'bg_type': 'gradient',  # 'gradient', 'color', 'image'
            'bg_color1': '#FF6B6B',
            'bg_color2': '#4ECDC4',
            'bg_image': '',
            'submit_message': 'Okay! {levelname} submitted to {streamername}',
            'offline_message': 'he doesnt have the app on btw :<',
            'show_donate': True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except:
                pass
        
        return default_config
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def load_queue(self):
        """Load queue from file"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_queue(self):
        """Save queue to file"""
        with open(self.queue_file, 'w') as f:
            json.dump(self.queue, f, indent=2)
    
    def load_history(self):
        """Load history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_history(self):
        """Save history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)


class QueueSyncThread(QThread):
    """Background thread for syncing queue with server"""
    
    queue_updated = Signal(list)
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.running = True
    
    def run(self):
        """Poll server for new submissions every 3 seconds"""
        while self.running:
            if self.config_manager.config.get('app_id'):
                try:
                    # Fetch queue from server
                    response = requests.get(
                        f"https://hwgdreqs.rf.gd/api.php",
                        params={
                            'id': self.config_manager.config['app_id'],
                            'action': 'fetch'
                        },
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            server_queue = data.get('queue', [])
                            if server_queue != self.config_manager.queue:
                                self.config_manager.queue = server_queue
                                self.config_manager.save_queue()
                                self.queue_updated.emit(server_queue)
                    
                    # Send heartbeat to show app is online
                    requests.post(
                        f"https://hwgdreqs.rf.gd/api.php",
                        data={
                            'id': self.config_manager.config['app_id'],
                            'action': 'heartbeat'
                        },
                        timeout=5
                    )
                except:
                    pass
            
            time.sleep(3)
    
    def stop(self):
        """Stop the sync thread"""
        self.running = False


class SettingsDialog(QDialog):
    """Settings dialog for filters and customization"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.init_ui()
    
    def init_ui(self):
        """Initialize settings UI"""
        layout = QVBoxLayout()
        
        # Streamer Name
        name_group = QGroupBox("Streamer Info")
        name_layout = QVBoxLayout()
        self.name_input = QLineEdit(self.config_manager.config.get('streamer_name', ''))
        self.name_input.setPlaceholderText("Your display name for viewers")
        name_layout.addWidget(QLabel("Streamer Name:"))
        name_layout.addWidget(self.name_input)
        name_group.setLayout(name_layout)
        layout.addWidget(name_group)
        
        # Filters Group
        filters_group = QGroupBox("Level Filters")
        filters_layout = QVBoxLayout()
        
        # Length filter
        filters_layout.addWidget(QLabel("Allowed Lengths:"))
        self.length_checks = {}
        length_layout = QHBoxLayout()
        for length in ['Tiny', 'Short', 'Medium', 'Long', 'XL']:
            cb = QCheckBox(length)
            cb.setChecked(length in self.config_manager.config['filters']['length'])
            self.length_checks[length] = cb
            length_layout.addWidget(cb)
        filters_layout.addLayout(length_layout)
        
        # Difficulty filter
        filters_layout.addWidget(QLabel("Allowed Difficulties:"))
        self.diff_checks = {}
        diff_layout1 = QHBoxLayout()
        diff_layout2 = QHBoxLayout()
        difficulties = ['NA', 'Easy', 'Normal', 'Hard', 'Harder', 'Insane']
        demons = ['Easy Demon', 'Medium Demon', 'Hard Demon', 'Insane Demon', 'Extreme Demon']
        
        for diff in difficulties:
            cb = QCheckBox(diff)
            cb.setChecked(diff in self.config_manager.config['filters']['difficulty'])
            self.diff_checks[diff] = cb
            diff_layout1.addWidget(cb)
        
        for diff in demons:
            cb = QCheckBox(diff)
            cb.setChecked(diff in self.config_manager.config['filters']['difficulty'])
            self.diff_checks[diff] = cb
            diff_layout2.addWidget(cb)
        
        filters_layout.addLayout(diff_layout1)
        filters_layout.addLayout(diff_layout2)
        
        # Rated filter
        filters_layout.addWidget(QLabel("Rated Status:"))
        self.rated_combo = QComboBox()
        self.rated_combo.addItems(['Both', 'Rated Only', 'Unrated Only'])
        current_rated = self.config_manager.config['filters']['rated']
        if current_rated == 'both':
            self.rated_combo.setCurrentIndex(0)
        elif current_rated == 'rated':
            self.rated_combo.setCurrentIndex(1)
        else:
            self.rated_combo.setCurrentIndex(2)
        filters_layout.addWidget(self.rated_combo)
        
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Background Customization
        bg_group = QGroupBox("Website Background")
        bg_layout = QVBoxLayout()
        
        self.bg_type = QComboBox()
        self.bg_type.addItems(['Gradient', 'Solid Color', 'Image'])
        current_bg = self.config_manager.config.get('bg_type', 'gradient')
        self.bg_type.setCurrentText(current_bg.title() if current_bg != 'color' else 'Solid Color')
        bg_layout.addWidget(QLabel("Background Type:"))
        bg_layout.addWidget(self.bg_type)
        
        # Gradient colors
        color_layout = QHBoxLayout()
        self.color1_input = QLineEdit(self.config_manager.config.get('bg_color1', '#FF6B6B'))
        self.color2_input = QLineEdit(self.config_manager.config.get('bg_color2', '#4ECDC4'))
        color_layout.addWidget(QLabel("Color 1:"))
        color_layout.addWidget(self.color1_input)
        color_layout.addWidget(QLabel("Color 2:"))
        color_layout.addWidget(self.color2_input)
        bg_layout.addLayout(color_layout)
        
        # Image upload
        img_layout = QHBoxLayout()
        self.img_path = QLineEdit(self.config_manager.config.get('bg_image', ''))
        img_btn = QPushButton("Browse...")
        img_btn.clicked.connect(self.browse_image)
        img_layout.addWidget(QLabel("Image:"))
        img_layout.addWidget(self.img_path)
        img_layout.addWidget(img_btn)
        bg_layout.addLayout(img_layout)
        
        bg_group.setLayout(bg_layout)
        layout.addWidget(bg_group)
        
        # Messages
        msg_group = QGroupBox("Custom Messages")
        msg_layout = QVBoxLayout()
        
        msg_layout.addWidget(QLabel("Submit Message (use {levelname}, {author}, {streamername}):"))
        self.submit_msg = QLineEdit(self.config_manager.config.get('submit_message', 
                                                                    'Okay! {levelname} submitted to {streamername}'))
        msg_layout.addWidget(self.submit_msg)
        
        msg_layout.addWidget(QLabel("Offline Message:"))
        self.offline_msg = QLineEdit(self.config_manager.config.get('offline_message', 
                                                                     'he doesnt have the app on btw :<'))
        msg_layout.addWidget(self.offline_msg)
        
        msg_group.setLayout(msg_layout)
        layout.addWidget(msg_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def browse_image(self):
        """Browse for background image"""
        filename, _ = QFileDialog.getOpenFileName(self, "Select Background Image", "", 
                                                   "Images (*.png *.jpg *.jpeg *.gif)")
        if filename:
            self.img_path.setText(filename)
    
    def save_settings(self):
        """Save all settings"""
        # Update config
        self.config_manager.config['streamer_name'] = self.name_input.text()
        
        # Update filters
        self.config_manager.config['filters']['length'] = [
            length for length, cb in self.length_checks.items() if cb.isChecked()
        ]
        self.config_manager.config['filters']['difficulty'] = [
            diff for diff, cb in self.diff_checks.items() if cb.isChecked()
        ]
        
        rated_map = {0: 'both', 1: 'rated', 2: 'unrated'}
        self.config_manager.config['filters']['rated'] = rated_map[self.rated_combo.currentIndex()]
        
        # Update background
        bg_type_map = {'Gradient': 'gradient', 'Solid Color': 'color', 'Image': 'image'}
        self.config_manager.config['bg_type'] = bg_type_map[self.bg_type.currentText()]
        self.config_manager.config['bg_color1'] = self.color1_input.text()
        self.config_manager.config['bg_color2'] = self.color2_input.text()
        self.config_manager.config['bg_image'] = self.img_path.text()
        
        # Update messages
        self.config_manager.config['submit_message'] = self.submit_msg.text()
        self.config_manager.config['offline_message'] = self.offline_msg.text()
        
        self.config_manager.save_config()
        
        # Sync settings to server
        if self.config_manager.config.get('app_id'):
            try:
                # Upload image if needed
                bg_image_url = ''
                if self.config_manager.config['bg_type'] == 'image' and self.config_manager.config['bg_image']:
                    # TODO: Upload image to server
                    bg_image_url = self.config_manager.config['bg_image']
                
                requests.post(
                    f"https://hwgdreqs.rf.gd/api.php",
                    data={
                        'id': self.config_manager.config['app_id'],
                        'action': 'update_config',
                        'config': json.dumps({
                            'streamer_name': self.config_manager.config['streamer_name'],
                            'filters': self.config_manager.config['filters'],
                            'bg_type': self.config_manager.config['bg_type'],
                            'bg_color1': self.config_manager.config['bg_color1'],
                            'bg_color2': self.config_manager.config['bg_color2'],
                            'bg_image': bg_image_url,
                            'submit_message': self.config_manager.config['submit_message'],
                            'offline_message': self.config_manager.config['offline_message']
                        })
                    },
                    timeout=5
                )
            except:
                pass
        
        self.accept()


class AboutDialog(QDialog):
    """About dialog with creator info and donation"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("About HwGDReqs")
        self.setMinimumWidth(400)
        self.init_ui()
    
    def init_ui(self):
        """Initialize about UI"""
        layout = QVBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_path = self.get_resource_path('icon.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # Title
        title = QLabel("HwGDReqs")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Geometry Dash Level Request Manager")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Creator
        creator = QLabel("\nMade by MalikHw47")
        creator.setFont(QFont("Arial", 12, QFont.Bold))
        creator.setAlignment(Qt.AlignCenter)
        layout.addWidget(creator)
        
        # Social links
        links_layout = QVBoxLayout()
        
        yt_btn = QPushButton("YouTube: @MalikHw47")
        yt_btn.clicked.connect(lambda: self.open_url("https://youtube.com/@MalikHw47"))
        links_layout.addWidget(yt_btn)
        
        twitch_btn = QPushButton("Twitch: MalikHw47")
        twitch_btn.clicked.connect(lambda: self.open_url("https://twitch.tv/MalikHw47"))
        links_layout.addWidget(twitch_btn)
        
        github_btn = QPushButton("GitHub: MalikHw47")
        github_btn.clicked.connect(lambda: self.open_url("https://github.com/MalikHw47"))
        links_layout.addWidget(github_btn)
        
        layout.addLayout(links_layout)
        
        # Donation section
        if self.config_manager.config.get('show_donate', True):
            layout.addWidget(QLabel())  # Spacer
            donate_label = QLabel("❤️ Support the project:")
            donate_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(donate_label)
            
            donate_btn_layout = QHBoxLayout()
            donate_btn = QPushButton("Donate to MHw47")
            donate_btn.clicked.connect(lambda: self.open_url("https://malikhw.github.io/donate"))
            donate_btn_layout.addWidget(donate_btn)
            
            dont_show = QPushButton("Don't show again")
            dont_show.clicked.connect(self.disable_donate)
            donate_btn_layout.addWidget(dont_show)
            
            layout.addLayout(donate_btn_layout)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def get_resource_path(self, relative_path):
        """Get absolute path to resource"""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.dirname(__file__), relative_path)
    
    def open_url(self, url):
        """Open URL in browser"""
        import webbrowser
        webbrowser.open(url)
    
    def disable_donate(self):
        """Disable donation popup"""
        self.config_manager.config['show_donate'] = False
        self.config_manager.save_config()
        self.accept()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.sync_thread = None
        self.init_ui()
        self.check_authentication()
        
        # Show donation dialog on first run
        if self.config_manager.config.get('show_donate', True) and not self.config_manager.config.get('donate_shown'):
            self.config_manager.config['donate_shown'] = True
            self.config_manager.save_config()
            QTimer.singleShot(1000, self.show_about)
    
    def init_ui(self):
        """Initialize main UI"""
        self.setWindowTitle("HwGDReqs - GD Level Request Manager")
        self.setMinimumSize(900, 600)
        
        # Set icon
        icon_path = self.get_resource_path('icon.ico' if sys.platform == 'win32' else 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Top bar with info
        top_layout = QHBoxLayout()
        self.status_label = QLabel("Not authenticated")
        self.status_label.setFont(QFont("Arial", 10, QFont.Bold))
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        
        self.link_label = QLabel()
        self.link_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        top_layout.addWidget(self.link_label)
        
        main_layout.addLayout(top_layout)
        
        # Content area - split view
        content_layout = QHBoxLayout()
        
        # Left side - Queue
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        queue_label = QLabel("Level Queue")
        queue_label.setFont(QFont("Arial", 12, QFont.Bold))
        left_layout.addWidget(queue_label)
        
        self.queue_list = QListWidget()
        self.queue_list.itemClicked.connect(self.show_level_details)
        left_layout.addWidget(self.queue_list)
        
        # Queue action buttons
        queue_btn_layout = QGridLayout()
        
        self.copy_btn = QPushButton("Copy ID")
        self.copy_btn.clicked.connect(self.copy_level_id)
        queue_btn_layout.addWidget(self.copy_btn, 0, 0)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_level)
        queue_btn_layout.addWidget(self.delete_btn, 0, 1)
        
        self.random_btn = QPushButton("Choose Random")
        self.random_btn.clicked.connect(self.choose_random)
        queue_btn_layout.addWidget(self.random_btn, 1, 0)
        
        self.report_btn = QPushButton("Report")
        self.report_btn.clicked.connect(self.report_level)
        queue_btn_layout.addWidget(self.report_btn, 1, 1)
        
        self.clear_btn = QPushButton("Clear Queue")
        self.clear_btn.clicked.connect(self.clear_queue)
        queue_btn_layout.addWidget(self.clear_btn, 2, 0)
        
        self.export_btn = QPushButton("Export Queue")
        self.export_btn.clicked.connect(self.export_queue)
        queue_btn_layout.addWidget(self.export_btn, 2, 1)
        
        left_layout.addLayout(queue_btn_layout)
        
        left_widget.setLayout(left_layout)
        content_layout.addWidget(left_widget, 2)
        
        # Right side - Level details
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        details_label = QLabel("Level Details")
        details_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        right_layout.addWidget(self.details_text)
        
        right_widget.setLayout(right_layout)
        content_layout.addWidget(right_widget, 1)
        
        main_layout.addLayout(content_layout)
        
        # Bottom action buttons
        bottom_layout = QHBoxLayout()
        
        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.show_settings)
        bottom_layout.addWidget(settings_btn)
        
        donate_btn = QPushButton("Donate to MHw47")
        donate_btn.clicked.connect(lambda: self.open_url("https://malikhw.github.io/donate"))
        bottom_layout.addWidget(donate_btn)
        
        about_btn = QPushButton("About")
        about_btn.clicked.connect(self.show_about)
        bottom_layout.addWidget(about_btn)
        
        bottom_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh Queue")
        refresh_btn.clicked.connect(self.refresh_queue)
        bottom_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(bottom_layout)
        
        central.setLayout(main_layout)
        
        # Load initial queue
        self.update_queue_display()
    
    def get_resource_path(self, relative_path):
        """Get absolute path to resource"""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.dirname(__file__), relative_path)
    
    def check_authentication(self):
        """Check if user is authenticated"""
        if not self.config_manager.config.get('app_id'):
            # Show auth dialog
            app_id, ok = QInputDialog.getText(self, "Authentication Required", 
                                              "Enter your APP-ID from hwgdreqs.rf.gd:")
            if ok and app_id:
                self.config_manager.config['app_id'] = app_id
                self.config_manager.save_config()
                self.update_status()
                self.start_sync()
            else:
                QMessageBox.warning(self, "Not Authenticated", 
                                  "Please visit https://hwgdreqs.rf.gd to get your APP-ID")
        else:
            self.update_status()
            self.start_sync()
    
    def update_status(self):
        """Update status bar"""
        if self.config_manager.config.get('app_id'):
            app_id = self.config_manager.config['app_id']
            streamer_name = self.config_manager.config.get('streamer_name', 'Unknown')
            self.status_label.setText(f"✓ Authenticated as: {streamer_name}")
            self.link_label.setText(f"Submission Link: https://hwgdreqs.rf.gd/{app_id}/submit")
        else:
            self.status_label.setText("Not authenticated")
            self.link_label.setText("")
    
    def start_sync(self):
        """Start background sync thread"""
        if not self.sync_thread:
            self.sync_thread = QueueSyncThread(self.config_manager)
            self.sync_thread.queue_updated.connect(self.update_queue_display)
            self.sync_thread.start()
    
    def update_queue_display(self):
        """Update queue list display"""
        self.queue_list.clear()
        
        for level in self.config_manager.queue:
            level_id = level.get('id', 'Unknown')
            level_name = level.get('name', 'Unknown Level')
            difficulty = level.get('difficultyFace', 'na').lower()
            is_flagged = level.get('flagged', False)
            
            # Get difficulty icon
            icon_name = difficulty if difficulty != 'extreme demon' else 'demon'
            if 'demon' in difficulty and difficulty != 'demon':
                icon_name = 'demon'
            
            icon_path = self.get_resource_path(f'icons/{icon_name}.png')
            
            item_text = f"{level_name} (ID: {level_id})"
            if is_flagged:
                item_text = f"⚠️ {item_text}"
            
            item = self.queue_list.addItem(item_text)
            
            # Try to set icon
            if os.path.exists(icon_path):
                try:
                    icon = QIcon(icon_path)
                    self.queue_list.item(self.queue_list.count() - 1).setIcon(icon)
                except:
                    pass
    
    def show_level_details(self, item):
        """Show details for selected level"""
        index = self.queue_list.row(item)
        if 0 <= index < len(self.config_manager.queue):
            level = self.config_manager.queue[index]
            
            details = f"""
<h2>{level.get('name', 'Unknown')}</h2>
<p><b>ID:</b> {level.get('id', 'N/A')}</p>
<p><b>Author:</b> {level.get('author', 'Unknown')}</p>
<p><b>Difficulty:</b> {level.get('difficulty', 'N/A')}</p>
<p><b>Length:</b> {level.get('length', 'N/A')}</p>
<p><b>Stars:</b> {level.get('stars', 0)}</p>
<p><b>Downloads:</b> {level.get('downloads', 0)}</p>
<p><b>Likes:</b> {level.get('likes', 0)}</p>
<p><b>Description:</b> {level.get('description', 'No description')}</p>
"""
            
            if level.get('flagged'):
                details += f"\n<p style='color: red;'><b>⚠️ WARNING:</b> {level.get('flag_reason', 'Flagged level')}</p>"
            
            self.details_text.setHtml(details)
    
    def copy_level_id(self):
        """Copy selected level ID to clipboard"""
        current = self.queue_list.currentRow()
        if 0 <= current < len(self.config_manager.queue):
            level_id = self.config_manager.queue[current].get('id', '')
            QApplication.clipboard().setText(str(level_id))
            QMessageBox.information(self, "Copied", f"Level ID {level_id} copied to clipboard!")
    
    def delete_level(self):
        """Delete selected level from queue"""
        current = self.queue_list.currentRow()
        if 0 <= current < len(self.config_manager.queue):
            level = self.config_manager.queue[current]
            reply = QMessageBox.question(self, "Delete Level", 
                                        f"Delete '{level.get('name')}' from queue?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                # Add to history
                self.config_manager.history.append(level)
                self.config_manager.save_history()
                
                # Remove from queue
                del self.config_manager.queue[current]
                self.config_manager.save_queue()
                self.update_queue_display()
                self.details_text.clear()
    
    def choose_random(self):
        """Choose a random level from queue"""
        if self.config_manager.queue:
            random_level = random.choice(self.config_manager.queue)
            QMessageBox.information(self, "Random Level", 
                                  f"Random pick: {random_level.get('name')} (ID: {random_level.get('id')})")
            # Select it in the list
            for i, level in enumerate(self.config_manager.queue):
                if level.get('id') == random_level.get('id'):
                    self.queue_list.setCurrentRow(i)
                    self.show_level_details(self.queue_list.item(i))
                    break
        else:
            QMessageBox.information(self, "Empty Queue", "No levels in queue!")
    
    def report_level(self):
        """Report selected level"""
        current = self.queue_list.currentRow()
        if 0 <= current < len(self.config_manager.queue):
            level = self.config_manager.queue[current]
            reason, ok = QInputDialog.getText(self, "Report Level", 
                                             f"Why are you reporting '{level.get('name')}'?")
            if ok and reason:
                try:
                    requests.post(
                        "https://hwgdreqs.rf.gd/fuck-it.php",
                        data={
                            'level_id': level.get('id'),
                            'reason': reason
                        },
                        timeout=5
                    )
                    QMessageBox.information(self, "Reported", "Level has been reported for review.")
                except:
                    QMessageBox.warning(self, "Error", "Failed to report level. Check your connection.")
    
    def clear_queue(self):
        """Clear entire queue"""
        if self.config_manager.queue:
            reply = QMessageBox.question(self, "Clear Queue", 
                                        "Are you sure you want to clear the entire queue?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                # Add all to history
                self.config_manager.history.extend(self.config_manager.queue)
                self.config_manager.save_history()
                
                # Clear queue
                self.config_manager.queue = []
                self.config_manager.save_queue()
                self.update_queue_display()
                self.details_text.clear()
    
    def export_queue(self):
        """Export queue to text file"""
        filename, _ = QFileDialog.getSaveFileName(self, "Export Queue", "", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("HwGDReqs Queue Export\n")
                    f.write("=" * 50 + "\n\n")
                    for i, level in enumerate(self.config_manager.queue, 1):
                        f.write(f"{i}. {level.get('name')} (ID: {level.get('id')})\n")
                        f.write(f"   Author: {level.get('author')}\n")
                        f.write(f"   Difficulty: {level.get('difficulty')}\n")
                        f.write(f"   Length: {level.get('length')}\n\n")
                QMessageBox.information(self, "Exported", f"Queue exported to {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export: {str(e)}")
    
    def refresh_queue(self):
        """Manually refresh queue from server"""
        if self.config_manager.config.get('app_id'):
            try:
                response = requests.get(
                    f"https://hwgdreqs.rf.gd/api.php",
                    params={
                        'id': self.config_manager.config['app_id'],
                        'action': 'fetch'
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.config_manager.queue = data.get('queue', [])
                        self.config_manager.save_queue()
                        self.update_queue_display()
                        QMessageBox.information(self, "Refreshed", "Queue refreshed from server!")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to fetch queue from server.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Connection error: {str(e)}")
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            self.update_status()
    
    def show_about(self):
        """Show about dialog"""
        dialog = AboutDialog(self.config_manager, self)
        dialog.exec()
    
    def open_url(self, url):
        """Open URL in browser"""
        import webbrowser
        webbrowser.open(url)
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.sync_thread:
            self.sync_thread.stop()
            self.sync_thread.wait()
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("HwGDReqs")
    
    # Show splash screen
    splash_path = os.path.join(os.path.dirname(__file__), 'icon.png')
    if os.path.exists(splash_path):
        splash_pix = QPixmap(splash_path).scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        splash = QSplashScreen(splash_pix)
        splash.show()
        app.processEvents()
        time.sleep(1)
    
    # Initialize config manager
    config_manager = ConfigManager()
    
    # Create and show main window
    window = MainWindow(config_manager)
    window.show()
    
    if os.path.exists(splash_path):
        splash.finish(window)
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
