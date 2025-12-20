from dash import html, dcc, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import numpy as np

locode_df = pd.read_csv('UN_LOCODE.csv')

# Returns the layout how the route info should be displayed
def result_card(start_code, start_name, end_code, end_name, distance_km, days, hours, emissions_tonnes):
    return html.Div(
        style={"background": "white", "borderRadius": "12px", "width": "410px", "display": "flex", "padding":"5px 5px ",
            "flexDirection": "column", "gap": "12px", "fontFamily": "sans-serif", "border":"1px solid #0474ce"},
        children=[# TOP ROW
            html.Div(style={"display": "flex", "justifyContent": "space-between"},
                     children=[html.Div([ html.Div(start_code, style={"fontWeight": "bold", "fontSize": "20px"}),
                    html.Div(start_name, style={"color": "#555"})]),
                    html.Div([html.Div(end_code, style={"fontWeight": "bold", "fontSize": "20px"}),
                    html.Div(end_name, style={"color": "#555"})
                    ])]),
            html.Div(f"{days} days {hours} hrs", style={"fontSize": "17px", "fontWeight": "500"}),
            # BOTTOM  ROW
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                children=[
                    html.Div(f"{round(distance_km)} kilometers",
                             style={"fontSize": "16px", "color": "#555"}),
                    html.Div(
                        f"{round(emissions_tonnes, 2)} t CO₂",
                        style={"background": "#E8F8EE", "borderRadius": "8px", "color": "#2A8C4A", "fontWeight": "600"}
                    )])])

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

        # Title and image logo
        html.Div([
            html.Div([
                html.Img(src="/assets/NAVICARGO.png", style={"height": "20px", "margin-right": "5px"}),
                html.Div("NaviCargo",
                         style={"position": "absolute", "font-size": "15px", "top": "10px", "left": "30px",
                                "font-weight": "550", "color": "#8b8b8b"})],
                style={"display": "flex", "flex-direction": "row"}),

            html.Div("Route and Emissions Calculator",
                     style={"position": "absolute", "top": "10px", "right": "12px", "font-size": "9px",
                            "font-weight": 450, "color": "#8b8b8b"}, )
        ], style={"display": "flex", "background-color": "white", }),

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
                html.Br(), html.Br(),
                html.A("⬅ Back to Live Map", href="/",
                       style={"font-weight": "bold", "font-size": "16px"})],
            style={"width": "30%", "display": "inline-block", "vertical-align": "top"}),

            html.Div([
                dcc.Graph(id="route-map", figure=map)],
            style={"width": "65%", "display": "inline-block"})
        ])
    ])