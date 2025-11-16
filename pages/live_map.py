import numpy
from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.graph_objects as go
import pandas as pd
import threading
import time
import warnings
import logging
import dash

# Filter Warnings
logging.getLogger().setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

from ais_data import start_websocket, return_df, ais_df
from mmsi_to_country import mmsi_country_map

ship_type_options = ["Wing In Ground", "Fishing", "Towing", "Towing (Large)", "Dredging or Underwater Operations", "Diving Operations", "Military Operations",
                     "Sailing Boat", "Pleasure Craft", "High Speed Craft", "Pilot Vessel", "Search and Rescue vessel", "Tug Boat", "Port Tender",
                     "Anti-pollution Vessels", "Law Enforcement", "Spare - Local Vessel", "Medical Transport", "Noncombatant ship", "Passenger Ship",
                     "Cargo", "Tanker"]


# Creates an empty initial map figure
def create_initial_figure():
    fig = go.Figure()
    fig.update_layout(
        mapbox_style="open-street-map",
        height=800,
        mapbox_zoom=1,
        mapbox_center={"lat": 0, "lon": 0},
        hovermode='closest',
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    # Add empty trace to be populated later with ship markers
    fig.add_trace(go.Scattermapbox(
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
    return fig

# Return the layout of the live_map page
def layout():
    return html.Div([
    # Title and image logo
        html.Img(src="/assets/NAVICARGO.png",
                 style={"height": "20px", "margin-right": "5px"}),
        html.Div("NaviCargo", style={"position": "absolute",
                                     "top": "10px", "left": "30px", "font-size": "15px", "font-weight": 550,
                                     "color": "#8b8b8b"}),
        html.Div("Live Maritime Tracking", style={"position": "absolute",
                                                  "top": "10px", "right": "12px", "font-size": "9px",
                                                  "font-weight": 450, "color": "#8b8b8b"}),

        html.Div([
            html.Button("Open Route & Emissions Calculator", id="open-route-page", n_clicks=0,
                style={"position": "absolute", "right": "12px", "top": "50px", "padding": "3px 3px", "font-weight": "bold", "background-color": "#0474ce",
                       "color": "white", "border": "none", "border-radius": "5px","cursor": "pointer"})
        ]),
    # Dropdown Filters
    html.Div([
        html.Div([
        html.Div("Ship Type", style={"margin-top":"5px", "font-size": "10px", "font-weight":450, "color": "#8b8b8b"}),
        dcc.Dropdown(sorted(ship_type_options), None, id='ship-type-dropdown', multi=True, placeholder="Ship Type",
                           style={"width": "300px", "margin-right":"10px"})]),
    html.Div([
        html.Div('Country Of Origin', style={"font-size": "10px", "margin-top":"5px", "margin-left":"4px", "font-weight":450, "color": "#8b8b8b"}),
        dcc.Dropdown(sorted(list(set(mmsi_country_map.values()))), None, id='country-dropdown', multi=True, placeholder="Country",
                     style={"width": "300px", "margin-left": "2px"})]),
        html.Div(id="message-box", style={"margin-top": "40px", "margin-left": "auto", "font-weight": "bold", "font-size":"12px"})],
        style={"display": "flex", "flex-direction": "row", "margin-top": "10px", "margin-bottom": "2px"}),

    # Map
    dcc.Graph(id='live-map', figure=create_initial_figure()),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # every 5 seconds
        n_intervals=0
    )
])

# Callback to update periodically
@callback(
    [Output('live-map', 'figure'),
     Output("message-box", "children"),
     Output("clicked-mmsi-store", "data")],
    [Input('interval-component', 'n_intervals'),
     Input('ship-type-dropdown', 'value'),
     Input('country-dropdown', 'value'),
     Input("live-map", "clickData")],
    [State('live-map', 'figure')],
    allow_duplicate=True
)


def update_map(n_intervals, selected_types, selected_countries, clickData, existing_fig):
    # Retrieve current ship data as a dataframe
    ais_df = return_df()

    # Display all columns and print dataframe for debugging purposes.
    pd.set_option('display.max_columns', None)

    df_copy = ais_df.copy()
    print(df_copy)

    # Apply ship type filter
    if selected_types and len(selected_types) > 0:
        df_copy = df_copy[df_copy["Ship Type"].isin(selected_types)]

    # Apply country filter
    if selected_countries and len(selected_countries) > 0:
        df_copy = df_copy[df_copy["Country of Origin"].isin(selected_countries)]

    # If empty existing figure, create a new one
    if existing_fig is None:
        existing_fig = create_initial_figure()

    fig = go.Figure(existing_fig)

    # Preserve the current user zoom/ pan
    fig.update_layout(uirevision='persistent_view')

    fig.data = []
    # Update ships markers
    if not df_copy.empty:
        fig.add_trace(go.Scattermapbox(
            lat=df_copy["Latitude"],
            lon=df_copy["Longitude"],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=5,
                color=df_copy["Ship Colour"].tolist(),
                opacity=0.8
            ),
            # The layout of the text shown on the tooltip popup
            text=[
                (f"<span style='color:#8b8b8b; font-size:6px'>NaviCargo</span><br>"
                 f"<span style='font-size:18px; font-weight:bold'>Name:</span> " + f"<span style='font-size:18px'>{name}</span><br>" +
                 f"<span style='color:darkslategray; font-weight:bold'>{status}</span> <br>"
                 if not pd.isna(status) and status not in ("Unknown", None, '') else "<br>") +
                f"<span style='font-size:14px'>{country}</span> <br>"
                f"📍({round(float(lat), 5)}, {round(float(lon), 5)})"

                for name, country, status, lat, lon in zip(df_copy["Name"], df_copy["Country of Origin"], df_copy["Navigational Status"],
                df_copy["Latitude"], df_copy["Longitude"])],
            # Features of the tooltip box itself
            hoverinfo='text',
            hoverlabel=dict(bgcolor='white', font_size=12, font_color='black', bordercolor='Gainsboro'),
            customdata=df_copy["MMSI"].astype(str).tolist()
        ))
    else:
        # Add an empty trace so the map shows even if dataframe is empty
        fig.add_trace(go.Scattermapbox(lat=[], lon=[]))

    clicked_mmsi = None
    if clickData:
        clicked_mmsi = clickData["points"][0]["customdata"]

    return fig, f"Currently showing: {df_copy.shape[0]} ships", {"mmsi": clicked_mmsi} if clicked_mmsi else None

