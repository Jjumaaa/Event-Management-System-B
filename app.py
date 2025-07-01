from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_restful import Api
from config import db, bcrypt
from models import User, Event, Registration
from datetime import datetime
import os

app = Flask(__name__)

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

@app.post('/auth/register')
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return {'error': 'Email and password are required'}, 400

    if User.query.filter_by(email=email).first():
        return {'error': 'Email already registered'}, 400

    user = User(email=email)
    user.password_hash = password
    db.session.add(user)
    db.session.commit()

    return user.to_dict(), 201

@app.post('/auth/login')
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()

    if user and user.authenticate(password):
        token = create_access_token(identity=user.id)
        return {'token': token, 'user': user.to_dict()}, 200
    return {'error': 'Invalid credentials'}, 401

@app.get('/auth/me')
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return user.to_dict(), 200

@app.route('/users', methods=['GET', 'POST'])
def handle_users():
    if request.method == 'GET':
        return jsonify([u.to_dict() for u in User.query.all()])
    data = request.get_json()
    user = User(email=data.get('email'))
    user.password_hash = data.get('password')
    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 201

@app.route('/users/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def handle_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'GET':
        return user.to_dict(), 200
    if request.method == 'PATCH':
        data = request.get_json()
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.password_hash = data['password']
        db.session.commit()
        return user.to_dict(), 200
    db.session.delete(user)
    db.session.commit()
    return {}, 204

@app.route('/events', methods=['GET', 'POST'])
@jwt_required()
def handle_events():
    if request.method == 'GET':
        return jsonify([e.to_dict() for e in Event.query.all()])
    data = request.get_json()
    user_id = get_jwt_identity()
    event = Event(
        title=data['title'],
        description=data.get('description'),
        location=data['location'],
        category=data.get('category'),
        organizer_id=user_id
    )
    db.session.add(event)
    db.session.commit()
    return event.to_dict(), 201

@app.route('/events/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def handle_event(id):
    event = Event.query.get_or_404(id)
    if request.method == 'GET':
        return event.to_dict(), 200
    if request.method == 'PATCH':
        data = request.get_json()
        for attr in ['title', 'description', 'location', 'category']:
            if attr in data:
                setattr(event, attr, data[attr])
        db.session.commit()
        return event.to_dict(), 200
    db.session.delete(event)
    db.session.commit()
    return {}, 204

@app.route('/registrations', methods=['GET', 'POST'])
@jwt_required()
def handle_registrations():
    if request.method == 'GET':
        return jsonify([r.to_dict() for r in Registration.query.all()])
    data = request.get_json()
    user_id = get_jwt_identity()
    registration = Registration(
        user_id=user_id,
        event_id=data['event_id'],
        registration_status=data.get('registration_status', 'pending')
    )
    db.session.add(registration)
    db.session.commit()
    return registration.to_dict(), 201

@app.route('/registrations/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def handle_registration(id):
    reg = Registration.query.get_or_404(id)
    if request.method == 'GET':
        return reg.to_dict(), 200
    if request.method == 'PATCH':
        data = request.get_json()
        if 'registration_status' in data:
            reg.registration_status = data['registration_status']
        db.session.commit()
        return reg.to_dict(), 200
    db.session.delete(reg)
    db.session.commit()
    return {}, 204

if __name__ == '__main__':
    app.run(port=5555, debug=True)