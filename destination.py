import pandas as pd
import re
from fuzzywuzzy import fuzz, process
import numpy as np
import math
import warnings

# Column names for both dataframes
column_names = ['Country', 'LOCODE', 'Name', 'Sub-division', 'Function', 'Date', 'Coordinates']
column_names2 = ['Name', 'Alpha 2', 'Alpha 3']

# Load the new destination csv
destination_locodes = pd.read_csv('UN_LOCODE.csv', names=column_names, header=0)
country_names = pd.read_csv('UN CountryCodes.csv', names=column_names2,header=0)


# Remove common suffixes (e.g. OFF, ANCH, ANCHORAGE, HARBOUR, etc.) only if they appear at the END of the port name.
def clean_port_name(name):
    suffixes = {
        "OFF", "ANCH", "ANCHORAGE", "HARBOUR", "HBR",
        "PORT", "OPL", "ROADS", "ROADSTEAD", "PWBGA",
        "BAY", "PEBGA", "SEA", "TRIAL"
    }

    words = name.upper().split()

    # Keep removing suffixes from the end until no more matches
    while words and words[-1] in suffixes:
        words.pop()

    return " ".join(words)
#Convert 'St.' or 'St' (when used as a standalone prefix) into 'Saint' in port names.
def expand_st_to_saint(name):
    # Use regex with word boundaries to avoid changing substrings in other words
    return re.sub(r'\bST[.]?\b', 'SAINT', name, flags=re.IGNORECASE)

# Split a raw port name into the main name and optional subdivision/country code.
def split_name_and_subdivision(raw_destination):
    if ',' in raw_destination:
        parts = [p.strip() for p in raw_destination.split(',', 1)]
        return parts[0], parts[1]  # (name, subdivision/country code)

    if '-' in raw_destination:
        parts = [p.strip() for p in raw_destination.split('-', 1)]
        return parts[0], parts[1]
    return raw_destination.strip(), None

def lookup_locode(locode):
    # Look up a UN LOCODE and return its name and country.
    locode = locode.replace(' ', '')
    result = destination_locodes.loc[
        (destination_locodes['LOCODE'] == locode[2:]) &
        (destination_locodes['Country'] == locode[:2]),
        'Name'
    ]
    country = country_names.loc[country_names['Alpha 2'] == locode[:2], 'Name']
    if not result.empty:
        return locode, result.iloc[0], country.iloc[0]
    return '', '', ''


def lookup_plain_name(name, country_of_origin=None, subdivision_code=None):
    # Expand "St" to "Saint"
    name = expand_st_to_saint(name.strip().title())

    # First try exact match
    result = destination_locodes.loc[destination_locodes['Name'] == name, ['Country', 'Sub-division', 'LOCODE']]

    # If subdivision/country code provided, filter by it
    if subdivision_code and not result.empty:
        filtered = result.loc[
            (result['Sub-division'] == subdivision_code) |
            (result['Country'] == subdivision_code)
        ]
        if not filtered.empty:
            result = filtered

    # If country_of_origin provided, use as secondary filter
    if country_of_origin and not result.empty:
        alpha2 = country_names.loc[country_names['Name'] == country_of_origin, 'Alpha 2'].iloc[0]
        filtered = result.loc[result['Country'] == alpha2]
        if not filtered.empty:
            result = filtered

    # Return if match found
    if not result.empty:
        return (
            result['Country'].iloc[0] + result['LOCODE'].iloc[0],
            name,
            country_names.loc[country_names['Alpha 2'] == result['Country'].iloc[0], 'Name'].iloc[0]
        )

    # Fuzzy fallback
    best_match = process.extractOne(name, destination_locodes['Name'], scorer=fuzz.partial_ratio, processor=None)
    if best_match and best_match[1] >= 70:
        match_name = best_match[0]
        result = destination_locodes.loc[destination_locodes['Name'] == match_name, ['Country', 'LOCODE']]
        if not result.empty:
            return result['Country'].iloc[0] + result['LOCODE'].iloc[0], match_name, \
                    country_names.loc[country_names['Alpha 2'] == result['Country'].iloc[0], 'Name'].iloc[0]

    return '', '', ''


def parse_with_separator(raw_destination, country_of_origin=None):
    # Handle destinations with separators (e.g. 'OMSUH>>NLVLI').
    for sep in ['>>', '->', '=>', '<->', '<>', '-', '>']:
        if sep in raw_destination:
            destination = raw_destination.split(sep, 1)[1].strip()
            if len(destination.replace(' ', '')) == 5:
                return lookup_locode(destination)
            elif not any(char.isdigit() for char in destination):
                return lookup_plain_name(destination, country_of_origin)
    return '', '', ''

# Main entry function for resolving raw destinations into structured info.
def get_destination(raw_destination, country_of_origin=None):
    if raw_destination.lower() == "coastguard" or "fishing" in raw_destination.lower():
        return "Unknown", "Unknown", "Unknown"
    raw_destination = raw_destination.strip()
    raw_destination = clean_port_name(raw_destination)
    # CASE 1: Direct LOCODE
    if len(raw_destination.replace(' ', '')) == 5:
        code, name, country = lookup_locode(raw_destination)
        if code:
            return code, name, country
    # CASE 2: With separator
    code, name, country = parse_with_separator(raw_destination, country_of_origin)
    if code:
        return code, name, country
    # CASE 3: Plain name (possibly with subdivision)
    if not any(char.isdigit() for char in raw_destination):
        main_name, subdivision_code = split_name_and_subdivision(raw_destination)
        code, name, country = lookup_plain_name(main_name, country_of_origin, subdivision_code)
        if code:
            return code, name, country

    # Fallback fuzzy match if everything else fails
    best_match = process.extractOne(raw_destination.title(), destination_locodes['Name'], scorer=fuzz.token_sort_ratio, processor=None)
    if best_match and best_match[1] >= 70:
        match_name = best_match[0]
        result = destination_locodes.loc[destination_locodes['Name'] == match_name, ['Country', 'LOCODE']]
        return result['Country'].iloc[0] + result['LOCODE'].iloc[0], match_name, \
            country_names.loc[country_names['Alpha 2'] == result['Country'].iloc[0], 'Name'].iloc[0]

    return 'Unknown', 'Unknown', 'Unknown'


def destination_to_coordinates(destination_locode):
    country_code = destination_locode[:2]
    port_code = destination_locode[2:]
    coordinates = destination_locodes.loc[((destination_locodes['Country'] == country_code) &
                                           (destination_locodes['LOCODE'] == port_code)), ['Coordinates']]
    if not coordinates.empty:
        coordinates = coordinates["Coordinates"].iloc[0]
        return coordinates
    else:
        return None
