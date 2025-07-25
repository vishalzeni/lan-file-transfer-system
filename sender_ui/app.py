import subprocess
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages, jsonify
from werkzeug.utils import secure_filename
from requests_toolbelt.multipart.encoder import MultipartEncoder
import webbrowser
import threading
import os

app = Flask(__name__)
app.secret_key = 'zenith-lan-transfer'
app.jinja_env.cache = {}


GOOGLE_SHEET_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzS5igJISvYY1mIGL0OGrveyFPeQWFEu2WmBGQh6ahFG4dVGQa1TGHwF3gw3qtWnxC4rQ/exec"

def is_online(ip):
    return subprocess.run(f"ping -n 1 -w 100 {ip}", shell=True, stdout=subprocess.DEVNULL).returncode == 0

def get_known_devices():
    try:
        response = requests.get(GOOGLE_SHEET_WEBHOOK_URL)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("❌ Error fetching known devices:", e)
    return {}

def log_transfer(sender_ip, receiver_ip, filename, status):
    log_data = {
        "sender_ip": sender_ip,
        "receiver_ip": receiver_ip,
        "filename": filename,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status
    }
    try:
        requests.post(GOOGLE_SHEET_WEBHOOK_URL, json=log_data)
    except Exception as e:
        print("❌ Error sending log to Google Sheets:", e)

def send_file(ip, file_storage):
    filename = secure_filename(file_storage.filename)
    mimetype = file_storage.mimetype or 'application/octet-stream'

    # Get sender name
    sender_ip = request.remote_addr
    sender_name = get_known_devices().get(sender_ip, "Unknown")

    m = MultipartEncoder(fields={
        'file': (filename, file_storage.read(), mimetype),
        'sender_name': sender_name
    })

    try:
        response = requests.post(
            f"http://{ip}:5050/",
            data=m,
            headers={'Content-Type': m.content_type},
            timeout=60
        )
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False


@app.route("/", methods=["GET", "POST"])
def index():
    known_devices = get_known_devices()
    active_online = {}
    inactive_offline = {}

    for ip, name in known_devices.items():
        (active_online if is_online(ip) else inactive_offline)[ip] = name

    if request.method == "POST":
        ip = request.form.get("device_ip")
        files = request.files.getlist("file")

        if ip in active_online and files:
            success = 0
            for f in files:
                if not f.filename:
                    continue
                result = send_file(ip, f)
                status = "Success" if result else "Failed"
                log_transfer(request.remote_addr, ip, f.filename, status)
                if result:
                    success += 1

            if success == len(files):
                flash(f"✓ Sent {success} file(s) to {ip}", "success")
            elif success > 0:
                flash(f"⚠️ Partially sent: {success}/{len(files)} files", "warning")
            else:
                flash("❌ No files sent", "error")

            return redirect(url_for("index"))

    status = None
    messages = get_flashed_messages(with_categories=True)
    if messages:
        status = {"message": messages[0][1]}

    return render_template("sender.html", active_devices=active_online, inactive_devices=inactive_offline, status=status)


def open_browser():
    script_dir = os.path.dirname(os.path.abspath(__file__))        # Folder of app.py
    parent_dir = os.path.dirname(script_dir)                        # One level up
    ip_file_path = os.path.join(parent_dir, "ip_config.txt")        # ../ip_config.txt

    try:
        with open(ip_file_path, "r") as f:
            ip = f.read().strip()
        webbrowser.open(f"http://{ip}:8000")
    except Exception as e:
        print(f"❌ Could not read IP from ip_config.txt: {e}")


if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)


