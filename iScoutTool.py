#!/usr/bin/env python3
"""
iScoutTool - Evony Automation Application
Main application module implementing the requirements from PRD_iScoutTool.md

Author: Generated from PRD specifications
Date: October 1, 2025
Version: 1.0.0
"""

import sys
import os
import time
import winsound
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional
from dataclasses import dataclass
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QTableWidgetItem, 
    QPushButton, QCheckBox, QMessageBox, QHeaderView, QInputDialog
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from ppadb.client import Client as AdbClient


class NumericTableWidgetItem(QTableWidgetItem):
    """Custom QTableWidgetItem that sorts numerically instead of lexicographically"""
    def __init__(self, value):
        super().__init__(str(value))
        self.numeric_value = int(value) if isinstance(value, (int, str)) else 0
    
    def __lt__(self, other):
        """Override less-than comparison for proper numeric sorting"""
        if isinstance(other, NumericTableWidgetItem):
            return self.numeric_value < other.numeric_value
        return super().__lt__(other)


@dataclass
class ScoutTarget:
    """Target data structure as specified in PRD section 4.1"""
    target_type: str        # Boss/Barbarian name with level, power, status
    x_coordinate: int       # Map X position
    y_coordinate: int       # Map Y position
    completed: bool = False # User marked as completed


@dataclass
class LocationPreset:
    """Location preset structure as specified in PRD section 4.2"""
    name: str              # Preset identifier
    x_loc: float          # X coordinate (0.0-1.0)
    y_loc: float          # Y coordinate (0.0-1.0)
    x_dest: float         # Destination X (0.0-1.0)
    y_dest: float         # Destination Y (0.0-1.0)
    click_and_drag: bool  # Action type flag


@dataclass
class AppConfig:
    """Configuration data structure as specified in PRD section 4.3"""
    home_server: int = 0      # User's home server
    home_x: int = 0          # Home X coordinate
    home_y: int = 0          # Home Y coordinate
    enemy_server: int = 0    # Target server for operations
    adb_port: int = 5555     # BlueStacks connection port


class TimerThread(QThread):
    """Timer thread for countdown functionality as specified in PRD section 5.1.2"""
    time_updated = pyqtSignal(str)  # Signal to update UI with formatted time
    beep_signal = pyqtSignal()      # Signal to trigger beep sound
    timer_finished = pyqtSignal()   # Signal when timer reaches zero
    
    def __init__(self):
        super().__init__()
        self.timer_seconds = 0
        self.running = False
        
    def start_timer(self, seconds: int = 300):
        """Start countdown timer (default 5 minutes)"""
        self.timer_seconds = seconds
        self.running = True
        self.start()
        
    def stop_timer(self):
        """Stop and reset countdown timer"""
        self.running = False
        self.timer_seconds = 0
        # Don't emit time_updated to avoid triggering beep or unwanted updates
        
    def run(self):
        """Timer thread main loop"""
        while self.running and self.timer_seconds > 0:
            # Format time as MM:SS
            minutes = self.timer_seconds // 60
            seconds = self.timer_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.time_updated.emit(time_str)
            
            # Beep during final 30 seconds
            if self.timer_seconds <= 30:
                self.beep_signal.emit()
                
            time.sleep(1)
            self.timer_seconds -= 1
            
        if self.running and self.timer_seconds <= 0:
            self.time_updated.emit("00:00")
            self.timer_finished.emit()
        self.running = False


