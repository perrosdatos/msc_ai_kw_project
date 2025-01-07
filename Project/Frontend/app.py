from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS
from Queries.spotify import get_spotify_token, get_artist_songs, search_artist, fetch_songs_by_artist, fetch_artist
import requests

app = Flask(__name__)
CORS(app)

# Spotify API setup
CLIENT_ID = 'fc19e8277188449795d08758c50b76ed'
CLIENT_SECRET = '1f3ffb7277ed444c8b194772ed8e383c'

fav_artits = []
liked_songs = []
disliked_songs = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/songs', methods=['GET'])
def get_songs():

    global fav_artits
    recommended_songs = []
    print(fav_artits)
    if not fav_artits:
        print("No favorite artists")
        return jsonify("No favorite artists")
    
    for artist in fav_artits:
        print(artist)
        recommended_songs += get_artist_songs(artist['id'], limit=5)
        print(recommended_songs)
    return jsonify(recommended_songs)

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
    global liked_songs, disliked_songs
    try:
        data = request.get_json()
        feedback = data.get('feedback')
        song = data.get('song')

        if not song or feedback not in ['like', 'dislike']:
            return jsonify({"error": "Invalid feedback or song"}), 400

        if feedback == 'like':
            liked_songs.append(song)
            print(f"Liked songs: {liked_songs}")
        elif feedback == 'dislike':
            disliked_songs.append(song)
            print(f"Disliked songs: {disliked_songs}")

        # Return success response
        return jsonify({"message": f"Song {'liked' if feedback == 'like' else 'disliked'} successfully!"}), 200
    except Exception as e:
        print("Error handling song feedback:", str(e))
        return jsonify({"error": "Failed to process song feedback"}), 500

