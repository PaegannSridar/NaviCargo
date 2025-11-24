import threading
import time
import logging
import pandas as pd

from dash import Dash, dcc, html, Input, Output, State, no_update
from routing import dm_to_decimal, shortest_maritime_route, build_graph_knn
from destination import destination_to_coordinates
import dash
import plotly.graph_objects as go

logging.getLogger().setLevel(logging.ERROR)

# import your websocket & dataframe functions
from ais_data import start_websocket, return_df, ais_df

# import page renderers
from pages import live_map, ship_info, route_page

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# App layout
app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="page-content"),
    dcc.Store(id="clicked-mmsi-store")
])

# Router: serve different pages depending on pathname
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)

def display_page(pathname):
    if pathname.startswith("/ship/"):
        mmsi = pathname.split("/")[-1]
        return ship_info.layout(mmsi)
    elif pathname == "/route":
        return route_page.layout()
    return live_map.layout()

# When live_map sets clicked-mmsi-store, navigate to ship page
@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("clicked-mmsi-store", "data"),
    prevent_initial_call=True,
)
def navigate_to_ship(store_data):
    if not store_data:
        raise dash.exceptions.PreventUpdate
    return f"/ship/{store_data['mmsi']}"

# Clicking the button redirects the user to the route calculator page by changing the URL
@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("open-route-page", "n_clicks"),
    prevent_initial_call=True
)
def go_to_route_page(n_clicks):
    if n_clicks:
        return "/route"
    return no_update

# Display the route on the map when the 'Calculate Route' button is clicked.
@app.callback(
    Output("route-map", "figure"),
    Input("calculate-route", "n_clicks"),
    State("start-port", "value"),
    State("end-port", "value"),
    prevent_initial_call=True
)

def update_route_map(n_clicks, start_port, end_port):
    locode_df = pd.read_csv('UN_LOCODE.csv')

    if not start_port or not end_port:
        raise dash.exceptions.PreventUpdate

    # Convert port names to coordinates
    start_locode = locode_df.loc[locode_df["Name"] == start_port, "Coordinates"].iloc[0]
    end_locode   = locode_df.loc[locode_df["Name"] == end_port, "Coordinates"].iloc[0]
    print(start_locode, end_locode)

    # Coordinates in the CSV file are in degrees-minutes form. Convert this to decimal form.
    start = dm_to_decimal(start_locode)
    end   = dm_to_decimal(end_locode)

    # Build a maritime graph
    graph = build_graph_knn('ais_nodes.csv')

    # Use the routing function
    path, dist = shortest_maritime_route(graph, start, end)

    # Extract lat/lon
    lats = [p[0] for p in path]
    lons = [p[1] for p in path]

    # Build map
    fig = go.Figure()

    # Add the path trace
    fig.add_trace(go.Scattermapbox(
        lon=lons,
        lat=lats,
        mode="lines+markers",
        line=dict(width=2, color="red"),
        marker=dict(size=2, color="red"),
        hoverinfo='none'
    ))
    # Update layout: The centre of the map is the average of the coordinates that lie on the path
    fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            mapbox_style='open-street-map',
            mapbox_zoom=2,
            mapbox_center=dict(lat=sum(lats) / len(lats),
                        lon=sum(lons) / len(lons)))

    return fig

if __name__ == "__main__":
    # Start the websocket data collection thread (so ais_df populates)
    ws_thread = threading.Thread(target=start_websocket, daemon=True)
    ws_thread.start()
    # small wait so some data can populate
    time.sleep(2)
    app.run(debug=True)
