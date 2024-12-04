# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    saved_places = db.relationship('SavedPlace', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    reviews = db.relationship('Review', backref='place', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class SavedPlace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)
    place = db.relationship('Place', backref='saved_by', lazy=True)


class SavedRestaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)  # Измените на nullable=True
    image_url = db.Column(db.String(255), nullable=True)
    saved_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('saved_restaurants', lazy='dynamic'))


class SavedNatureOfPskov(db.Model):
    __tablename__ = 'saved_nature_of_pskov'
    id = db.Column(db.Integer, primary_key=True)
    nature_name = db.Column(db.String(255), nullable=False, unique=True)
    nature_description = db.Column(db.Text, nullable=False, unique=True)


class FinalRouteInformation(db.Model):
    __tablename__ = 'final_route_information'
    id = db.Column(db.Integer, primary_key=True)
    info = db.Column(db.Text, nullable=False, unique=True)


class SavedHotels(db.Model):
    __tablename__ = 'saved_hotels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Text(), nullable=True)
    price = db.Column(db.String(255), nullable=False)  #

class BestAndWorst(db.Model):
    __tablename__ = 'best_and_worst'
    id = db.Column(db.Integer, primary_key=True)
    best = db.Column(db.String(255), nullable=False)
    worst = db.Column(db.String(255), nullable=False)