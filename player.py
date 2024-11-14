import sys
import pyautogui
from PySide6.QtGui import QMouseEvent, QWheelEvent, QTouchEvent, QIcon
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                              QHBoxLayout, QWidget, QPushButton, QMessageBox)
from PySide6.QtCore import Qt, QUrl, QTimer, QSize
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage

class CustomWebPage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent

    def javaScriptConfirm(self, url, msg):
        return False

    def javaScriptAlert(self, url, msg):
        return

    def javaScriptPrompt(self, url, msg, default):
        return False, ""

    def createWindow(self, _type):
        new_page = CustomWebPage(self.main_window)
        new_page.urlChanged.connect(self.main_window.browser.setUrl)
        return new_page

class ShifIQKioskBrowser(QMainWindow):
    def __init__(self, url: str, browser=None) -> None:
        super().__init__()
        
        # Initialize pyautogui
        pyautogui.FAILSAFE = False
        
        # Create a timer for global mouse tracking
        self.mouse_track_timer = QTimer(self)
        self.mouse_track_timer.timeout.connect(self.check_mouse_position)
        self.mouse_track_timer.start(100)  # Check every 100ms
        
        self.last_mouse_pos = pyautogui.position()
        
        self.url = url
        self.setWindowTitle("ShifIQ Kiosk Player")

        # Create floating back button
        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon("back.svg"))
        self.back_button.setIconSize(QSize(32, 32))
        self.back_button.clicked.connect(self.go_to_start)
        self.back_button.setFixedSize(50, 50)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #cccccc;
                border-radius: 25px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border: 2px solid #999999;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        self.back_button.hide()

        # Create a container for the browser
        self.browser = browser if browser else QWebEngineView()
        self.browser.installEventFilter(self)
        self.browser.setPage(CustomWebPage(self))
        self.browser.setUrl(QUrl(url))
        self.browser.urlChanged.connect(self.update_url)

        # Main layout without the button
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Position the floating button
        self.back_button.setParent(self)
        self.back_button.raise_()
        
        # Position button in bottom-left corner with margin
        margin = 20
        self.back_button.move(margin, self.height() - self.back_button.height() - margin)

        self.showFullScreen()
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setMouseTracking(True)
        self.browser.setMouseTracking(True)

        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.timeout.connect(self.report_inactivity)
        self.inactivity_timer.start(1000)

        self.last_mouse_move_time = 0

        self.warning_shown = False  # Flag for the warning
        self.warning_time = 300  # 5 minutes in seconds
        self.reset_time = 600    # 10 minutes in seconds

    def eventFilter(self, watched_object, event):
        # Check events in the browser
        if watched_object == self.browser:
            if event.type() in [
                event.Type.MouseMove,
                event.Type.MouseButtonPress,
                event.Type.Wheel,
                event.Type.TouchBegin,
                event.Type.TouchUpdate,
                event.Type.TouchEnd
            ]:
                self.reset_inactivity_timer()
                
        return super().eventFilter(watched_object, event)

    def enterEvent(self, event: QMouseEvent) -> None:
        self.reset_inactivity_timer()
        super().enterEvent(event)

    def leaveEvent(self, event: QMouseEvent) -> None:
        super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.reset_inactivity_timer()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.reset_inactivity_timer()
        super().mousePressEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.reset_inactivity_timer()
        super().wheelEvent(event)

    def touchEvent(self, event: QTouchEvent) -> None:
        self.reset_inactivity_timer()
        super().touchEvent(event)

    def report_inactivity(self):
        self.last_mouse_move_time += 1
        
        # After 5 minutes: Show warning
        if self.last_mouse_move_time >= self.warning_time and not self.warning_shown:
            self.show_warning_message()
            self.warning_shown = True
            
        # After 10 minutes: Reset to main page
        if self.last_mouse_move_time >= self.reset_time:
            self.reset_url()

    def show_warning_message(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Inactivity warning")
        msg.setText("You were inactive for a longer time!")
        msg.setInformativeText("In 5 minutes you will be automatically redirected to the main page.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowFlags(Qt.WindowStaysOnTopHint)  # Window stays on top
        msg.exec()

    def reset_inactivity_timer(self):
        self.last_mouse_move_time = 0
        self.warning_shown = False  # Reset des Warning-Flags

    def reset_url(self):
        self.browser.setUrl(QUrl(self.url))
        self.reset_inactivity_timer()

    def update_url(self, qurl: QUrl):
        current_url = qurl.toString()
        self.back_button.setVisible(current_url != self.url)
        self.reset_inactivity_timer()

    def go_to_start(self):
        self.browser.setUrl(QUrl(self.url))

    # Add resizeEvent to update button position when window is resized
    def resizeEvent(self, event):
        super().resizeEvent(event)
        margin = 20
        self.back_button.move(margin, self.height() - self.back_button.height() - margin)

    def check_mouse_position(self):
        current_pos = pyautogui.position()
        if current_pos != self.last_mouse_pos:
            self.reset_inactivity_timer()
            self.last_mouse_pos = current_pos

if __name__ == "__main__":
    app = QApplication(sys.argv)
    url = "https://docs.secnex.io/"
    window = ShifIQKioskBrowser(url)
    window.show()

    sys.exit(app.exec())