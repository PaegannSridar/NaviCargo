from dash import html, dcc

def layout():
    return html.Div([
        html.H2("Route and Emissions Calculator", style={"margin-bottom": "15px"}),

        html.Div([
            html.Label("Start Port (Latitude, Longitude)"),
            dcc.Input(id="start-coord", type="text", placeholder="e.g. 34.05, -118.25", style={"width": "250px", "margin-right": "10px"}),

            html.Label("End Port (Latitude, Longitude)"),
            dcc.Input(id="end-coord", type="text", placeholder="e.g. 22.57, 88.36", style={"width": "250px", "margin-right": "10px"}),

            html.Button("Calculate Route", id="calculate-route", n_clicks=0, style={"margin-left": "10px"}),
        ], style={"margin-bottom": "20px"}),

        html.Div(id="route-results", style={"margin-top": "20px"}),

        html.Br(),
        html.A("⬅ Back to Live Map", href="/", style={"font-weight": "bold", "font-size": "16px", "text-decoration": "none"})
    ])