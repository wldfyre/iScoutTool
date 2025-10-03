# Product Requirements Document (PRD) - iScoutTool

## 1. Executive Summary

### 1.1 Product Overview
iScoutTool is a Python-based automation application designed to interface with the Evony mobile game running on BlueStacks 5 Android emulator. The tool provides automated scouting capabilities for identifying and navigating to various targets (bosses, barbarians, resources) within the game world, streamlining repetitive scouting tasks for players.

### 1.2 Target Users
- Evony game players who need to efficiently scout multiple targets
- Alliance members coordinating scouting activities
- Players managing multiple accounts or performing repetitive tasks

### 1.3 Key Benefits
- Automated target identification and navigation
- Reduced manual clicking and repetitive tasks
- Improved efficiency in scouting operations
- Centralized management of target lists and coordinates

### 1.4 Current code base
- Python => 1468 lines of code
- PyQT5 .ui => 651 lines of code
- XML => 9 lines of code
- Product Requirements Document => 917 lines of text

- Total lines to maintain project => 3045 (Sum of the above code/text lines)

## 2. Technical Architecture

### 2.1 Core Technologies
- **Python 3.x**: Primary development language
- **PyQt5**: GUI framework for modern user interface
- **UI Design**: `iScoutToolModern.ui` - Modern dark theme interface with enhanced workflow
- **ppadb (Pure Python ADB)**: Android Debug Bridge interface for BlueStacks communication
- **BlueStacks 5**: Android emulator platform (target port 5555)
- **XML**: Configuration and preset data storage

### 2.2 System Requirements
- Windows 10/11 operating system
- BlueStacks 5 installed and configured with ADB debugging enabled
- Python 3.8+ with required dependencies:
    - PyQt5 >= 5.15.0
    - ppadb >= 3.0.0
    - xml.etree.ElementTree (built-in)
    - threading (built-in)
    - configparser (built-in)
- Network connectivity to BlueStacks on localhost:5555
- Minimum 4GB RAM, 2GB free disk space

## 3. Functional Requirements

### 3.1 Core Features

#### 3.1.1 BlueStacks Integration
- **Requirement**: Establish connection to BlueStacks 5 using ppadb with automatic ADB server management
- **Implementation**: 
  - Automatic ADB server startup if not running (`adb start-server`)
  - Dynamic device detection on any port containing "5555"
  - Intelligent connection retry with detailed error reporting
- **Error Handling**: 
  - Automatic ADB server initialization
  - Comprehensive error messages for different failure scenarios
  - Graceful fallback and user guidance for connection issues

#### 3.1.2 Evony Game Automation
- **Requirement**: Send precise clicks and input data to Evony application
- **Coordinate System**: Relative positioning (0.0-1.0) for screen-independent operation based on a percent of the max screenshot image width (x) and height (y)
- **Actions Supported**:
  - Single clicks at specified coordinates
  - Text input for coordinates and server navigation
  - Text input as a cut/paste from an external data source not interfaced with this application

#### 3.1.3 Target Management
- **Requirement**: Parse and manage lists of scouting targets
    - parsing will result in 3 distinct elements, that will comprise a row in the tblBossList widget
- **Data Format**: Tab-separated text format supporting either "Arctic Barbarians" or Boss entries
    - **Parsing Logic**: Each line contains tab-separated fields. Parse from right to left:
        1. Last field: Y-coordinate (integer)
        2. Second-to-last field: X-coordinate (integer) 
        3. Remaining fields (left side): Combined into Boss/Barb description string

  - **Arctic Barbarians Format**:
    - Input: `Arctic Barbarians Lv5 502M \t Free \t 338 \t 249`
    - Parsed as:
        - Boss/Barb: "Arctic Barbarians Lv5 502M Free" (space-separated combination)
        - X coordinate: 338
        - Y coordinate: 249

  - **Boss Format**:
    - Input: `(Boss) Kamaitachi \t Lv12 \t 440 \t 267`
    - Parsed as:
        - Boss/Barb: "(Boss) Kamaitachi Lv12" (space-separated combination)
        - X coordinate: 440
        - Y coordinate: 267


### 3.2 User Interface Components

**Note**: The application should use `iScoutToolModern.ui` for the modern interface design with dark theme, improved layout, and enhanced user experience.

#### 3.2.1 Modern Interface Layout
- **UI File**: Use `iScoutToolModern.ui` instead of `iScoutTool.ui`
- **Layout Structure**: Vertical splitter with Data Input (top, compact) and Scout Targets (bottom, expanded)
- **Theme**: Dark theme with cyan accents automatically applied via embedded stylesheet
- **Responsive Design**: Flexible layouts that adapt to window resizing
- **Enhanced Typography**: Improved fonts, spacing, and visual hierarchy

