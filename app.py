from flask import Flask, request, render_template, jsonify, render_template_string
from datetime import datetime
import os

app = Flask(__name__)

# Log file ka naam aur path set karna
LOG_FILE = "visitor_ips.txt"

def write_to_log(ip_address, user_agent, event_type="PAGE_LOAD", extra_info=""):
    """Visitor ka IP, device details aur time text file me save karne ke liye function"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{event_type}] IP: {ip_address} | Browser/Device: {user_agent}"
    if extra_info:
        log_entry += f" | Details: {extra_info}"
    log_entry += "\n"
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(log_entry)

@app.route('/')
def home():
    # 1. Visitor ka IP address capture karna
    # Agar website proxy/hosting par hai toh X-Forwarded-For use hota hai, nahi toh remote_addr
    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Agar multiple IPs milte hain proxy se, toh pehla wala extract karna
    if visitor_ip and ',' in visitor_ip:
        visitor_ip = visitor_ip.split(',')[0].strip()

    user_agent = request.headers.get('User-Agent', 'Unknown')

    # 2. IP address ko file me log karna
    write_to_log(visitor_ip, user_agent, event_type="PAGE_LOAD")
    
    # 3. HTML page browser par display karna
    return render_template('index.html', ip_address=visitor_ip)

@app.route('/log_details', methods=['POST'])
def log_details():
    try:
        data = request.json or {}
        visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if visitor_ip and ',' in visitor_ip:
            visitor_ip = visitor_ip.split(',')[0].strip()
            
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Client-side specs extract karna
        screen = data.get('screen_resolution', 'Unknown')
        platform = data.get('platform', 'Unknown')
        lang = data.get('language', 'Unknown')
        tz = data.get('timezone', 'Unknown')
        
        extra_info = f"Screen: {screen}, OS Platform: {platform}, Language: {lang}, Timezone: {tz}"
        
        write_to_log(visitor_ip, user_agent, event_type="DEVICE_INFO", extra_info=extra_info)
        return jsonify({"status": "logged"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logs')
def show_logs():
    if not os.path.exists(LOG_FILE):
        return "No logs found yet. Visit the home page to generate some logs!", 404
        
    with open(LOG_FILE, "r", encoding="utf-8") as file:
        logs_content = file.read()
        
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Visitor Logs Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Outfit', sans-serif;
                background-color: #0b0f19;
                color: #f3f4f6;
                padding: 40px 20px;
                margin: 0;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
            }
            h1 {
                background: linear-gradient(135deg, #ffffff 0%, #ef4444 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 20px;
                font-size: 2.2rem;
                font-weight: 800;
            }
            pre {
                background: rgba(20, 30, 48, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
                padding: 20px;
                font-family: monospace;
                overflow-x: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
                font-size: 0.9rem;
                line-height: 1.6;
                color: #ef4444;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            }
            .btn {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 12px;
                cursor: pointer;
                font-weight: 600;
                text-decoration: none;
                display: inline-block;
                margin-bottom: 25px;
                font-size: 0.9rem;
                transition: opacity 0.2s, transform 0.1s;
            }
            .btn:hover {
                opacity: 0.9;
                transform: translateY(-1px);
            }
            .btn:active {
                transform: translateY(0);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ IP Tracker & Visitor Logs</h1>
            <a href="/" class="btn">← Back to Profile</a>
            <button onclick="window.location.reload()" class="btn" style="background: #ef4444; margin-left: 10px;">Refresh Logs</button>
            <pre>{{ logs }}</pre>
        </div>
    </body>
    </html>
    """, logs=logs_content)

if __name__ == '__main__':
    print("Server launching... Open http://127.0.0.1:5000 in your browser.")
    # host='0.0.0.0' se yeh tumhare local network par bhi access ho sakega
    app.run(host='0.0.0.0', port=5000, debug=True)
