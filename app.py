from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_restful import Api
from config import db, bcrypt
from models import User, Event, Registration
from datetime import datetime
import os
from flask_cors import CORS

app = Flask(__name__)
# CORS(app,
#      origins=[
#          "http://localhost:3000",
#          "https://tima-frontend-7hke.vercel.app"
#      ],
#      supports_credentials=True)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.secret_key = 'shhh-very-secret'

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
jwt = JWTManager(app)

@app.route('/')
def notice():
    return "Hey there, I just want to let you know that this URL is working 💋... Cristina ;)"

@app.post('/register')
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

    return {
        'id': user.id,
        'email': user.email
    }, 201

@app.post('/login')
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()

    if user and user.authenticate(password):
        token = create_access_token(identity=user.id)
        return {
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email
            }
        }, 200
    return {'error': 'Invalid credentials'}, 401

@app.get('/me')
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return {
        'id': user.id,
        'email': user.email
    }, 200

@app.route('/users', methods=['GET', 'POST'])
def handle_users():
    if request.method == 'GET':
        users = User.query.all()
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'email': user.email,
                'registrations': [r.id for r in user.registrations],
                'events': [e.id for e in user.events]
            })
        return jsonify(users_data), 200

    data = request.get_json()
    user = User(email=data.get('email'))
    user.password_hash = data.get('password')
    db.session.add(user)
    db.session.commit()
    return {
        'id': user.id,
        'email': user.email
    }, 201

@app.route('/users/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def handle_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'GET':
        return {
            'id': user.id,
            'email': user.email,
            'registrations': [r.id for r in user.registrations],
            'events': [e.id for e in user.events]
        }, 200
    if request.method == 'PATCH':
        data = request.get_json()
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.password_hash = data['password']
        db.session.commit()
        return {
            'id': user.id,
            'email': user.email
        }, 200
    db.session.delete(user)
    db.session.commit()
    return {}, 204

@app.route('/events', methods=['GET', 'POST'])
@jwt_required()
def handle_events():
    if request.method == 'GET':
        events = Event.query.all()
        return jsonify([
            {
                'id': e.id,
                'title': e.title,
                'description': e.description,
                'location': e.location,
                'category': e.category,
                'organizer_id': e.organizer_id
            } for e in events
        ]), 200

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
    return {
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'location': event.location,
        'category': event.category,
        'organizer_id': event.organizer_id
    }, 201

@app.route('/events/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def handle_event(id):
    event = Event.query.get_or_404(id)
    if request.method == 'GET':
        return {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'location': event.location,
            'category': event.category,
            'organizer_id': event.organizer_id
        }, 200
    if request.method == 'PATCH':
        data = request.get_json()
        for attr in ['title', 'description', 'location', 'category']:
            if attr in data:
                setattr(event, attr, data[attr])
        db.session.commit()
        return {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'location': event.location,
            'category': event.category,
            'organizer_id': event.organizer_id
        }, 200
    db.session.delete(event)
    db.session.commit()
    return {}, 204

@app.route('/registrations', methods=['GET', 'POST'])
@jwt_required()
def handle_registrations():
    if request.method == 'GET':
        registrations = Registration.query.all()
        return jsonify([
            {
                'id': r.id,
                'user_id': r.user_id,
                'event_id': r.event_id,
                'registration_status': r.registration_status
            } for r in registrations
        ]), 200

    data = request.get_json()
    user_id = get_jwt_identity()
    registration = Registration(
        user_id=user_id,
        event_id=data['event_id'],
        registration_status=data.get('registration_status', 'pending')
    )
    db.session.add(registration)
    db.session.commit()
    return {
        'id': registration.id,
        'user_id': registration.user_id,
        'event_id': registration.event_id,
        'registration_status': registration.registration_status
    }, 201

@app.route('/registrations/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def handle_registration(id):
    reg = Registration.query.get_or_404(id)
    if request.method == 'GET':
        return {
            'id': reg.id,
            'user_id': reg.user_id,
            'event_id': reg.event_id,
            'registration_status': reg.registration_status
        }, 200
    if request.method == 'PATCH':
        data = request.get_json()
        if 'registration_status' in data:
            reg.registration_status = data['registration_status']
        db.session.commit()
        return {
            'id': reg.id,
            'user_id': reg.user_id,
            'event_id': reg.event_id,
            'registration_status': reg.registration_status
        }, 200
    db.session.delete(reg)
    db.session.commit()
    return {}, 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