#### 3.2.2 Main Table (tblBossList)
- **Purpose**: Display parsed target list with interactive controls
- **Columns**:
  - "Got It": Checkbox to mark completed targets, this box will automatically be checked when the "Go" button for the row is pressed, indicating that navigation to this server/x/y Evony coordinate has been completed
  - "Boss/Barb": Target name and details as derived from the txtiScoutBoss text field, and parsed as per rules in section 3.1.3
    - this is a locked field
  - "Go": Action button to navigate to target
    - the dimensions of the Evony screen are obtained for x(width) and y(height)
    - for each value retrieved from locations.xml, the xLoc and xDest are each multiplied by the Evony screen x value for their dimension appropriate numbers
    - for each value retrieved from locations.xml, the yLoc and yDest are each multiplied by the Evony screen y value for their dimension appropriate numbers
    - when button is pressed, the navigation indicator location in Evony will be calculated using coordinates stored in the locations.xml file, specifically "NavBox" will be used to retrieve the midpoint of the line defined by the cooresponding xloc, yloc, xdest, ydest, and a click event at these coordinates in Evony will be sent, which will open a Search dialog in Evony.  
        - the "Server field will be sent a click event, which will open a text field where two button combinations, 'Ctrl-A' and 'Del'
            will be sent to clear the field.  Then the Server integer from the field 'intEnemyServer' will be sent, followed by a 'Return' character
    - "X": X-coordinate
        - Evony will be sent a click event at the centerpoint of the line, defined by using 'NavX' for the row in locations.xml, to retrieve the coordinates xLoc, yLoc, xDest, yDest, which will open a text field in Evony where two button combinations, 'Ctrl-A' and 'Del' will be sent to clear the field.  Then the integer retrieved from the 'X' column of the corresponding row will be sent, followed by a 'Return' character
    - "Y": Y-coordinate
        - Evony will be sent a click event at the centerpoint of the line, defined by using 'NavY' for the row in locations.xml, to retrieve the coordinates xLoc, yLoc, xDest, yDest, which will open a text field in Evony where two button combinations, 'Ctrl-A' and 'Del' will be sent to clear the field.  Then the integer retrieved from the 'Y' column of the corresponding row will be sent, followed by a 'Return' character
    - next click in Evony on the centerpoint of the line as defined by using "NavGo"  in locations.xml to retrieve xLoc, yLoc, xDest, yDest to determine the line
    - if all is successful, set the checkbox in the "Got It" column to checked
- **Features**:
  - Alternating row colors for readability
  - Sortable columns
  - Action buttons within the "Go" column of 'tblBossList'
  - Action checkmarks within the "Got It column of 'tblBossList'


#### 3.2.2 Configuration Controls
- **Home Location Settings for returning to home server**:
  - `intHomeServer`: Home server number (Editable, required 4-digit input)
  - `intHomeXLoc`: Home X-coordinate (Editable, required 4-digit input)
  - `intHomeYLoc`: Home Y-coordinate (Editable, required 4-digit input)
- **Enemy Server Setting**:
  - `intEnemyServer`: Editable, required 4 digit number for the Target server for operations
    in the case of "Artic Barbarians", this will be the same as the home server
    in the case of a boss, this could either be the home server or the enemy server

#### 3.2.3 Action Controls
- **btnIScoutLoadTable**: Load target data from text data pasted into 'txtiScoutBoss'
- **btnIScoutClearAll**: Clear all data in 'txtiScoutBoss' and 'tblBossList'
- **btnIScoutGoHome**: Navigate to home coordinates and start 5-minute bubble countdown timer
    - Will navigate to home server coordinates as specified in configuration
    - Starts countdown timer for bubble protection duration
- **lblTimer**: Display operation timing/countdown. Not user editable, runs in separate thread so not impacted by other functionality.

#### 3.2.4 Data Input
- **txtiScoutBoss**: Multi-line text input for paste operations from scout reports

### 3.3 Preset Management System

#### 3.3.1 Screen Location Presets
- **File**: `Resources/locations.xml`
- **Purpose**: Define reusable screen coordinates for common actions
- **Preset Types**:
  - Evony Navigation elements (NavBox, NavServer, NavX, NavY, NavGo)
  - % offset coordinates of the upper left and lower right corners of the Navigation Elements
    - these will be used to determine the center of the Navigation element as the adb click action point

#### 3.3.2 Coordinate System
- **Format**: Relative coordinates (0.0-1.0) for resolution independence
    - 0.0 = top/left edge of screen
    - 1.0 = bottom/right edge of screen
    - Example: (0.5, 0.5) = center of screen
- **Conversion Process**:
    1. Detect Evony screen dimensions via ADB (e.g., 1920x1080)
    2. Convert relative to pixel: pixel_x = relative_x * screen_width
    3. Send ADB click command: `input tap <pixel_x> <pixel_y>`
