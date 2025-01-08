from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS
from Queries.spotify import get_spotify_token, get_artist_songs, search_artist, fetch_songs_by_artist, fetch_artist, fetch_songs
from Queries.yago import get_recommendarions_based_on_influencedBy_likes_dislikes, get_recommendations_based_on_influencedBy
import requests
import random

app = Flask(__name__)
CORS(app)

# Spotify API setup
CLIENT_ID = 'fc19e8277188449795d08758c50b76ed'
CLIENT_SECRET = '1f3ffb7277ed444c8b194772ed8e383c'

fav_artits = []
liked_artists = []
disliked_artists = []

@app.route('/')
def index():
    return render_template('index.html')
"""
@app.route('/songs', methods=['GET'])
def get_songs():

    global fav_artits
    recommended_songs = []
    print(fav_artits)
    if not fav_artits:
        print("No favorite artists")
        return jsonify("No favorite artists")
    
    for artist in fav_artits:
        recommended_songs += get_artist_songs(artist['id'], limit=5)
    return jsonify(recommended_songs)
"""
@app.route('/songs', methods=['GET'])
def get_newsongs():

    global fav_artits, liked_artists, disliked_artists
    print("Getting recomendations")
    recommended_songs = []
    recommendation_list = []
    if not fav_artits:
        print("No favorite artists")
        return jsonify("No favorite artists")
    
    if liked_artists or disliked_artists == []:
        for artist in fav_artits:
            recommendation_list.append(get_recommendations_based_on_influencedBy(artist["name"], 2))
        print(f"Recomended List: {recommendation_list}")
    else:
        recommendation_list = get_recommendarions_based_on_influencedBy_likes_dislikes(liked_artists, disliked_artists, 2, True)

    for recommendation in recommendation_list:
        for song in recommendation["songs"]:
            recommended_songs.append(song["label"])
    print(f"Recomended Songs: {recommended_songs}")
    random.shuffle(recommended_songs)
    songs = fetch_songs(recommended_songs)
    return jsonify(songs)

@app.route('/getartist', methods=['GET'])
def get_artist():

    artist_name = request.args.get('artist_name', '')
    if not artist_name:
        return jsonify({"error": "Artist name is required"}), 400

    artists = fetch_artist(artist_name)
    return jsonify(artists)

@app.route('/saveFavArtists', methods=['POST'])
def save_fav_artists():

    global fav_artits
    try:
        data = request.get_json()
        fav_artits = data.get('artists', [])

        # Process the artists (both id and name)
        for artist in fav_artits:
            print(f"Received artist: ID={artist['id']}, Name={artist['name']}")

        # Return success response
        return jsonify({"message": "Artists saved successfully!"}), 200
    except Exception as e:
        print("Error saving artists:", str(e))
        return jsonify({"error": "Failed to save artists"}), 500

@app.route('/feedbackSong', methods=['POST'])
def handle_song_feedback():
    global liked_artists, disliked_artists
    try:
        data = request.get_json()
        feedback = data.get('feedback')
        artists = data.get('artists')
        if not artists or feedback not in ['like', 'dislike']:
            return jsonify({"error": "Invalid feedback or song"}), 400

        if feedback == 'like':
            for artist in artists:
                liked_artists.append(artist["name"])
            print(f"Liked songs: {liked_artists}")
        elif feedback == 'dislike':
            for artist in artists:
                disliked_artists.append(artist["name"])
            print(f"Disliked songs: {disliked_artists}")

        # Return success response
        return jsonify({"message": f"Song {'liked' if feedback == 'like' else 'disliked'} successfully!"}), 200
    except Exception as e:
        print("Error handling song feedback:", str(e))
        return jsonify({"error": "Failed to process song feedback"}), 500

