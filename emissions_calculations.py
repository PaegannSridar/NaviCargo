# Dictionary containing base speeds for major types of ships
base_speeds = {"Cargo": 20, "Tanker": 15, "Fishing": 8.5, "Military Operations": 20, "Passenger Ship": 25, "Wing in Ground": 80,
               "Search and Rescue vessel": 6}

# Dictionary containing average fuel consumption per day for major types of ships
fuel_consumptions = {"Tanker": 90, "Cargo": 150, "Fishing": 7, "Passenger Ship": 150, "Military Operations": 50, "Wing in Ground": 0.9,
                     "Search and Rescue vessel": 3}

# Reference areas for different ship types to be used in the scaling of fuel consumption
reference_areas = {"Tanker": 200*30, "Cargo": 240*32, "Fishing": 40*10, "Passenger Ship": 200*30, "Military Operations": 180*28, "Wing in Ground": 50*15,
    "Search and Rescue vessel": 30*6}

# Emissions factor is dependent on fuel type so the same for all ships
emissions_factor = 3.114
default_base_speed = 14
default_fuel_day = 50
default_ref_area = 200*30

# Calculate emissions per kilometer in kg
def emissions_per_km(ship_type, emission_factor, current_speed, length=None, width=None):

    if ship_type in base_speeds.keys():
        # Get base speed in knots and fuel per day from the dictionaries
        base_speed_knots = base_speeds[ship_type]
        fuel_per_day = fuel_consumptions[ship_type]
    else:
        # Use default values if the ship type is not in the list
        base_speed_knots = default_base_speed
        fuel_per_day = default_fuel_day

    if (length is not None and width is not None) and (length != 0 and width != 0):

        # Reference hull area for scaling
        reference_area = reference_areas[ship_type] if ship_type in reference_areas.keys() else default_ref_area

        hull_area = length * width
        area_ratio = hull_area / reference_area

        # Scale fuel with ship size (hull area-based adjustment)
        fuel_per_day = fuel_per_day * (area_ratio ** 1.1)

    base_speed_kmph = base_speed_knots * 1.852
    # Convert fuel consumption to tons/hour.
    fuel_per_hour = fuel_per_day / 24

    # Fuel consumed per km at base speed — normal cruising speed
    fuel_per_km = fuel_per_hour / base_speed_kmph

    # CO2 emissions per km at the base speed; emissions factor is known for every type of vessel
    emissions_per_km = fuel_per_km * emission_factor
    # As ship speed increases above its base speed, fuel consumption increases
    speed_factor = max((current_speed / base_speed_knots) ** 3, 0.15)
    emissions_per_km = emissions_per_km * speed_factor

    # Return emissions per kilometer in kg
    return emissions_per_km * 1000

# Allocate a proportion of total ship CO₂ emissions to a given container shipment
def container_emissions(container_type, quantity, total_ship_emissions):
    # Total ship emissions is 10000 TEU. Divide the TEU of the container by 10000 to get the proportion of total emissions.
    # Multiply by total emissions of the ship to get emissions and multiply by the number of containers being shipped by the user
    # 10ft is 0.5 TEU, 20ft is 1 TEU, 30ft is 1.5 TEU and 40 ft is 2 TEU
    if container_type == "10ft GP" or container_type == "10ft HC":
        shipment_emissions = (0.5/ 10000) * total_ship_emissions * quantity

    elif container_type == "20ft GP" or container_type == "20ft HC":
        shipment_emissions = (1/10000) * total_ship_emissions * quantity

    elif container_type == "30ft GP" or container_type == "30ft HC":
        shipment_emissions = (1.5/10000) * total_ship_emissions * quantity

    else:
        shipment_emissions = (2/10000) * total_ship_emissions * quantity

    # If the container is high cube, increase emissions by 13% in order to account for higher volume
    if container_type == "10ft HC" or container_type == "20ft HC" or container_type == "30ft HC" or container_type == "40ft HC":
        shipment_emissions = shipment_emissions * 1.13

    # Return the proportion of the ship's emissions allocated to the users shipment
    return shipment_emissions