- **Click Actions**: Single-point targeting only
- **Validation**: 
    - Relative coordinates must be 0.0-1.0
    - Pixel coordinates must be within detected screen bounds
    - Screen detection required before any click operations

#### 3.3.3 Go Button Navigation Process

**Overview**: The Go button implements a complete navigation sequence to move the Evony game screen to target coordinates specified in the Scout Targets table.

**Navigation Sequence**:
1. **Open Navigation Box**: Click the NavBox element in Evony to open the navigation interface
2. **Input Coordinates**: Enter target X and Y coordinates from the table row
3. **Execute Navigation**: Trigger the "Go" action within Evony's navigation system
4. **Mark Complete**: Auto-check the "Got It" checkbox for the target row

**Detailed Implementation Steps**:

**Step 1: Screen Dimension Detection**
```python
def get_screen_dimensions():
    """Get current screen resolution from BlueStacks emulator via ADB"""
    # Execute: adb shell wm size
    # Parse output: "Physical size: 1920x1080" 
    # Return: (width=1920, height=1080)
    # Handle errors: connection failed, invalid format, no response
```

**Step 2: XML Location Parsing**
```python
def get_navbox_coordinates():
    """Extract NavBox click coordinates from locations.xml"""
    # Parse: Resources/locations.xml
    # Find: <navigation name="NavBox" xLoc="0.394" yLoc="0.872" xDest="0.648" yDest="0.897"/>
    # Extract: xLoc, yLoc, xDest, yDest as float values (0.0-1.0 range)
    # Return: (xLoc, yLoc, xDest, yDest)
```

**Step 3: Centerpoint Calculation**
```python
def calculate_click_coordinates(screen_width, screen_height, xLoc, yLoc, xDest, yDest):
    """Calculate absolute centerpoint coordinates for NavBox click"""
    # Convert relative to pixel coordinates:
    x1 = xLoc * screen_width    # Left edge pixel
    y1 = yLoc * screen_height   # Top edge pixel  
    x2 = xDest * screen_width   # Right edge pixel
    y2 = yDest * screen_height  # Bottom edge pixel
    
    # Calculate centerpoint:
    center_x = int(abs(x1 + x2) / 2)  # Absolute value of average
    center_y = int(abs(y1 + y2) / 2)  # Absolute value of average
    
    # Return: (center_x, center_y) in pixels
```

**Step 4: ADB Click Execution**
```python
def click_navbox(center_x, center_y):
    """Send click command to NavBox centerpoint"""
    # Execute: adb shell input tap <center_x> <center_y>
    # Wait: 500ms for navigation box to open
    # Validate: Success/failure of click action
```

**Step 5: Target Navigation**
```python
def navigate_to_target(target_x, target_y):
    """Complete navigation sequence to target coordinates"""
    # 1. Click NavBox (using calculated centerpoint)
    # 2. Wait for navigation interface to appear
    # 3. Input target_x into X coordinate field  
    # 4. Input target_y into Y coordinate field
    # 5. Click "Go" button within Evony navigation
    # 6. Auto-check "Got It" checkbox in target row
```

**Error Handling Requirements**:
- **XML Parse Errors**: Missing NavBox entry, malformed coordinates
- **ADB Connection**: BlueStacks not running, device disconnected  
- **Screen Detection**: Invalid resolution, no response from device
- **Coordinate Validation**: Out of range values, negative coordinates
- **Navigation Timeout**: Evony not responding, interface not appearing

## 4. Data Models

### 4.1 Target Data Structure
```python
class ScoutTarget:
    target_type: str        # "Boss" or "Barbarian" actual Name, combined with Target level, Power rating, and barb status
    x_coordinate: int      # Map X position
    y_coordinate: int      # Map Y position
    completed: bool        # User marked as completed
```

### 4.2 Location Preset Structure
```python
class LocationPreset:
    name: str              # Boss/Barb identifier
    x_loc: float          # X coordinate (0.0-1.0)
    y_loc: float          # Y coordinate (0.0-1.0)
    x_dest: float         # Destination X (0.0-1.0)
    y_dest: float         # Destination Y (0.0-1.0)
    click_and_drag: bool  # Action type flag, but will not be used in this application.  It is used by other apps
```

### 4.3 Configuration Data
```python
class AppConfig:
    home_server: int      # User's home server
    home_x: int          # Home X coordinate
    home_y: int          # Home Y coordinate
    enemy_server: int    # Target server for operations
    adb_port: int        # BlueStacks connection port (5555)
```
    this data will be saved/fetched from a flat file named iScoutTool.cfg, in a comma delimited format

## 5. Key Interactions and Methods
User will manually copy and paste information from an app called iScout, to the text box named txtiScoutBoss
The only external application this one will interact with is the Evony application running on the Android Emulator named Bluestacks 5
For now, it will 

