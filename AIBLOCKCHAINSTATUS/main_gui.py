# main_gui.py
import sys
import asyncio
import uuid
from datetime import datetime
from io import BytesIO

# PyQt Imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QMenuBar, QAction, QFileDialog,
    QLabel, QMessageBox, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QMetaObject, Q_ARG, QGenericArgument
from PyQt5.QtGui import QColor, QPalette, QFont, QPixmap, QImage

# External Libraries
import qrcode
from PIL import Image

# Import the core components
from ai_algo_manager import AIAlgoManager

# --- QThread for Asynchronous Engine (NOW WITH THREAD-SAFE SIGNAL) ---
class AsyncEngineThread(QThread):
    """Hosts the asyncio event loop and handles thread-safe logging."""
    
    # 🚨 Thread-Safe Signal: (message, color)
    log_signal = pyqtSignal(str, str) 
    
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.loop = asyncio.new_event_loop()
        
    def run(self):
        """Sets the event loop and runs the engine start task."""
        asyncio.set_event_loop(self.loop)
        
        # Inject the thread-safe logging mechanism into the manager's engine
        # This replaces the direct GUI update with a signal emission
        self.engine.manager.log_signal = self.log_signal
        
        self.engine.task = self.loop.create_task(self.engine.start_engine())
        self.loop.run_forever() 

    def stop(self):
        """Gracefully stops the engine and the asyncio loop."""
        if self.engine.running:
            self.engine.stop_engine()
        
        if self.engine.task and not self.engine.task.done():
            # Schedule cancellation safely on the event loop thread
            self.loop.call_soon_threadsafe(self.engine.task.cancel)
        
        # Stop the loop thread-safely
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.wait()

