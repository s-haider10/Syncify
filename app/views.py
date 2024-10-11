# views.py 

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user
# from .models import Rating, User, Playlist, Song
from . import db
from main import get_recommendations
from lyrics_added import get_recommendations
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from sqlalchemy import inspect
import os

views = Blueprint('views', __name__)

# ----------------------- SPOTIFY PROCEDURE -------------------------

@views.route('/spotify_login')
@login_required
def spotify_login():
    # Initialize Spotify Authorization
    sp_oauth = SpotifyOAuth(client_id=current_app.config['SPOTIPY_CLIENT_ID'],
                            client_secret=current_app.config['SPOTIPY_CLIENT_SECRET'],
                            redirect_uri=current_app.config['SPOTIPY_REDIRECT_URI'],
                            scope=current_app.config['SCOPE'])
    
    # Get authorization URL
    auth_url = sp_oauth.get_authorize_url()
    flash('Spotify Log in Successful')
    print('SpotifyLogin Done, Auth URL:', auth_url)
    return redirect(auth_url)

# Spotify API redirect route
@views.route('/spotify_callback')
def spotify_callback():
    # Verify user
    sp_oauth = SpotifyOAuth(client_id=current_app.config['SPOTIPY_CLIENT_ID'],
                            client_secret=current_app.config['SPOTIPY_CLIENT_SECRET'],
                            redirect_uri=current_app.config['SPOTIPY_REDIRECT_URI'],
                            scope=current_app.config['SCOPE'])
    session.clear()
    # Get authorization code from request
    code = request.args.get('code')
    if not code:
        print('Authorization code missing')
        return redirect(url_for('views.home'))

    try:
        # Exchange code for access token
        token_info = sp_oauth.get_access_token(code)
        session["token_info"] = token_info
    except Exception as e:
        print(f'Error getting token: {e}')
        return redirect(url_for('views.home'))

    return redirect(url_for('views.home'))

def get_spotify_client():
    # Get token info from session
    token_info = session.get("token_info", None)
    if not token_info:
        print('No token info in session, redirecting to Spotify login')
        return None

    try:
        # Create Spotify client
        sp = spotipy.Spotify(auth=token_info['access_token'])
        print('Spotify client created successfully')
        return sp
    except Exception as e:
        print(f'Error creating Spotify client: {e}')
        return None

@views.route('/add_to_spotify_playlist', methods=['POST'])
@login_required
def add_to_spotify_playlist():
    song_name = request.form.get('song_name')
    song_artist = request.form.get('song_artist')
    sp = get_spotify_client()

    if sp is None:
        print('Spotify client not available, redirecting to login')
        return redirect(url_for('views.spotify_login'))
    
    user_id = sp.current_user()['id']
    print(f'Adding song: {song_name} by {song_artist}')

    # Search for the song on Spotify
    query = f"{song_name} artist:{song_artist}"
    results = sp.search(q=query, type='track', limit=1)
    if results['tracks']['items']:
        track_id = results['tracks']['items'][0]['id']
        print(f'Song found, Track ID: {track_id}')

        # Get the user's playlists and select/create a playlist
        user_playlists = sp.current_user_playlists()
        playlist_id = None
        for playlist in user_playlists['items']:
            if playlist['name'].strip() == 'My Recommended Songs':
                playlist_id = playlist['id']
                break
        
        if not playlist_id:
            print('Creating new playlist: My Recommended Songs')
            playlist = sp.user_playlist_create(user=user_id, name='My Recommended Songs', public=False)
            playlist_id = playlist['id']
        else:
            print(f'Using existing playlist: My Recommended Songs (ID: {playlist_id})')

        # Add track to playlist
        sp.playlist_add_items(playlist_id, [track_id])
        flash('Song added to your Spotify playlist!')
    else:
        flash('Song not found on Spotify.')

    return redirect(url_for('views.show_recommendations'))

# ----------------------- HOME ---------------------------------------

@views.route('/')
@login_required
def home():
    # Access data within a route where an application context is available
    data = current_app.data
    cosine_similarity_df = current_app.cosine_similarity_df

    # data2 = current_app.data2
    # cosine_similarity_df2 = current_app.cosine_similarity_df2
    return render_template('home.html')