### 5.1 Core Application Methods

#### 5.1.1 Application Initialization
```python
def __init__(self):
    """Initialize main application with modern UI"""
    # Load iScoutToolModern.ui file
    # Call setup_modern_interface() to configure UI elements
    # Call configure_splitter_layout() to set optimal proportions
    # Call setup_enhanced_table() to configure table display
    # Load configuration from iScoutTool.cfg
    # Initialize ADB connection
    # Set up timer thread
    # Connect signal handlers for UI events
```

#### 5.1.2 Timer Management
```python
def start_timer():
    """Start 5 minute (300 second) countdown timer in separate thread"""
    # Initialize timer_seconds = 300
    # Start timer_thread with update_timer() called every 1000ms
    # Update lblTimer display
    
def stop_timer():
    """Stop and reset countdown timer"""
    # Set timer_seconds = 0
    # Stop timer_thread
    # Update lblTimer to show "00:00"
    
def update_timer():
    """Update lblTimer with current countdown time in MM:SS format"""
    # Decrement timer_seconds by 1
    # Format as MM:SS (e.g., "04:23")
    # Update lblTimer.setText()
    # If timer_seconds <= 30, call beep_sound()
    # If timer_seconds <= 0, call stop_timer()
    
def beep_sound():
    """Generate system beep sound once per second for final 30 seconds of countdown"""
    # Use platform-specific beep (Windows: winsound.Beep())
    # 1000Hz tone for 200ms duration
    # Import required: import winsound
```

#### 5.1.2 Modern UI Initialization
```python
def setup_modern_interface():
    """Initialize modern UI elements from iScoutToolModern.ui"""
    # Load iScoutToolModern.ui instead of iScoutTool.ui
    # Apply dark theme styling automatically loaded from .ui file
    # Configure splitter proportions for optimal workflow
    # Set up enhanced table features
    # Initialize connection status indicators
    
def configure_splitter_layout():
    """Set up optimal splitter proportions programmatically"""
    # Set mainSplitter sizes: [180, 600] (Data Input compact, Scout Targets expanded)
    # self.mainSplitter.setSizes([180, 600])
    # Ensure Data Input section stays compact (max 180px)
    # Scout Targets gets majority of space for better workflow
    
def setup_enhanced_table():
    """Configure Scout Targets table for optimal display"""
    # Set custom column widths for better readability:
    # - Column 0 (✓): 60px for checkboxes
    # - Column 1 (🎯 Target): 350px for target descriptions
    # - Column 2 (➡️ Action): 100px for Go buttons
    # - Column 3 (X): 80px for X coordinates
    # - Column 4 (Y): 80px for Y coordinates
    # Enable sorting and row selection
    # Set alternating row colors for better readability

def create_go_button_widget(row_index):
    """Create properly positioned Go button widget for table cells"""
    # CRITICAL: Use container-based approach for proper button centering
    # Direct button placement with CSS margins causes clipping issues
    
    # Create container widget to hold the button
    button_container = QtWidgets.QWidget()
    button_layout = QtWidgets.QHBoxLayout(button_container)
    
    # Asymmetric margins for proper vertical positioning
    # Top margin smaller than bottom to prevent bottom clipping
    button_layout.setContentsMargins(1, 2, 1, 4)  # Left, Top, Right, Bottom
    button_layout.setAlignment(QtCore.Qt.AlignCenter)
    
    # Button with constrained dimensions to fit in 100px column width
    go_button = QPushButton("➡️ Go")
    go_button.setStyleSheet("""
        QPushButton {
            margin: 0px;           # No margins - container handles positioning
            padding: 2px 6px;      # Internal button spacing
            font-size: 9px;        # Compact font for small button
            width: 78px;           # Fits in 100px column with container margins
            max-width: 78px;       # Prevent expansion
            height: 18px;          # Reduced height to prevent clipping
            min-height: 18px;      # Consistent minimum
            max-height: 18px;      # Consistent maximum
            border-radius: 4px;    # Rounded corners
        }
    """)
    
    # Set row height to accommodate container and button
    # Row: 32px, Button: 18px, Container margins: 2px+4px = 6px
    # Total used: 18px + 6px = 24px, Buffer: 8px
    self.tblBossList.setRowHeight(row_index, 32)
    
    # IMPORTANT: Return container, not button directly
    return button_container
    
def update_connection_status(connected: bool):
    """Update connection status indicator in UI"""
    # Update lblConnectionStatus text and color
    # 🟢 Emulator Connected (green) or 🔴 Emulator Disconnected (red)
    # Also update status bar with connection details
    
def update_target_count(count: int):
    """Update target counter in table toolbar"""
    # Update lblTargetCount with current number of loaded targets
    # Format: "Targets: {count}"
```