# --- AIAlgoGUI Class (Fully Implemented) ---
class AIAlgoGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PROOF OF A.I. ALGORITHM: CORE WALLET")
        self.setGeometry(100, 100, 1000, 750)
        
        self.apply_dark_theme()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.create_menu_bar()
        
        # 1. Create the essential logging terminal first.
        self.create_logging_terminal() 
        
        # 2. Initialize the Manager immediately after the terminal is ready.
        self.manager = AIAlgoManager(self.log_terminal) 
        
        # 3. Create GUI panels that rely on manager attributes.
        self.create_wallet_panel()
        self.create_api_panel()
        
        # 4. Set up the Async Engine Thread and connect the signal.
        self.engine_thread = AsyncEngineThread(self.manager.engine)
        self.engine_thread.log_signal.connect(self.thread_log_message) # 🚨 Thread-safe connection
        
        # 5. QTimer for periodic GUI status updates.
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_labels)
        self.status_timer.start(1000) # Update status every second

        self.manager.log_message("GUI Shell Initialized. Ready for API Key.")
        
    def apply_dark_theme(self):
        """Sets a custom dark/cyberpunk color palette."""
        palette = QPalette()
        DARK_CHARCOAL = QColor(30, 30, 30)
        DARK_GRAY = QColor(45, 45, 45)
        BRIGHT_TEAL = QColor(0, 255, 255)
        BRIGHT_GOLD = QColor(255, 215, 0)

        palette.setColor(QPalette.Window, DARK_CHARCOAL)
        palette.setColor(QPalette.WindowText, BRIGHT_TEAL)
        palette.setColor(QPalette.Base, DARK_GRAY)
        palette.setColor(QPalette.Text, BRIGHT_TEAL)
        palette.setColor(QPalette.Button, DARK_GRAY)
        palette.setColor(QPalette.ButtonText, BRIGHT_TEAL)
        self.status_text_color = BRIGHT_GOLD 
        self.setPalette(palette)
        
    def create_menu_bar(self):
        """Creates the File, Settings, Help menu bar."""
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("File")
        
        save_log_action = QAction("Save Log (JSON/CSV)", self)
        save_log_action.triggered.connect(self.save_log_popup)
        file_menu.addAction(save_log_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        menu_bar.addMenu("Network (P2P)")
        menu_bar.addMenu("Help")
        
    def create_wallet_panel(self):
        """Creates the top panel with Wallet details and action buttons."""
        wallet_panel = QFrame()
        wallet_panel.setFrameShape(QFrame.Box)
        wallet_panel.setFrameShadow(QFrame.Raised)
        wallet_panel.setStyleSheet("border: 1px solid #00FFFF; padding: 5px;")
        
        grid = QGridLayout(wallet_panel)
        
        # 1. Address Label (Real Unique Address)
        grid.addWidget(QLabel("Unique Address:"), 0, 0)
        self.address_label = QLabel(self.manager.wallet_address) 
        self.address_label.setFont(QFont('Courier New', 10))
        self.address_label.setStyleSheet("color: #FFD700;")
        grid.addWidget(self.address_label, 0, 1)

        # 2. Balance Label
        grid.addWidget(QLabel("Current Balance:"), 1, 0)
        self.balance_label = QLabel("0.00 %AIA%")
        self.balance_label.setStyleSheet("color: #00FF00; font-size: 16pt; font-weight: bold;")
        grid.addWidget(self.balance_label, 1, 1)

        # 3. Difficulty Label
        grid.addWidget(QLabel("Current Difficulty:"), 2, 0)
        self.difficulty_label = QLabel("N/A")
        self.difficulty_label.setStyleSheet("color: #FF5555; font-weight: bold;")
        grid.addWidget(self.difficulty_label, 2, 1)

        # 4. Status Widgets (Block/Peers)
        self.block_label = QLabel("Block: 0")
        self.peer_label = QLabel("Peers: 0")
        self.block_label.setStyleSheet(f"color: {self.status_text_color.name()};")
        self.peer_label.setStyleSheet(f"color: {self.status_text_color.name()};")
        
        status_hlayout = QHBoxLayout()
        status_hlayout.addWidget(self.block_label)
        status_hlayout.addWidget(self.peer_label)
        status_hlayout.addStretch(1)
        grid.addLayout(status_hlayout, 3, 0, 1, 2)
        
        # 5. QR Code Display and Buttons
        qr_widget = self.create_qr_widget(self.manager.wallet_address)
        grid.addWidget(qr_widget, 0, 2, 3, 1)
        
        # 6. Action Buttons (Send, Scan QR Code)
        btn_send = QPushButton("Send Token (TX)")
        btn_send.setStyleSheet("background-color: #0088AA; color: white;")
        btn_send.clicked.connect(self.send_token_popup)
        
        btn_qr_scan = QPushButton("Scan QR Code")
        btn_qr_scan.setStyleSheet("background-color: #8800AA; color: white;")
        btn_qr_scan.clicked.connect(lambda: self.show_popup("Scan QR Code", "Simulated feature: Opens camera/file dialog for scanning."))
        
        action_vlayout = QVBoxLayout()
        action_vlayout.addWidget(btn_send)
        action_vlayout.addWidget(btn_qr_scan)
        grid.addLayout(action_vlayout, 3, 2, 1, 1)
        
        self.main_layout.addWidget(wallet_panel)

    def create_qr_widget(self, data: str) -> QWidget:
        """Generates a QR code for the address and displays it in a widget."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img_pil = qr.make_image(fill_color="white", back_color="black").convert('RGB')
        
        # Convert PIL Image to QPixmap
        data = BytesIO()
        img_pil.save(data, "PNG")
        qimage = QImage.fromData(data.getvalue())
        pixmap = QPixmap.fromImage(qimage)

        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        qr_label.setAlignment(Qt.AlignCenter)
        
        return qr_label

    def create_api_panel(self):
        """Creates the API Key input and control buttons."""
        api_panel = QHBoxLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter AI API Key (Gemini/ChatGPT/Copilot...)")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        api_panel.addWidget(self.api_key_input)
        
        load_btn = QPushButton("Load Key")
        load_btn.clicked.connect(self.load_api_key)
        api_panel.addWidget(load_btn)
        
        self.start_btn = QPushButton("START AI ALGORITHM")
        self.start_btn.setStyleSheet("background-color: #FF5733; color: white; font-weight: bold;")
        self.start_btn.clicked.connect(self.toggle_algorithm)
        api_panel.addWidget(self.start_btn)
        
        self.main_layout.addLayout(api_panel)

    def create_logging_terminal(self):
        """Creates the scrollable terminal for logging."""
        log_label = QLabel("A.I. Algorithm Network Terminal")
        log_label.setStyleSheet("color: white; margin-top: 10px;")
        self.main_layout.addWidget(log_label)
        
        self.log_terminal = QTextEdit() 
        self.log_terminal.setReadOnly(True)
        self.log_terminal.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', Courier, monospace;
                background-color: #2D2D2D;
                color: #00FFCC; 
                border: 2px solid #00FFFF;
            }
        """)
        self.main_layout.addWidget(self.log_terminal)

    # --- Thread-Safe Logging Method ---
    def thread_log_message(self, message: str, color: str):
        """Receives the signal from the engine thread and updates the log safely."""
        # This function is called via the signal and runs in the GUI's main thread.
        self.manager.log_message(message, color)

    # --- Interaction and Logic Methods ---
    
    def update_status_labels(self):
        """Updates all labels with current manager state."""
        self.block_label.setText(f"Block: {self.manager.block_height}")
        self.peer_label.setText(f"Peers: {self.manager.peer_count}")
        self.balance_label.setText(f"{self.manager.balance:.4f} %AIA%")
        
        diff = f"{self.manager.current_difficulty:.2f}" if self.manager.current_difficulty > 0 else "N/A"
        self.difficulty_label.setText(diff)

    def load_api_key(self):
        """Loads key into the manager."""
        key = self.api_key_input.text().strip()
        self.manager.set_api_key(key)
        
    def toggle_algorithm(self):
        """Starts or stops the async engine."""
        if not self.manager.is_running:
            if not self.manager.set_api_key(self.api_key_input.text().strip()):
                return
            
            self.engine_thread.start()
            self.manager.is_running = True
            
            self.start_btn.setText("STOP ALGORITHM")
            self.start_btn.setStyleSheet("background-color: #008000; color: white; font-weight: bold;")
        else:
            self.engine_thread.stop()
            self.manager.is_running = False
            
            self.start_btn.setText("START AI ALGORITHM")
            self.start_btn.setStyleSheet("background-color: #FF5733; color: white; font-weight: bold;")

    def send_token_popup(self):
        """
        Fully implemented 'Send Token' utility pop-up.
        """
        dialog = QMessageBox()
        dialog.setWindowTitle("Send %AIA% Token Transaction")
        dialog.setIcon(QMessageBox.Information)
        
        # Create custom layout for input
        layout = QVBoxLayout()
        address_input = QLineEdit()
        address_input.setPlaceholderText("Recipient Address (AIA-QTL-...)")
        amount_input = QLineEdit()
        amount_input.setPlaceholderText("Amount of %AIA% to send")
        
        layout.addWidget(QLabel(f"Current Balance: {self.manager.balance:.4f} %AIA%"))
        layout.addWidget(address_input)
        layout.addWidget(amount_input)
        
        # Apply layout to the dialog
        dialog.layout().addWidget(QWidget()).setLayout(layout)
        dialog.setStandardButtons(QMessageBox.Send | QMessageBox.Cancel)
        dialog.button(QMessageBox.Send).setText("Confirm TX")
        
        if dialog.exec_() == QMessageBox.Send:
            recipient = address_input.text().strip()
            try:
                amount = float(amount_input.text().strip())
                if amount <= 0 or amount > self.manager.balance:
                     self.show_popup("Error", "Invalid amount or insufficient balance.")
                     return
                
                # --- Simulated TX Logic ---
                self.manager.balance -= amount
                self.manager.log_message(f"TRANSACTION: Sent {amount:.4f} %AIA% to {recipient[:15]}...", color="gold")
                self.update_status_labels()
                # --- End Simulated TX Logic ---
                
            except ValueError:
                self.show_popup("Error", "Please enter a valid numeric amount.")
        
    def save_log_popup(self):
        """Handles the save log menu action."""
        default_name = f"AIAlgo_Log_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        file_name, file_filter = QFileDialog.getSaveFileName(self, 
            "Save Log File", 
            default_name, 
            "JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if file_name:
            file_format = 'json' if file_filter.lower().endswith('.json') else 'csv'
            if not file_name.lower().endswith(f".{file_format}"):
                file_name += f".{file_format}"
                
            self.manager.save_log(file_name, file_format)
                
    def show_popup(self, title, message):
        """Standard PyQT pop-up dialog."""
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()
        
    def closeEvent(self, event):
        """Ensure the background thread is stopped when closing the GUI."""
        if self.manager.is_running:
            self.toggle_algorithm() 
        self.engine_thread.quit() 
        self.engine_thread.wait()
        super().closeEvent(event)

if __name__ == '__main__':
    # Add the current directory to the path to find manager/engine files
    sys.path.append('.') 
    
    app = QApplication(sys.argv)
    window = AIAlgoGUI()
    window.show()
    sys.exit(app.exec_())