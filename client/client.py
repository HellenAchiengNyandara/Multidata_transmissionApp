# client.py
import socket

PRIMARY_SERVER_IP = "127.0.0.1"
PRIMARY_SERVER_PORT = 5003

def start_client(file_path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((PRIMARY_SERVER_IP, PRIMARY_SERVER_PORT))
    
    with open(file_path, 'rb') as file:
        data = file.read()
        client_socket.sendall(data)
        print(f"Sent data from {file_path}, length: {len(data)} bytes")

    client_socket.close()

if __name__ == "__main__":
    start_client("C:/Users/Hellena/Downloads/Alexproject2/data/worksOn.dat")  # Specify the path to your .dat file