# ----------------------- USER RATING PROCEDURE -------------------------

# Initialize ratings dataframe
ratings_data = pd.DataFrame(columns=['user_id', 'song_index', 'rating'])

def get_random_songs(num_songs=5):
    # Access global data 
    data = current_app.data
    return data.sample(n=num_songs)

    # data2 = current_app.data2
    # return data2.sample(n=num_songs)

def rate_song(user_id, song_index, rating, ratings_data):
    new_rating = pd.DataFrame({'user_id': [user_id], 'song_index': [song_index], 'rating': [rating]})
    ratings_data = pd.concat([ratings_data, new_rating], ignore_index=True)
    print("Song rated successfully!")
    return ratings_data

# def rate_song(user_id, song_index, rating):
#     new_rating = Rating(user_id=user_id, song_index=song_index, rating=rating)
#     db.session.add(new_rating)
#     db.session.commit()
    
#     # inspector = inspect(Rating)
#     # # Get all column attributes
#     # columns = [column.name for column in inspector.mapper.columns]
#     # print("Rating Columns:", columns)

#     print("Song rated successfully!")

@views.route('/rate_songs', methods=['GET', 'POST'])
def rate_songs():
    # Ensure that the user is logged in
    if not current_user.is_authenticated:
        flash("You need to login first!")
        return redirect(url_for('auth.login'))
    # Handle the form submission for rating songs
    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('rating-'):
                song_index = int(key.split('-')[1])
                rating = int(value)
                global ratings_data
                ratings_data = rate_song(current_user.id, song_index, rating, ratings_data)
        flash('Thank you for rating the songs!')
        print('Thank you for rating the songs!')
        # Redirect the user to display songs recommended for them
        return redirect(url_for('views.show_recommendations'))

    # Get 5 random songs to display to collect ratings
    random_songs = get_random_songs()
    return render_template('rating.html', songs=random_songs)

@views.route('/show_recommendations')
def show_recommendations():
    data = current_app.data  # Access data within a route
    cosine_similarity_df = current_app.cosine_similarity_df

    # data2 = current_app.data2 
    # cosine_similarity_df2 = current_app.cosine_similarity_df2

    # Ensure that the user is logged in
    if not current_user.is_authenticated:
        flash("Please login to view recommendations.")
        return redirect(url_for('auth.login'))

    user_ratings = ratings_data[ratings_data['user_id'] == current_user.id]
    if user_ratings.empty:
        return "You need to rate some songs first."

     # Find the top-rated songs
    top_rated_index = user_ratings.loc[user_ratings['rating'].idxmax(), 'song_index']
    top_rated_song = data.loc[top_rated_index, 'name']
    # top_rated_song = data2.loc[top_rated_index, 'name']

    # Fetch recommendations
    recommendations = get_recommendations(top_rated_song, cosine_similarity_df, data)
    return render_template('recommendations.html', recommendations=recommendations, song_name=top_rated_song)

    # recommendations2 = get_recommendations(top_rated_song, request.form.get('song_artist'), cosine_similarity_df2, data2)
    # return render_template('recommendations.html', recommendations=recommendations2, song_name=top_rated_song)


# ----------------------- RECORD USER PREFERANCES -------------------------

@views.route('/add_to_playlist', methods=['POST'])
@login_required
def add_to_playlist():
    # Extract song details from the form submission
    song_name = request.form.get('song_name')
    song_artist = request.form.get('song_artist')
    print(song_name, song_artist)

    # Construct the file path using the current user's username
    file_path = os.path.join(current_app.root_path, f"{current_user.username}_playlist.txt")

    # Write the song details to the user's playlist file
    with open(file_path, 'a') as file:
        file.write(f"{song_name} by {song_artist}\n")

    flash('Song added to your playlist!')
    return redirect(url_for('views.playlist'))

@views.route('/playlist')
@login_required
def playlist():
    file_path = os.path.join(current_app.root_path, f"{current_user.username}_playlist.txt")
    try:
        with open(file_path, 'r') as file:
            songs = file.readlines()
    except FileNotFoundError:
        flash('Your playlist is currently empty.')
        songs = []

    return render_template('playlist.html', songs=songs)

