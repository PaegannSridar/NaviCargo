# Imports
import websocket
import json
import pandas as pd
import time
import os
import datetime
import warnings

from mmsi_to_country import get_country_from_mmsi
from ship_type_numbers import get_ship_type, get_ship_colour, ship_types
from navigational_status import get_navigation_status
from destination import get_destination

# Ignore warnings
warnings.filterwarnings("ignore")
# Load existing data from CSV if available
if os.path.exists("ais_data.csv"):
    column_names = [
        "Name", "MMSI", "Latitude", "Longitude", "Speed", "Timestamp",
        "Ship Type", "Ship Colour", "Raw Destination", "Destination Code",
        "Destination Port/ City", "Destination Country", "Country of Origin",
        "Direction", "Length", "Width", "Rate of Turn", "Navigational Status", "IMO", "Draught"]
    try:
        ais_df = pd.read_csv("ais_data.csv", names=column_names, header=0)

    # If some rows have errors (too many columns) then remove them
    except:
        print("CSV corrupted")
        with open("ais_data.csv", "r", errors="ignore") as f:
            lines = [line for line in f if line.count(",") == 14]  # Keep only lines with 15 fields
        with open("recovered.csv", "w") as f:
            f.writelines(lines)
        ais_df = pd.read_csv("recovered.csv")

    # Sort by time order of messages and remove the oldest row if there is a duplicate ship
    ais_df = ais_df.sort_values(by="Timestamp", ascending=True).reset_index(drop=True)
    ais_df.drop_duplicates(keep="first", inplace=True)

    # Current UTC time
    now = pd.Timestamp.utcnow().replace(tzinfo=None)

    # Convert the 'Timestamp' column to a dataframe
    ais_df["Timestamp"] = ais_df["Timestamp"].astype(str).str.split(".").str[0].pipe(pd.to_datetime, format="%Y-%m-%d %H:%M:%S", errors="coerce")



    # Filter all columns more than 20 hours old
    ais_df = ais_df.loc[ais_df["Timestamp"] >= now - pd.Timedelta(hours=20)]

    # Keep only the last/ newest 60000 ships to track
    ais_df = ais_df.tail(25000)
    time.sleep(5)

# Create new dataframe if CSV not available
else:
    ais_df = pd.DataFrame(columns=[
        "Name", "MMSI", "Latitude", "Longitude", "Speed", "Timestamp",
        "Ship Type", "Ship Colour", "Raw Destination", "Destination Code",
        "Destination Port/ City", "Destination Country", "Country of Origin",
        "Direction", "Length", "Width", "Rate of Turn", "Navigational Status", "IMO", "Draught"])
    print("Creating new DataFrame")

# Global counter for number of messages
message_count = 0

# Save the entire DataFrame to CSV
def save_csv():
    ais_df.to_csv("ais_data.csv", index=False)

# Called when a message is received
def on_message(ws, message):
    global message_count
    global ais_df
    global last_processed_time

    data = json.loads(message)
    msg_type = data.get("MessageType")

    # Call the respective subroutines to handle different types of messages
    if msg_type == "PositionReport":
        handle_position_report(data)
    elif msg_type == "ShipStaticData":
        handle_ship_static_data(data)
    elif msg_type == "StaticDataReport":
       handle_static_data_report(data)

    message_count += 1
    if message_count >= 200:
        save_csv()
        message_count = 0
        time.sleep(2)

# Handle PositionReport Messages
def handle_position_report(data):
    global ais_df

    # Extract relevant data
    position_data = data.get("Message", {}).get("PositionReport", {})
    metadata = data.get("MetaData", {})
    mmsi = metadata.get("MMSI")
    lat = round(position_data.get("Latitude"), 4)
    lon = round(position_data.get("Longitude"), 4)
    speed = position_data.get("Sog")
    name = metadata.get("ShipName") or "Unknown Vessel"
    timestamp = metadata.get("time_utc")
    direction = position_data.get("Cog")
    country = get_country_from_mmsi(mmsi)
    rate_of_turn = position_data.get("RateOfTurn")
    navigational_status = get_navigation_status(position_data.get("NavigationalStatus"))

    # Only fishing vessels can be engaged in fishing
    if navigational_status == "Engaged in fishing":
        ship_type = 'Fishing'
        ship_colour = 'Gold'
    else:
        ship_type = 'Unknown'
        ship_colour = 'DarkTurquoise'

    # Update relevant row if MMSI exists in the Dataframe
    if mmsi in ais_df["MMSI"].values:
        ais_df.loc[ais_df["MMSI"] == mmsi, ["Name", "Latitude", "Longitude", "Speed",
                                            "Timestamp", "Country of Origin", "Direction",
                                            "Rate of Turn", "Navigational Status"]] = \
            [name, lat, lon, speed, timestamp, country, direction, rate_of_turn, navigational_status]

        if navigational_status == "Engaged in fishing":
            ais_df.loc[ais_df['MMSI'] == mmsi, ['Ship Type', 'Ship Colour']] = [ship_type, ship_colour]
    # Add a new row if ship doesn't exist in the Dataframe and the maximum limit hasn't been reached
    elif ais_df.shape[0] < 25000:
        new_row = pd.DataFrame([[name, mmsi, lat, lon, speed, timestamp, ship_type, ship_colour, "Unknown", "Unknown",
                                 "Unknown", "Unknown", country, direction, "Unknown", "Unknown", rate_of_turn, navigational_status, "Unknown", "Unknown"]],
                               columns=ais_df.columns)
        ais_df = pd.concat([ais_df, new_row], ignore_index=True)