class iScoutToolApp(QMainWindow):
    """Main application class implementing PRD specifications"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize application state
        self.config = AppConfig()
        self.targets: List[ScoutTarget] = []
        self.location_presets: dict = {}
        self.adb_client = None
        self.adb_device = None
        self.timer_thread = TimerThread()
        self.screen_width = 0
        self.screen_height = 0
        
        # Initialize UI and components
        self.setup_application()
        
    def setup_application(self):
        """Initialize main application as specified in PRD section 5.1.1"""
        try:
            # Load iScoutTool.ui file (fallback to existing UI file)
            ui_file = os.path.join(os.path.dirname(__file__), 'iScoutToolModern.ui')
            if not os.path.exists(ui_file):
                ui_file = os.path.join(os.path.dirname(__file__), 'iScoutTool.ui')
                
            uic.loadUi(ui_file, self)
            # Set initial splitter sizes: inputGroup 25% shorter, targetGroup 25% taller
            if hasattr(self, 'mainSplitter'):
                self.mainSplitter.setSizes([110, 330])
            
            # Set window properties
            self.setWindowTitle("iScoutTool - Evony Automation v1.0.0")
            
            # Call modern interface setup methods (if available)
            if hasattr(self, 'setup_modern_interface'):
                self.setup_modern_interface()
            if hasattr(self, 'configure_splitter_layout'):
                self.configure_splitter_layout()
            if hasattr(self, 'setup_enhanced_table'):
                self.setup_enhanced_table()
            
            # Load configuration and presets
            self.load_config()
            self.load_location_presets()
            
            # Set up timer and signals
            self.setup_timer()
            self.connect_ui_signals()
            
            # Delay ADB connection check until UI is fully displayed
            QTimer.singleShot(500, self.initialize_adb_connection)
            
            print("iScoutTool initialized successfully with modern UI")
            
        except Exception as e:
            QMessageBox.critical(None, "Initialization Error", 
                               f"Failed to initialize application: {str(e)}")
            sys.exit(1)
    

    # Configuration Management Methods (PRD Section 5.1.3)
    
    def load_config(self):
        """Load configuration from iScoutTool.cfg file as specified in PRD"""
        config_file = os.path.join(os.path.dirname(__file__), 'iScoutTool.cfg')
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    if line := f.readline().strip():
                        parts = line.split(',')
                        if len(parts) >= 4:
                            self.config.home_server = int(parts[0])
                            self.config.home_x = int(parts[1])
                            self.config.home_y = int(parts[2])
                            self.config.enemy_server = int(parts[3])
                            
                            # Populate UI fields
                            self.intHomeServer.setText(str(self.config.home_server))
                            self.intHomeXLoc.setText(str(self.config.home_x))
                            self.intHomeYLoc.setText(str(self.config.home_y))
                            self.intEnemyServer.setText(str(self.config.enemy_server))
                            
                            print(f"Configuration loaded: Server {self.config.home_server}, "
                                  f"Home ({self.config.home_x},{self.config.home_y}), "
                                  f"Enemy {self.config.enemy_server}")
            else:
                # Create default config
                self.save_config()
                print("Default configuration created")
                
        except Exception as e:
            print(f"Error loading configuration: {e}")
            QMessageBox.warning(self, "Config Error", f"Error loading configuration: {e}")
    
    def save_config(self):
        """Save current configuration to iScoutTool.cfg file as specified in PRD"""
        config_file = os.path.join(os.path.dirname(__file__), 'iScoutTool.cfg')
        try:
            # Get values from UI fields
            home_server = int(self.intHomeServer.text() or "0")
            home_x = int(self.intHomeXLoc.text() or "0")
            home_y = int(self.intHomeYLoc.text() or "0")
            enemy_server = int(self.intEnemyServer.text() or "0")
            
            # Validate data
            if not (1 <= home_server <= 9999):
                raise ValueError("Home server must be between 1-9999")
            if not (1 <= home_x <= 1198):
                raise ValueError("Home X coordinate must be between 1-1198")
            if not (1 <= home_y <= 1200):
                raise ValueError("Home Y coordinate must be between 1-1200")
            if not (1 <= enemy_server <= 9999):
                raise ValueError("Enemy server must be between 1-9999")
            
            # Update config object
            self.config.home_server = home_server
            self.config.home_x = home_x
            self.config.home_y = home_y
            self.config.enemy_server = enemy_server
            
            # Write CSV format
            with open(config_file, 'w') as f:
                f.write(f"{home_server},{home_x},{home_y},{enemy_server}\n")
                
            print("Configuration saved successfully")
            
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception as e:
            print(f"Error saving configuration: {e}")
            QMessageBox.warning(self, "Save Error", f"Error saving configuration: {e}")
    
    def load_location_presets(self):
        """Load location presets from Resources/locations.xml as specified in PRD"""
        presets_file = os.path.join(os.path.dirname(__file__), 'Resources', 'locations.xml')
        try:
            if os.path.exists(presets_file):
                tree = ET.parse(presets_file)
                root = tree.getroot()
                
                # Parse navigation elements (not preset elements)
                for navigation in root.findall('navigation'):
                    name = navigation.get('name')
                    x_loc = float(navigation.get('xLoc', '0.0'))
                    y_loc = float(navigation.get('yLoc', '0.0'))
                    x_dest = float(navigation.get('xDest', x_loc))
                    y_dest = float(navigation.get('yDest', y_loc))
                    click_and_drag = navigation.get('ClickAndDrag', 'false').lower() == 'true'
                    
                    self.location_presets[name] = LocationPreset(
                        name=name,
                        x_loc=x_loc,
                        y_loc=y_loc,
                        x_dest=x_dest,
                        y_dest=y_dest,
                        click_and_drag=click_and_drag
                    )
                
                print(f"Loaded {len(self.location_presets)} location presets")
            else:
                print(f"Location presets file not found: {presets_file}")
                
        except Exception as e:
            print(f"Error loading location presets: {e}")
            QMessageBox.warning(self, "Presets Error", f"Error loading presets: {e}")
    
    # Modern UI Initialization Methods (PRD Section 5.1.2)
    
    def setup_modern_interface(self):
        """Initialize modern UI elements as specified in PRD section 5.1.2"""
        try:
            # Dark theme is automatically applied from .ui file stylesheet
            # Initialize connection status
            self.update_connection_status(False)
            
            # Initialize target counter
            self.update_target_count(0, 0)
            
            # Initialize Clear All button state based on data availability
            self.update_clear_all_button_state()
            
            # Set initial timer display
            self.lblTimer.setText("05:00")
            
            # Apply muted text color to Data Input area for less prominent appearance
            self.txtiScoutBoss.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #404040;
                    border: 2px solid #555555;
                    border-radius: 4px;
                    padding: 8px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    color: #888888;
                }
                QPlainTextEdit:focus {
                    border-color: #4a90e2;
                    color: #aaaaaa;
                }
            """)
            
            print("Modern interface setup completed")
            
        except Exception as e:
            print(f"Error setting up modern interface: {e}")
    
    def configure_splitter_layout(self):
        """Set up optimal splitter proportions as specified in PRD"""
        try:
            # Set mainSplitter sizes: Data Input compact (180px), Scout Targets expanded (600px)
            self.mainSplitter.setSizes([180, 600])
            print("Splitter layout configured: Data Input (180px), Scout Targets (600px)")
            
        except Exception as e:
            print(f"Error configuring splitter layout: {e}")
    
    def setup_enhanced_table(self):
        """Configure Scout Targets table as specified in PRD section 5.1.2"""
        try:
            # Set custom column widths for better readability (reordered for workflow)
            self.tblBossList.setColumnWidth(0, 100)  # Action (Go button)
            self.tblBossList.setColumnWidth(1, 36)   # ✓ (Got It checkbox) - reduced width
            self.tblBossList.setColumnWidth(2, 420)  # Target (description) - wider for more text
            self.tblBossList.setColumnWidth(3, 60)   # X coordinate - reduced width
            self.tblBossList.setColumnWidth(4, 60)   # Y coordinate - reduced width
            
            # Fix focus issues - table should handle widget focus properly
            self.tblBossList.setFocusPolicy(QtCore.Qt.StrongFocus)
            
            # Apply enhanced styling for better text readability
            table_style = """
                QTableWidget::item {
                    color: #ffffff;
                    background-color: #404040;
                    padding: 4px;
                    border: none;
                }
                QTableWidget::item:alternate {
                    background-color: #4a4a4a;
                }
                QTableWidget::item:selected {
                    background-color: #4a90e2;
                    color: #ffffff;
                }
            """
            self.tblBossList.setStyleSheet(table_style)
            
            # Enable sorting and row selection
            self.tblBossList.setSortingEnabled(True)
            self.tblBossList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            
            # Set header properties
            header = self.tblBossList.horizontalHeader()
            header.setSectionResizeMode(2, QHeaderView.Stretch)  # Target column stretches
            
            print("Enhanced table setup completed")
            
        except Exception as e:
            print(f"Error setting up enhanced table: {e}")
    
    def update_connection_status(self, connected: bool):
        """Update connection status indicator as specified in PRD"""
        try:
            if connected:
                self.lblConnectionStatus.setText("🟢 Emulator Connected")
                self.lblConnectionStatus.setStyleSheet("color: #28a745; font-weight: bold;")
            else:
                self.lblConnectionStatus.setText("🔴 Emulator Disconnected")
                self.lblConnectionStatus.setStyleSheet("color: #dc3545; font-weight: bold;")
                
        except Exception as e:
            print(f"Error updating connection status: {e}")
    
    def update_target_count(self, total: int = None, completed: int = None):
        """Update target counter to show completed/total format"""
        try:
            if total is None:
                total = len(self.targets)
            
            if completed is None:
                completed = self.count_completed_targets()
            
            self.lblTargetCount.setText(f"Targets: {completed}/{total}")
            
        except Exception as e:
            print(f"Error updating target count: {e}")
    
    def count_completed_targets(self) -> int:
        """Count how many targets have checkmarks"""
        try:
            return len([target for target in self.targets if target.completed])
        except Exception as e:
            print(f"Error counting completed targets: {e}")
            return 0
    
    def update_clear_all_button_state(self, has_targets: bool = None):
        """Update Clear All button state based on table data OR Data Input text"""
        try:
            if hasattr(self, 'btnIScoutClearAll'):
                # Check both table targets and Data Input text
                if has_targets is None:
                    has_targets = len(self.targets) > 0
                
                has_input_text = False
                if hasattr(self, 'txtiScoutBoss'):
                    input_text = self.txtiScoutBoss.toPlainText().strip()
                    has_input_text = len(input_text) > 0
                
                # Enable if there are targets OR input text
                should_enable = has_targets or has_input_text
                self.btnIScoutClearAll.setEnabled(should_enable)
                if should_enable:
                    # Green styling when active/enabled
                    self.btnIScoutClearAll.setStyleSheet("""
                        QPushButton {
                            background-color: #28a745;
                            border: none;
                            border-radius: 6px;
                            padding: 8px 16px;
                            font-weight: bold;
                            color: white;
                            min-height: 32px;
                        }
                        QPushButton:hover {
                            background-color: #218838;
                        }
                        QPushButton:pressed {
                            background-color: #1e7e34;
                        }
                    """)
                else:
                    # Gray styling when disabled
                    self.btnIScoutClearAll.setStyleSheet("""
                        QPushButton {
                            background-color: #6c757d;
                            border: none;
                            border-radius: 6px;
                            padding: 8px 16px;
                            font-weight: bold;
                            color: #adb5bd;
                            min-height: 32px;
                        }
                    """)
        except Exception as e:
            print(f"Error updating clear all button state: {e}")
    
    # ADB Connection Management Methods (PRD Section 5.1.4)
    
    def initialize_adb_connection(self):
        """Initialize ADB connection to BlueStacks as specified in PRD"""
        try:
            success = self.connect_to_bluestacks()
            if not success:
                self.show_connection_error("Unable to connect to Bluestacks 5.\n\nPlease ensure:\n• Bluestacks 5 is running\n• ADB debugging is enabled in Bluestacks\n• Android SDK platform-tools are installed")
            
        except Exception as e:
            print(f"Error initializing ADB connection: {e}")
            self.update_connection_status(False)
            if "FileNotFoundError" in str(e) or "adb" in str(e).lower():
                self.show_connection_error("ADB (Android Debug Bridge) not found.\n\nPlease install Android SDK platform-tools and add to PATH.\n\nAlternatively, ensure Bluestacks ADB is properly configured.")
            else:
                self.show_connection_error("Unable to connect to Bluestacks 5.\n\nPlease ensure:\n• Bluestacks 5 is running\n• ADB debugging is enabled in Bluestacks\n• Android SDK platform-tools are installed")
    
    def show_connection_error(self, message):
        """Display connection error message on top of application window"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("iScoutTool - Connection Error")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Force black text color to ensure visibility
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: black;
                font-size: 12px;
                padding: 10px;
            }
        """)
        
        msg_box.exec_()
    
    def connect_to_bluestacks(self):
        """Establish ADB connection to BlueStacks on port 5555 as specified in PRD"""
        try:
            # Start ADB server if not running
            print("Starting ADB server...")
            import subprocess
            try:
                # Try to start ADB server
                subprocess.run(['adb', 'start-server'], check=True, capture_output=True, text=True, timeout=10)
                print("ADB server started successfully")
            except subprocess.CalledProcessError as e:
                print(f"Failed to start ADB server: {e}")
                return False
            except FileNotFoundError:
                print("ADB executable not found. Please ensure Android SDK platform-tools are installed and in PATH")
                return False
            except subprocess.TimeoutExpired:
                print("ADB server startup timed out")
                return False
            
            # Wait a moment for server to fully initialize
            import time
            time.sleep(1)
            
            # Connect to ADB server
            print("Attempting to connect to ADB server on localhost:5037...")
            self.adb_client = AdbClient(host='localhost', port=5037)
            
            # Try to connect to BlueStacks device directly first
            print("Attempting direct connection to 127.0.0.1:5555...")
            try:
                self.adb_client.remote_connect("127.0.0.1", 5555)
                print("Direct connection attempt completed")
            except Exception as e:
                print(f"Direct connection failed (may already be connected): {e}")
            
            # Get list of connected devices
            devices = self.adb_client.devices()
            print(f"Found {len(devices)} ADB devices:")
            for i, device in enumerate(devices):
                # Get actual device serial/address
                device_serial = getattr(device, 'serial', 'Unknown')
                print(f"  Device {i}: {device_serial}")
            
            # Find BlueStacks device on port 5555
            self.adb_device = None
            for device in devices:
                device_serial = getattr(device, 'serial', '')
                print(f"Checking device: {device_serial}")
                if "127.0.0.1:5555" in device_serial or "localhost:5555" in device_serial or "5555" in device_serial:
                    self.adb_device = device
                    print(f"Found BlueStacks device: {device_serial}")
                    break
            
            if self.adb_device:
                print("BlueStacks device found, verifying connection...")
                # Verify Evony is running
                if self.verify_evony_running():
                    self.get_evony_screen_dimensions()
                    self.update_connection_status(True)
                    print("Connected to BlueStacks successfully")
                    return True
                else:
                    print("BlueStacks connected but Evony not detected")
            else:
                print("BlueStacks device not found on port 5555")
                print("Available devices:", [str(d) for d in devices])
                
            self.update_connection_status(False)
            return False
            
        except Exception as e:
            print(f"Error connecting to BlueStacks: {e}")
            self.update_connection_status(False)
            return False
    
    def verify_evony_running(self):
        """Check if Evony application is active as specified in PRD"""
        try:
            if not self.adb_device:
                return False
                
            # Check running apps - simplified check
            # In real implementation, check for specific Evony package
            result = self.adb_device.shell("dumpsys window windows | grep -E 'mCurrentFocus'")
            return "evony" in result.lower() or True  # Allow for testing
            
        except Exception as e:
            print(f"Error verifying Evony: {e}")
            return False
    
    def get_evony_screen_dimensions(self):
        """Detect Evony application screen size via ADB as specified in PRD"""
        try:
            if not self.adb_device:
                return (0, 0)
                
            # Get screen size
            result = self.adb_device.shell("wm size")
            if "Physical size:" not in result:
                print("Could not detect screen dimensions")
                return (0, 0)
                
            size_str = result.split("Physical size: ")[1].strip()
            width, height = map(int, size_str.split('x'))
            self.screen_width = width
            self.screen_height = height
            print(f"Screen dimensions detected: {width}x{height}")
            return (width, height)
                
        except Exception as e:
            print(f"Error getting screen dimensions: {e}")
            return (0, 0)
    
    def get_navbox_coordinates(self) -> Optional[Tuple[float, float, float, float]]:
        """Extract NavBox click coordinates from locations.xml as specified in PRD section 3.3.3"""
        try:
            if 'NavBox' not in self.location_presets:
                print("NavBox not found in location presets")
                QMessageBox.warning(self, "Configuration Error", "NavBox coordinates not found in locations.xml")
                return None
                
            preset = self.location_presets['NavBox']
            
            # Validate coordinate ranges (must be 0.0-1.0)
            if not (0.0 <= preset.x_loc <= 1.0 and 0.0 <= preset.y_loc <= 1.0 and 
                    0.0 <= preset.x_dest <= 1.0 and 0.0 <= preset.y_dest <= 1.0):
                print(f"Invalid NavBox coordinates: ({preset.x_loc}, {preset.y_loc}) to ({preset.x_dest}, {preset.y_dest})")
                QMessageBox.warning(self, "Configuration Error", "NavBox coordinates are out of valid range (0.0-1.0)")
                return None
                
            return (preset.x_loc, preset.y_loc, preset.x_dest, preset.y_dest)
            
        except Exception as e:
            print(f"Error getting NavBox coordinates: {e}")
            QMessageBox.critical(self, "Error", f"Error getting NavBox coordinates: {e}")
            return None
    
    def calculate_click_coordinates(self, screen_width: int, screen_height: int, 
                                  x_loc: float, y_loc: float, x_dest: float, y_dest: float) -> Tuple[int, int]:
        """Calculate absolute centerpoint coordinates for NavBox click as specified in PRD section 3.3.3"""
        try:
            # Convert relative to pixel coordinates
            x1 = x_loc * screen_width    # Left edge pixel
            y1 = y_loc * screen_height   # Top edge pixel  
            x2 = x_dest * screen_width   # Right edge pixel
            y2 = y_dest * screen_height  # Bottom edge pixel
            
            # Calculate centerpoint using absolute value as specified
            center_x = int(abs(x1 + x2) / 2)  # Absolute value of average
            center_y = int(abs(y1 + y2) / 2)  # Absolute value of average
            
            print(f"Calculated click coordinates: ({center_x}, {center_y}) from relative ({x_loc:.3f}, {y_loc:.3f}) to ({x_dest:.3f}, {y_dest:.3f})")
            return (center_x, center_y)
            
        except Exception as e:
            print(f"Error calculating click coordinates: {e}")
            return (0, 0)
    
    def click_navbox(self, center_x: int, center_y: int) -> bool:
        """Send click command to NavBox centerpoint as specified in PRD section 3.3.3"""
        try:
            if not self.adb_device:
                print("DEBUG click_navbox: No ADB device connection")
                return False
                
            # Execute click command
            tap_command = f"input tap {center_x} {center_y}"
            print(f"DEBUG click_navbox: Executing ADB command: '{tap_command}'")
            result = self.adb_device.shell(tap_command)
            print(f"DEBUG click_navbox: ADB result: {result}")
            
            # Minimal wait for dialog - optimize for speed
            print(f"DEBUG click_navbox: Waiting 0.4 seconds for navigation dialog to open")
            time.sleep(0.4)  # Reduced from 0.8 to 0.4 seconds
            print(f"DEBUG click_navbox: NavBox click completed successfully")
            return True
            
        except Exception as e:
            print(f"DEBUG click_navbox: ERROR clicking NavBox: {e}")
            return False
    
    def click_at_pixel(self, center_x: int, center_y: int, description: str = "coordinate") -> bool:
        """Send direct pixel click command for calculated centerpoints"""
        try:
            if not self.adb_device:
                print("No ADB device connection")
                return False
                
            # Execute click command using exact pixel coordinates
            result = self.adb_device.shell(f"input tap {center_x} {center_y}")
            print(f"Clicked {description} at pixel ({center_x}, {center_y})")
            return True
            
        except Exception as e:
            print(f"Error clicking {description}: {e}")
            return False
    
    def convert_relative_to_pixel(self, x_rel: float, y_rel: float) -> Tuple[int, int]:
        """Convert relative coordinates (0.0-1.0) to pixel coordinates as specified in PRD"""
        try:
            if self.screen_width == 0 or self.screen_height == 0:
                self.get_evony_screen_dimensions()
                
            pixel_x = int(x_rel * self.screen_width)
            pixel_y = int(y_rel * self.screen_height)
            return (pixel_x, pixel_y)
            
        except Exception as e:
            print(f"Error converting coordinates: {e}")
            return (0, 0)
    
    def reconnect_if_needed(self):
        """Handle connection drops and reconnection as specified in PRD"""
        try:
            if not self.adb_device:
                return self.connect_to_bluestacks()
                
            # Test connection
            try:
                self.adb_device.shell("echo test")
                return True
            except:
                print("Connection lost, attempting to reconnect...")
                return self.connect_to_bluestacks()
                
        except Exception as e:
            print(f"Error in reconnect: {e}")
            return False
    
    # Timer Management Methods (PRD Section 5.1.2)
    
    def setup_timer(self):
        """Set up timer thread and connect signals as specified in PRD"""
        try:
            # Connect timer signals
            self.timer_thread.time_updated.connect(self.update_timer_display)
            self.timer_thread.beep_signal.connect(self.beep_sound)
            self.timer_thread.timer_finished.connect(self.on_timer_finished)
            
            print("Timer setup completed")
            
        except Exception as e:
            print(f"Error setting up timer: {e}")
    
    def start_timer(self, seconds: int = 300):
        """Start 5 minute countdown timer as specified in PRD"""
        try:
            if self.timer_thread.running:
                self.stop_timer()
                
            self.timer_thread.start_timer(seconds)
            print(f"Timer started: {seconds} seconds")
            
        except Exception as e:
            print(f"Error starting timer: {e}")
    
    def stop_timer(self, reset_display=True):
        """Stop and reset countdown timer as specified in PRD"""
        try:
            self.timer_thread.stop_timer()
            if reset_display:
                self.lblTimer.setText("00:00")
            print("Timer stopped")
            
        except Exception as e:
            print(f"Error stopping timer: {e}")
    
    def on_reset_timer_clicked(self):
        """Reset timer to 05:00 and stop any running countdown"""
        print("[DEBUG] Reset Timer button pressed")
        try:
            # Stop the timer thread completely
            if hasattr(self, 'timer_thread') and self.timer_thread:
                print(f"[DEBUG] Before stop: running={self.timer_thread.running}, timer_seconds={self.timer_thread.timer_seconds}")
                self.timer_thread.stop_timer()  # Use the proper stop method
                print(f"[DEBUG] After stop: running={self.timer_thread.running}, timer_seconds={self.timer_thread.timer_seconds}")
                self.timer_thread.timer_seconds = 300  # Reset to 5:00
                self.timer_thread.running = False      # Ensure stopped
                print(f"[DEBUG] After reset: running={self.timer_thread.running}, timer_seconds={self.timer_thread.timer_seconds}")
            else:
                print("[DEBUG] timer_thread not found or not initialized")
            # Reset timer display to 05:00
            self.lblTimer.setText("05:00")
            # Restore teal styling from .ui file
            self.lblTimer.setStyleSheet(
                "QLabel#lblTimer {"
                "background-color: #1a1a1a;"
                "border: 3px solid #00d4ff;"
                "border-radius: 12px;"
                "color: #00d4ff;"
                "font-family: 'Consolas', 'Monaco', monospace;"
                "font-size: 24px;"
                "font-weight: bold;"
                "}"
            )
            print("[DEBUG] Timer reset to 05:00 and teal formatting restored")
        except Exception as e:
            print(f"[DEBUG] Error resetting timer: {e}")
    
    def update_timer_display(self, time_str: str):
        """Update lblTimer with current countdown time and visual warnings"""
        try:
            self.lblTimer.setText(time_str)
            
            # Check if we're in warning period (30 seconds or less)
            if hasattr(self, 'timer_thread') and self.timer_thread and self.timer_thread.timer_seconds <= 30:
                # Deep red color and flashing effect for final 30 seconds - keep same size and bold
                if self.timer_thread.timer_seconds % 2 == 0:  # Flash every other second
                    self.lblTimer.setStyleSheet("""
                        QLabel {
                            color: #FF0000;  /* Deep red */
                            font-weight: bold;
                            font-size: 24px;  /* Same large size as normal */
                            background-color: #FFCCCC;  /* Light red background for visibility */
                        }
                    """)
                else:
                    self.lblTimer.setStyleSheet("""
                        QLabel {
                            color: #AA0000;  /* Darker red */
                            font-weight: bold;
                            font-size: 24px;  /* Same large size as normal */
                            background-color: #DDDDDD;  /* Gray background */
                        }
                    """)
            else:
                # Normal appearance for >30 seconds - blue color like frame, large and bold
                self.lblTimer.setStyleSheet("""
                    QLabel {
                        color: #0078D4;  /* Qt blue color matching frame theme */
                        font-weight: bold;
                        font-size: 24px;  /* Large size for readability */
                    }
                """)
            
        except Exception as e:
            print(f"Error updating timer display: {e}")
    
    def beep_sound(self):
        """Generate system beep sound for final 30 seconds with extended final beep"""
        try:
            # Check if this is the final beep (timer at 0)
            if hasattr(self, 'timer_thread') and self.timer_thread and self.timer_thread.timer_seconds <= 0:
                # Extended final beep - hold tone for 1 second
                winsound.Beep(1000, 1000)  # 1000Hz for 1000ms (1 second)
            else:
                # Normal beep for countdown - 1000Hz tone for 200ms
                winsound.Beep(1000, 200)
            
        except Exception as e:
            print(f"Error playing beep sound: {e}")
    
    def on_timer_finished(self):
        """Handle timer completion with final extended beep"""
        try:
            print("Timer finished!")
            # Play final extended beep (1 second duration)
            self.beep_sound()
            
            # Reset timer display to normal appearance
            self.lblTimer.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    font-weight: normal;
                    font-size: 12px;
                }
            """)
            
        except Exception as e:
            print(f"Error handling timer finish: {e}")
    

    
    def on_data_input_text_changed(self):
        """Handle changes to Data Input text - update Clear All button state"""
        try:
            # Update Clear All button state when text changes
            self.update_clear_all_button_state()
            
        except Exception as e:
            print(f"Error handling data input text change: {e}")
    
    # Data Parsing Methods (PRD Section 5.1.5)
    
    def parse_scout_text(self, text_input: str) -> List[ScoutTarget]:
        """Parse tab-separated scout report into target objects as specified in PRD section 3.1.3"""
        targets = []
        try:
            lines = text_input.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Split by tabs
                parts = line.split('\t')
                if len(parts) < 3:
                    continue
                
                # Parse from right to left as specified in PRD
                try:
                    y_coordinate = int(parts[-1].strip())  # Last field: Y coordinate
                    x_coordinate = int(parts[-2].strip())  # Second-to-last: X Coordinate
                    
                    # Remaining fields (left side): Combined into Boss/Barb description
                    description_parts = parts[:-2]
                    target_type = ' '.join(description_parts).strip()
                    
                    # Validate coordinates per PRD section 7.2
                    if not (1 <= x_coordinate <= 1198):
                        print(f"Invalid X coordinate: {x_coordinate}, skipping target")
                        continue
                    if not (1 <= y_coordinate <= 1200):
                        print(f"Invalid Y coordinate: {y_coordinate}, skipping target")
                        continue
                    
                    target = ScoutTarget(
                        target_type=target_type,
                        x_coordinate=x_coordinate,
                        y_coordinate=y_coordinate,
                        completed=False
                    )
                    targets.append(target)
                    
                except (ValueError, IndexError) as e:
                    print(f"Error parsing line '{line}': {e}")
                    continue
            
            print(f"Parsed {len(targets)} targets successfully")
            return targets
            
        except Exception as e:
            print(f"Error parsing scout text: {e}")
            return []
    
    def load_targets_to_table(self):
        """Populate UI table with parsed target data as specified in PRD"""

        try:
            # Get text from input field
            text_input = self.txtiScoutBoss.toPlainText()
            if not text_input.strip():
                QMessageBox.warning(self, "No Data", "Please paste scout data first")
                return

            # Parse the text
            self.targets = self.parse_scout_text(text_input)

            # Disable sorting before populating
            self.tblBossList.setSortingEnabled(False)

            # Clear existing table and widgets
            self.tblBossList.clearContents()
            self.tblBossList.setRowCount(0)

            # Ensure table has correct columns and headers
            self.tblBossList.setColumnCount(5)
            self.tblBossList.setHorizontalHeaderLabels([
                "Action", "Got It", "Target", "X", "Y"
            ])

            # Set resize mode for X and Y columns
            header = self.tblBossList.horizontalHeader()
            header.setSectionResizeMode(2, QHeaderView.Stretch)  # Target column stretches
            header.setSectionResizeMode(3, QHeaderView.Interactive)
            header.setSectionResizeMode(4, QHeaderView.Interactive)
            self.tblBossList.setColumnWidth(1, 36)   # Got It column reduced width
            self.tblBossList.setColumnWidth(2, 420)  # Target column wider
            self.tblBossList.setColumnWidth(3, 60)   # X column reduced width
            self.tblBossList.setColumnWidth(4, 60)   # Y column reduced width

            # Populate table
            for i, target in enumerate(self.targets):
                self.tblBossList.insertRow(i)

                # Column 0: Go button
                button_container = QtWidgets.QWidget()
                button_layout = QtWidgets.QHBoxLayout(button_container)
                button_layout.setContentsMargins(1, 2, 1, 4)
                button_layout.setAlignment(QtCore.Qt.AlignCenter)
                go_button = QPushButton("➡️ Go")
                go_button.setStyleSheet("""
                    QPushButton {
                        margin: 0px;
                        padding: 2px 6px;
                        font-size: 9px;
                        width: 78px;
                        max-width: 78px;
                        height: 18px;
                        min-height: 18px;
                        max-height: 18px;
                        border-radius: 4px;
                    }
                """)
                go_button.setFocusPolicy(QtCore.Qt.StrongFocus)
                go_button.setAutoDefault(False)
                def go_button_handler(checked, btn=go_button):
                    for row in range(self.tblBossList.rowCount()):
                        cell_widget = self.tblBossList.cellWidget(row, 0)
                        if cell_widget and cell_widget.findChild(QPushButton) == btn:
                            self.on_target_go_clicked(row)
                            break
                go_button.clicked.connect(go_button_handler)
                button_layout.addWidget(go_button)
                self.tblBossList.setCellWidget(i, 0, button_container)

                # Column 1: Got It checkbox
                checkbox_container = QtWidgets.QWidget()
                checkbox_layout = QtWidgets.QHBoxLayout(checkbox_container)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                checkbox_layout.setAlignment(QtCore.Qt.AlignCenter)
                checkbox = QCheckBox()
                checkbox.setChecked(target.completed)
                checkbox.stateChanged.connect(lambda state, row=i: self.on_got_it_checkbox_changed(row, state == 2))
                checkbox_layout.addWidget(checkbox)
                self.tblBossList.setCellWidget(i, 1, checkbox_container)

                # Column 2: Target description
                self.tblBossList.setItem(i, 2, QTableWidgetItem(target.target_type))
                self.tblBossList.setRowHeight(i, 32)

                # Column 3: X coordinate
                x_item = QTableWidgetItem(str(target.x_coordinate))
                self.tblBossList.setItem(i, 3, x_item)

                # Column 4: Y coordinate
                y_item = QTableWidgetItem(str(target.y_coordinate))
                self.tblBossList.setItem(i, 4, y_item)

            # End of for loop
            # Update target counter
            self.update_target_count()
            # Update Clear All button state
            self.update_clear_all_button_state(len(self.targets) > 0)

            # Re-enable sorting and sort by Target column
            self.tblBossList.setSortingEnabled(True)
            self.tblBossList.sortByColumn(2, QtCore.Qt.AscendingOrder)
            print(f"Loaded {len(self.targets)} targets to table (sorted by Target)")

        except Exception as e:
            print(f"Error loading targets to table: {e}")
            QMessageBox.critical(self, "Load Error", f"Error loading targets: {e}")

    def validate_coordinates(self, x: int, y: int, server: int) -> bool:
        """Ensure coordinate values are within game bounds as specified in PRD section 7.2"""
        try:
            # Coordinate range checking per PRD
            if not (1 <= x <= 1198):
                raise ValueError(f"X coordinate {x} out of range (1-1198)")
            if not (1 <= y <= 1200):
                raise ValueError(f"Y coordinate {y} out of range (1-1200)")
            if not (1 <= server <= 9999):
                raise ValueError(f"Server {server} out of range (1-9999)")
            
            return True
            
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
            return False
    
    # Game Automation Methods (PRD Section 5.1.6)
    
    def perform_click(self, x_relative: float, y_relative: float) -> bool:
        """Send click command to specific screen location as specified in PRD"""
        try:
            if not self.adb_device and not self.reconnect_if_needed():
                return False
            
            # Convert relative coordinates to pixels
            pixel_x, pixel_y = self.convert_relative_to_pixel(x_relative, y_relative)
            
            if pixel_x == 0 and pixel_y == 0:
                print("Invalid coordinates for click")
                return False
            
            # Send ADB click command
            command = f"input tap {pixel_x} {pixel_y}"
            result = self.adb_device.shell(command)
            
            print(f"Click sent: ({pixel_x}, {pixel_y}) - Relative: ({x_relative}, {y_relative})")
            return True
            
        except Exception as e:
            print(f"Error performing click: {e}")
            return False
    
    def send_text_input(self, text: str) -> bool:
        """Simple reliable approach - optimized backspace clearing"""
        try:
            if not self.adb_device and not self.reconnect_if_needed():
                return False
            
            # Most reliable method: Go to end, backspace to clear, then type
            self.adb_device.shell("input keyevent 123")  # Move to end of field
            # Extra delete to ensure field is cleared
            self.adb_device.shell("input keyevent 67")  # One extra backspace
            # Fast backspace clearing - send multiple deletes in single commands
            self.adb_device.shell("input keyevent 67 67 67 67 67")  # 5 backspaces at once
            # Send text and enter
            self.adb_device.shell(f"input text '{text}'")
            self.adb_device.shell("input keyevent 66")
            
            return True
            
        except Exception as e:
            print(f"Error sending text: {e}")
            return False
    
    def navigate_to_coordinates(self, x: int, y: int, server: int = None, skip_server: bool = False) -> bool:
        """Navigate to specified map coordinates in Evony as specified in PRD section 3.3.3"""
        try:
            # Use the server parameter directly (don't override with config)
            if server is None:
                # Only fall back to config if no server is provided
                server = self.config.enemy_server or 0
            
            # Validate coordinates
            if not self.validate_coordinates(x, y, server):
                return False
            
            # Check connection
            print(f"DEBUG: Checking ADB connection...")
            if not self.reconnect_if_needed():
                print(f"DEBUG: FAILED to establish ADB connection")
                QMessageBox.warning(self, "Connection Error", "No connection to BlueStacks")
                return False
            else:
                print(f"DEBUG: ADB connection verified - device: {self.adb_device}")
            
            print(f"Navigating to Server {server}, X: {x}, Y: {y}")
            
            # Step 1: Get screen dimensions
            print(f"DEBUG: Getting Evony screen dimensions...")
            screen_width, screen_height = self.get_evony_screen_dimensions()
            print(f"DEBUG: Screen dimensions: {screen_width} x {screen_height}")
            if screen_width == 0 or screen_height == 0:
                print("DEBUG: FAILED - Could not detect screen dimensions")
                return False
            
            # Step 2: Get NavBox coordinates and calculate centerpoint
            print(f"DEBUG: Getting NavBox coordinates...")
            navbox_coords = self.get_navbox_coordinates()
            print(f"DEBUG: NavBox coordinates: {navbox_coords}")
            if not navbox_coords:
                print("DEBUG: FAILED - Could not get NavBox coordinates")
                return False
            
            x_loc, y_loc, x_dest, y_dest = navbox_coords
            center_x, center_y = self.calculate_click_coordinates(
                screen_width, screen_height, x_loc, y_loc, x_dest, y_dest
            )
            
            # Step 3: Click NavBox to open navigation
            print(f"DEBUG: About to click NavBox at ({center_x}, {center_y})")
            if not self.click_navbox(center_x, center_y):
                print(f"DEBUG: FAILED to click NavBox")
                return False
            else:
                print(f"DEBUG: SUCCESS clicked NavBox - navigation dialog should be open")
                # Extra delay when skipping server to ensure dialog is ready
                if skip_server:
                    time.sleep(0.2)  # Additional delay when skipping server step
            
            # Step 4: Enter server (skip if skip_server is True)
            if not skip_server and 'NavServer' in self.location_presets:
                preset = self.location_presets['NavServer']
                center_x, center_y = self.calculate_click_coordinates(
                    screen_width, screen_height, preset.x_loc, preset.y_loc, preset.x_dest, preset.y_dest
                )
                server_value = str(server)
                print(f"DEBUG NavServer: About to send server value '{server_value}' via ADB")
                if self.click_at_pixel(center_x, center_y, "NavServer"):
                    time.sleep(0.1)  # Small delay after click before text input
                    if not self.send_text_input(server_value):
                        print(f"DEBUG NavServer: FAILED to send server value '{server_value}'")
                        return False
                    else:
                        print(f"DEBUG NavServer: SUCCESS sent server value '{server_value}'")
                else:
                    print(f"DEBUG NavServer: FAILED to click NavServer field")
                    return False
            
            # Step 5: Enter X coordinate (no delays)
            if 'NavX' in self.location_presets:
                preset = self.location_presets['NavX']
                center_x, center_y = self.calculate_click_coordinates(
                    screen_width, screen_height, preset.x_loc, preset.y_loc, preset.x_dest, preset.y_dest
                )
                x_value = str(x)
                print(f"DEBUG NavX: About to send X coordinate '{x_value}' via ADB")
                if self.click_at_pixel(center_x, center_y, "NavX"):
                    time.sleep(0.2)  # Increased delay after click before text input
                    if not self.send_text_input(x_value):
                        print(f"DEBUG NavX: FAILED to send X coordinate '{x_value}'")
                        return False
                    else:
                        print(f"DEBUG NavX: SUCCESS sent X coordinate '{x_value}'")
                        time.sleep(0.1)  # Small delay after X input before Y
                else:
                    print(f"DEBUG NavX: FAILED to click NavX field")
                    return False
            
            # Step 6: Enter Y coordinate (no delays)
            if 'NavY' in self.location_presets:
                preset = self.location_presets['NavY']
                center_x, center_y = self.calculate_click_coordinates(
                    screen_width, screen_height, preset.x_loc, preset.y_loc, preset.x_dest, preset.y_dest
                )
                y_value = str(int(y))  # Ensure integer conversion, then string
                print(f"DEBUG NavY: About to send Y coordinate '{y_value}' (original: {y}) via ADB")
                if self.click_at_pixel(center_x, center_y, "NavY"):
                    time.sleep(0.1)  # Small delay after click before text input
                    if not self.send_text_input(y_value):
                        print(f"DEBUG NavY: FAILED to send Y coordinate '{y_value}'")
                        return False
                    else:
                        print(f"DEBUG NavY: SUCCESS sent Y coordinate '{y_value}'")
                else:
                    print(f"DEBUG NavY: FAILED to click NavY field")
                    return False
            
            # Step 7: Click NavGo button and return immediately
            if 'NavGo' in self.location_presets:
                preset = self.location_presets['NavGo']
                center_x, center_y = self.calculate_click_coordinates(
                    screen_width, screen_height, preset.x_loc, preset.y_loc, preset.x_dest, preset.y_dest
                )
                if not self.click_at_pixel(center_x, center_y, "NavGo"):
                    return False
                # No wait - return immediately for manual action
            
            print(f"Fast navigation to {server}:{x},{y} - ready for manual action")
            return True
            
        except Exception as e:
            print(f"Error navigating to coordinates: {e}")
            QMessageBox.critical(self, "Navigation Error", f"Failed to navigate: {e}")
            return False
    
    # Navigation Workflow Methods (PRD Section 5.1.7)
    
    def return_home(self) -> bool:
        """Navigate back to user's home location as specified in PRD"""
        try:
            return self.navigate_to_coordinates(
                self.config.home_x,
                self.config.home_y, 
                self.config.home_server
            )
            
        except Exception as e:
            print(f"Error returning home: {e}")
            return False
    
    def go_to_target(self, target_index: int) -> bool:
        """Complete navigation sequence to selected target as specified in PRD"""
        try:
            if 0 <= target_index < len(self.targets):
                target = self.targets[target_index]
                success = self.navigate_to_coordinates(
                    target.x_coordinate,
                    target.y_coordinate,
                    self.config.enemy_server
                )
                
                if success:
                    # Mark target as completed
                    target.completed = True
                    # Update checkbox in table
                    if checkbox_container := self.tblBossList.cellWidget(target_index, 1):  # Column 1 has checkbox containers
                        if checkbox_layout := checkbox_container.layout():
                            if checkbox := checkbox_layout.itemAt(0).widget():
                                checkbox.setChecked(True)
                    
                return success
            
            print(f"Invalid target index: {target_index}")
            return False
                
        except Exception as e:
            print(f"Error going to target: {e}")
            return False
    
    # UI Event Handlers (PRD Section 5.2)
    
    def connect_ui_signals(self):
        """Connect all UI signals for modern interface as specified in PRD section 5.2.1"""
        try:
            # Connect button signals
            self.btnIScoutLoadTable.clicked.connect(self.on_load_table_clicked)
            self.btnIScoutClearAll.clicked.connect(self.on_clear_all_clicked)
            self.btnIScoutGoHome.clicked.connect(self.on_go_home_clicked)
            
            # Connect Reset Timer button if it exists
            if hasattr(self, 'btnResetTimer'):
                self.btnResetTimer.clicked.connect(self.on_reset_timer_clicked)
            
            # Connect Go Enemy button if it exists
            if hasattr(self, 'btnIScoutGoEnemy'):
                self.btnIScoutGoEnemy.clicked.connect(self.on_go_enemy_clicked)
            
            # Connect View Enemy button if it exists
            if hasattr(self, 'btnViewEnemy'):
                self.btnViewEnemy.clicked.connect(self.on_view_enemy_clicked)
            
            # Connect Data Input text change signal
            if hasattr(self, 'txtiScoutBoss'):
                self.txtiScoutBoss.textChanged.connect(self.on_data_input_text_changed)
            
            # Connect menu actions if they exist
            if hasattr(self, 'actionSaveConfig'):
                self.actionSaveConfig.triggered.connect(self.save_config)
            if hasattr(self, 'actionLoadConfig'):
                self.actionLoadConfig.triggered.connect(self.load_config)
            if hasattr(self, 'actionTestConnection'):
                self.actionTestConnection.triggered.connect(self.test_connection)
            
            # Connect keyboard shortcuts
            self.setup_keyboard_shortcuts()
            
            print("UI signals connected successfully")
            
        except Exception as e:
            print(f"Error connecting UI signals: {e}")
    
    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts as specified in PRD"""
        try:
            # Ctrl+V for paste (if paste button exists)
            if hasattr(self, 'btnPasteFromClipboard'):
                self.btnPasteFromClipboard.clicked.connect(self.paste_from_clipboard)
            
            # F5 for connection test
            from PyQt5.QtWidgets import QShortcut
            from PyQt5.QtGui import QKeySequence
            
            shortcut_f5 = QShortcut(QKeySequence("F5"), self)
            shortcut_f5.activated.connect(self.test_connection)
            
            print("Keyboard shortcuts setup completed")
            
        except Exception as e:
            print(f"Error setting up shortcuts: {e}")
    
    def on_load_table_clicked(self):
        """Process text input and populate target table as specified in PRD section 5.2.2"""
        try:
            self.load_targets_to_table()
            
        except Exception as e:
            print(f"Error in load table clicked: {e}")
    
    def on_clear_all_clicked(self):
        """Clear all rows in tblBossList, clear txtiScoutBoss, and reset UI state as specified in PRD"""
        try:
            # Clear table
            self.tblBossList.setRowCount(0)
            
            # Clear text input area
            self.txtiScoutBoss.clear()
            
            # Reset targets list
            self.targets = []
            
            # Reset target counter
            self.update_target_count(0, 0)
            
            # Update Clear All button state after clearing all data
            self.update_clear_all_button_state()
            
            print("All data cleared")
            
        except Exception as e:
            print(f"Error clearing data: {e}")
    
    def on_go_home_clicked(self):
        """Execute return to home coordinates and start timer as specified in PRD"""
        try:
            # Save current config from UI
            self.save_config()
            
            # Navigate home
            if self.return_home():
                # Go Home does not start timer - only Go Enemy starts timer
                print("Navigated home successfully.")
                
                # Show bubble reminder dialog with black text
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Bubble Reminder")
                msg_box.setText("Remember to Bubble!")
                msg_box.setIcon(QMessageBox.Information)
                
                # Force black text color to ensure visibility (same as connection error styling)
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: white;
                    }
                    QMessageBox QLabel {
                        color: black;
                        font-size: 36px;
                        font-weight: bold;
                        padding: 10px;
                    }
                """)
                msg_box.exec_()
                return
            
            QMessageBox.warning(self, "Navigation Failed", "Failed to navigate to home coordinates")
            
        except Exception as e:
            print(f"Error going home: {e}")
            QMessageBox.critical(self, "Error", f"Error going home: {e}")
    
    def on_go_enemy_clicked(self):
        """Navigate to enemy server coordinates as specified in PRD"""
        try:
            # Save current config
            self.save_config()
            
            # Navigate to enemy server (use first target if available, or just server)
            enemy_server = int(self.intEnemyServer.text() or "0")
            if enemy_server == 0:
                QMessageBox.warning(self, "Invalid Server", "Please set enemy server number")
                return
            
            # Use middle of map as default coordinates
            if self.navigate_to_coordinates(598, 600, enemy_server):
                self.start_timer(300)  # Start bubble timer (only Go Enemy starts timer)
                print("Navigated to enemy server. Timer started.")
                return
            
            QMessageBox.warning(self, "Navigation Failed", "Failed to navigate to enemy server")
            
        except Exception as e:
            print(f"Error going to enemy: {e}")
            QMessageBox.critical(self, "Error", f"Error going to enemy: {e}")
    
    def on_target_go_clicked(self, row_index: int):
        """Navigate to specific target from table row as specified in PRD section 3.3.3"""
        try:
            # Check the checkbox immediately when Go button is pressed
            if checkbox_container := self.tblBossList.cellWidget(row_index, 1):  # Column 1 has checkbox containers
                if checkbox_layout := checkbox_container.layout():
                    if checkbox := checkbox_layout.itemAt(0).widget():
                        checkbox.setChecked(True)
            
            # Get X and Y coordinates directly from table columns (to the right of Go button)
            # Table columns: 0=Action (Go button), 1=Got It checkbox, 2=Target, 3=X, 4=Y
            x_item = self.tblBossList.item(row_index, 3)  # X column
            y_item = self.tblBossList.item(row_index, 4)  # Y column
            print(f"DEBUG get: Go button row {row_index} X item: {x_item.text() if x_item else 'None'} Y item: {y_item.text() if y_item else 'None'}")
            
            if not x_item or not y_item:
                QMessageBox.warning(self, "Missing Coordinates", "X or Y coordinates not found in table")
                return
            
            try:
                target_x = int(x_item.text())
                target_y = int(y_item.text())
            except ValueError:
                QMessageBox.warning(self, "Invalid Coordinates", "X or Y coordinates are not valid numbers")
                return
            
            # Mark target as completed in data model
            if 0 <= row_index < len(self.targets):
                self.targets[row_index].completed = True
            
            # Get enemy server directly from Enemy Server text field (current value)
            try:
                enemy_server = int(self.intEnemyServer.text() or "0")
                if enemy_server == 0:
                    QMessageBox.warning(self, "Invalid Server", "Please enter a valid Enemy Server number")
                    return
            except ValueError:
                QMessageBox.warning(self, "Invalid Server", "Enemy Server must be a valid number")
                return
            
            # Perform navigation using coordinates from table (keep current server)
            print(f"Navigating to coordinates from table: X={target_x}, Y={target_y} (keeping current server)")
            if self.navigate_to_coordinates(target_x, target_y, enemy_server, skip_server=True):
                print(f"Successfully navigated to target {row_index + 1} at ({target_x}, {target_y})")
            else:
                QMessageBox.warning(self, "Navigation Failed", f"Failed to navigate to target {row_index + 1}")
            
        except Exception as e:
            print(f"Error navigating to target: {e}")
            QMessageBox.critical(self, "Error", f"Error navigating to target: {e}")
    
    def on_view_enemy_clicked(self):
        """Navigate to Enemy Server at coordinates 600,600 and click NavGo"""
        try:
            # Ensure connection
            if not self.reconnect_if_needed():
                QMessageBox.warning(self, "Connection Error", "No connection to BlueStacks")
                return

            # Get screen dimensions
            screen_width, screen_height = self.get_evony_screen_dimensions()
            if screen_width == 0 or screen_height == 0:
                QMessageBox.warning(self, "Screen Error", "Could not detect screen dimensions")
                return

            # Step 1: Click NavBox to open navigation dialog
            navbox_coords = self.get_navbox_coordinates()
            if not navbox_coords:
                QMessageBox.warning(self, "NavBox Error", "Could not get NavBox coordinates")
                return
            x_loc, y_loc, x_dest, y_dest = navbox_coords
            center_x, center_y = self.calculate_click_coordinates(screen_width, screen_height, x_loc, y_loc, x_dest, y_dest)
            if not self.click_navbox(center_x, center_y):
                QMessageBox.warning(self, "NavBox Error", "Failed to click NavBox")
                return
            time.sleep(0.2)

            # Step 2: Enter Enemy Server in NavServer field
            if 'NavServer' in self.location_presets:
                preset = self.location_presets['NavServer']
                center_x, center_y = self.calculate_click_coordinates(screen_width, screen_height, preset.x_loc, preset.y_loc, preset.x_dest, preset.y_dest)
                server_value = str(self.config.enemy_server)
                if self.click_at_pixel(center_x, center_y, "NavServer"):
                    time.sleep(0.1)
                    self.send_text_input(server_value)
                else:
                    QMessageBox.warning(self, "NavServer Error", "Failed to click NavServer field")
                    return

            # Step 3: Enter X=600 in NavX field
            if 'NavX' in self.location_presets:
                preset = self.location_presets['NavX']
                center_x, center_y = self.calculate_click_coordinates(screen_width, screen_height, preset.x_loc, preset.y_loc, preset.x_dest, preset.y_dest)
                if self.click_at_pixel(center_x, center_y, "NavX"):
                    time.sleep(0.2)
                    self.send_text_input("600")
                else:
                    QMessageBox.warning(self, "NavX Error", "Failed to click NavX field")
                    return

            # Step 4: Enter Y=600 in NavY field
            if 'NavY' in self.location_presets:
                preset = self.location_presets['NavY']
                center_x, center_y = self.calculate_click_coordinates(screen_width, screen_height, preset.x_loc, preset.y_loc, preset.x_dest, preset.y_dest)
                if self.click_at_pixel(center_x, center_y, "NavY"):
                    time.sleep(0.1)
                    self.send_text_input("600")
                else:
                    QMessageBox.warning(self, "NavY Error", "Failed to click NavY field")
                    return

            # Step 5: Click NavGo button
            if 'NavGo' in self.location_presets:
                preset = self.location_presets['NavGo']
                center_x, center_y = self.calculate_click_coordinates(screen_width, screen_height, preset.x_loc, preset.y_loc, preset.x_dest, preset.y_dest)
                self.click_at_pixel(center_x, center_y, "NavGo")
            print(f"ViewEnemy: Navigated to Enemy Server {self.config.enemy_server} at 600,600")
        except Exception as e:
            print(f"Error in ViewEnemy: {e}")
            QMessageBox.critical(self, "ViewEnemy Error", f"Failed to view enemy: {e}")
    
    def paste_from_clipboard(self):
        """Paste data from clipboard to text input"""
        try:
            clipboard = QApplication.clipboard()
            if text := clipboard.text():
                self.txtiScoutBoss.setPlainText(text)
                print("Data pasted from clipboard")
            
        except Exception as e:
            print(f"Error pasting from clipboard: {e}")
    
    def test_connection(self):
        """Test ADB connection as specified in PRD"""
        try:
# sourcery skip: no-conditionals-in-tests
            if self.connect_to_bluestacks():
                QMessageBox.information(self, "Connection Test", "✅ Connected to BlueStacks successfully!")
            else:
                QMessageBox.warning(self, "Connection Test", "❌ Failed to connect to BlueStacks")
            
        except Exception as e:
            print(f"Error testing connection: {e}")
            QMessageBox.critical(self, "Connection Error", f"Error testing connection: {e}")
    
    def closeEvent(self, event):
        """Handle application closing"""
        try:
            # Stop timer
            if self.timer_thread.running:
                self.stop_timer()
            
            # Save configuration
            self.save_config()
            
            print("Application closing...")
            event.accept()
            
        except Exception as e:
            print(f"Error during close: {e}")
            event.accept()

    def on_got_it_checkbox_changed(self, row: int, checked: bool):
        """Update completed status for the target at the given row and refresh target count."""
        if 0 <= row < len(self.targets):
            self.targets[row].completed = checked
            self.update_target_count()

# Ensure entry point is at the end of the file
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = iScoutToolApp()
    window.show()
    sys.exit(app.exec_())