#### 5.1.3 Configuration Management
```python
def load_config():
    """Load configuration from iScoutTool.cfg file"""
    # Read CSV format: home_server,home_x,home_y,enemy_server
    # Example: "1234,400,500,5678"
    # Populate intHomeServer, intHomeXLoc, intHomeYLoc, intEnemyServer
    # Create default config if file doesn't exist
    
def save_config():
    """Save current configuration to iScoutTool.cfg file"""
    # Write CSV format with current UI field values
    # Validate data before saving
    
def get_evony_screen_dimensions():
    """Detect Evony application screen size via ADB"""
    # Use adb shell wm size to get screen resolution
    # Return tuple (width, height) in pixels
    # Cache results for performance
    
def convert_relative_to_pixel(x_rel, y_rel):
    """Convert relative coordinates (0.0-1.0) to pixel coordinates"""
    # Get screen dimensions
    # pixel_x = x_rel * screen_width
    # pixel_y = y_rel * screen_height
    # Return tuple (pixel_x, pixel_y)
```

#### 5.1.4 Connection Management
```python
def connect_to_bluestacks():
    """Establish ADB connection with automatic server management"""
    # 1. Start ADB server using subprocess: 'adb start-server'
    # 2. Connect to ADB client on localhost:5037
    # 3. Attempt direct connection to 127.0.0.1:5555
    # 4. Enumerate all connected devices with detailed logging
    # 5. Find device with "5555" in serial/address
    
def verify_evony_running():
    """Check if Evony application is active"""
    
def reconnect_if_needed():
    """Handle connection drops and reconnection with intelligent retry"""
    
def show_connection_error(message):
    """Display ADB connection errors with specific troubleshooting guidance"""
```

#### 5.1.5 Input Processing
```python
def parse_scout_text(text_input):
    """Parse tab-separated scout report into target objects"""
    
def load_targets_to_table():
    """Populate UI table with parsed target data"""
    # After loading, call update_target_count(len(targets))
    # Ensure table uses modern styling from iScoutToolModern.ui
    
def validate_coordinates(x, y, server):
    """Ensure coordinate values are within game bounds"""
```

#### 5.1.6 Game Automation
```python
def navigate_to_coordinates(x, y, server=None):
    """Navigate to specified map coordinates in Evony"""
    #1. verify the magnifying glass icon is on the Evony screen.
        #if not, ask user to manually navigate to server screen and exit method
    #2. Click on the centerpoint for NavBox
    #3. Click on the centerpoint for NavServer
    #4. Clear the server field in Evony by sending 'select all' and 'delete' via adb to Evony
    #5.  Send the server value passed to function, to Evony via adb
    #6. Send <Enter>
    #7. Repeat steps 3 - 7 using centerpoint for NavX and the passed 'x' value
    #8. Repeat steps 3-7 using centerpoint for NavY and the passed 'y' value
    #9. Click on the centerpoint for NavGo
    
def perform_click(x_relative, y_relative):
    """Send click command to specific screen location"""
    #1. Use adb to send a click command to Evony, to be performed at the passed coordinates  

```

#### 5.1.7 Navigation Workflow
```python
def go_to_target(target_index):
    """Complete navigation sequence to selected target"""
    # 1. Open world map
    # 2. Navigate to correct server (if different)
    # 3. Input target coordinates
    # 4. Execute "Go" action
    # 5. Return success/failure status
    
def return_home():
    """Navigate back to user's home location"""
    #1. pass coordinates (x, y, server) as obtained from (intHomeXLoc, intHomeYLoc, intHomeServer) to method navigate_to_coordinates
```

### 5.2 UI Event Handlers

#### 5.2.1 Modern UI Event Setup
```python
def connect_ui_signals():
    """Connect all UI signals for modern interface"""
    # Connect button signals
    # Connect table signals
    # Connect menu action signals
    # Connect splitter resize signals
    # Set up keyboard shortcuts (Ctrl+V for paste, F5 for connection test)
```

#### 5.2.2 Button Actions
```python
def on_load_table_clicked():
    """Process text input and populate target table"""
    # Use modern table styling from iScoutToolModern.ui
    # Update target counter after loading
    
def on_clear_all_clicked():
    """Clear all rows in tblBossList, clear txtiScoutBoss, and reset UI state"""
    # Reset target counter to 0
    
def on_go_home_clicked():
    """Execute return to home coordinates and start timer"""
    # Execute return to home coordinates using intHomeServer, intHomeXLoc, intHomeYLoc
    # Start 5-minute countdown timer
    # Update connection status if needed
    
def on_go_enemy_clicked():
    """Navigate to enemy server coordinates"""
    # Navigate using intEnemyServer coordinates
    # Start bubble countdown timer
    
def on_target_go_clicked(row_index):
    """Navigate to specific target from table row"""
    # Use intEnemyServer, row cell from 'X' and 'Y' columns
    # Mark target as completed in modern UI
```

