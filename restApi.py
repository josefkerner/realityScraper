# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api
from flask_cors import CORS
from restApiController import RestApiController
import json
import sys
parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    pass

app = Flask(__name__)
#CORS(app)
app.config['JSON_AS_ASCII'] = False

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

class RealityWebService:
    def __init__(self):
        self.app = app

    @staticmethod
    def build_cors_prelight_response():
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        response.headers.add("Access-Control-Allow-Headers", "content-type")
        response.headers.add("Access-Control-Allow-Methods", "POST, GET,OPTIONS")

        return response

    @staticmethod
    def corsify_actual_response(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        response.headers.add("Access-Control-Allow-Headers", "content-type")
        response.headers.add("Access-Control-Allow-Methods", "POST, GET,OPTIONS")
        return response


    def run(self):
        JSON_AS_ASCII = False
        self.app.run(debug=True, host='127.0.0.1', port=5177)

    @staticmethod
    @app.route('/', methods=['GET'])
    def index():
        return 'Hello, this is reality REST API'

    @staticmethod
    @app.route('/api/flats/<level_from>/<level_to>', methods=['GET', 'OPTIONS'])
    def get_flats(level_from,level_to):
        controller = RestApiController()
        flats = controller.get_flats(level_from,level_to)
        flats = json.dumps(flats,ensure_ascii=False)

        print(flats)
        return jsonify({"flats": flats})

    @staticmethod
    @app.route('/api/set_interest_level', methods=['POST', 'OPTIONS'])
    def set_interest_level():
        if request.method == "OPTIONS":  # CORS preflight
            return RealityWebService.build_cors_prelight_response()

        try:
            req= request.form
            id = req['id']
            interest_level = req['interest_level']
            controller = RestApiController()
            print(request.json)
            controller.set_interest_level(id, interest_level)
            error = {"status": "OK"}
            return jsonify(error)
        except Exception as e:
            error = {"error":str(e),"request":request.form}
            return jsonify(error)


if __name__ == '__main__':
    RealityWebService().run()