# Handle ShipStaticData Messages
def handle_ship_static_data(data):
    global ais_df
    static_data = data.get("Message", {}).get("ShipStaticData", {})
    metadata = data.get("MetaData", {})
    mmsi = metadata.get("MMSI")
    lat = round(metadata.get("latitude"), 4)
    lon = round(metadata.get("longitude"), 4)
    ship_type = get_ship_type(static_data.get("Type"))
    ship_colour = get_ship_colour(static_data.get("Type"))
    name = static_data.get("Name") or "Unknown Vessel"
    timestamp = metadata.get("time_utc")
    country = get_country_from_mmsi(mmsi)
    raw_destination = static_data.get("Destination")
    destination_code = get_destination(raw_destination, str(country.split()[:-1]))[0] if ship_type not in ['Fishing', 'Towing', 'Tug Boat', 'Port Tender'] \
        else 'Unknown'
    destination_port = get_destination(raw_destination, str(country.split()[:-1]))[1] if ship_type not in ['Fishing', 'Towing', 'Tug Boat', 'Port Tender'] \
        else 'Unknown'
    destination_country = get_destination(raw_destination, str(country.split()[:-1]))[2] if ship_type not in ['Fishing', 'Towing', 'Tug Boat', 'Port Tender'] \
        else 'Unknown'
    dimensions = static_data.get("Dimension")
    length = dimensions.get("A") + dimensions.get("B")
    width = dimensions.get("C") + dimensions.get("D")
    length = "Unknown" if length == 0 else length
    width = "Unknown" if width == 0 else width
    imo_number = static_data.get("ImoNumber")
    draught = static_data.get("MaximumStaticDraught")

    # Update relevant row if MMSI exists in the Dataframe
    if mmsi in ais_df["MMSI"].values:
        ais_df.loc[ais_df["MMSI"] == mmsi, ["Name", "Latitude", "Longitude", "Timestamp", "Ship Type", "Ship Colour",
                                            "Raw Destination", "Destination Code", "Destination Port/ City", "Destination Country",
                                            "Country of Origin", "Length", "Width", "IMO", "Draught"]] = \
            [name, lat, lon, timestamp, ship_type, ship_colour, raw_destination, destination_code,
             destination_port, destination_country, country, length, width, imo_number, draught]

    # Add a new row if ship doesn't exist in the Dataframe and the maximum limit hasn't been reached
    elif ais_df.shape[0] < 25000:
        new_row = pd.DataFrame([[name, mmsi, lat, lon, "Unknown", timestamp, ship_type,
                                 ship_colour, raw_destination, destination_code, destination_port,
                                 destination_country, country, "Unknown", length, width,
                                 "Unknown", "Unknown", imo_number, draught]], columns=ais_df.columns)
        ais_df = pd.concat([ais_df, new_row], ignore_index=True)

# Handle StaticDataReport Messages
def handle_static_data_report(data):
    global ais_df
    static_data_report = data.get("Message", {}).get("StaticDataReport", {})
    metadata = data.get("MetaData", {})
    mmsi = metadata.get("MMSI")
    lat = round(metadata.get("latitude"), 4)
    lon = round(metadata.get("longitude"), 4)
    name = metadata.get("ShipName") or "Unknown Vessel"
    timestamp = metadata.get("time_utc")
    country = get_country_from_mmsi(mmsi)
    ship_type = get_ship_type(static_data_report.get("ShipType"))
    ship_colour = get_ship_colour(static_data_report.get("ShipType"))
    dimensions = static_data_report.get("ReportB").get("Dimension")
    length = dimensions.get("A") + dimensions.get("B")
    width = dimensions.get("C") + dimensions.get("D")
    length = "Unknown" if length == 0 else length
    width = "Unknown" if width == 0 else width

    # Update relevant row if MMSI exists in the Dataframe
    if mmsi in ais_df["MMSI"].values:
        ais_df.loc[ais_df["MMSI"] == mmsi, ["Name", "Latitude", "Longitude", "Timestamp",
                                            "Ship Type", "Ship Colour", "Country of Origin",
                                            "Length", "Width"]] = \
            [name, lat, lon, timestamp, ship_type, ship_colour, country, length, width]

    # Add a new row if ship doesn't exist in the Dataframe and the maximum limit hasn't been reached
    elif ais_df.shape[0] < 25000:
        new_row = pd.DataFrame([[name, mmsi, lat, lon, "Unknown", timestamp, ship_type,
                                 ship_colour, "Unknown", "Unknown", "Unknown", "Unknown", country, "Unknown", length, width,
                                 "Unknown", "Unknown", "Unknown", "Unknown"]], columns=ais_df.columns)
        ais_df = pd.concat([ais_df, new_row], ignore_index=True)

# Error handlers
def on_error(ws, error):
    print("Error:", error)

# Shows that connection is closed
def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

# Called when connection is opened
def on_open(ws):
    print("Connected to AISStream.io")
    subscribe_message = {
        "APIKey": "b978b0aba6f2d878221e58ba19851fe0178622d2",
        "BoundingBoxes": [[[-90, 180], [90, -180]]],
        "FilterMessageTypes": ["PositionReport", "ShipStaticData", "StaticDataReport"]
    }
    ws.send(json.dumps(subscribe_message))

# WebSocket
def start_websocket():
    count = 0
    while True:
        try:
            ws = websocket.WebSocketApp(
                "wss://stream.aisstream.io/v0/stream",
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever()
        except Exception as e:
            print("WebSocket error:", e)

        count = count + 1
        if count == 5:
            print("Trying to reconnect...")
            time.sleep(180)
            count = 0

        print("Reconnecting in 5 seconds...")
        time.sleep(5)

# Return DataFrame
def return_df():
    return ais_df

