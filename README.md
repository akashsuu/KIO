# Kio Cat

A cute desktop pet cat built with PyQt6 that roams around your screen, interacts with you, and stays on top of other windows.

## Features

- **Animated states**: Sit, walk, stand, turn, and transition animations
- **Screen navigation**: Walks around, avoids the taskbar, and bounces off screen edges
- **Interactive**: 
  - Left-click and drag to move the cat
  - Right-click to open the system tray menu
  - Pause/resume functionality via tray menu
- **System tray integration**: Minimize to tray, access controls from tray menu
- **Automatic ground detection**: Cat walks on "ground" above the taskbar

## Requirements

- Python 3.8+
- PyQt6 >= 6.5.0
- pywin32 >= 306 (Windows only, for taskbar detection)

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure you have the cat animation PNG frames in the `kio_cat/` directory

## Running

```bash
python main.py
```

The cat will appear on your screen. Use the system tray icon (bottom-right on Windows) to:
- Pause/Resume the cat's behavior
- Exit the application

## Project Structure

- `main.py` - Main application code
- `requirements.txt` - Python dependencies
- `kio_cat/` - Animation frames organized by state:
  - `SIT/` - Sitting animation
  - `WALK/` - Walking animation
  - `STAND/` - Standing animation
  - `STANDUP_TO_SIT/` - Transition animations
  - `SIT_TO_STANDUP/` - Transition animations