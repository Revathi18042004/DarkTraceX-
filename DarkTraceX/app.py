from flask import Flask, render_template, request
import time
import sqlite3
import threading
import sys
from flask import Flask, render_template, request, redirect
from ai_engine import detect_attack 
from threading import Lock

# ======================================================
# RUNTIME ATTACK CONTROL (LIVE TERMINAL)
# ======================================================
ACTIVE_ATTACK = "none"
attack_lock = Lock()

def attack_control_listener():
    global ACTIVE_ATTACK
    print("\n🛡️ EduSecureX Runtime Attack Control Ready")
    print("Commands:")
    print("  attack brute")
    print("  attack phishing")
    print("  attack seo")
    print("  attack exfiltration")
    print("  attack link")
    print("  attack rewards")
    print("  attack none")
    print("---------------------------------------")

    while True:
        cmd = sys.stdin.readline().strip().lower()
        if cmd.startswith("attack "):
            with attack_lock:
                ACTIVE_ATTACK = cmd.split(" ", 1)[1]
            print(f"⚠ ACTIVE ATTACK SET TO: {ACTIVE_ATTACK}")

# ======================================================
# APP SETUP
# ======================================================
app = Flask(__name__)

CORRECT_USERNAME = "student"
CORRECT_PASSWORD = "edu123"
failed_attempts = {}

# ======================================================
# HELPERS
# ======================================================
def is_anonymous_ip(ip):
    return not (ip.startswith("127.") or ip.startswith("192.168"))

def store_log(attack, ip, darknet, risk, timestamp):
    try:
        conn = sqlite3.connect("logs.db", timeout=10)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO attack_logs
            (attack_type, source_ip, darknet_origin, risk_level, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (attack, ip, darknet, risk, timestamp))
        conn.commit()
        conn.close()
    except:
        pass
def is_tor_request():
    host = request.headers.get("Host", "")
    return host.endswith(".onion")


def log_attack(title, details, ip, risk):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    darknet = "Likely" if is_tor_request() else "No"


    print("\n🚨 ATTACK DETECTED")
    print("Attack Type     :", title)
    for k, v in details.items():
        print(f"{k:<16}:", v)
    print("Source IP       :", ip)
    print("Darknet Origin  :", darknet)
    print("Risk Level      :", risk)
    print("Time            :", timestamp)
    print("------------------------------------")

    store_log(title, ip, darknet, risk, timestamp)

# ======================================================
# ROUTES – NORMAL WEBSITE FIRST
# ======================================================
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- LOGIN (BRUTE FORCE) ----------------
@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/login-check", methods=["POST"])
def login_check():
    ip = request.remote_addr
    user = request.form["username"]
    pwd = request.form["password"]

    if ip not in failed_attempts:
        failed_attempts[ip] = 0

    if user == CORRECT_USERNAME and pwd == CORRECT_PASSWORD:
        failed_attempts[ip] = 0
        return render_template("success.html")

    failed_attempts[ip] += 1
    response = render_template("login.html", message="Invalid credentials")

    with attack_lock:
        mode = ACTIVE_ATTACK

    if mode == "brute":
        features = {"failed_attempts": failed_attempts[ip], "file_size": 0}
        attack, atype, risk = detect_attack(features)
        if attack:
            log_attack(
                atype,
                {"Failed Attempts": failed_attempts[ip]},
                ip,
                risk
            )

    return response

# ---------------- DATA EXFILTRATION ----------------
@app.route("/upload")
def upload_page():
    return render_template("assignment_upload.html")

@app.route("/upload-assignment", methods=["POST"])
def upload_assignment():
    ip = request.remote_addr
    size = len(request.files["file"].read())
    response = render_template("upload_success.html")

    with attack_lock:
        mode = ACTIVE_ATTACK

    if mode == "exfiltration":
        features = {"failed_attempts": 0, "file_size": size}
        attack, atype, risk = detect_attack(features)
        if attack:
            log_attack(
                atype,
                {"Uploaded Size": f"{size} bytes"},
                ip,
                risk
            )

    return response

# ---------------- SEO INJECTION ----------------
@app.route("/submit-content")
def submit_content():
    return render_template("content_submit.html")

@app.route("/content-check", methods=["POST"])
def content_check():
    content = request.form["content"].lower()
    response = render_template("content_success.html")
    keywords = ["buy now", "casino", "crypto", "<script>"]

    with attack_lock:
        mode = ACTIVE_ATTACK

    if mode == "seo":
        if any(k in content for k in keywords):
            log_attack(
                "SEO Injection Attack",
                {"Injected Content": content},
                request.remote_addr,
                "High"
            )

    return response

# ---------------- WEBSITE LOGIN PAGE PHISHING ----------------
@app.route("/phishing-page")
def phishing_page():
    return render_template("phishing_login.html")
@app.route("/digital-library")
def digital_library():

    with attack_lock:
        mode = ACTIVE_ATTACK

    # if phishing simulation is active show redirect page
    if mode == "phishing":
        return render_template("library_redirect.html")

    return render_template("library_access.html")


@app.route("/library-login", methods=["POST"])
def library_login():

    return render_template("library_content.html")


@app.route("/phishing-login", methods=["POST"])
def phishing_login():

    ip = request.remote_addr
    username = request.form.get("username")
    password = request.form.get("password")

    log_attack(
        "Website Login Page Phishing",
        {
            "Captured User": username,
            "Captured Pass": password
        },
        ip,
        "High"
    )

    # after capturing credentials return to library login page
    return render_template("library_access.html")

# ---------------- LINK-BASED PHISHING ----------------
@app.route("/external-resource")
def external_resource():
    return render_template("external_resource.html")

@app.route("/resource-download")
def resource_download():

    with attack_lock:
        mode = ACTIVE_ATTACK

    if mode == "link":

        log_attack(
            "Link-Based Phishing",
            {"Action": "Malicious Redirect"},
            request.remote_addr,
            "High"
        )

        return render_template("redirect1.html")

    return render_template("download_complete.html")
@app.route("/redirect2")
def redirect2():
    return render_template("suspicious_download.html")

# ---------------- REWARDS & SURVEY PHISHING ----------------
@app.route("/rewards")
def rewards():
    return render_template("rewards.html")

@app.route("/survey")
def survey_page():
    return render_template("survey.html")

@app.route("/survey-submit", methods=["POST"])
def survey_submit():

    with attack_lock:
        mode = ACTIVE_ATTACK

    if mode == "rewards":
        log_attack(
            "Rewards & Survey Phishing",
            {"Action": "Fake reward"},
            request.remote_addr,
            "High"
        )

        return render_template("reward_claim.html")

    return render_template("survey_thanks.html")
# ======================================================
# RUN SERVER (CRITICAL FIX – NO OUTPUT CHANGE)
# ======================================================
if __name__ == "__main__":
    listener = threading.Thread(
        target=attack_control_listener,
        daemon=True
    )
    listener.start()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )
