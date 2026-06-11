from flask import Flask, request, render_template, jsonify
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

if __name__ == '__main__':
    print("Server launching... Open http://127.0.0.1:5000 in your browser.")
    # host='0.0.0.0' se yeh tumhare local network par bhi access ho sakega
    app.run(host='0.0.0.0', port=5000, debug=True)
