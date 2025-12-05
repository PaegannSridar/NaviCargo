from dash import html, dcc, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import numpy as np

locode_df = pd.read_csv('UN_LOCODE.csv')

def layout():
    map = go.Figure()
    map.update_layout(
        mapbox_style="open-street-map",
        height=600,
        width=1000,
        mapbox_zoom=1,
        mapbox_center={"lat": 0, "lon": 0},
        hovermode='closest',
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    # Add empty trace to be populated later with ship markers
    map.add_trace(go.Scattermapbox(
        lat=[],
        lon=[],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=5,
            color='green',
            opacity=0.8
        ),
        text=[],  # Placeholder for hover text
        hoverinfo='text'
    ))

    return html.Div([

        html.H2("Route and Emissions Calculator", style={"margin-bottom": "15px"}),

        html.Div([
            html.Div([
                # Dropdown list for start ports
                html.Label("Start Port"),
                dcc.Dropdown(id="start-port", options=locode_df['Name'], placeholder="Select a starting port", style={"width": "250px"}),
                html.Br(),
                # Dropdown list for end ports
                html.Label("End Port"),
                dcc.Dropdown(id="end-port", options=locode_df['Name'], placeholder="Select a destination port", style={"width": "250px"}),
                html.Br(),
                # Button to calculate route
                html.Button("Calculate Route", id="calculate-route", n_clicks=0, style={"margin-top": "10px"}),
                # Blank 'box' in which the distance will be displayed
                html.Div(id="info-box", style={"margin-top": "40px", "margin-left": "auto", "font-weight": "bold",
                                                  "font-size": "18px"}),
                # Blank 'box' in which the CO2 emission will be displayed
                html.Div(id="info-box2", style={"margin-top": "5px", "margin-left": "auto", "font-weight": "bold",
                                               "font-size": "18px"}),

                html.Br(), html.Br(),
                html.A("⬅ Back to Live Map", href="/",
                       style={"font-weight": "bold", "font-size": "16px"})],
            style={"width": "30%", "display": "inline-block", "vertical-align": "top"}),

            html.Div([
                dcc.Graph(id="route-map", figure=map)],
            style={"width": "65%", "display": "inline-block"})
        ])
    ])