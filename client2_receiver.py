import socket
# Client 1'deki hesaplama fonksiyonlarını kullanır [cite: 59]
from client1_sender import get_parity, get_2d_parity, get_crc, get_hamming, get_ip_checksum

def start_receiver():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('localhost', 9000))
        server.listen(5)
        print("Client 2: Listening on port 9000... (Press Ctrl+C to stop)")
        
        while True: # Sürekli dinleme döngüsü eklendi
            conn, _ = server.accept()
            with conn:
                packet = conn.recv(1024).decode()
                if not packet: continue
                
                try:
                    msg, method, incoming_ctrl = packet.split('|')
                    calc_func = {"PARITY": get_parity, "2DPARITY": get_2d_parity, 
                                 "CRC": get_crc, "HAMMING": get_hamming, "CHECKSUM": get_ip_checksum}
                    
                    calculated = calc_func[method](msg)
                    status = "DATA CORRECT" if calculated == incoming_ctrl else "DATA CORRUPTED"
                    
                    print("\n" + "="*30)
                    print(f"Received: {msg} | Status: {status}")
                    print("="*30)
                except Exception as e:
                    print(f"Error: {e}")
if __name__ == "__main__":
    start_receiver()