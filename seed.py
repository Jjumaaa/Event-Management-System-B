from app import app
from config import db
from models import User, Event, Registration, UserRole
from faker import Faker
import random

fake = Faker()

def seed_users():
    users = []
    for i in range(20):
        email = fake.unique.email()
        password = "password123"
        role = random.choice([UserRole.admin, UserRole.attendee])
        profile_picture = fake.image_url()
        user = User(email=email, profile_picture=profile_picture, role=role)
        user.password_hash = password
        users.append(user)
        db.session.add(user)
    db.session.commit()
    return users

def seed_events(admin_users):
    events = []
    categories = ["Tech", "Music", "Health", "Education", "Sports"]
    for i in range(5):
        event = Event(
            title=fake.catch_phrase(),
            description=fake.text(),
            time=fake.date_time_this_year(),
            location=fake.city(),
            category=random.choice(categories),
            organizer_id=random.choice(admin_users).id
        )
        events.append(event)
        db.session.add(event)
    db.session.commit()
    return events

def seed_registrations(users, events):
    statuses = ["confirmed", "pending", "unsuccessful"]
    for _ in range(40): 
        user = random.choice(users)
        event = random.choice(events)

        existing = Registration.query.filter_by(user_id=user.id, event_id=event.id).first()
        if existing:
            continue

        registration = Registration(
            user_id=user.id,
            event_id=event.id,
            registration_status=random.choice(statuses)
        )
        db.session.add(registration)
    db.session.commit()

def run_seeds():
    with app.app_context():
        db.create_all()
        print(" Seeding database...")
        Registration.query.delete()
        Event.query.delete()
        User.query.delete()
        db.session.commit()

        users = seed_users()
        admin_users = [u for u in users if u.role == UserRole.admin]
        if len(admin_users) < 1:
            raise Exception("Need at least one admin user to seed events!")

        events = seed_events(admin_users)
        seed_registrations(users, events)

        print("Seeding complete!")

if __name__ == '__main__':
    run_seeds()
