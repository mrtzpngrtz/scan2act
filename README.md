# scan2act

This is a system that allows users to submit prompts for image generation by scanning a changing QR code on a screen.

## Setup Instructions

1. **Install Python dependencies:**
   ```bash
   pip install requests qrcode PyQt5
   ```

2. **Start the local PHP server:**
   In this directory, run:
   ```bash
   php -S localhost:8000
   ```

3. **Start the Python display app:**
   In another terminal, run:
   ```bash
   python app.py
   ```

4. **Usage:**
   - The Python app will display a QR code.
   - Scan the QR code with your phone (or click the URL if testing locally).
   - Enter your prompt on the web page and submit.
   - The Python app will detect the prompt, print it to the console (where you can later hook it up to ComfyUI), and generate a new QR code.
