from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, unquote
from pathlib import Path
import mimetypes
import json
import socket
from skyfield.api import load, wgs84

# Load satellite data (ISS)
stations_url = 'http://celestrak.org/NORAD/elements/stations.txt'
satellites = load.tle_file(stations_url)
sat_by_name = {sat.name: sat for sat in satellites}
iss = sat_by_name.get('ISS (ZARYA)', None)
ts = load.timescale()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path.lstrip("/")) or "index.html"

        if parsed_path.path == "/location":
            if not iss:
                self.send_error(500, "ISS TLE not loaded")
                return

            t = ts.now()
            geocentric = iss.at(t)
            subpoint = wgs84.subpoint(geocentric)
            data = {
                "lat": subpoint.latitude.degrees,
                "lon": subpoint.longitude.degrees
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            return

        # Try to serve static file
        file_path = Path(path)
        if file_path.exists() and file_path.is_file():
            self.send_response(200)
            mime_type, _ = mimetypes.guess_type(file_path)
            self.send_header("Content-Type", mime_type or "application/octet-stream")
            self.end_headers()
            self.wfile.write(file_path.read_bytes())
            return

        self.send_error(404, f"File not found: {path}")

# Determine LAN IP
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "localhost"
    return ip

if __name__ == '__main__':
    host = ''
    port = 8000
    print("Loading TLE data for ISS...")
    server = HTTPServer((host, port), Handler)
    ip = get_local_ip()
    print(f"Server running at:")
    print(f"  Local:   http://localhost:{port}")
    print(f"  Network: http://{ip}:{port}")
    print(f"  ISS data: http://{ip}:{port}/location")
    print(f"  HTML page: put your index.html in this folder")
    server.serve_forever()
