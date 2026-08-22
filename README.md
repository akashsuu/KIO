# Kio Cat

Your new digital companion that's always got your back (or in front of your face)!

---

## What's This?

Kio Cat is a delightful desktop pet built with PyQt6 that roams around your screen, interacts with you, and adds a bit of whimsy to your daily computing. Think of it as a digital cat that doesn't shed, doesn't need feeding, and actually stays off your keyboard (most of the time).

---

## Features

| Feature | Description |
|---------|-------------|
| **Animated States** | Sit, walk, stand, turn, and smooth transitions between them |
| **Screen Navigation** | Walks around, avoids your taskbar, and bounces off screen edges |
| **Interactive** | Left-click & drag to move, right-click for the tray menu |
| **System Tray** | Minimize to tray, pause/resume, exit from the icon menu |
| **Smart Ground** | Automatically walks "above" the taskbar, never gets stuck |

---

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Run
python main.py
```

The cat will appear on your screen. Here's how to interact with it:

- **Left-click + drag** – Pick up and move the cat
- **Right-click** – Open the system tray menu
- **Tray icon** – Pause, resume, or exit the app

---

## Requirements

- Python 3.8+
- [PyQt6](https://pypi.org/project/PyQt6/) >= 6.5.0
- [pywin32](https://pypi.org/project/pywin32/) >= 306 *(Windows only for taskbar detection)*

---

## Project Structure

```
kio_cat/          # Animation frames
├── SIT/          # Sitting animation
├── WALK/         # Walking animation  
├── STAND/        # Standing animation
├── STANDUP_TO_SIT/  # Transition: standing → sitting
└── SIT_TO_STANDUP/  # Transition: sitting → standing

main.py           # The cat's brain (and body)
requirements.txt  # Python dependencies
```

---

## States & Behavior

The cat's state machine decides what it does every few seconds:

- **Sit** (30% chance) – Just sit there, looking cute
- **Walk** (40% chance) – Roam around the screen
- **Stand** (20% chance) – Stand up tall
- **Turn** (10% chance) – Change direction, then choose a new action

When it transitions between sitting and standing, you'll see smooth animation sequences!

---

## Fun Facts

- The cat respects your taskbar and walks *above* it
- Drag the cat anywhere on screen – it'll remember the spot
- Right-click the tray icon for quick controls

---

## Building / Customizing

Want to add more animations or modify behavior? The code is heavily commented and the state machine is in `main.py`. Animation frames go in `kio_cat/<state>/` as PNG files.

---

**Made with PyQt6**

*May your cat always land on its feet (and stay on top of your windows).*