#### 5.2.3 Table Interactions
```python
def on_got_it_checkbox_changed(row, checked):
    """Mark target as completed/incomplete"""
    # Update modern table styling for completed rows
    
def on_table_row_selected(row):
    """Handle target selection for actions"""
    # Use modern selection styling from iScoutToolModern.ui
    
def on_menu_action_triggered(action):
    """Handle menu actions from modern menu bar"""
    # Save/Load Configuration, Test Connection, Screenshot, Settings, etc.
```

## 6. Integration Specifications

### 6.1 ppadb Integration
- **Connection Management**: Automatic ADB server startup and device connection
- **Device Detection**: Dynamic discovery with flexible port matching ("5555" in device serial)
- **ADB Server Management**: 
    - Automatic `adb start-server` execution via subprocess
    - Timeout protection (10-second limit)
    - Comprehensive error handling for different failure scenarios
- **Connection String**: Dynamic detection (typically `127.0.0.1:5555`)
- **Command Execution**: Shell commands for input simulation
- **Screen Interaction**: Touch events via ADB input commands
- **ADB Commands Used**:
    - Server startup: `adb start-server`
    - Device connection: `remote_connect("127.0.0.1", 5555)`
    - Click: `input tap <x> <y>`
    - Text input: `input text "<string>"`
    - Key events: `input keyevent <keycode>`
        - KEYCODE_CTRL_LEFT: 113
        - KEYCODE_A: 29  
        - KEYCODE_DEL: 67
        - KEYCODE_ENTER: 66
    - Screen size: `wm size`
- **Error Handling**:
    - FileNotFoundError: ADB executable not found in PATH
    - CalledProcessError: ADB command execution failed
    - TimeoutExpired: ADB operations exceeded time limit
    - ConnectionRefusedError: ADB server not accepting connections
- **Evony Package**: `com.topgamesinc.evony` (to be verified during implementation)

### 6.2 Evony Application Interface
- **Package Name**: Target Evony application package
- **Activity Detection**: Verify correct game screen is active
- **Input Methods**:
  - Touch events for clicks
  - Text input for coordinate entry

### 6.3 Data Persistence
- **Configuration File**: `iScoutTool.cfg` in application root directory
    - Format: CSV (home_server,home_x,home_y,enemy_server)
    - Auto-created with defaults if missing
    - Validated on load with error handling
- **Target Lists**: Session-based only (not persisted between runs)
- **Presets**: XML-based location configuration management
    - File: `Resources/locations.xml`
    - Read-only during runtime
    - Validated XML structure on startup

### 6.4 Security Considerations
- **ADB Connection**: Local-only (127.0.0.1) to prevent remote access
- **Input Validation**: All user inputs sanitized before ADB commands
- **Process Isolation**: Application runs with standard user privileges
- **Error Information**: No sensitive data exposed in error messages
- **Configuration Protection**: Config file permissions restricted to user only

### 6.5 Critical Implementation Notes - UI Widget Placement

**IMPORTANT**: The following technical details are essential for proper implementation and were discovered through extensive iteration during development.

#### 6.5.1 Go Button Placement Challenge
**Problem**: Direct placement of QPushButton widgets in QTableWidget cells using `setCellWidget()` creates significant positioning and clipping issues:
- CSS margin-based centering causes buttons to extend beyond cell boundaries
- Direct button sizing conflicts with table row height calculations
- Bottom portions of buttons get clipped regardless of button height adjustments
- Uneven spacing between button and cell edges

#### 6.5.2 Container-Based Solution (REQUIRED)
**Solution**: Use container widget approach for proper button centering:

```python
# Create container widget to hold button
button_container = QtWidgets.QWidget()
button_layout = QtWidgets.QHBoxLayout(button_container)

# CRITICAL: Asymmetric margins prevent bottom clipping
button_layout.setContentsMargins(1, 2, 1, 4)  # Left, Top, Right, Bottom
button_layout.setAlignment(QtCore.Qt.AlignCenter)

# Button with specific constraints
go_button = QPushButton("➡️ Go")
go_button.setStyleSheet("""
    QPushButton {
        margin: 0px;           # No margins - container handles positioning
        width: 78px;           # Fits in 100px Action column
        height: 18px;          # Prevents clipping in 32px row
        border-radius: 4px;    # Proper rounded corners
        font-size: 9px;        # Readable in compact button
    }
""")

# Add button to container, then container to table
button_layout.addWidget(go_button)
self.tblBossList.setCellWidget(row_index, 2, button_container)
self.tblBossList.setRowHeight(row_index, 32)  # Accommodate container
```

