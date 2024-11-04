import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import threading
import socket
import time

# Initialize Dash app
dash_app = dash.Dash(__name__)

# Performance metrics shared with the server
performance_metrics = {
    "total_segments": 0,
    "processed_segments": 0,
    "transfer_speed": 0
}
speed_history = []

# Layout of the dashboard
dash_app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # Update every second
        n_intervals=0
    ),
    html.Div(id='metrics-display'),
    dcc.Graph(id='speed-graph')
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
    figure = go.Figure()
    if speed_history:  # Check if there's data to plot
        figure.add_trace(go.Scatter(
            x=list(range(len(speed_history))), 
            y=speed_history, 
            mode='lines+markers',
            name='Transfer Speed'
        ))
        figure.update_layout(
            title='Real-Time Transfer Speed',
            xaxis_title='Time (intervals)',
            yaxis_title='Speed (bytes/sec)',
            yaxis=dict(range=[0, max(speed_history) * 1.1]),  # Dynamic y-axis range
            xaxis=dict(range=[0, len(speed_history)]),  # Dynamic x-axis range
        )
    else:
        figure.add_trace(go.Scatter(
            x=[0], 
            y=[0], 
            mode='lines+markers',
            name='Transfer Speed'
        ))
        figure.update_layout(
            title='Real-Time Transfer Speed',
            xaxis_title='Time (intervals)',
            yaxis_title='Speed (bytes/sec)',
        )

    return figure

# Start the Dash app
if __name__ == '__main__':
    threading.Thread(target=start_server, daemon=True).start()  # Start server in the background
    dash_app.run_server(debug=True, use_reloader=False)  # Start the Dash app
