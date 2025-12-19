import tkinter as tk
from tkinter import messagebox
import socket
import threading
import random
from server_corruptor import apply_error

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server - Agent & Corruptor")
        self.root.geometry("500x600")
        
        self.is_running = False
        self.server_socket = None
        self.thread = None
        
        self.label_font = ("Arial", 12, "bold")
        self.btn_font = ("Arial", 12)
        
        tk.Label(root, text="Server Status:", font=self.label_font).pack(pady=10)
        
        self.status_label = tk.Label(root, text="STOPPED", font=("Arial", 14, "bold"), fg="red")
        self.status_label.pack(pady=5)
        
        self.start_btn = tk.Button(root, text="Start Server", font=self.btn_font, bg="#4CAF50", fg="white", command=self.start_server)
        self.start_btn.pack(pady=5, fill="x", padx=50)
        
        self.stop_btn = tk.Button(root, text="Stop Server", font=self.btn_font, bg="#f44336", fg="white", command=self.stop_server, state="disabled")
        self.stop_btn.pack(pady=5, fill="x", padx=50)
        
        tk.Label(root, text="Activity Log:", font=self.label_font).pack(pady=10)
        self.log_area = tk.Text(root, height=20, width=60, state='disabled', bg="#f0f0f0")
        self.log_area.pack(pady=5, padx=10)
        
    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        
    def start_server(self):
        self.is_running = True
        self.status_label.config(text="RUNNING", fg="green")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        self.thread = threading.Thread(target=self.run_server_logic, daemon=True)
        self.thread.start()
        self.log("Server started on port 8000...")

    def stop_server(self):
        self.is_running = False
        self.status_label.config(text="STOPPING...", fg="orange")
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.status_label.config(text="STOPPED", fg="red")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.log("Server stopped.")

    def run_server_logic(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', 8000))
            self.server_socket.listen(5)
            
            while self.is_running:
                try:
                    self.server_socket.settimeout(1.0)
                    try:
                        conn, addr = self.server_socket.accept()
                    except socket.timeout:
                        continue
                        
                    with conn:
                        packet = conn.recv(1024).decode()
                        if not packet: continue
                        
                        self.root.after(0, self.log, f"Received: {packet}")
                        
                        try:
                            if "|" in packet:
                                data, method, control = packet.split('|')
                                if random.random() < 0.7:
                                    corrupted_data = apply_error(data)
                                    if corrupted_data != data:
                                        self.root.after(0, self.log, f"-> Error Applied: {corrupted_data}")
                                else:
                                    corrupted_data = data
                                    self.root.after(0, self.log, "-> No Error Applied")
                                
                                new_packet = f"{corrupted_data}|{method}|{control}"
                                
                                try:
                                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:
                                        sender.connect(('localhost', 9000))
                                        sender.sendall(new_packet.encode())
                                        self.root.after(0, self.log, f"Forwarded to Client 2: {new_packet}")
                                except ConnectionRefusedError:
                                    self.root.after(0, self.log, "Error: Client 2 not found on port 9000")
                            else:
                                self.root.after(0, self.log, "Error: Invalid Packet Format")
                                
                        except Exception as e:
                            self.root.after(0, self.log, f"Processing Error: {e}")
                            
                except OSError:
                    break
                    
        except Exception as e:
            self.root.after(0, self.log, f"Server Error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
