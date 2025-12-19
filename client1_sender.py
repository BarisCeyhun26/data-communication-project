import socket
import zlib

def text_to_binary(text):
    return ''.join(format(ord(c), '08b') for c in text)

def get_parity(text):
    binary = text_to_binary(text)
    return '0' if binary.count('1') % 2 == 0 else '1'

def get_2d_parity(text):
    row_parities = ""
    col_parities = [0] * 8
    for char in text:
        bin_val = format(ord(char), '08b')
        row_parities += '0' if bin_val.count('1') % 2 == 0 else '1'
        for i in range(8):
            if bin_val[i] == '1': col_parities[i] += 1
    col_result = "".join(['0' if x % 2 == 0 else '1' for x in col_parities])
    return row_parities + col_result

def get_crc(text):
    crc = zlib.crc32(text.encode())
    return hex(crc & 0xffffffff)[2:].upper()

def get_hamming(text):
    result_code = ""
    for char in text:
        b = format(ord(char), '08b')
        d = [int(x) for x in b]
        p1 = d[0]^d[1]^d[3]^d[4]^d[6]
        p2 = d[0]^d[2]^d[3]^d[5]^d[6]
        p4 = d[1]^d[2]^d[3]^d[7]
        p8 = d[4]^d[5]^d[6]^d[7]
        result_code += f"{p1}{p2}{p4}{p8}"
    return result_code

def get_ip_checksum(text):
    data = text.encode()
    if len(data) % 2 == 1: data += b'\x00'
    checksum = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + (data[i+1])
        checksum += w
    while (checksum >> 16) > 0:
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    return hex(~checksum & 0xFFFF)[2:].upper()

def start_sender():
    host = 'localhost'
    port = 8000
    
    text = input("Enter the text to send: ")
    print("\n--- SELECT METHOD ---")
    print("1. Parity, 2. 2D Parity, 3. CRC, 4. Hamming, 5. Checksum")
    choice = input("Choice (1-5): ")
    
    methods = {"1": ("PARITY", get_parity), "2": ("2DPARITY", get_2d_parity), 
               "3": ("CRC", get_crc), "4": ("HAMMING", get_hamming), "5": ("CHECKSUM", get_ip_checksum)}
    
    if choice in methods:
        method_name, func = methods[choice]
        control_info = func(text)
        
        packet = f"{text}|{method_name}|{control_info}"
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(packet.encode())
            print(f"Client 1: Packet sent -> {packet}")
    else:
        print("Invalid Choice.")

if __name__ == "__main__":
    start_sender()