ship_types = {20: ("Wing In Ground", "OliveDrab"), 21: ("Wing in Ground", "OliveDrab"), 22: ("Wing in Ground", "OliveDrab"), 23: ("Wing in Ground", "OliveDrab"),
24: ("Wing in Ground", "OliveDrab"), 25: ("Wing in Ground", "OliveDrab"), 26: ("Wing in Ground", "OliveDrab"), 27: ("Wing in Ground", "OliveDrab"),
28: ("Wing in Ground", "OliveDrab"), 29: ("Wing in Ground", "OliveDrab"), 30: ("Fishing", "Gold"), 31: ("Towing", "DarkGreen"), 32: ("Towing", "DarkGreen"),
33: ("Dredging or Underwater Operations", "Black"), 34: ("Diving Operations", "Magenta"), 35: ("Military Operations", "Indigo"),
36: ("Sailing Boat", "DarkSlateBlue"), 37: ("Pleasure Craft", "PeachPuff"), 40: ("High Speed Craft", "DarkOrange"), 41: ("High Speed Craft", "DarkOrange"),
42: ("High Speed Craft", "DarkOrange"), 43: ("High Speed Craft", "DarkOrange"), 44: ("High Speed Craft", "DarkOrange"), 45: ("High Speed Craft", "DarkOrange"),
46: ("High Speed Craft", "DarkOrange"), 47: ("High Speed Craft", "DarkOrange"), 48: ("High Speed Craft", "DarkOrange"), 49: ("High Speed Craft", "DarkOrange"),
50: ("Pilot Vessel", "LightGreen"), 51: ("Search and Rescue vessel", "WhiteSmoke"), 52: ("Tug Boat", "Silver"), 53: ("Port Tender", "LimeGreen"),
54: ("Anti-pollution Vessels", "Sienna"), 55: ("Law Enforcement", "SaddleBrown"), 56: ("Spare - Local Vessel", "DarkGoldenRod"),
57: ("Spare - Local Vessel", "DarkGoldenRod"), 58: ("Medical Transport", "Tomato"), 59: ("Noncombatant ship", "LightCoral"), 60: ("Passenger Ship", "Crimson"),
61: ("Passenger Ship", "Crimson"), 62: ("Passenger Ship", "Crimson"), 63: ("Passenger Ship", "Crimson"), 64: ("Passenger Ship", "Crimson"),
65: ("Passenger Ship", "Crimson"), 66: ("Passenger Ship", "Crimson"), 67: ("Passenger Ship", "Crimson"), 68: ("Passenger Ship", "Crimson"),
69: ("Passenger Ship", "Crimson"), 70: ("Cargo", "ForestGreen"), 71: ("Cargo", "ForestGreen"), 72: ("Cargo", "ForestGreen"), 73: ("Cargo", "ForestGreen"),
74: ("Cargo", "ForestGreen"), 75: ("Cargo", "ForestGreen"), 76: ("Cargo", "ForestGreen"), 77: ("Cargo", "ForestGreen"), 78: ("Cargo", "ForestGreen"),
79: ("Cargo", "ForestGreen"), 80: ("Tanker", "Navy"), 81: ("Tanker", "Navy"), 82: ("Tanker", "Navy"), 83: ("Tanker", "Navy"), 84: ("Tanker", "Navy"),
85: ("Tanker", "Navy"), 86: ("Tanker", "Navy"), 87: ("Tanker", "Navy"), 88: ("Tanker", "Navy"), 89: ("Tanker", "Navy"), 90: ("Other Type", "RoyalBlue"),
91: ("Other Type", "RoyalBlue"), 92: ("Other Type", "RoyalBlue"), 93: ("Other Type", "RoyalBlue"), 94: ("Other Type", "RoyalBlue"), 95: ("Other Type", "RoyalBlue"),
96: ("Other Type", "RoyalBlue"), 97: ("Other Type", "RoyalBlue"), 98: ("Other Type", "RoyalBlue"), 99: ("Other Type", "RoyalBlue")}

# Get the ship type string
def get_ship_type(ship_type):
    try:
        ship_tuple = ship_types[ship_type]
    except:
        return "Unknown"
    return ship_tuple[0]

# Get the colour of the ship that will be used in the map
def get_ship_colour(ship_type):
    try:
        ship_tuple = ship_types[ship_type]
    except:
        return "DarkTurquoise"
    return ship_tuple[1]