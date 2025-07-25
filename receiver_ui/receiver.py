from flask import Flask, request, render_template
import os, json
from datetime import datetime
import requests
import webbrowser
import threading
import os

try:
    import magic
    MIME_CHECK = True
except ImportError:
    MIME_CHECK = False

app = Flask(__name__, template_folder="templates")

desktop = os.path.join(os.path.expanduser("~"), "Desktop")
UPLOAD_FOLDER = os.path.join(desktop, "Received_Files_From_Zenith")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'docx', 'pptx', 'xlsx'}
METADATA_FILE = os.path.join(UPLOAD_FOLDER, "file_metadata.json")
DEVICE_MAP_URL = "https://script.google.com/macros/s/AKfycbzS5igJISvYY1mIGL0OGrveyFPeQWFEu2WmBGQh6ahFG4dVGQa1TGHwF3gw3qtWnxC4rQ/exec?sheet=Devices"

file_metadata = {}
if os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "r") as f:
        try:
            file_metadata = json.load(f)
        except json.JSONDecodeError:
            file_metadata = {}

def save_metadata():
    with open(METADATA_FILE, "w") as f:
        json.dump(file_metadata, f, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_unique_filename(directory, filename):
    name, ext = os.path.splitext(filename)
    counter, new_filename = 1, filename
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{name} ({counter}){ext}"
        counter += 1
    return new_filename

def get_device_name_from_google_sheet(ip):
    try:
        response = requests.get(DEVICE_MAP_URL)
        if response.status_code == 200:
            data = response.json()
            return data.get(ip, "Unknown")
    except Exception as e:
        print("❌ Failed to fetch device name:", e)
    return "Unknown"

def get_file_info(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    mime_type = magic.from_file(path, mime=True) if MIME_CHECK else "application/octet-stream"
    meta = file_metadata.get(filename, {})
    return {
        "name": filename,
        "size": os.path.getsize(path),
        "modified": datetime.fromtimestamp(os.path.getmtime(path)),
        "type": mime_type,
        "received_at": meta.get("received_at", "Unknown"),
        "sender_ip": meta.get("sender_ip", "Unknown"),
        "sender_name": meta.get("sender_name", "Unknown")
    }

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part", 400
        file = request.files["file"]

        # Fetch sender_name from request (sent by sender)
        sender_name = request.form.get("sender_name")
        if not sender_name:
            sender_name = get_device_name_from_google_sheet(request.remote_addr)

        if file.filename == "" or not allowed_file(file.filename):
            return "Invalid file", 400

        filename = get_unique_filename(UPLOAD_FOLDER, file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        file_metadata[filename] = {
            "sender_ip": request.remote_addr,
            "sender_name": sender_name,
            "received_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        save_metadata()
        print(f"✅ Saved: {filename} from {request.remote_addr} ({sender_name})")
        return "File received", 200

    # GET request
    files = [get_file_info(f) for f in os.listdir(UPLOAD_FOLDER) if f != "file_metadata.json"]
    files.sort(key=lambda x: x["modified"], reverse=True)
    return render_template("index.html", files=files)


def open_browser():
    script_dir = os.path.dirname(os.path.abspath(__file__))        # Folder of app.py
    parent_dir = os.path.dirname(script_dir)                        # One level up
    ip_file_path = os.path.join(parent_dir, "ip_config.txt")        # ../ip_config.txt

    try:
        with open(ip_file_path, "r") as f:
            ip = f.read().strip()
        webbrowser.open(f"http://{ip}:5050")
    except Exception as e:
        print(f"❌ Could not read IP from ip_config.txt: {e}")


if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(host="0.0.0.0", port=5050, debug=False, use_reloader=False)
