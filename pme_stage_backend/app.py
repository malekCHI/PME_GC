from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
import os
from flask import Flask,jsonify
from db import db
import time 
from flask_restful import Api
from Profile.views import profiles
from Entreprise.views import entreprise
from Previlege.views import previlege
from User.views import user
from mail_utils import mail
from flask_jwt_extended import (
    JWTManager
)
load_dotenv()
app = Flask(__name__)

app.config["CORS_HEADERS"] = "Content-Type"
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'malek.chiha@esprit.tn'
app.config['MAIL_PASSWORD'] = 'yooysitbqfnuqlyh'
app.config['MAIL_USE_TLS'] = True   # Set to True for TLS
app.config['MAIL_USE_SSL'] = False  # Set to False for SSL
app.config['MAIL_DEFAULT_SENDER'] = 'malek.chiha@esprit.tn' 
mail.init_app(app)






app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True


api = Api(app)
db.init_app(app)
SECRET_KEY = os.getenv("SECRET_KEY")
app.config['SECRET_KEY'] = SECRET_KEY
jwt = JWTManager(app)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'






app.register_blueprint(profiles)
app.register_blueprint(previlege)
app.register_blueprint(entreprise)
app.register_blueprint(user)

with app.app_context():
    db.create_all()
# @app.before_first_request
# def create_tables():
#     with app.app_context():
#         db.create_all()


if __name__ == '__main__':
    app.run(debug=True, port=5000)