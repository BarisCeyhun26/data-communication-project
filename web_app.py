from flask import Flask, render_template_string, request, jsonify
import threading
import socket
import time
import random

from client1_sender import get_parity, get_2d_parity, get_crc, get_hamming, get_ip_checksum
from server_corruptor import apply_error

app = Flask(__name__)

LOGS = {
    "sender": [],
    "server": [],
    "receiver": []
}

RECEIVER_STATUS = {
    "data": "-",
    "method": "-",
    "sent_checksum": "-",
    "calc_checksum": "-",
    "status": "-",
    "color": "gray"
}

SERVER_RUNNING = False
RECEIVER_RUNNING = False


def run_socket_server_node():
    """Runs the Intermediate Server (Corruptor) on Port 8000"""
    global SERVER_RUNNING
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(('localhost', 8000))
        listener.listen(5)
        
        while True:
            if not SERVER_RUNNING:
                time.sleep(1)
                continue
                
            listener.settimeout(1.0)
            try:
                conn, _ = listener.accept()
            except socket.timeout:
                continue
                
            with conn:
                packet = conn.recv(1024).decode()
                if not packet: continue
                
                LOGS["server"].append(f"Received: {packet}")
                
                if "|" in packet:
                    data, method, control = packet.split('|')
                    
                    if random.random() < 0.7:
                        corrupted_data = apply_error(data)
                        if corrupted_data != data:
                            LOGS["server"].append(f"-> Error Applied: {corrupted_data}")
                        else:
                            LOGS["server"].append("-> No Error Applied (Random pass)")
                    else:
                        corrupted_data = data
                        LOGS["server"].append("-> No Error Applied (Clean pass)")
                    
                    new_packet = f"{corrupted_data}|{method}|{control}"
                    
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:
                            sender.connect(('localhost', 9000))
                            sender.sendall(new_packet.encode())
                            LOGS["server"].append(f"Forwarded: {new_packet}")
                    except ConnectionRefusedError:
                        LOGS["server"].append("Error: Client 2 (Port 9000) not reachable.")
                else:
                    LOGS["server"].append("Error: Invalid packet format.")

def run_socket_receiver_node():
    """Runs the Receiver (Client 2) on Port 9000"""
    global RECEIVER_RUNNING
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(('localhost', 9000))
        listener.listen(5)
        
        while True:
            if not RECEIVER_RUNNING:
                time.sleep(1)
                continue
                
            listener.settimeout(1.0)
            try:
                conn, _ = listener.accept()
            except socket.timeout:
                continue
                
            with conn:
                packet = conn.recv(1024).decode()
                if not packet: continue
                
                try:
                    msg, method, incoming_ctrl = packet.split('|')
                    
                    calc_func = {
                        "PARITY": get_parity, 
                        "2DPARITY": get_2d_parity, 
                        "CRC": get_crc, 
                        "HAMMING": get_hamming, 
                        "CHECKSUM": get_ip_checksum
                    }
                    
                    if method in calc_func:
                        calculated = calc_func[method](msg)
                    else:
                        calculated = "UNKNOWN"
                    
                    is_correct = (calculated == incoming_ctrl)
                    
                    RECEIVER_STATUS["data"] = msg
                    RECEIVER_STATUS["method"] = method
                    RECEIVER_STATUS["sent_checksum"] = incoming_ctrl
                    RECEIVER_STATUS["calc_checksum"] = calculated
                    RECEIVER_STATUS["status"] = "DATA CORRECT" if is_correct else "DATA CORRUPTED"
                    RECEIVER_STATUS["color"] = "green" if is_correct else "red"
                    
                    LOGS["receiver"].append(f"Recv: {msg} | {RECEIVER_STATUS['status']}")
                    
                except Exception as e:
                    LOGS["receiver"].append(f"Error parse: {e}")

t1 = threading.Thread(target=run_socket_server_node, daemon=True)
t1.start()

