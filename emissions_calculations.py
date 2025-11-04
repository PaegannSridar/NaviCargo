base_speeds = {"Cargo": 20, "Tanker": 15, "Fishing": 8.5, "Military Operations": 20, "Passenger Ship": 25, "Wing in Ground": 80,
               "Search and Rescue vessel": 6}

fuel_consumptions = {"Tanker": 90, "Cargo": 150, "Fishing": 7, "Passenger Ship": 150, "Military Operations": 50, "Wing in Ground": 0.9,
                     "Search and Rescue vessel": 3}

def emmisions_per_km(base_speed_knots, fuel_per_day, emission_factor, current_speed):
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
    return emissions_per_km

