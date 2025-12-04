from dash import html, dcc

from ais_data import return_df
import plotly.graph_objects as go
from datetime import datetime
import math
from routing import dm_to_decimal, calculate_eta
from destination import destination_to_coordinates

# Extract all ship information to be displayed on the page
def extract_ship_info(mmsi):
    df = return_df()

    # Get the dataframe rwo that corresponds to the MMSI
    row = df[df["MMSI"].astype(str) == str(mmsi)]

    if row.empty:
        return html.Div([html.H3(f"Ship {mmsi} not found")])

    ship = row.iloc[0]

    # Extract data
    name = ship["Name"]
    colour = ship["Ship Colour"]
    country = ship["Country of Origin"]
    ship_type = ship["Ship Type"]
    speed = ship["Speed"]
    status = ship["Navigational Status"]
    lat = ship["Latitude"]
    lon = ship["Longitude"]
    timestamp = str(ship["Timestamp"])
    direction = ship["Direction"]
    rate_of_turn = ship["Rate of Turn"]
    length = ship["Length"]
    width = ship["Width"]
    flag_emoji = country.split()[-1]
    imo_number = ship["IMO"]
    draught = ship["Draught"]
    destination_country = ship["Destination Country"]
    destination_port = ship["Destination Port/ City"]
    destination_code = ship["Destination Code"]

    # Only if the destination is known can we try to get the distance and ETA
    if destination_code != "Unknown":
        try:
            # Try to find the destination coordinates in the CSV file and attempt to calculate a distance with it
            destination_coordinates = dm_to_decimal(destination_to_coordinates(destination_code))
            eta, distance = calculate_eta((lat,lon), destination_coordinates, float(speed))

            # If ETA is not 'Unavailable' then round it. The calculate ETA function either returns a float or 'Unavailable' if speed is 0
            if not isinstance(eta, str):
                eta = round(eta, 1)

            distance = round(distance)
            if distance <= 1:  # less than 1 km is considered as arrival at destination
                distance = "Destination reached"

        # If a distance could not be calculated then eta and distance are both unavailable
        except:
            eta = "Unavailable"
            distance = "Unavailable"
    else:
        eta = "Unavailable"
        distance = "Unavailable"

    try:
        # In order to convert to timestamp data type anything smaller than seconds and the '+ UTC...' needs to be removed
        clean_time = timestamp.split(".")[0]

        # Convert to timestamp in order to subtract from current time
        dt = datetime.strptime(clean_time, "%Y-%m-%d %H:%M:%S")
        total_minutes = math.floor((datetime.utcnow() - dt).total_seconds() / 60)
        hours_ago = total_minutes // 60
        minutes_ago = total_minutes % 60

        # Create a string that will display time in a nice format
        if total_minutes < 60:
            time_str = f"{minutes_ago} minutes ago"
        else:
            time_str = f"{hours_ago}h {minutes_ago}m ago"
    except:
        total_minutes = 'Unknown'

    return (name, colour, country, ship_type, speed, status, lat, lon, timestamp, direction, rate_of_turn, length, width,
            flag_emoji, imo_number, draught, destination_country, destination_port, total_minutes, time_str, eta, distance)

