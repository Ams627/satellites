from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        try:
            a = int(params.get('a', [0])[0])
            b = int(params.get('b', [0])[0])
            result = a + b
            response = f"Result: {a} + {b} = {result}"
        except:
            response = "Please provide integers ?a=3&b=4"

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(response.encode())

server = HTTPServer(('', 8000), Handler)
print("Serving on port 8000...")
server.serve_forever()
