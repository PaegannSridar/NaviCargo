import math
import pandas as pd
import networkx as nx
import numpy as np
from sklearn.neighbors import BallTree
import plotly.graph_objects as go


# Calculate the Haversine distance between two points
def haversine(coord1, coord2):
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return 6371.0 * c

# Build a graph by connecting each point to its five nearest neighbours
def build_graph_knn(csv_file, k=5):
    # Load the points from the CSV file
    df = pd.read_csv(csv_file)
    coords = df[["Latitude", "Longitude"]].values
    G = nx.Graph()

    # Add all nodes
    for lat, lon in coords:
        G.add_node((lat, lon))

    # Build BallTree in radians
    coords_radians = np.radians(coords)
    tree = BallTree(coords_radians, metric="haversine")

    # k-Nearest Neighbours query
    distances, indices = tree.query(coords_radians, k=k+1)

    for i, neighbors in enumerate(indices):
        for j, n in enumerate(neighbors):
            if n == i:
                continue
            p1 = tuple(coords[i])
            p2 = tuple(coords[n])
            dist_km = distances[i][j] * 6371.0
            G.add_edge(p1, p2, weight=dist_km)

    return G


def shortest_maritime_route(G, start, end):
    # Find the closest nodes in graph
    nodes = np.array(G.nodes)
    tree = BallTree(np.radians(nodes), metric="haversine")

    _, idx_start = tree.query([np.radians(start)], k=1)
    _, idx_end = tree.query([np.radians(end)], k=1)

    start_node = tuple(nodes[idx_start[0][0]])
    end_node = tuple(nodes[idx_end[0][0]])

    # Calculate
    path = nx.shortest_path(G, source=start_node, target=end_node, weight="weight")
    distance = nx.shortest_path_length(G, source=start_node, target=end_node, weight="weight")
    return path, distance

# Plot the path on a plotly world map to visually see the route (also used for debugging purposes)
def plot_path(path):
    import pandas as pd
    import plotly.graph_objects as go

    df = pd.read_csv("ais_nodes.csv")

    # Extract longitudes and latitudes for the path
    path_lons = [p[1] for p in path]
    path_lats = [p[0] for p in path]

    fig = go.Figure()

    # Add the path trace
    fig.add_trace(go.Scattermapbox(
        lon=path_lons,
        lat=path_lats,
        mode="lines+markers",
        line=dict(width=2, color="red"),
        marker=dict(size=4, color="red"),
        text=[f"{lat}, {lon}" for lat, lon in zip(path_lats, path_lons)],
        hoverinfo="lat+lon",
    ))

    # Update layout — make map larger & remove whitespace
    fig.update_layout(
        autosize=False,
        width=580,     # increase overall figure width
        height=400,     # increase figure height
        margin=dict(l=0, r=0, t=50, b=0),  # remove excess whitespace
        mapbox=dict(
            style="open-street-map",
            zoom=3,  # adjust to your desired zoom level
            center=dict(lat=sum(path_lats)/len(path_lats),
                        lon=sum(path_lons)/len(path_lons))
        ),
    )

    fig.show()

graph = build_graph_knn("ais_nodes.csv")
start = (34.0549, -118.242)
end = (22.5744, 88.3629)
path, distance = shortest_maritime_route(graph, start, end)
plot_path(path)

def calculate_eta(current_loc, destination, current_speed_knots):
    # Speed is stored in my dataframe and displayed on the page in knots.
    # Convert to km/h in order to calculate ETA in hours
    current_speed_km = current_speed_knots * 1.852

    graph = build_graph_knn("ais_nodes.csv")
    route, distance = shortest_maritime_route(graph, current_loc, destination)
    if current_speed_km != 0:
        eta = distance / current_speed_km
    else:
        eta = "Unavailable"
    return eta, distance


# Converts degrees/ minutes coordinates into decimal coordinates
def dm_to_decimal(dm_position):
    dm_lat = dm_position.split()[0]
    dm_lon = dm_position.split()[1]

    # Parse latitude
    hemi_lat = dm_lat[-1].upper()
    val_lat = dm_lat[:-1]
    deg_lat = int(val_lat[:2])
    min_lat = float(val_lat[2:])
    lat = deg_lat + min_lat / 60.0
    if hemi_lat == 'S':
        lat = -lat

    # Parse longitude
    hemi_lon = dm_lon[-1].upper()
    val_lon = dm_lon[:-1]
    deg_lon = int(val_lon[:3])
    min_lon = float(val_lon[3:])
    lon = deg_lon + min_lon / 60.0
    if hemi_lon == 'W':
        lon = -lon

    return (lat, lon)