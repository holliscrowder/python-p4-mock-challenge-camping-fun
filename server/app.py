#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

class Campers(Resource):
    def get(self):
        return make_response(jsonify([camper.to_dict() for camper in Camper.query.all()]), 200)

    def post(self):
        camper_data = request.get_json()
        try:
            new_camper = Camper(
                name = camper_data.get("name"),
                age = camper_data.get("age")
            )
            db.session.add(new_camper)
            db.session.commit()

            return make_response(
                jsonify((new_camper).to_dict()), 201
            )
        except ValueError as error:
            return make_response({"errors": ["validation errors"]}, 400)


class CampersByID(Resource):
    def get(self, id):
        camper = db.session.get(Camper, id)
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        return make_response(jsonify(camper.to_dict(rules=("signups",))), 200)
    
    def patch(self, id):
        camper = db.session.get(Camper, id)
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        camper_data = request.get_json()
        try:
            for attr in camper_data:
                setattr(camper, attr, camper_data.get(attr))

            db.session.add(camper)
            db.session.commit()

            return make_response(jsonify(camper.to_dict()), 202)
        except ValueError as error:
            return make_response({"errors": ["validation errors"]}, 400)
        
class Activities(Resource):
    def get(self):
        return make_response(jsonify([activity.to_dict() for activity in Activity.query.all()]), 200)

class ActivitiesByID(Resource):
    def delete(self, id):
        activity = db.session.get(Activity, id)

        if not activity:
            return make_response({"error": "Activity not found"}, 404)
        db.session.delete(activity)
        db.session.commit()

        return make_response("", 204)

class Signups(Resource):
    def post(self):
        signup_data = request.get_json()
        try:
            new_signup = Signup(
                camper_id = signup_data.get("camper_id"),
                activity_id = signup_data.get("activity_id"),
                time = signup_data.get("time")
            )
            db.session.add(new_signup)
            db.session.commit()

            return make_response(
                jsonify(new_signup.to_dict(rules=("camper",))), 201
            )
        except ValueError as error:
            return make_response({"errors": ["validation errors"]}, 400)
    
api.add_resource(Campers, "/campers")
api.add_resource(CampersByID, "/campers/<int:id>")
api.add_resource(Activities, "/activities")
api.add_resource(ActivitiesByID, "/activities/<int:id>")
api.add_resource(Signups, "/signups")

@app.route('/')
def home():
    return ''

if __name__ == '__main__':
    app.run(port=5555, debug=True)