#### 6.5.3 Size Calculations (CRITICAL)
**Row Height**: 32px (minimum for proper button display)
**Button Height**: 18px (maximum without clipping)
**Container Margins**: 2px top + 4px bottom = 6px
**Total Used**: 18px + 6px = 24px
**Safety Buffer**: 32px - 24px = 8px

#### 6.5.4 Clear All Button State Management
**Visual Feedback**: Button must change color based on state
- **Disabled/Gray**: `background-color: #6c757d` when no targets
- **Enabled/Green**: `background-color: #28a745` when targets loaded
- **State Changes**: Must update both `setEnabled()` and styling together

#### 6.5.5 Alternative Approaches That Failed
**Do NOT use these approaches** - they cause positioning/clipping issues:
- Direct CSS margins for button centering
- Fixed button heights above 20px in 30px rows
- Symmetric container margins (causes bottom clipping)
- Direct button placement without container widgets

### 6.6 Critical ADB Text Input Challenges and Solutions

**CRITICAL FOR REUSE**: The following ADB text input methodology was developed through extensive testing and represents the most reliable approach for Android emulator text field manipulation. This knowledge is essential for any future applications requiring ADB text input.

#### 6.6.1 The Text Input Problem
**Challenge**: Reliably clearing and replacing text in Android application input fields via ADB without appending to existing content or leaving partial values.

**Common Failures Encountered**:
- **Direct `input text` commands**: Append to existing content instead of replacing
- **Ctrl+A key combinations**: Multiple ADB syntaxes failed to replicate manual Ctrl+A behavior
- **Meta modifier approaches**: `--meta 4096 29` and similar methods inconsistent across Android versions
- **Selection-based clearing**: Home+Shift+End, triple-click, and other selection methods unreliable
- **Timing issues**: Race conditions between clearing and text input commands

#### 6.6.2 Failed Approaches (DO NOT USE)
```python
# THESE APPROACHES FAILED - documented for future reference
self.adb_device.shell("input text 'value'")                    # Appends to existing
self.adb_device.shell("input keyevent --meta 4096 29")         # Inconsistent Ctrl+A
self.adb_device.shell("input keyevent 113 29")                 # Separate keys don't combine
self.adb_device.shell("input keyevent --longpress 29")         # Produces 'A' character
self.adb_device.shell("input keyevent 122; input keyevent 59 123")  # Selection unreliable
```

#### 6.6.3 Proven Solution (USE THIS PATTERN)
**Method**: Move-to-end + Multiple-backspace + Text-input + Enter

```python
def send_text_input_reliable(self, adb_device, text: str) -> bool:
    """
    PROVEN METHOD for reliable ADB text input across all Android versions
    Use this exact pattern in future applications
    """
    try:
        # Step 1: Move to end of field (ensures consistent cursor position)
        adb_device.shell("input keyevent 123")  # KEYCODE_MOVE_END
        
        # Step 2: Clear field with multiple backspaces (handles varying field lengths)
        adb_device.shell("input keyevent 67 67 67 67 67")  # 5 backspaces in single command
        
        # Step 3: Send new text
        adb_device.shell(f"input text '{text}'")
        
        # Step 4: Confirm with Enter
        adb_device.shell("input keyevent 66")  # KEYCODE_ENTER
        
        return True
    except Exception as e:
        print(f"ADB text input error: {e}")
        return False
```

#### 6.6.4 Critical Implementation Notes

**Backspace Count Optimization**:
- **5 backspaces**: Handles most coordinate/server values (up to 5 digits)
- **Adjustable**: Increase for longer expected values, decrease for performance
- **Single command**: `67 67 67 67 67` faster than loop of individual commands

**Key Code Reference** (for future applications):
- `123`: MOVE_END - Positions cursor at end of field content
- `67`: DEL/BACKSPACE - Deletes character before cursor
- `66`: ENTER - Confirms input and moves to next field

**Performance Characteristics**:
- **4 ADB commands total**: Move + Backspace + Text + Enter
- **Execution time**: ~0.01-0.02 seconds per field
- **Reliability**: 100% success rate across BlueStacks 5 and Android versions

#### 6.6.5 Speed vs Reliability Trade-offs

**This Method Balances**:
- **Speed**: Fast enough for rapid navigation (3-4 fields in ~0.1 seconds)
- **Reliability**: Works consistently without text appending or partial clearing
- **Simplicity**: No complex key combinations or timing dependencies
- **Compatibility**: Functions across Android versions and emulator types

**Performance Benchmarks**:
- **Navigation sequence**: NavBox (0.4s) + 3 fields (0.06s) + NavGo = ~0.5s total
- **Acceptable for rapid scouting**: Allows manual actions between navigation jumps
- **Scalable**: Pattern works for any number of text fields

#### 6.6.6 Reusability Guidelines