# Defines and returns the page layout
def layout(mmsi):
    (name, colour, country, ship_type, speed, status, lat, lon, timestamp, direction, rate_of_turn, length, width,
     flag_emoji, imo_number, draught, destination_country, destination_port, total_minutes, time_str, eta, distance) = extract_ship_info(mmsi)

    # Defines the mini map to be shown in the left half of the page
    mini_map = dcc.Graph(
        id="mini-map",
        figure=go.Figure(
            go.Scattermapbox(
                lat=[lat],
                lon=[lon],
                mode="markers",
                marker=dict(size=9, color=colour),
                text=[name],
                hoverinfo="text"
            )
        ).update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=6,
            mapbox_center={"lat": lat, "lon": lon},
            height=280,
            width=600,
            margin={"r": 0, "l": 0, "t": 0, "b": 0}
        )
    )

    # Returns the layout of the ship_info page
    return html.Div([
        # Title and image logo
        html.Div([
            html.Div([
                html.Img(src="/assets/NAVICARGO.png", style={"height": "20px", "margin-right": "5px"}),
                html.Div("NaviCargo",
                         style={"position": "absolute", "font-size": "15px", "top":"10px", "left": "30px", "font-weight": "550", "color": "#8b8b8b"})],
                style={"display": "flex", "flex-direction": "row"}),

            html.Div("More Ship Information",  style={"position": "absolute", "top": "10px", "right": "12px", "font-size": "9px",
                                                  "font-weight": 450, "color": "#8b8b8b"},)
        ], style={"display": "flex", "background-color": "white",}),
        # Header with ship name and MMSI
        html.Div([
            html.H2(f"{flag_emoji}  {name}", style={"margin-bottom": "0px"}),
            html.Div(f"{ship_type} — MMSI {mmsi}" if ship_type != "Unknown" else f"MMSI {mmsi}", style={"color": "gray"}),
        ], style={"padding": "5px"}),

        html.Hr(),

        html.Div([
            # Mini map and summary
            html.Div([
                html.H4("Latest Position", style={"color":"#0474ce"}),
                mini_map,
                html.Div([
                    html.P([html.B("Latitude/Longitude: "), f"{lat}, {lon}"]),
                    html.P([html.B("Position received: "), f"{time_str}"] if (total_minutes != "Unknown" and total_minutes != 0)
                        else [html.B("Position received: "), "Just now"] if total_minutes == 0 else [html.B("Position received: "), "-"])
                ]),
                html.Br(),
                html.A("⬅ Back to Live Map", href="/", style={"font-weight": "bold", "font-size": "16px", "text-decoration": "none"}),
            ], style={"border": "2px solid #dfdfdf", "border-radius": "10px", "padding": "15px", "width": "600px","position": "absolute", "top": "130px",
                "left": "5px", "background-color": "white"}),


            # Middle and right section (Ship and AIS Details)
            html.Div([
                html.H4("Detailed AIS information", style={"margin-bottom": "15px", "color":"#0474ce"}),

                # A 2-column table layout there are checks so that any empty or unknown information is displayed with a '-'
                html.Div([
                    html.Div("Speed", style={"font-weight": "600", "color": "#555"}),
                    html.Div(f"{speed} kn" if speed != "Unknown" else "-", style={"font-weight": "500"}),
                    html.Div("Direction", style={"font-weight": "600", "color": "#555"}),
                    html.Div(f"{direction}°" if direction != "Unknown" else "-", style={"font-weight": "500"}),
                    html.Div("Rate of Turn", style={"font-weight": "600", "color": "#555"}),
                    html.Div(f"{rate_of_turn} °/min" if rate_of_turn != "Unknown" else "-", style={"font-weight": "500"}),
                    html.Div("Length", style={"font-weight": "600", "color": "#555"}),
                    html.Div(f"{length} m" if (length != 0 and length !="Unknown") else "-", style={"font-weight": "500"}),
                    html.Div("Width", style={"font-weight": "600", "color": "#555"}),
                    html.Div(f"{width} m" if (width != 0 and width != "Unknown") else "-", style={"font-weight": "500"}),
                    html.Div("Destination Country", style={"font-weight": "600", "color": "#555"}),
                    html.Div(destination_country if destination_country != "Unknown" else "-", style={"font-weight": "500"}),
                    html.Div("Destination Port", style={"font-weight": "600", "color": "#555"}),
                    html.Div(destination_port if destination_port != "Unknown" else "-", style={"font-weight": "500"}),
                    html.Div("IMO", style={"font-weight": "600", "color": "#555"}),
                    html.Div(imo_number if (imo_number != "Unknown" and imo_number != 0) else "-", style={"font-weight": "500"}),
                    html.Div("Draught", style={"font-weight": "600", "color": "#555"}),
                    html.Div(f"{draught} m" if draught != "Unknown" else "-", style={"font-weight": "500"}),
                    html.Div("Last AIS Message", style={"font-weight": "600", "color": "#555"}),
                    html.Div(f"{timestamp} ({time_str})", style={"font-weight": "500"})],
                    # Table-like layout styling
                    style={"display": "grid", "grid-template-columns": "170px auto", "row-gap": "12px"})],
                style={"border": "2px solid #dfdfdf", "border-radius": "10px", "padding": "15px", "width": "350px","position": "absolute", "top": "130px",
                "right": "5px", "background-color": "white"}),

            html.Div([
                html.H4("General Ship and Route Information", style={"margin-bottom": "15px", "color":"#0474ce"}),
                # A 2-column table layout
                html.Div([
                    html.Div("Name", style={"font-weight": "600", "color": "#555"}),
                    html.Div(name, style={"font-weight": "500"}),
                    html.Div("Country", style={"font-weight": "600", "color": "#555"}),
                    html.Div(country if country != "Unknown" else "-", style={"font-weight": "500"}),
                    html.Div("Ship Type", style={"font-weight": "600", "color": "#555"}),
                    html.Div(ship_type if ship_type != "Unknown" else "-", style={"font-weight": "500"}),
                    html.Div("MMSI", style={"font-weight": "600", "color": "#555"}),
                    html.Div(mmsi if mmsi != "Unknown" else "-", style={"font-weight": "500"}),
                    html.Div("Status", style={"font-weight": "600", "color": "#555"}),
                    html.Div(status if status != "Unknown" else "-", style={"font-weight": "500"}),
                    html.Div("ETA", style={"font-weight": "600", "color": "#555"}),
                    html.Div(f"{eta} hours" if eta != "Unavailable" else eta, style={"font-weight": "500"}),
                    html.Div("Distance to Destination", style={"font-weight": "600", "color": "#555"}),
                    html.Div(f"{distance} km" if isinstance(distance, int) == True else distance, style={"font-weight": "500"}),],
                    # Table-like layout styling
                    style={"display": "grid", "grid-template-columns": "170px auto", "row-gap": "12px"})],
            style={"border": "2px solid #dfdfdf", "border-radius": "10px", "padding": "15px", "width": "350px","position": "absolute", "top": "130px",
                "right": "403px", "background-color": "white"})
            ])])