import csv
import numpy as np
from skyfield.api import load, EarthSatellite
from datetime import timedelta


ts = load.timescale()

with open('satellites.csv', newline='', encoding='utf-8') as f:
    data = list(csv.DictReader(f))

sats = [EarthSatellite.from_omm(ts, row) for row in data]
sat_dict = {sat.name: sat for sat in sats}


def get_satellite_names(csv_path='satellites.csv'):
    names = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            names.append(row['OBJECT_NAME'])  # or 'NORAD_CAT_ID', etc.
    return names
    
def get_satellite_subpoint(name):
    print(f"name is {name}")
    t = ts.now()
    sat = sat_dict.get(name)
    if sat is None:
        raise ValueError(f"Satellite {name} not found")
    subpoint = sat.at(t).subpoint()
    return {
        'name': name,
        'latitude': subpoint.latitude.degrees,
        'longitude': subpoint.longitude.degrees,
        'altitude_km': subpoint.elevation.km
    }
        
def get_orbit_path(name, minutes_before=90, minutes_after=90, step_seconds=30):
    if name not in sat_dict:
        raise ValueError(f"Satellite '{name}' not found")

    sat = sat_dict[name]
    now = ts.now()
    
    # Convert to datetime for offsetting
    now_dt = now.utc_datetime()
    start = now_dt - timedelta(minutes=minutes_before)
    stop = now_dt + timedelta(minutes=minutes_after)
    steps = int((minutes_before + minutes_after) * 60 / step_seconds)

    # Convert back to Skyfield Time array
    times = ts.utc(start.year, start.month, start.day,
                   start.hour, start.minute,
                   [start.second + i * step_seconds for i in range(steps)])

    subpoints = sat.at(times).subpoint()
    lats = subpoints.latitude.degrees
    lons = subpoints.longitude.degrees

    # Unwrap longitude to prevent flyback across ±180°
    unwrapped_lons = np.unwrap(np.radians(lons))
    unwrapped_lons = np.degrees(unwrapped_lons)

    path = [{'lat': lat, 'lon': lon} for lat, lon in zip(lats, unwrapped_lons)]
    return path


if __name__ == "__main__":
    from pprint import pprint

    name = "ISS (ZARYA)"  # or any satellite in your CSV
    print(f"Computing orbit path for: {name}")
    
    try:
        path = get_orbit_path(name)
        pprint(path[:5])  # Show just the first few points
        print(f"... total points: {len(path)}")
    except Exception as e:
        print("Error:", e)