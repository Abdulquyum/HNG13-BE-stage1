#! /usr/bin/env python3

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest
import hashlib
from datetime import datetime, timezone
import re

app = Flask(__name__)

collected_strings = {}

@app.route('/strings', methods=['POST'], strict_slashes=False)
def analyze_strings():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid request body or missing 'value' field"}), 400
        
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({"error": "Invalid request body or missing 'value' field"}), 400
            
        string = data.get('value', '')
        
        if not isinstance(string, str):
            return jsonify({"error": f"Invalid data type for value (must be string)"}), 422

        if string in collected_strings:
            return jsonify({"error": "String already exists in the system"}), 409
            
    except BadRequest as e:
        return jsonify({"error": "Invalid JSON"}), 400

    hashed_string = hashlib.sha256(string.encode()).hexdigest()
    
    result = {
        "id": hashed_string,
        "value": string,
        "properties": {
            "length": len(string),
            "is_palindrome": string == string[::-1],
            "unique_characters": len(set(string)),
            "word_count": len(string.split()),
            "sha256_hash": hashed_string,
            "character_frequency_map": {
                char: string.count(char) for char in set(string)
            }
        },
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    collected_strings[string] = result

    return jsonify(result), 201

@app.route('/strings/<string:value>', methods=['GET'], strict_slashes=False)
def get_string(value):
    string_data = collected_strings.get(value)

    if not string_data:
        return jsonify({"error": "String does not exist in the system"}), 404

    else:
        return jsonify(string_data), 200


@app.route('/strings', methods=['GET'], strict_slashes=False)
def filtered_strings():
    try:
        is_palindrome = request.args.get('is_palindrome', type=str)
        if is_palindrome is not None:
            is_palindrome = is_palindrome.lower()
            if is_palindrome == 'true':
                is_palindrome = True
            elif is_palindrome == 'false':
                is_palindrome = False
    
        min_length = request.args.get('min_length', type=int)
        max_length = request.args.get('max_length', type=int)
        word_count = request.args.get('word_count', type=int)
        contains_character = request.args.get('contains_character', type=str)
        
        if contains_character and len(contains_character) != 1:
            return jsonify({"error": "contains_character must be a single character"}), 400
            
    except ValueError:
        return jsonify({"error": "Invalid query parameter type"}), 400

    filtered = []
    for data in collected_strings.values():
        if not isinstance(data, dict):
            continue
        
        properties = data.get('properties', {})
        value_str = data.get('value', '')
        
        if is_palindrome is not None and properties.get('is_palindrome') != is_palindrome:
            continue
        if min_length is not None and properties.get('length', 0) < min_length:
            continue
        if max_length is not None and properties.get('length', 0) > max_length:
            continue
        if word_count is not None and properties.get('word_count', 0) != word_count:
            continue
        if contains_character is not None and contains_character not in value_str:
            continue
        
        filtered.append(data)

    return jsonify({
        "count": len(filtered),
        "strings": filtered
    }), 200

@app.route('/strings/filter-by-natural-language', methods=['GET'], strict_slashes=False)
def filter_by_natural_language():
    query = request.args.get('query', '').strip().lower()
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    parsed_filters = parse_natural_language(query)
    
    if parsed_filters is None:
        return jsonify({"error": "Unable to parse natural language query"}), 400
    
    conflict_error = check_filter_conflicts(parsed_filters)
    if conflict_error:
        return jsonify({
            "error": "Query parsed but resulted in conflicting filters",
            "details": conflict_error
        }), 422
    
    filtered = []
    for data in collected_strings.values():
        if not isinstance(data, dict):
            continue
        
        properties = data.get('properties', {})
        value_str = data.get('value', '')
        
        if 'is_palindrome' in parsed_filters and properties.get('is_palindrome') != parsed_filters['is_palindrome']:
            continue
        if 'min_length' in parsed_filters and properties.get('length', 0) <= parsed_filters['min_length']:
            continue
        if 'max_length' in parsed_filters and properties.get('length', 0) >= parsed_filters['max_length']:
            continue
        if 'word_count' in parsed_filters and properties.get('word_count', 0) != parsed_filters['word_count']:
            continue
        if 'contains_character' in parsed_filters and parsed_filters['contains_character'] not in value_str:
            continue
        
        filtered.append(data)
    
    return jsonify({
        "data": filtered,
        "count": len(filtered),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed_filters
        }
    }), 200

def parse_natural_language(query):
    filters = {}
    
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['palindrome', 'palindromic']):
        filters['is_palindrome'] = True

    if 'single word' in query_lower or 'one word' in query_lower:
        filters['word_count'] = 1
    
    length_match = re.search(r'longer than\s+(\d+)\s+characters?', query_lower)
    if length_match:
        filters['min_length'] = int(length_match.group(1)) + 1
    
    length_match = re.search(r'shorter than\s+(\d+)\s+characters?', query_lower)
    if length_match:
        filters['max_length'] = int(length_match.group(1)) - 1
    
    length_match = re.search(r'length\s+(\d+)\s+characters?', query_lower)
    if length_match:
        filters['min_length'] = int(length_match.group(1))
        filters['max_length'] = int(length_match.group(1))

    if 'first vowel' in query_lower:
        filters['contains_character'] = 'a'

    if 'letter z' in query_lower:
        filters['contains_character'] = 'z'

    if not filters:
        return None
    
    return filters

def check_filter_conflicts(filters):
    if 'min_length' in filters and 'max_length' in filters:
        if filters['min_length'] > filters['max_length']:
            return f"min_length ({filters['min_length']}) cannot be greater than max_length ({filters['max_length']})"
    
    if 'word_count' in filters and filters['word_count'] == 1 and 'contains_character' in filters:
        if filters['contains_character'] == ' ':
            return "single word strings cannot contain spaces"
    
    return None

@app.route('/strings/<string:value>', methods=['DELETE'], strict_slashes=False)
def delete_string(value):
    if value not in collected_strings:
        return jsonify({"error": "String does not exist in the system"}), 404
    
    for value in collected_strings:
        if isinstance(collected_strings[value], dict) and collected_strings[value].get('value') == value:
            del collected_strings[value]
            return jsonify({}), 204

if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0', debug=True)
