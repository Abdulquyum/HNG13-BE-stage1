#!/usr/bin/env python3

# Test array to collect strings
value = input("enter your value? ")
Collected_Strings = ['name', 'quyum', 'app', 'me']
for x in Collected_Strings:
    if x == value:
        print(value)


# Get All Strings
@app.route('/strings', methods=['GET'], strict_slashes=False)
def get_all_strings():
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
