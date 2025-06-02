import folium
from skyfield.api import EarthSatellite, load
from datetime import datetime, timedelta
import numpy as np
from datetime import timezone

# Helper: split the path when it jumps across the International Date Line
def split_at_dateline(coords):
    segments = []
    current_segment = [coords[0]]

    for prev, curr in zip(coords, coords[1:]):
        lon_diff = abs(curr[1] - prev[1])
        if lon_diff > 180:
            # Significant jump -> split here
            segments.append(current_segment)
            current_segment = [curr]
        else:
            current_segment.append(curr)

    segments.append(current_segment)
    return segments
    
# URL to fetch TLE data from a remote server. We need to do this 
# because the TLE parameters very quickly go out of date:
TLE_URL = 'https://celestrak.org/NORAD/elements/stations.txt'

# Load TLE data (once at start)
print("Fetching TLE data for ISS...")
satellites = load.tle_file(TLE_URL)
by_name = {sat.name: sat for sat in satellites}
sat = by_name['ISS (ZARYA)']

ts = load.timescale()

# --- Generate time points for the last two hours ---
now = datetime.now(timezone.utc)
times = [ts.utc(now - timedelta(minutes=i)) for i in reversed(range(120))]

# --- Calculate positions ---
positions = [sat.at(t).subpoint() for t in times]
lat_lon = [(p.latitude.degrees, p.longitude.degrees) for p in positions]

# --- Create Folium map centered near the middle of the path ---
avg_lat = sum(lat for lat, _ in lat_lon) / len(lat_lon)
avg_lon = sum(lon for _, lon in lat_lon) / len(lat_lon)
map = folium.Map(location=[avg_lat, avg_lon], zoom_start=2, tiles="OpenStreetMap")

# Add individual points with timestamps as tooltips
for t, (lat, lon) in zip(times, lat_lon):
    timestamp_str = t.utc_iso().split("T")[1][:8]  # Just show HH:MM:SS
    folium.CircleMarker(
        location=(lat, lon),
        radius=3,
        color="red",
        fill=True,
        fill_opacity=0.8,   
        tooltip=f"UTC {timestamp_str}"
    ).add_to(map)


# Split path to avoid drawing lines across the globe
segments = split_at_dateline(lat_lon)

# Add each segment as its own PolyLine
for segment in segments:
    folium.PolyLine(segment, color="red", weight=2.5, opacity=0.8).add_to(map)

# --- Mark current position ---
folium.Marker(lat_lon[-1], popup="Current ISS Position", icon=folium.Icon(color="blue")).add_to(map)

# --- Save or display ---
map.save("iss_last_hour.html")
print("Map saved to iss_last_hour.html")
