from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt
from datetime import datetime
import enum
from sqlalchemy import Enum

class UserRole(enum.Enum):
    admin = 'admin'
    attendee = 'attendee'


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    # serialize_rules = ('-terms.user', '-grades.user',)

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    _password_hash = db.Column(db.String, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    
    role = db.Column(Enum(UserRole), nullable=False, nullable=False, default=UserRole.attendee)


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

    def __repr__(self):
        return f"<User {self.username} (id={self.id})>"
    

class Event(db.Model, SerializerMixin):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullanle=False )
    description = db.Column(db.String, default=datetime.utcnow)
    time = db.Column(db.Integer, default=datetime.utcnow, onupdate=datetime.utcnow)
    loctaion = db.Column(db.String,nullable=False)
    category = db.Column(db.String)
    organizer_id = db.Column(db.Integer,ForeignKey=True)




class Registration(db.Model, SerializerMixin):
    __tablename__ = 'registrations'

    id = db.Column(db.Integer, primary_key=True)
    user_id =db.Column(db.Integer, ForeignKey=True)
    event_id=db.Column(db.Integer, ForeignKey=True)
    registration_status = db.Column(
        Enum("confirmed", "pending", "unsuccessful", name="status_enum"),
        nullable=False,
        default="pending"
    )

    

  
