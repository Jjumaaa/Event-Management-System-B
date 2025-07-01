from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_restful import Api
from config import db, bcrypt
from models import User, Event, Registration
from datetime import datetime
import os
# from flask_cors import CORS

app = Flask(__name__)
# CORS(app,
#      origins=[
#          "http://localhost:3000",
#          "https://tima-frontend-7hke.vercel.app"
#      ],
#      supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tima.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.secret_key = 'shhh-very-secret'

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
jwt = JWTManager(app)

@app.route('/')
def notice():
    return "Hey there, I just want to let you know that this URL is working 💋... Cristina;)"

if __name__ == '__main__':
    app.run(port=5555, debug=True)

