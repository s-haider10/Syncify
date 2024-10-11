#!/usr/bin/env python3
# __init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import app

# Initialize database and login manager 
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # improves performance
    app.config['SESSION_COOKIE_SECURE'] = False

    # Spotify config
    app.config['SPOTIPY_CLIENT_ID'] = '4c450f43f6204ac89446ff6051c166da'
    app.config['SPOTIPY_CLIENT_SECRET'] = '2f01490445f943fcbcbb12076c69e0c5'
    app.config['SPOTIPY_REDIRECT_URI'] = 'http://127.0.0.1:5000/spotify_callback'
    app.config['SCOPE'] = 'playlist-modify-public playlist-modify-private'

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Load and normalize data1
    data = pd.read_csv('spotify_data/train.csv')
    data = data.sample(frac=0.05, random_state=1)
    norm_data = normalize_data(data)
    cosine_similarity_df = pd.DataFrame(cosine_similarity(norm_data), index=data.index, columns=data.index)

    # Load and normalize data2
    # data2 = pd.read_csv('cosine_similarity_svd.csv')
    # data2 = data2.sample(frac=0.05, random_state=1)
    # norm_data2 = normalize_data(data2)
    # cosine_similarity_df2 = pd.DataFrame(cosine_similarity(norm_data2), index=data2.index, columns=data2.index)

    # Store data in the app context (like a global variable for the entire app)
    app.data = data
    app.cosine_similarity_df = cosine_similarity_df

    # app.data2 = data2
    # app.cosine_similarity_df2 = cosine_similarity_df2

    from .auth import auth as auth_blueprint
    from .views import views as views_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(views_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    return app

def normalize_data(df):
    df_numeric = df.select_dtypes(include=[np.number])
    return (df_numeric - df_numeric.min()) / (df_numeric.max() - df_numeric.min())
