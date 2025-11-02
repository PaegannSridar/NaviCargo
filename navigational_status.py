nav_status = {0: "Under way using engine", 1: "At anchor", 2: "Not under command", 3: "Restricted manoeuvrability", 4: "Constrained by her draught",
5: "Moored", 6: "Aground", 7: "Engaged in fishing", 8: "Under way sailing", 15: "Undefined"}

def get_navigation_status(navigational_status):
    status = nav_status.get(navigational_status)
    return status


