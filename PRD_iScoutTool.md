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

## 2. Technical Architecture

### 2.1 Core Technologies
- **Python 3.x**: Primary development language
- **PyQt5**: GUI framework for user interface
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
- **Requirement**: Establish connection to BlueStacks 5 on port 5555 using ppadb
- **Implementation**: Automatic detection and connection to running BlueStacks instance
- **Error Handling**: Connection retry logic and user notifications for connection issues

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

#### 3.2.1 Main Table (tblBossList)
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

#### 5.1.1 Timer Management
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

#### 5.1.2 Configuration Management
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

#### 5.1.3 Connection Management
```python
def connect_to_bluestacks():
    """Establish ADB connection to BlueStacks on port 5555"""
    
def verify_evony_running():
    """Check if Evony application is active"""
    
def reconnect_if_needed():
    """Handle connection drops and reconnection"""
```

#### 5.1.2 Input Processing
```python
def parse_scout_text(text_input):
    """Parse tab-separated scout report into target objects"""
    
def load_targets_to_table():
    """Populate UI table with parsed target data"""
    
def validate_coordinates(x, y, server):
    """Ensure coordinate values are within game bounds"""
```

#### 5.1.3 Game Automation
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

#### 5.1.4 Navigation Workflow
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

#### 5.2.1 Button Actions
```python
def on_load_table_clicked():
    """Process text input and populate target table"""
    
def on_clear_all_clicked():
    """Clear all rows in tblBossList, clear txtiScoutBoss, and reset UI state"""
    
def on_go_home_clicked():
    """Execute return to home coordinates using intHomeServer, intHomeXLoc, intHomeYLoc """
    
def on_target_go_clicked(row_index):
    """Navigate to specific target from table row using intEnemyServer,  row cell from column labeled 'X', and row cell from column labeled 'Y'"""
```

#### 5.2.2 Table Interactions
```python
def on_got_it_checkbox_changed(row, checked):
    """Mark target as completed/incomplete"""
    
def on_table_row_selected(row):
    """Handle target selection for actions"""
```

## 6. Integration Specifications

### 6.1 ppadb Integration
- **Connection String**: `127.0.0.1:5555` (BlueStacks default)
- **Device Detection**: Automatic discovery of connected devices
- **Command Execution**: Shell commands for input simulation
- **Screen Interaction**: Touch events via ADB input commands
- **ADB Commands Used**:
    - Click: `input tap <x> <y>`
    - Text input: `input text "<string>"`
    - Key events: `input keyevent <keycode>`
        - KEYCODE_CTRL_LEFT: 113
        - KEYCODE_A: 29  
        - KEYCODE_DEL: 67
        - KEYCODE_ENTER: 66
    - Screen size: `wm size`
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
    - Launch iScoutTool application
    - Configure home server coordinates in UI fields
    - Test ADB connection with "Go Home" button
    - Verify timer functionality

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