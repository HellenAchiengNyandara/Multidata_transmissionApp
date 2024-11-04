# worker_server.py
import socket

WORKER_SERVER_IP = "127.0.0.1"
WORKER_SERVER_PORT = 5005  # Change this port for each worker server

def handle_worker_connection(worker_socket):
    while True:
        try:
            segment = worker_socket.recv(1024)
            if not segment:
                break
            print(f"Worker received segment: {segment.decode()}")
            # Process the segment (e.g., write to a file, etc.)
            # For simplicity, we are just printing it.
        except Exception as e:
            print(f"Error handling worker connection: {e}")
            break

    worker_socket.close()

def start_worker_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((WORKER_SERVER_IP, WORKER_SERVER_PORT))
    server.listen(5)
    print(f"Worker server listening on port {WORKER_SERVER_PORT}")

    while True:
        worker_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        handle_worker_connection(worker_socket)

if __name__ == "__main__":
    start_worker_server()
