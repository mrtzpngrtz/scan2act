import sys
import time
import requests
import qrcode
from io import BytesIO
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QDesktopWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading

# Configuration
# Change these to point to your actual hosted cloud environment.
# Example: "https://yourwebsite.com/scan2act/backend.php"
BACKEND_URL = "https://aop.studio/projects/qr1/backend.php"
FRONTEND_URL = "https://aop.studio/projects/qr1/index.html"
POLL_INTERVAL_MS = 2000 # 2 seconds
MODE = 2 # 1: Text Prompt, 2: Drawing, 3: Yes/No, 4: Sliders, 5: Voting 1-10

# Shared state for local HTTP Server
latest_data = {"type": "none", "data": "Waiting for input..."}

class LocalServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/latest':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(latest_data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_local_server():
    server = HTTPServer(('127.0.0.1', 8080), LocalServerHandler)
    server.serve_forever()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.current_token = None
        self.expiry_time = 0
        self.initUI()
        self.generate_new_token()

        # Timer for polling
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_backend)
        self.timer.start(POLL_INTERVAL_MS)

    def initUI(self):
        self.setWindowTitle('QR Prompt Display')
        self.setFixedSize(500, 500)
        self.setStyleSheet("background-color: #1a1a2e;")
        
        layout = QVBoxLayout()
        
        self.label = QLabel("Loading...", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 24px; font-family: sans-serif;")
        
        self.qr_label = QLabel(self)
        self.qr_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.label)
        layout.addWidget(self.qr_label)
        
        self.setLayout(layout)
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def generate_new_token(self):
        try:
            response = requests.get(f"{BACKEND_URL}?action=generate_token&mode={MODE}")
            data = response.json()
            if data.get('success'):
                self.current_token = data['token']
                self.expiry_time = data['expiry']
                self.label.setText("Scan to change the image:")
                self.update_qr_code(f"{FRONTEND_URL}?token={self.current_token}")
            else:
                self.label.setText("Error generating code")
        except Exception as e:
            self.label.setText("Connection error")
            print(f"Error: {e}")

    def update_qr_code(self, url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL image to QPixmap
        buf = BytesIO()
        img.save(buf, format="PNG")
        qimage = QImage()
        qimage.loadFromData(buf.getvalue())
        pixmap = QPixmap.fromImage(qimage)
        
        self.qr_label.setPixmap(pixmap)

    def poll_backend(self):
        # 1. Check if we need a new token (expired)
        if time.time() > self.expiry_time:
            print("Token expired. Generating a new one.")
            self.generate_new_token()
            return

        # 2. Poll for new prompts
        try:
            response = requests.get(f"{BACKEND_URL}?action=poll_prompt")
            data = response.json()
            if data.get('has_prompt'):
                global latest_data
                prompt = data.get('prompt')
                
                # Detect format based on type if it's a dict (Modes 2-5), else it's raw text (Mode 1)
                if isinstance(prompt, dict):
                    latest_data = prompt
                else:
                    latest_data = {"type": "text", "data": prompt}

                print(f"--- NEW PROMPT RECEIVED ---")
                print(latest_data)
                print("---------------------------")
                # TODO: Here you would send the prompt to ComfyUI
                # e.g., send_to_comfyui(prompt)
                
                # Show temporarily on screen
                self.label.setText("Generating image...")
                self.qr_label.clear()
                
                # Generate new token immediately since the old one is used
                QTimer.singleShot(2000, self.generate_new_token)
                
        except Exception as e:
            print(f"Poll error: {e}")

if __name__ == '__main__':
    # Start the local server to feed display.html
    server_thread = threading.Thread(target=run_local_server, daemon=True)
    server_thread.start()
    
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
