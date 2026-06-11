from flask import Flask, request, render_template
from datetime import datetime
import os

app = Flask(__name__)

# Log file ka naam aur path set karna
LOG_FILE = "visitor_ips.txt"

def write_to_log(ip_address):
    """Visitor ka IP aur time text file me save karne ke liye function"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as file:
        file.write(f"[{timestamp}] Visitor IP: {ip_address}\n")

@app.route('/')
def home():
    # 1. Visitor ka IP address capture karna
    # Agar website proxy/hosting par hai toh X-Forwarded-For use hota hai, nahi toh remote_addr
    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Agar multiple IPs milte hain proxy se, toh pehla wala extract karna
    if visitor_ip and ',' in visitor_ip:
        visitor_ip = visitor_ip.split(',')[0].strip()

    # 2. IP address ko file me log karna
    write_to_log(visitor_ip)
    
    # 3. HTML page browser par display karna
    return render_template('index.html', ip_address=visitor_ip)

if __name__ == '__main__':
    print("Server launching... Open http://127.0.0.1:5000 in your browser.")
    # host='0.0.0.0' se yeh tumhare local network par bhi access ho sakega
    app.run(host='0.0.0.0', port=5000, debug=True)
