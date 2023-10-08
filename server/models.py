from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates


from config import db, bcrypt

import pdb


class User(db.Model):
    __tablename__ = 'users'

    # pdb.set_trace()

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship('Recipe', backref='user', lazy=True)

    # def __init__(self, username, password, image_url=None, bio=None):
    #     if not username:
    #         raise ValueError('Username is required.')
        
    #     if not password:
    #         return ValueError('Password is required.')
        
    #     self.username = username
    #     self.password = password
    #     self.image_url = image_url
    #     self.bio = bio

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'image_url': self.image_url,
            'bio': self.bio,
        }

    @validates('_password_hash')
    def validate_password(self, key, value):
        if not value:
            raise ValueError('Password is required.')
        return value

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hash cannot be accessed directly.')

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password.encode('utf-8')).decode('utf-8')
    
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    def __repr__(self):
        return f"User({self.id}, {self.username}, {self._password_hash}, {self.image_url}, {self.bio})"

class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'instructions': self.instructions,
            'minutes_to_complete': self.minutes_to_complete,
        }
    
    @validates('title')
    def validate_title(self, key, value):
        if value == None:
            raise ValueError('Title is required.')
        return value
    
    @validates('instructions')
    def validate_instructions(self, key, value):
        if len(value) < 50:
            raise ValueError('Instructions must be at least 50 characters long.')
        return value
    
    def __repr__(self) -> str:
        return f'Recipe({self.id}, {self.title}, {self.instructions}, {self.minutes_to_complete})'
        