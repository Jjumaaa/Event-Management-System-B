from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt
from datetime import datetime
import enum
from sqlalchemy import Enum, ForeignKey

class UserRole(enum.Enum):
    admin = 'admin'
    attendee = 'attendee'


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    serialize_rules = ('-registrations.user', '-events.organizer',)

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    _password_hash = db.Column(db.String, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    role = db.Column(Enum(UserRole), nullable=False, default=UserRole.attendee)

    registrations = relationship('Registration', backref='user', cascade='all, delete-orphan')
    events = relationship('Event', backref='organizer', cascade='all, delete-orphan', foreign_keys='Event.organizer_id')

    @validates('email')
    def validate_email(self, key, email):
        if email and ('@' not in email or '.' not in email):
            raise ValueError("Please provide a valid email address.")
        return email

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes are write-only.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password.encode()).decode()

    def authenticate(self, password):
        return self._password_hash and bcrypt.check_password_hash(self._password_hash, password.encode())

    def to_dict(self):
        data = super().to_dict()
        data['role'] = self.role.value if self.role else None
        return data

    def __repr__(self):
        return f"<User {self.email} (id={self.id})>"


class Event(db.Model, SerializerMixin):
    __tablename__ = 'events'
    serialize_rules = ('-registrations.event', '-organizer.events',)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String, nullable=True)
    time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    location = db.Column(db.String, nullable=False)
    category = db.Column(db.String)
    organizer_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)

    registrations = relationship('Registration', backref='event', cascade='all, delete-orphan')


class Registration(db.Model, SerializerMixin):
    __tablename__ = 'registrations'
    serialize_rules = ('-user.registrations', '-event.registrations',)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, ForeignKey('events.id'), nullable=False)
    registration_status = db.Column(
        Enum("confirmed", "pending", "unsuccessful", name="status_enum"),
        nullable=False,
        default="pending"
    )

    def to_dict(self):
        data = super().to_dict()
        data['registration_status'] = self.registration_status
        return data
