from flask import Flask, request, jsonify
import requests
import os
import time

app = Flask(__name__)

GOOGLE_API_KEY = "AIzaSyAQybAfL2P_hn7ggfheV5_ljEWgWbnmEz8"

# Caché en memoria
distance_cache = {}
CACHE_DURATION = 300  # segundos

@app.route('/getSettings', methods=['GET'])
def get_settings():
    return jsonify({
        "idioma": "es",
        "rechazar_baja_calificacion": True,
        "min_calificacion": 4.5,
        "zona_segura": ["Bogotá", "Usaquén", "Chapinero"]
    })

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Servidor activo con Google API y caché", "version": "2.1"})

@app.route('/distance', methods=['GET'])
def distance():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    if not origin or not destination:
        return jsonify({"error": "Parámetros 'origin' y 'destination' requeridos"}), 400

    cache_key = (origin, destination)
    if cache_key in distance_cache:
        timestamp, data = distance_cache[cache_key]
        if time.time() - timestamp < CACHE_DURATION:
            return jsonify({"cached": True, "data": data})

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destination,
        "mode": "driving",
        "language": "es",
        "region": "co",
        "key": GOOGLE_API_KEY
    }

    r = requests.get(url, params=params)
    data = r.json()
    distance_cache[cache_key] = (time.time(), data)

    return jsonify({"cached": False, "data": data})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
