import tkinter as tk
from tkinter import messagebox
import socket
from client1_sender import get_parity, get_2d_parity, get_crc, get_hamming, get_ip_checksum

class SenderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Client 1 - Data Sender")
        self.root.geometry("400x500")
        
        # Styles
        self.label_font = ("Arial", 12)
        self.entry_font = ("Arial", 10)
        
        # Data Entry
        tk.Label(root, text="Enter Text to Send:", font=self.label_font).pack(pady=10)
        self.text_entry = tk.Entry(root, font=self.entry_font, width=40)
        self.text_entry.pack(pady=5)
        
        # Method Selection
        tk.Label(root, text="Select Error Detection Method:", font=self.label_font).pack(pady=10)
        
        self.method_var = tk.StringVar(value="1")
        methods = [
            ("1. Parity (Odd/Even)", "1"),
            ("2. 2D Parity", "2"),
            ("3. CRC (Cyclic Redundancy)", "3"),
            ("4. Hamming Code", "4"),
            ("5. Internet Checksum", "5")
        ]
        
        for text, val in methods:
            tk.Radiobutton(root, text=text, variable=self.method_var, value=val, font=("Arial", 10)).pack(anchor="w", padx=40)
            
        # Send Button
        self.send_btn = tk.Button(root, text="SEND PACKET", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=self.send_packet)
        self.send_btn.pack(pady=20, fill="x", padx=40)
        
        # Log Area
        tk.Label(root, text="Log:", font=self.label_font).pack(pady=5)
        self.log_area = tk.Text(root, height=10, width=45, state='disabled', bg="#f0f0f0")
        self.log_area.pack(pady=5, padx=10)
        
    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        
    def send_packet(self):
        text = self.text_entry.get()
        if not text:
            messagebox.showwarning("Input Error", "Please enter some text.")
            return
            
        choice = self.method_var.get()
        
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
                
                host = 'localhost'
                port = 8000
                
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, port))
                    s.sendall(packet.encode())
                    self.log(f"Sent to Server: {packet}")
                    
            except ConnectionRefusedError:
                self.log("Error: Connection refused. Is the Server (Corruptor) running?")
            except Exception as e:
                self.log(f"Error: {e}")
        else:
            self.log("Invalid Method Selected.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SenderGUI(root)
    root.mainloop()
