from flask import jsonify

def getFetch():
    data = {
        'message': 'Hello from the /fetch endpoint!',
        'data': [1, 2, 3, 4, 5]
    }
    return jsonify(data)