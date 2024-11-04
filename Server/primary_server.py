import socket
import threading
import time
from flask import Flask
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import numpy as np

PRIMARY_SERVER_IP = "127.0.0.1"
PRIMARY_SERVER_PORT = 5003

# List of worker server addresses (add more workers as needed)
WORKER_SERVERS = [
    ("127.0.0.1", 5004),  # Worker 1
    ("127.0.0.1", 5005),  # Worker 2
    ("127.0.0.1", 5006),  # Worker 3 (new worker added)
]

# Performance metrics
performance_metrics = {
    "total_segments": 0,
    "processed_segments": 0,
    "transfer_speed": 0.0,
}

# For real-time graph data
speed_history = []

# Chunk size for segments
CHUNK_SIZE = 1024  # You can adjust this value as needed

# List to store log details of each chunk sent to workers
chunk_logs = []

def split_data(data):
    """Split data into chunks."""
    return [data[i:i + CHUNK_SIZE] for i in range(0, len(data), CHUNK_SIZE)]

def distribute_to_workers(segment, chunk_id):
    """Distribute segment to all worker servers."""
    for worker_address in WORKER_SERVERS:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as worker_socket:
                worker_socket.connect(worker_address)
                worker_socket.sendall(segment)
                print(f"Sent segment to worker at {worker_address}")
                
                # Log the chunk details with chunk ID, worker address, and data preview
                chunk_logs.append(
                    f"Chunk {chunk_id} | Sent to {worker_address} | Size: {len(segment)} bytes | "
                    f"Content Preview: {segment[:50]}..."
                )

        except Exception as e:
            print(f"Failed to send segment to worker {worker_address}: {e}")
            chunk_logs.append(
                f"Chunk {chunk_id} | Failed to send to {worker_address}: {e}"
            )

def handle_client(client_socket):
    """Handle incoming client connections."""
    global performance_metrics, speed_history
    try:
        file_data = client_socket.recv(4096)  # Adjust buffer size as necessary
        print(f"Received data from client, length: {len(file_data)} bytes")

        # Split data into segments
        segments = split_data(file_data)
        performance_metrics["total_segments"] += len(segments)

        # Distribute segments to worker servers
        start_time = time.time()
        for chunk_id, segment in enumerate(segments, start=1):
            distribute_to_workers(segment, chunk_id)
            performance_metrics["processed_segments"] += 1
        end_time = time.time()

        # Calculate transfer speed
        transfer_speed = len(file_data) / (end_time - start_time) if end_time - start_time > 0 else 0
        performance_metrics["transfer_speed"] = transfer_speed
        speed_history.append(transfer_speed)

    finally:
        client_socket.close()

# Flask application for Dash
app = Flask(__name__)
dash_app = Dash(__name__, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP])

dash_app.layout = html.Div([
    dbc.Container([
        html.H1("Multi-Server Data Transmission Dashboard"),
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0),  # Update every second
        html.Div(id='metrics-display'),
        dcc.Graph(id='speed-graph'),
        html.Hr(),
        html.H3("Chunk Log Details"),
        html.Div(id='chunk-log', style={'maxHeight': '300px', 'overflowY': 'scroll'}),
    ])
])

@dash_app.callback(
    Output('metrics-display', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_metrics(n):
    return [
        html.Div(f"Total Segments: {performance_metrics['total_segments']}"),
        html.Div(f"Processed Segments: {performance_metrics['processed_segments']}"),
        html.Div(f"Current Transfer Speed: {performance_metrics['transfer_speed']:.2f} bytes/sec"),
    ]

@dash_app.callback(
    Output('speed-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    """Update the transfer speed graph as a bar graph."""
    figure = go.Figure()

    # Create bar graph for speed
    figure.add_trace(go.Bar(
        x=np.arange(len(speed_history)),
        y=speed_history,
        name='Transfer Speed',
    ))

    figure.update_layout(
        title='Real-Time Transfer Speed',
        xaxis_title='Time (intervals)',
        yaxis_title='Speed (bytes/sec)',
        yaxis=dict(range=[0, max(speed_history) * 1.1 if speed_history else 1]),  # Dynamic y-axis range
        xaxis=dict(range=[0, len(speed_history)]),  # Dynamic x-axis range
    )

    return figure

@dash_app.callback(
    Output('chunk-log', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_chunk_log(n):
    # Display the latest log entries with a limit to avoid overflow
    max_logs_to_display = 10
    recent_logs = chunk_logs[-max_logs_to_display:]
    return [html.Div(log) for log in recent_logs]

def start_primary_server():
    """Start the primary server to accept connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((PRIMARY_SERVER_IP, PRIMARY_SERVER_PORT))
    server.listen(5)
    print(f"Primary server listening on port {PRIMARY_SERVER_PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    threading.Thread(target=start_primary_server, daemon=True).start()
    dash_app.run_server(port=8050)
