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
- Windows operating system
- BlueStacks 5 installed and configured
- ADB debugging enabled on BlueStacks
- Python 3.x with required dependencies
- Network connectivity to BlueStacks on localhost:5555

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
- **Data Format**: Tab-separated text format supporting either "Artic Barbarians" or a Boss
    Data is best parsed by working from right to left, parsing the y coordinate, x coordinate, with the rest combined to result in the "Boss/Barb" data string

  - Artic Barbarians
    - "Artic Barbians" with level, power, and "Free" or "Occupied" term
        - These four elements are tab separated, but will be merged and separated by a space for each component
        - The merged string will be placed in the "Boss/Barb" column of the row
    - X coordinate in Evony
        - an integer value indicating where to navigate in the x screen coordinates of Evony
    - Y coordinate in Evony
        - an integer value indicating where to navigate in the y screen coordinates of Evony

  - Boss
        - Boss Name combined with Level
        - an integer value indicating where to navigate in the x screen coordinates of Evony
        - an integer value indicating where to navigate in the y screen coordinates of Evony


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
- **btnIScoutGoHome**: Navigate to home coordinates
- **btnIScoutGoEnemy**:  Navigate to enemy server and start bubble countdown timer.
    - First time to enemy server requires selecting a different choice to move to a different server, and will drop the gamer in a randam location.
- **lblTimer**: Display operation timing/countdown.  Not user editable, and will run in a separate thread so not impacted by other functionality.

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
- **Click Actions**: Single-point targeting
- **Drag Actions**: Will not use drag actions in this application
- **Validation**: Coordinate bounds checking based on Evony screen size in pixels

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
```python
def start_timer():
    """Start 5 minute countdown timer"""

def beep_30_secs()
    """Begin beep sound once per second after countdown timer reaches 30 seconds, and until it reaches 0 seconds"""

def update_timer()
    """ Update lblTimer with the current countdown time, in the format MM:SS, once per second 

```

#### 5.1.1 Connection Management
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

### 6.2 Evony Application Interface
- **Package Name**: Target Evony application package
- **Activity Detection**: Verify correct game screen is active
- **Input Methods**:
  - Touch events for clicks
  - Text input for coordinate entry

### 6.3 Data Persistence
- **Target Lists**: Save/load target data for session continuation
    - intHomeServer
    - intHomeXLoc
    - intHomeYLoc
    - intEnemyServer
- **Presets**: XML-based location configuration management
    file name:  locations.xml in subdirectory ./Resources
## 7. Error Handling and Validation

### 7.1 Connection Errors
- BlueStacks not running or accessible
- ADB connection failures
- Device not responding

### 7.2 Input Validation
- Coordinate range checking (game map bounds)
    - width 0 - 1198
    - height 0 - 1200
- Server number validation
    - 0 - 9999
- Target data format verification

### 7.3 Game State Errors
- Evony application not active
- Unexpected screen state
- Navigation failures

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

## 10. Testing Strategy

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