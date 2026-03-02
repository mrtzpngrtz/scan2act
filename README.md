# scan2act

This is a system that allows users to submit prompts for image generation by scanning a changing QR code on a screen.

## Directory Structure

- `cloud/`: Contains the PHP backend (`backend.php`) and the web frontend (`index.html`) that users access with their phones. This should be hosted on a web server accessible via the internet.
- `local/`: Contains the Python application (`app.py`) that runs on the computer connected to your ComfyUI generation instance and the display screen.

## Setup Instructions

1. **Cloud Setup (Web Server):**
   Upload the contents of the `cloud/` folder to your web server (e.g., Apache, Nginx) that supports PHP. The `backend.php` will automatically create a `data.json` file in that directory when it's first accessed, so make sure the directory is writable by the web server.
   *(For local testing, you can navigate to the `cloud/` directory and run `php -S localhost:8000`)*

2. **Local Setup (Display & ComfyUI machine):**
   Install the Python dependencies:
   ```bash
   pip install requests qrcode PyQt5
   ```
   
   Open `local/app.py` and update the `BACKEND_URL` and `FRONTEND_URL` to point to your hosted cloud server.
   
   Run the display application:
   ```bash
   python app.py
   ```

4. **Usage:**
   - The Python app will display a QR code.
   - Scan the QR code with your phone (or click the URL if testing locally).
   - Enter your prompt on the web page and submit.
   - The Python app will detect the prompt, print it to the console (where you can later hook it up to ComfyUI), and generate a new QR code.
