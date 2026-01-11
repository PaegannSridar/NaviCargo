import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import numpy as np

locode_df = pd.read_csv('UN_LOCODE.csv')

dash.register_page(__name__, path="/route")


# Returns the layout of how the route info should be displayed
def result_card(start_code, start_name, end_code, end_name, distance_km, days, hours, emissions_tonnes):
    return html.Div(
        style={"background": "white", "borderRadius": "12px", "width": "410px", "display": "flex", "padding":"5px 5px ",
            "flexDirection": "column", "gap": "12px", "fontFamily": "sans-serif", "border":"1px solid #0474ce"},
        children=[# TOP ROW
            html.Div(style={"display": "flex", "justifyContent": "space-between"},
                     children=[html.Div([ html.Div(start_code, style={"font-weight": "bold", "font-size": "20px"}),
                    html.Div(start_name, style={"color": "#555"})]),
                    html.Div([html.Div(end_code, style={"font-weight": "bold", "font-size": "20px"}),
                    html.Div(end_name, style={"color": "#555"})
                    ])]),
            html.Div(f"{days} days {hours} hrs", style={"font-size": "17px", "font-weight": "500"}),
            # BOTTOM  ROW
            html.Div(
                style={"display": "flex", "justify-content": "space-between", "align-items": "center"},
                children=[
                    html.Div(f"{round(distance_km)} kilometers",
                             style={"fontSize": "16px", "color": "#555"}),
                    html.Div(
                        f"{round(emissions_tonnes, 2)} t CO₂",
                        style={"background": "#E8F8EE", "border-radius": "8px", "color": "#2A8C4A", "font-weight": "600"}
                    )])])

# Returns the layout of the route
def layout():
    # List of container sizes to be used in the dropdown menu
    containers=["10ft GP", "10ft HC", "20ft GP", "20ft HC", "30ft GP", "30ft HC", "40ft GP", "40ft HC"]
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
    # Add empty trace to be populated with the route lines later
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
                     style={"position": "absolute", "top": "10px", "right": "12px", "font-size": "9px", "font-weight": 450, "color": "#8b8b8b"}, )],
            style={"display": "flex", "background-color": "white", }),

        # Page heading
        html.H2("Route and Emissions Calculator", style={"margin-bottom": "15px"}),

        html.Div([
            html.Div([
                # Dropdown list for start ports
                html.Label("Start Port"),
                dcc.Dropdown(id="start-port", options=locode_df['Name'], placeholder="Select a starting port",
                             style={"width": "250px", "border":"1px solid #d9d9d9", "border-radius":"5px"},),
                html.Br(),
                # Dropdown list for end ports
                html.Label("End Port"),
                dcc.Dropdown(id="end-port", options=locode_df['Name'], placeholder="Select a destination port",
                             style={"width": "250px", "border":"1px solid #d9d9d9", "border-radius":"5px"}),
                html.Br(),

                # Dropdown lists, displayed side by side on the same row
                html.Div([
                    html.Div([
                        # Dropdown list for container sizes
                        html.Label([html.Img(src="/assets/Container Icon.png", style={"height": "16px", "margin-right": "6px",
                                                                                      "vertical-align": "middle"}), "Cargo"],
                                   style={"display": "flex", "align-items": "center"}),
                        dcc.Dropdown(id="container-size", options=containers, placeholder="Container size",
                                     style={"width": "200px", "margin-right":"10px", "border":"1px solid #d9d9d9", "border-radius":"5px"})]),

                    html.Div([
                        # Input box for quantity of cargo
                        html.Label("Quantity", style={"display": "flex", "alignItems": "center"}),
                        dcc.Input(id="quantity", type="text",
                                  style={"width": "40px", "height": "33px", "border":"1px solid #d9d9d9", "border-radius":"5px", "text-align":"center"})])],
                    style={"display": "flex", "flex-direction": "row", "margin-top": "10px", "margin-bottom": "2px"}),
                html.Br(),
                # Button to calculate route
                html.Button("Calculate Route", id="calculate-route", n_clicks=0,
                            style={"width":"250px", "margin-bottom":"10px", "font-size":"15px", "background-color":"#0474ce", "color":"white",
                                   "border":"none", "border-radius":"5px", "cursor":"pointer"}),
                # Invisible 'box' in which the route information will be displayed
                html.Div(id="info-box", style={"margin-top": "40px", "margin-left": "auto", "font-weight": "bold",
                                                  "font-size": "18px"}),
                html.Br(), html.Br(),
                # Link to go back to live map
                html.A("⬅ Back to Live Map", href="/",
                       style={"font-weight": "bold", "font-size": "16px"})],
            style={"width": "30%", "display": "inline-block", "vertical-align": "top"}),

            html.Div([
                dcc.Graph(id="route-map", figure=map, config={"scrollZoom": True})],
            style={"width": "65%", "display": "inline-block"})
        ])
    ])