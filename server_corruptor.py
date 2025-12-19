import socket
import random

def apply_error(text):
    if not text: return text
    error_type = random.choice(['BIT_FLIP', 'SUB', 'DEL', 'INS', 'SWAP'])
    
    if error_type == 'BIT_FLIP':
        blist = list(''.join(format(ord(x), '08b') for x in text))
        idx = random.randint(0, len(blist)-1)
        blist[idx] = '1' if blist[idx] == '0' else '0'
        new_text = "".join([chr(int("".join(blist[i:i+8]), 2)) for i in range(0, len(blist), 8)])
        print(f"LOG: Bit Flip applied.")
        return new_text

    elif error_type == 'SUB':
        idx = random.randint(0, len(text)-1)
        res = list(text)
        res[idx] = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        corrupted = "".join(res)
        print(f"LOG: Substitution applied ({text} -> {corrupted})")
        return corrupted

    elif error_type == 'DEL' and len(text) > 1:
        idx = random.randint(0, len(text)-1)
        print(f"LOG: Character Deletion applied.")
        return text[:idx] + text[idx+1:]

    elif error_type == 'INS':
        idx = random.randint(0, len(text))
        print(f"LOG: Random Character Insertion applied.")
        return text[:idx] + random.choice("XYZ") + text[idx:]

    elif error_type == 'SWAP' and len(text) >= 2:
        idx = random.randint(0, len(text)-2)
        res = list(text)
        res[idx], res[idx+1] = res[idx+1], res[idx]
        print(f"LOG: Character Swapping applied.")
        return "".join(res)

    return text

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(('localhost', 8000))
        listener.listen(5)
        print("Server: Waiting for Client 1 on port 8000... (Press Ctrl+C to stop)")
        
        while True:
            conn, _ = listener.accept()
            with conn:
                packet = conn.recv(1024).decode()
                if not packet: continue
                
                data, method, control = packet.split('|')
                corrupted_data = apply_error(data) if random.random() < 0.7 else data
                new_packet = f"{corrupted_data}|{method}|{control}"
                
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:
                        sender.connect(('localhost', 9000))
                        sender.sendall(new_packet.encode())
                        print(f"Server: Forwarded -> {new_packet}")
                except ConnectionRefusedError:
                    print("Error: Client 2 is not listening on port 9000!")

if __name__ == "__main__":
    start_server()