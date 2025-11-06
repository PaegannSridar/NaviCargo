# Dictionary containing base speeds for major types of ships
base_speeds = {"Cargo": 20, "Tanker": 15, "Fishing": 8.5, "Military Operations": 20, "Passenger Ship": 25, "Wing in Ground": 80,
               "Search and Rescue vessel": 6}

# Dictionary containing average fuel consumption per day for major types of ships
fuel_consumptions = {"Tanker": 90, "Cargo": 150, "Fishing": 7, "Passenger Ship": 150, "Military Operations": 50, "Wing in Ground": 0.9,
                     "Search and Rescue vessel": 3}

# Emissions factor is dependent on fuel type so the same for all ships
emissions_factor = 3.114

default_base_speed = 14
default_fuel_day = 50

def emissions_per_km(ship_type, emission_factor, current_speed):

    if ship_type in base_speeds.keys():
        # Get base speed in knots and fuel per day from the dictionaries
        base_speed_knots = base_speeds[ship_type]
        fuel_per_day = fuel_consumptions[ship_type]
    else:
        # Use default values if the ship type is not in the list
        base_speed_knots = default_base_speed
        fuel_per_day = default_fuel_day

    base_speed_kmph = base_speed_knots * 1.852
    # Convert fuel consumption to tons/hour.
    fuel_per_hour = fuel_per_day / 24

    # Fuel consumed per km at base speed — normal cruising speed
    fuel_per_km = fuel_per_hour / base_speed_kmph

    # CO2 emissions per km at the base speed; emissions factor is known for every type of vessel
    emissions_per_km = fuel_per_km * emission_factor
    # As ship speed increases above its base speed, fuel consumption increases
    speed_factor = (current_speed / base_speed_knots) ** 3
    emissions_per_km = emissions_per_km * speed_factor
    return emissions_per_km * 1000

print(emissions_per_km("Cargo", emissions_factor, 17.4))


