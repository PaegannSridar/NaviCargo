import threading
import time
import logging

from dash import Dash, dcc, html, Input, Output, State, no_update
import dash

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

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("open-route-page", "n_clicks"),
    prevent_initial_call=True
)
def go_to_route_page(n_clicks):
    if n_clicks:
        return "/route"
    return no_update

if __name__ == "__main__":
    # Start the websocket data collection thread (so ais_df populates)
    ws_thread = threading.Thread(target=start_websocket, daemon=True)
    ws_thread.start()
    # small wait so some data can populate
    time.sleep(2)
    app.run(debug=True)
