# View Enemy Button Feature

## Overview
The **View Enemy** button has been successfully added to the Quick Actions section of iScoutTool. This feature allows users to select any target from the Scout Targets table and view it on the Enemy Server without starting the bubble timer.

## Location
- **Section**: Quick Actions (bottom panel)
- **Position**: Third button after "iScout Go" and "Go Enemy"
- **Icon**: 👁️ (Eye icon)
- **Button Text**: "View Enemy"

## Functionality

### What it does:
1. **Target Selection**: Opens a dialog showing all loaded scout targets with their status (completed ✓ or pending ○)
2. **Enemy Server Navigation**: Uses the current Enemy Server value from the UI
3. **Coordinate Navigation**: Navigates to the selected target's coordinates on the specified enemy server
4. **No Timer**: Unlike "Go Enemy", this does NOT start the bubble timer (view-only mode)

### How to use:
1. **Load Targets**: First use "Load Targets" button to populate the Scout Targets table
2. **Set Enemy Server**: Enter the enemy server number in the Enemy Server field
3. **Click View Enemy**: Click the "View Enemy" button in Quick Actions
4. **Select Target**: Choose a target from the dropdown list showing:
   - Status indicator (✓ completed, ○ pending)
   - Target number (#1, #2, etc.)
   - Target type (Boss, Barb, etc.)
   - Coordinates (X, Y)
5. **Navigate**: The app will navigate to the selected target on the enemy server

### Example Dialog:
```
Select Target to View on Enemy Server
Choose a target to view on Enemy Server 123:

○ #1: Boss at (450, 678)
✓ #2: Barb at (234, 567)
○ #3: Boss at (789, 123)
```

## Key Features

### Validation:
- Checks if scout targets are loaded
- Validates enemy server number is set
- Shows appropriate error messages for missing data

### Smart Display:
- Shows completion status for each target
- Displays target type and coordinates
- Numbers targets for easy identification

### Navigation:
- Uses the same navigation system as other buttons
- Navigates to exact coordinates from the selected target
- Uses the enemy server value from the UI field
- Does NOT start the bubble timer (view-only mode)

## Technical Implementation

### Files Modified:
- `iScoutToolModern.ui`: Added btnViewEnemy button to Quick Actions layout
- `iScoutTool.py`: 
  - Added QInputDialog import
  - Connected button signal in `connect_ui_signals()`
  - Implemented `on_view_enemy_clicked()` method

### Code Integration:
- Uses existing target data structure (`self.targets`)
- Leverages existing navigation system (`navigate_to_coordinates()`)
- Follows same error handling patterns as other buttons
- Maintains UI consistency with existing button handlers

## Benefits
1. **Quick Target Review**: Easily view any target on enemy server without changing current target
2. **No Timer Impact**: View targets without starting bubble timer
3. **Target Selection**: Choose specific targets from dropdown instead of table navigation  
4. **Status Awareness**: See which targets are completed vs pending
5. **Server Flexibility**: Uses current enemy server setting for maximum flexibility

## Usage Scenarios
- **Reconnaissance**: Scout enemy server locations before committing to attacks
- **Verification**: Double-check target locations on enemy server
- **Planning**: Review multiple targets to plan attack sequences
- **Coordination**: Verify coordinates with team members on enemy server