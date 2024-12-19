from flask import Flask, jsonify
from flask_cors import CORS
import os
import json

app = Flask(__name__)

# Flask-CORS'u etkinleştir
CORS(app)

# JSON dosyasının yolunu belirtiyoruz
JSON_FILE_PATH = os.path.join(os.getcwd(), "response.json")


@app.route('/places', methods=['GET'])
def get_all_locations():
    try:
        # JSON dosyasını oku
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": "JSON file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON file"}), 500


if __name__ == '__main__':
    app.run(debug=True)
