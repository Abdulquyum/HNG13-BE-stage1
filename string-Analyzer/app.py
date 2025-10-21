#! /usr/bin/env python3

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest
import hashlib
from datetime import datetime, timezone

app = Flask(__name__)

# Store strings in memory (in production, use a database)
collected_strings = {}

@app.route('/strings', methods=['POST'], strict_slashes=False)
def analyze_strings():
    try:
        # Check if request has JSON data
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({"error": "Missing 'value' field in JSON"}), 400
            
        string = data.get('value', '')
        
        # Validate that value is a string
        if not isinstance(string, str):
            return jsonify({"error": f"Invalid data type for value (must be string)"}), 422
            
    except BadRequest as e:
        return jsonify({"error": "Invalid JSON"}), 400

    # Create hash and store the string
    hashed_string = hashlib.sha256(string.encode()).hexdigest()
    
    # Store string data with hash as key
    result = {
        "id": hashed_string,
        "value": string,
        "properties": {
            "length": len(string),
            "is_palindrome": string == string[::-1],
            "unique_characters": len(set(string)),
            "word_count": len(string.split()),
            "character_frequency": {
                char: string.count(char) for char in set(string)
            }
        },
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Store in memory
    collected_strings[hashed_string] = result
    collected_strings[string] = result  # Also store by original string for easy lookup

    return jsonify(result), 201

@app.route('/strings/<string:value>', methods=['GET'], strict_slashes=False)
def get_string(value):
    # Try to find by hash first, then by string value
    string_data = collected_strings.get(value)
    
    if not string_data:
        # Check if any stored string matches the value
        for data in collected_strings.values():
            if isinstance(data, dict) and data.get('value') == value:
                string_data = data
                break
    
    if string_data:
        return jsonify(string_data), 200
    else:
        return jsonify({"error": "String not found"}), 404

@app.route('/strings', methods=['GET'], strict_slashes=False)
def get_all_strings():
    # Return all unique strings (avoid duplicates from both key types)
    unique_strings = []
    seen_hashes = set()
    
    for data in collected_strings.values():
        if isinstance(data, dict) and data['id'] not in seen_hashes:
            unique_strings.append(data)
            seen_hashes.add(data['id'])
    
    return jsonify({
        "count": len(unique_strings),
        "strings": unique_strings
    }), 200

if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0', debug=True)