**For Future Applications**:
1. **Use exact method above** - don't attempt to optimize further
2. **Adjust backspace count** based on expected field content length
3. **Always use MOVE_END first** - ensures consistent cursor positioning
4. **Single command for multiple keys** - better performance than loops
5. **Include error handling** - ADB connections can fail

**Integration Pattern**:
```python
class ADBTextInputMixin:
    """Reusable mixin for reliable ADB text input in future applications"""
    
    def reliable_text_input(self, field_coordinates: tuple, text: str) -> bool:
        # Click field
        self.click_at_pixel(*field_coordinates)
        time.sleep(0.2)  # Brief pause for field focus
        
        # Use proven text input method
        return self.send_text_input_reliable(self.adb_device, text)
```

## 7. Error Handling and Validation

### 7.1 Error Codes
- **1001**: BlueStacks not running or accessible
- **1002**: ADB connection failed
- **1003**: Device not responding
- **1004**: Evony application not found/active
- **2001**: Invalid coordinate range
- **2002**: Invalid server number
- **2003**: Malformed target data
- **3001**: Navigation timeout
- **3002**: UI element not found
- **4001**: Configuration file error
- **4002**: Timer initialization failed

### 7.2 Input Validation
- **Coordinate range checking** (Evony map bounds):
    - X coordinates: 1 - 1198 (integer)
    - Y coordinates: 1 - 1200 (integer)
- **Server number validation**:
    - Range: 1 - 9999 (4-digit maximum)
    - Format: Integer only
- **Target data format verification**:
    - Minimum 3 tab-separated fields per line
    - Last two fields must be valid integers
    - Boss/Barb description cannot be empty

### 7.3 Game State Errors
- **Connection Recovery**: 3 retry attempts with 2-second delays
- **UI Element Detection**: Timeout after 5 seconds
- **Navigation Validation**: Verify successful coordinate entry
- **Logging**: All errors logged to iScoutTool.log with timestamps

## 8. Performance Requirements

### 8.1 Response Time
- countdown timer: < 100ms response
- UI interactions: < 100ms response
- ADB commands: < 500ms execution
- Navigation sequences: < 5 seconds complete

### 8.2 Reliability
- Connection stability with retry logic
- Graceful handling of game state changes
- Data validation and error recovery

### 8.3 Logging Strategy
- **Log File**: `iScoutTool.log` in application directory
- **Log Levels**: ERROR, WARNING, INFO, DEBUG
- **Log Rotation**: Maximum 10MB file size, keep 3 backup files
- **Log Content**:
    - Application startup/shutdown
    - ADB connection events
    - Navigation attempts and results
    - Error conditions with stack traces
    - User actions (button clicks, data loads)
- **Privacy**: No sensitive game data logged (coordinates only)

## 9. Future Enhancements

### 9.1 Planned Features
- Multiple target queue processing
- Alliance coordination features
- Advanced filtering and sorting
- Automated report generation
- Multiple BlueStacks instance support

### 9.2 Extensibility
- Plugin architecture for additional game automation
- Custom preset creation interface
- API for external tool integration
- Enhanced logging and analytics

## 10. Installation and Setup

### 10.1 Installation Steps
1. **Prerequisites**:
    - Install Python 3.8+ from python.org
    - Install BlueStacks 5 from bluestacks.com
    - Enable ADB debugging in BlueStacks settings

2. **Application Setup**:
    ```bash
    # Install required Python packages
    pip install PyQt5>=5.15.0 ppadb>=3.0.0
    
    # Clone or download iScoutTool application
    # Ensure Resources/locations.xml exists
    ```

3. **BlueStacks Configuration**:
    - Start BlueStacks 5
    - Install Evony application
    - Enable Advanced Settings > Android Debug Bridge (ADB)
    - Verify ADB connection: `adb devices` should show `127.0.0.1:5555`

4. **First Run Setup**:
    - Launch iScoutTool application (will load iScoutToolModern.ui automatically)
    - Modern dark theme interface will be applied
    - Configure home server coordinates in enhanced UI fields
    - Test ADB connection with "🏠 Go Home" button
    - Verify timer functionality and emulator connection status indicator

### 10.2 Troubleshooting
- **ADB Connection Issues**: Restart BlueStacks, check firewall settings
- **Screen Detection Problems**: Verify Evony is running and visible
- **Coordinate Accuracy**: Use screenshot tool to verify preset locations
- **Timer Not Working**: Check system audio settings and permissions

## 11. Testing Strategy

### 10.1 Unit Testing
- Data parsing validation
- Coordinate calculation accuracy
- Preset loading and execution

### 10.2 Integration Testing
- BlueStacks connection reliability
- Evony application interaction
- End-to-end navigation workflows

### 10.3 User Acceptance Testing
- Real-world scouting scenarios
- Performance under typical usage
- UI usability and workflow efficiency