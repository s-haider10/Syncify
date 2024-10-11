#!/usr/bin/env python3
# models.py

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(120))
    ratings = db.relationship('Rating', back_populates='user')
    # playlists = db.relationship('Playlist', backref='user', lazy=True)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False) 
    song_index = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='ratings')

# class Song(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(150), nullable=False)
#     artist = db.Column(db.String(150), nullable=False)
#     spotify_id = db.Column(db.String(150), unique=True, nullable=False) 
#     playlists = db.relationship('Playlist', back_populates='song')

# class Playlist(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
#     added_on = db.Column(db.DateTime, default=func.now())

#     user = db.relationship('User', back_populates='playlists')
#     song = db.relationship('Song', back_populates='playlists')
