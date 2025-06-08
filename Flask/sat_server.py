from flask import Flask, jsonify, url_for, request, send_from_directory
from sat_data import get_satellite_names, get_satellite_subpoint, get_orbit_path

app = Flask(__name__)

@app.route('/')
def index():
    print("SENDING index.html")
    return send_from_directory('static', 'index.html')

@app.route('/satellites')
def satellites():
    names = get_satellite_names()
    return jsonify(names)

@app.route("/subpoint")
def subpoint():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Missing ?name= parameter'}), 400
    try:
        return jsonify(get_satellite_subpoint(name))
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@app.route('/orbit')
def orbit():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Missing ?name= parameter'}), 400
    try:
        path = get_orbit_path(name)
        return jsonify(path)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@app.errorhandler(404)
def not_found(e):
    routes = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes[rule.rule] = rule.endpoint
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": routes
    }), 404
    
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)    

if __name__ == "__main__":
    app.run(debug = True)
