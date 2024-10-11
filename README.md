
# Syncify

## Contributors:

* Syed Ali Haider
* Jasmeen kaur

## Overview

Discover your next favorite song with Syncify, your personal music recommendation companion! This web app harnesses the power of advanced recommendation algorithms to deliver personalized song suggestions that resonate with your unique taste. By connecting with Spotify's huge music library and using advanced data analysis, Syncify makes sure every song recommendation is spot on. You can rate songs, get personalized suggestions, and add songs directly to your Spotify playlists. With Syncify, you can explore new music and keep your playlists exciting. Say goodbye to boring music and hello to endless musical discoveries!

## Objective

* Utilize song features such as acousticness, danceability etc. to recommend similar songs based on content-based filtering techniques.
* Utilize song lyrics to recommend similar songs based on content-based filtering techniques.
* Enable dynamic recommendations by incorporating user data such as their ratings for the recommended songs
* Explore hybrid models combining content-based and collaborative filtering methods for enhanced recommendations.

## Dataset

* Spotify Dataset
    - spotify/train.csv
* MusixMatch Dataset
    - consine_similarity_svd.csv

## App Directory Flow

```markdown
Syncify
├── main.py (recommendation system1)
├── lyrics_Added.py (recommendation system2)
└── spotify data (data1)
    ├── train.csv
└── musixMatch data (data2)
    ├── cosine_similarity_svd.csv 
├── ReadMe
├── IEEE Report
├── Appendix
└── app
    ├── __init__.py
    ├── auth.py
    ├── view.py
    ├── model.py
    └── template
        ├── login.html
        ├── home.html
        ├── search_page.html
        ├── rating.html
        ├── recommendation.html
        ├── playlist.html
```

## Instructions on how to run the application

1. Before running, make sure that all the required dependencies are installed on your computer, if not use the following command to install:
    * For Flask app
        * pip install flask flask_login spotipy spotipy.oauth2 pandas numpy sqlalchemy os sklearn.metrics.pairwise werkzeug.security
    * For main.py
    * For lyrics_added.py
    
2. cd Syncify 
3. use ./run.py command to run your application (Make sure you are running the application within the Syncify folder)
4. open your web browser (google chrome not recommended as it blocks certain functionalities, safari preferred)
    use http://127.0.0.1:5000 to access the running application from your browser.
    
    * Please note that after starting the program, there may be a brief wait while it completes the preprocessing. During this time, a pop-up graph showing the silhouette score & clusters may appear. If this occurs, please close the pop-up graph to proceed. Once the preprocessing is complete, you can access the web application in your browser."
    
5. When searching for a song to get recommendations, please use the following examples as to make the process efficiently, only a subset of the original data was used to test the program

| Artists                        | Name               |
|--------------------------------|--------------------|
| ['Coldplay']                   | Fix You            |
| ['Snow Patrol']                | Chasing Cars       |
| ['Van Morrison']               | Brown Eyed Girl    |
| ['Europe']                     | The Final Countdown|
| ['Dr. Dre', 'Eminem']          | Forgot About Dre   |
| ['Motörhead']                  | Ace of Spades      |
| ['Carly Simon']                | You're so Vain     |
| ['Ella Fitzgerald']            | Sleigh Ride        |
| ['Bruce Springsteen']          | I'm On Fire        |
| ['Weezer']                     | Say It Ain't So   |
| ['Aerosmith']                  | Cryin'             |
| ['Eminem', 'Dina Rae']         | Superman           |
| ['We The Kings']               | Check Yes, Juliet  |
| ['Norah Jones']                | Come Away With Me  |
| ['Cream']                      | Sunshine Of Your Love |
| ['Pearl Jam']                  | Last Kiss          |
| ['Brooks & Dunn']              | Neon Moon          |
| ['The Outfield']               | Your Love          |
| ['Elton John']                 | Crocodile Rock     |
| ['Weezer']                     | Beverly Hills      |

## How to run the notebooks 
There are 4 notebooks 
1. main.ipynb -> this contains the base model with audio features used only
2. lyrics_added.ipynb -> this contains the hybrid model with audio and lyrics features both
3. eda.ipynb -> this contains the exploratory data analysis done
4. scrap_new.ipynb -> this contains the scrip code to scrap metadata from the spotify api directly

You should have spotipy, python, panadas and numpy installed before running these notebooks 

