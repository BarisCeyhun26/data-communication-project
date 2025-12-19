import tkinter as tk
import socket
import threading
from client1_sender import get_parity, get_2d_parity, get_crc, get_hamming, get_ip_checksum

class ReceiverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Client 2 - Data Receiver")
        self.root.geometry("500x600")
        
        self.is_running = False
        self.receiver_socket = None
        self.thread = None
        
        self.label_font = ("Arial", 12, "bold")
        self.btn_font = ("Arial", 12)
        
        tk.Label(root, text="Receiver Status:", font=self.label_font).pack(pady=10)
        self.status_label = tk.Label(root, text="OFFLINE", font=("Arial", 14, "bold"), fg="red")
        self.status_label.pack(pady=5)
        
        self.start_btn = tk.Button(root, text="Start Listening", font=self.btn_font, bg="#4CAF50", fg="white", command=self.start_receiver)
        self.start_btn.pack(pady=5, fill="x", padx=50)
        
        self.stop_btn = tk.Button(root, text="Stop Listening", font=self.btn_font, bg="#f44336", fg="white", command=self.stop_receiver, state="disabled")
        self.stop_btn.pack(pady=5, fill="x", padx=50)
        
        self.info_frame = tk.LabelFrame(root, text="Latest Packet", font=self.label_font, padx=10, pady=10)
        self.info_frame.pack(pady=20, fill="x", padx=20)
        
        self.data_label = tk.Label(self.info_frame, text="Data: -", font=("Arial", 11), anchor="w")
        self.data_label.pack(fill="x")
        
        self.method_label = tk.Label(self.info_frame, text="Method: -", font=("Arial", 11), anchor="w")
        self.method_label.pack(fill="x")
        
        self.sent_check_label = tk.Label(self.info_frame, text="Sent Checksum: -", font=("Arial", 11), anchor="w")
        self.sent_check_label.pack(fill="x")
        
        self.calc_check_label = tk.Label(self.info_frame, text="Calc Checksum: -", font=("Arial", 11), anchor="w")
        self.calc_check_label.pack(fill="x")
        
        self.result_label = tk.Label(self.info_frame, text="STATUS: -", font=("Arial", 14, "bold"), fg="gray")
        self.result_label.pack(pady=10)
        
        tk.Label(root, text="History:", font=self.label_font).pack()
        self.log_area = tk.Text(root, height=10, width=60, state='disabled', bg="#f0f0f0")
        self.log_area.pack(pady=5, padx=10)

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        
    def start_receiver(self):
        self.is_running = True
        self.status_label.config(text="LISTENING (Port 9000)", fg="green")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        self.thread = threading.Thread(target=self.run_receiver_logic, daemon=True)
        self.thread.start()
        self.log("Started listening on port 9000...")

    def stop_receiver(self):
        self.is_running = False
        self.status_label.config(text="STOPPING...", fg="orange")
        
        if self.receiver_socket:
            try:
                self.receiver_socket.close()
            except:
                pass
                
        self.status_label.config(text="OFFLINE", fg="red")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.log("Stopped listening.")

    def run_receiver_logic(self):
        try:
            self.receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.receiver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.receiver_socket.bind(('localhost', 9000))
            self.receiver_socket.listen(5)
            
            while self.is_running:
                try:
                    self.receiver_socket.settimeout(1.0)
                    try:
                        conn, _ = self.receiver_socket.accept()
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
                            
                            calculated = calc_func.get(method, lambda x: "UNKNOWN")(msg)
                            
                            is_correct = (calculated == incoming_ctrl)
                            status_text = "DATA CORRECT" if is_correct else "DATA CORRUPTED"
                            status_color = "green" if is_correct else "red"
                            
                            self.root.after(0, self.update_display, msg, method, incoming_ctrl, calculated, status_text, status_color)
                            
                        except Exception as e:
                            self.root.after(0, self.log, f"Error processing packet: {e}")
                            
                except OSError:
                    break
        except Exception as e:
            self.root.after(0, self.log, f"Receiver Error: {e}")
        finally:
            if self.receiver_socket:
                self.receiver_socket.close()

    def update_display(self, msg, method, sent, calc, status, color):
        self.data_label.config(text=f"Data: {msg}")
        self.method_label.config(text=f"Method: {method}")
        self.sent_check_label.config(text=f"Sent Checksum: {sent}")
        self.calc_check_label.config(text=f"Calc Checksum: {calc}")
        self.result_label.config(text=status, fg=color)
        
        self.log(f"Recv: {msg} | {status} | {method}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReceiverGUI(root)
    root.mainloop()
