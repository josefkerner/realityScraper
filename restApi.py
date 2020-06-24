from flask import Flask, jsonify, request, make_response
from restApiController import RestApiController
import json
import sys
parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    pass
app = Flask(__name__)

class RealityWebService:
    def __init__(self):
        self.app = app


    def run(self):
        self.app.run(debug=True, host='127.0.0.1', port=5177)

    @staticmethod
    @app.route('/', methods=['GET'])
    def index():
        return 'Hello, this is reality REST API'

    @staticmethod
    @app.route('/api/flats', methods=['GET', 'OPTIONS'])
    def get_flats():
        controller = RestApiController()
        flats = controller.get_flats()
        return json.dumps(flats)

    @staticmethod
    @app.route('/api/set_interest_level', methods=['POST', 'OPTIONS'])
    def set_interest_level():
        id = request.json['id']
        interest_level = request.json['interest_level']


if __name__ == '__main__':
    RealityWebService().run()