@views.route('/like_song', methods=['POST'])
@login_required
def like_song():
    song_name = request.form.get('song_name')
    song_artist = request.form.get('song_artist')
    file_path = os.path.join(current_app.root_path, f"{current_user.username}_record.txt")

    # Check if the song is already in the file to avoid duplicates
    with open(file_path, 'a+') as file:
        file.seek(0)  # Go to the start of the file
        lines = file.readlines()
        song_entry = f"{song_name} by {song_artist}\n"
        if song_entry not in lines:
            file.write(song_entry)

    flash('Song Liked!')
    return redirect(url_for('views.show_recommendations'))

@views.route('/dislike_song', methods=['POST'])
@login_required
def dislike_song():
    song_name = request.form.get('song_name')
    file_path = os.path.join(current_app.root_path, f"{current_user.username}_record.txt")

    # Read the current entries and filter out the disliked song
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        file.seek(0)  # Go to the start of the file
        file.truncate()  # Clear the file
        song_entry = f"{song_name} by {request.form.get('song_artist')}\n"
        # Rewrite only those songs that are not disliked
        for line in lines:
            if line.strip() != song_entry.strip():
                file.write(line)

    flash('Song Disliked')
    return redirect(url_for('views.show_recommendations'))

# ----------------------- SONG SEARCH LOGIC -------------------------

def search_song(song_name):
    data = current_app.data  
    search_results = data[data['name'].str.contains(song_name, case=False)]

    # data2 = current_app.data2  
    # search_results = data2[data2['name'].str.contains(song_name, case=False)]
    try:
        if search_results.empty:
            print("No matching songs found.")
        else:
            print("Matching songs found:")
            print(search_results[['name', ]])
    except Exception as e:
        print(f'Song not found, Please try another song: {e}')
        return redirect(url_for('views.search'))


@views.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        song_name = request.form.get('song_name')
        song_artist = request.form.get('song_artist')
        file_path = os.path.join(current_app.root_path, f"{current_user.username}_record.txt")
        # Check if the song is already in the file to avoid duplicates
        with open(file_path, 'a+') as file:
            file.seek(0)  # Go to the start of the file
            lines = file.readlines()
            song_entry = f"{song_name} by {song_artist}\n"
            if song_entry not in lines: # Add the searched song into the User's record file
                file.write(song_entry)

        recommendations = get_recommendations(song_name, current_app.cosine_similarity_df, current_app.data)
        return render_template('recommendations.html', recommendations=recommendations, song_name=song_name)
    
        # recommendations2 = get_recommendations(song_name, request.form.get('song_artist'), current_app.cosine_similarity_df2, current_app.data2)
        # return render_template('recommendations.html', recommendations=recommendations2, song_name=song_name)

    return render_template('search_page.html')


# ----------------------- APP LOGIC USING DATABASE & API -------------------------

# @views.route('/add_to_playlist', methods=['POST'])
# @login_required
# def add_to_playlist():
#     song_id = request.form.get('song_id')
#     existing_song = Song.query.filter_by(spotify_id=song_id).first()
    
#     if not existing_song:
#         # Add song to Song database if not exists
#         # TO-DO: This part requires Spotify API to get song details if you don't have them already
#         new_song = Song(name="Song Name", artist="Song Artist", spotify_id=song_id)
#         db.session.add(new_song)
#         db.session.commit()
#         song_id = new_song.id
#     else:
#         song_id = existing_song.id

#     # Add song to the playlist
#     new_playlist_entry = Playlist(user_id=current_user.id, song_id=song_id)
#     db.session.add(new_playlist_entry)
#     db.session.commit()

#     flash('Song added to your playlist!')
#     return redirect(url_for('views.show_recommendations'))

# @views.route('/playlist')
# @login_required
# def playlist():
#     playlist_songs = Playlist.query.filter_by(user_id=current_user.id).join(Song).all()
#     return render_template('playlist.html', songs=playlist_songs)


