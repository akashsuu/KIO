import sys
import os
import random
import win32gui
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QMenu, QSystemTrayIcon
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect
from PyQt6.QtGui import QPixmap, QIcon, QAction, QTransform

class KioCat(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()
        self.loadAnimations()
        
        # State machine
        self.state = "sit"
        self.direction = 1 # 1 for right, -1 for left
        self.frame_index = 0
        
        # Timers
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(150) # ~6-7 fps for a relaxed cat feel
        
        self.behavior_timer = QTimer(self)
        self.behavior_timer.timeout.connect(self.update_behavior)
        self.behavior_timer.start(3000) # Every 3 seconds, decide what to do
        
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.update_position)
        self.move_timer.start(50) # 20fps for smooth movement
        
        # Position and physics
        self.is_dragging = False
        self.drag_offset = QPoint()
        
        self.velocity_x = 0
        self.velocity_y = 0
        
        self.place_randomly()

    def initUI(self):
        # Frameless, on top, hidden from alt-tab and taskbar
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        
        # Setup tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_menu = QMenu()
        
        self.pause_action = QAction("Pause", self)
        self.pause_action.triggered.connect(self.toggle_pause)
        
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        self.tray_menu.addAction(self.pause_action)
        self.tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(self.tray_menu)
        
        self.is_paused = False

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_action.setText("Resume")
            self.behavior_timer.stop()
            self.move_timer.stop()
            self.state = "sit"
        else:
            self.pause_action.setText("Pause")
            self.behavior_timer.start(3000)
            self.move_timer.start()

    def get_taskbar_rect(self):
        hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
        if hwnd:
            rect = win32gui.GetWindowRect(hwnd)
            return QRect(rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
        return None

    def get_screen_rect(self):
        return QApplication.primaryScreen().geometry()

    def place_randomly(self):
        screen = self.get_screen_rect()
        taskbar = self.get_taskbar_rect()
        
        pet_w, pet_h = 64, 64 # fallback size
        if hasattr(self, 'animations') and "sit" in self.animations and self.animations["sit"]:
            pet_w = self.animations["sit"][0].width()
            pet_h = self.animations["sit"][0].height()
        
        ground_y = screen.bottom() - pet_h
        
        if taskbar:
            # If taskbar is on the bottom
            if taskbar.bottom() == screen.bottom() and taskbar.width() == screen.width():
                ground_y = taskbar.top() - pet_h
        
        x = random.randint(0, screen.width() - pet_w)
        self.move(x, ground_y)

    def loadAnimations(self):
        self.animations = {}
        # Make sure we use the current script dir or a specific path
        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kio_cat")
        
        if not os.path.exists(base_path):
            print(f"Directory {base_path} not found.")
            return

        for state_dir in os.listdir(base_path):
            dir_path = os.path.join(base_path, state_dir)
            if os.path.isdir(dir_path):
                frames = []
                # Sort files naturally if possible, or just alphabetically
                files = sorted([f for f in os.listdir(dir_path) if f.lower().endswith('.png')])
                for f in files:
                    pixmap = QPixmap(os.path.join(dir_path, f))
                    frames.append(pixmap)
                
                if frames:
                    self.animations[state_dir.lower()] = frames
        
        # Set default size and tray icon based on first 'sit' frame
        if "sit" in self.animations and self.animations["sit"]:
            first_frame = self.animations["sit"][0]
            self.resize(first_frame.size())
            self.label.resize(first_frame.size())
            self.tray_icon.setIcon(QIcon(first_frame))
            self.tray_icon.show()
            self.tray_icon.setToolTip("Kio Cat")

    def update_animation(self):
        if not self.animations:
            return
            
        anim_state = self.state if self.state in self.animations else "sit"
        if anim_state not in self.animations:
            # Fallback to whatever is available
            anim_state = list(self.animations.keys())[0]
            
        frames = self.animations[anim_state]
        self.frame_index = (self.frame_index + 1) % len(frames)
        
        pixmap = frames[self.frame_index]
        if self.direction == -1:
            # Flip horizontally
            transform = QTransform().scale(-1, 1)
            pixmap = pixmap.transformed(transform)
            
        self.label.setPixmap(pixmap)

    def update_behavior(self):
        if self.is_dragging or self.is_paused:
            return
            
        # Behavior choices
        choices = ["sit", "walk", "turn", "pause", "look_around"]
        weights = [0.4, 0.3, 0.1, 0.1, 0.1]
        
        self.state = random.choices(choices, weights=weights)[0]
        
        if self.state == "turn":
            self.direction *= -1
            self.state = "sit" # Transition to sit after turning
            self.velocity_x = 0
        elif self.state == "walk":
            # Give a slow, relaxed walking speed
            self.velocity_x = random.randint(1, 3) * self.direction
        else:
            self.velocity_x = 0
            
        # Randomize timer for next behavior (2 to 6 seconds)
        self.behavior_timer.setInterval(random.randint(2000, 6000))

    def update_position(self):
        if self.is_dragging or self.is_paused:
            return
            
        screen = self.get_screen_rect()
        taskbar = self.get_taskbar_rect()
        
        # Define ground level (with a visual offset to push it ~2cm down)
        y_offset = 75
        ground_y = screen.bottom() - self.height() + y_offset
        
        # Determine if we are above the taskbar
        if taskbar:
            # Simple check for bottom taskbar
            if taskbar.bottom() == screen.bottom():
                # If cat is horizontally within taskbar area
                if self.x() + self.width() > taskbar.left() and self.x() < taskbar.right():
                    ground_y = taskbar.top() - self.height() + y_offset
        
        # Apply gravity if above ground
        if self.y() < ground_y:
            self.velocity_y += 1 # Gravity
        else:
            self.velocity_y = 0
            self.move(self.x(), ground_y)
            
        new_x = self.x() + self.velocity_x
        new_y = self.y() + self.velocity_y
        
        # Screen edge collisions
        if new_x < screen.left():
            new_x = screen.left()
            self.direction = 1 # Turn right
            self.velocity_x = abs(self.velocity_x) # Start moving right
        elif new_x > screen.right() - self.width():
            new_x = screen.right() - self.width()
            self.direction = -1 # Turn left
            self.velocity_x = -abs(self.velocity_x) # Start moving left
            
        # Ground collision
        if new_y > ground_y:
            new_y = ground_y
            
        self.move(new_x, new_y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            # Record offset for smooth dragging
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            
            # Cat is picked up
            self.state = "sit"
            self.velocity_x = 0
            self.velocity_y = 0
            
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            # Show context menu
            self.tray_menu.exec(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            # Resume normal behavior
            self.behavior_timer.start(1000) 
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Crucial for system tray apps without a standard main window
    app.setQuitOnLastWindowClosed(False)
    
    pet = KioCat()
    pet.show()
    
    sys.exit(app.exec())