t2 = threading.Thread(target=run_socket_receiver_node, daemon=True)
t2.start()



HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Communication Project</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background:
        .container { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; max-width: 1400px; margin: 0 auto; }
        .card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h2 { border-bottom: 2px solid
        .log-box { background:
        .status-box { padding: 15px; border-radius: 5px; margin-bottom: 10px; background:
        button { padding: 10px 20px; cursor: pointer; border: none; border-radius: 5px; font-size: 14px; font-weight: bold; }
        .btn-green { background:
        .btn-red { background:
        .btn-blue { background:
        input[type="text"] { width: 100%; padding: 10px; box-sizing: border-box; margin-bottom: 10px; border: 1px solid
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        .status-indicator { font-size: 24px; font-weight: bold; text-align: center; margin: 20px 0; }
    </style>
</head>
<body>

    <h1 style="text-align: center; margin-bottom: 30px;">Socket Programming Assignment - Error Detection</h1>

    <div class="container">
        
        <!-- CLIENT 1: SENDER -->
        <div class="card">
            <h2>1. Client (Sender)</h2>
            <div class="form-group">
                <label>Message Text:</label>
                <input type="text" id="msgInput" placeholder="Enter text (e.g. HELLO)">
            </div>
            
            <div class="form-group">
                <label>Method:</label>
                <select id="methodSelect" style="width: 100%; padding: 10px;">
                    <option value="1">1. Parity (Odd/Even)</option>
                    <option value="2">2. 2D Parity</option>
                    <option value="3">3. CRC (Cyclic Redundancy)</option>
                    <option value="4">4. Hamming Code</option>
                    <option value="5">5. Internet Checksum</option>
                </select>
            </div>
            
            <button class="btn-blue" onclick="sendPacket()" style="width: 100%;">SEND PACKET</button>
            
            <h3>Sender Log</h3>
            <div class="log-box" id="senderLog"></div>
        </div>

        <!-- SERVER: CORRUPTOR -->
        <div class="card">
            <h2>2. Server (Corruptor)</h2>
            <div style="text-align: center; margin-bottom: 10px;">
                <button id="serverBtn" class="btn-green" onclick="toggleServer()">Start Server</button>
            </div>
            <div id="serverStatus" style="text-align: center; font-weight: bold; color: red;">STOPPED</div>
            
            <h3>Server Log</h3>
            <div class="log-box" id="serverLog"></div>
        </div>

        <!-- CLIENT 2: RECEIVER -->
        <div class="card">
            <h2>3. Client (Receiver)</h2>
            <div style="text-align: center; margin-bottom: 10px;">
                <button id="receiverBtn" class="btn-green" onclick="toggleReceiver()">Start Listening</button>
            </div>
            <div id="receiverStatus" style="text-align: center; font-weight: bold; color: red;">OFFLINE</div>
            
            <div class="status-box">
                <div><strong>Data:</strong> <span id="rData">-</span></div>
                <div><strong>Method:</strong> <span id="rMethod">-</span></div>
                <div><strong>Sent Checksum:</strong> <span id="rSent">-</span></div>
                <div><strong>Calc Checksum:</strong> <span id="rCalc">-</span></div>
                <div class="status-indicator" id="rResult">-</div>
            </div>
            
            <h3>Receiver Log</h3>
            <div class="log-box" id="receiverLog"></div>
        </div>
    </div>

    <script>
        // Poll for updates every 1 second
        setInterval(fetchUpdates, 1000);

        function log(boxId, msg) {
            const box = document.getElementById(boxId);
            box.innerHTML = "<div>" + msg + "</div>" + box.innerHTML;
        }

        async function sendPacket() {
            const text = document.getElementById('msgInput').value;
            const method = document.getElementById('methodSelect').value;
            
            const response = await fetch('/api/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text, method})
            });
            const data = await response.json();
            if(data.success) {
                log('senderLog', `Sent: ${data.packet}`);
            } else {
                log('senderLog', `Error: ${data.error}`);
            }
        }

        async function toggleServer() {
            const response = await fetch('/api/toggle_server', {method: 'POST'});
            const data = await response.json();
            updateButton('serverBtn', 'serverStatus', data.running, "Server");
        }

        async function toggleReceiver() {
            const response = await fetch('/api/toggle_receiver', {method: 'POST'});
            const data = await response.json();
            updateButton('receiverBtn', 'receiverStatus', data.running, "Listening");
        }
        
        function updateButton(btnId, statusId, isRunning, label) {
            const btn = document.getElementById(btnId);
            const status = document.getElementById(statusId);
            if(isRunning) {
                btn.className = "btn-red";
                btn.innerText = "Stop " + label;
                status.innerText = "RUNNING";
                status.style.color = "green";
            } else {
                btn.className = "btn-green";
                btn.innerText = "Start " + label;
                status.innerText = "STOPPED";
                status.style.color = "red";
            }
        }

        async function fetchUpdates() {
            const response = await fetch('/api/updates');
            const data = await response.json();
            
            // Append new logs
            data.server_logs.forEach(l => log('serverLog', l));
            data.receiver_logs.forEach(l => log('receiverLog', l));
            
            // Update Receiver Status
            document.getElementById('rData').innerText = data.recv_status.data;
            document.getElementById('rMethod').innerText = data.recv_status.method;
            document.getElementById('rSent').innerText = data.recv_status.sent_checksum;
            document.getElementById('rCalc').innerText = data.recv_status.calc_checksum;
            
            const rRes = document.getElementById('rResult');
            rRes.innerText = data.recv_status.status;
            rRes.style.color = data.recv_status.color;
            
            // Sync Toggle Button States (in case of page reload)
            updateButton('serverBtn', 'serverStatus', data.server_running, "Server");
            updateButton('receiverBtn', 'receiverStatus', data.receiver_running, "Listening");
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/send', methods=['POST'])
def api_send():
    data = request.json
    text = data.get('text')
    choice = data.get('method')
    
    methods = {
        "1": ("PARITY", get_parity), 
        "2": ("2DPARITY", get_2d_parity), 
        "3": ("CRC", get_crc), 
        "4": ("HAMMING", get_hamming), 
        "5": ("CHECKSUM", get_ip_checksum)
    }
    
    if choice in methods:
        method_name, func = methods[choice]
        try:
            control_info = func(text)
            packet = f"{text}|{method_name}|{control_info}"
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', 8000))
                s.sendall(packet.encode())
                
            return jsonify({"success": True, "packet": packet})
        except Exception as e:
             return jsonify({"success": False, "error": str(e)})
    
    return jsonify({"success": False, "error": "Invalid Method"})

@app.route('/api/toggle_server', methods=['POST'])
def api_toggle_server():
    global SERVER_RUNNING
    SERVER_RUNNING = not SERVER_RUNNING
    return jsonify({"running": SERVER_RUNNING})

@app.route('/api/toggle_receiver', methods=['POST'])
def api_toggle_receiver():
    global RECEIVER_RUNNING
    RECEIVER_RUNNING = not RECEIVER_RUNNING
    return jsonify({"running": RECEIVER_RUNNING})

@app.route('/api/updates')
def api_updates():
    s_logs = list(LOGS["server"])
    LOGS["server"].clear()
    
    r_logs = list(LOGS["receiver"])
    LOGS["receiver"].clear()
    
    return jsonify({
        "server_logs": s_logs,
        "receiver_logs": r_logs,
        "recv_status": RECEIVER_STATUS,
        "server_running": SERVER_RUNNING,
        "receiver_running": RECEIVER_RUNNING
    })

if __name__ == '__main__':
    print("Starting Web Interface on http://localhost:8080")
    app.run(port=8080, debug=True, use_reloader=False)

