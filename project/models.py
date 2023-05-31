from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    role = db.Column(db.String(50))

    # Define Roles
    ROLES = [
        ('admin', 'Admin'),
        ('restaurant_owner', 'Restaurant Owner'),
        ('public_user', 'Public User')
    ]

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'         : self.id,
           'email'      : self.email,
           'password'   : self.password,
           'name'       : self.name,
           'role'       : self.role
       }

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.    relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
       }

 
class MenuItem(db.Model):
    name = db.Column(db.String(80), nullable = False)
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(250))
    price = db.Column(db.String(8))
    course = db.Column(db.String(250))
    restaurant_id = db.Column(db.Integer,db.ForeignKey('restaurant.id'))
    restaurant = db.    relationship(Restaurant)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'       : self.name,
           'description' : self.description,
           'id'         : self.id,
           'price'      : self.price,
           'course'     : self.course,
       }
    
class Rating(db.Model):
    rating_id = db.Column(db.Integer, primary_key = True)
    post_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, nullable=False, primary_key=True)    
    rating = db.Column(db.Integer)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'rate_id'      : self.rating_id,
           'post_id'      : self.post_id,
           'user_id'      : self.user_id,
           'rating'       : self.rating,
       }
