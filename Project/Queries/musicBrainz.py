import musicbrainzngs

# Configure the MusicBrainz client
musicbrainzngs.set_useragent(
    "MusicRecommendationSystem",
    "1.0",
    "eduardo.luis.vieira.pereira@gmail.com"  # Provide your email for contact purposes
)

def fetch_artist_genres(artist_name):
    try:
        # Search for the artist by name
        result = musicbrainzngs.search_artists(artist=artist_name, limit=1)
        
        if result["artist-count"] == 0:
            print(f"No artist found for '{artist_name}'")
            return []

        # Get the artist ID of the best match
        artist_id = result["artist-list"][0]["id"]

        # Fetch artist details by ID
        artist_data = musicbrainzngs.get_artist_by_id(artist_id, includes=["tags"])

        # Extract genres from tags
        genres = [tag["name"] for tag in artist_data["artist"].get("tag-list", [])]
        return genres
    except musicbrainzngs.MusicBrainzError as e:
        print(f"An error occurred while accessing MusicBrainz: {e}")
        return []
    
def fetch_artists_by_genre(genre, limit=10):
    try:
        # Search for artists using the genre as a tag
        result = musicbrainzngs.search_artists(tag=genre, limit=limit)

        if result["artist-count"] == 0:
            print(f"No artists found for genre '{genre}'")
            return []

        # Extract artist names and IDs
        artists = [
            {"name": artist["name"], "id": artist["id"]}
            for artist in result["artist-list"]
        ]
        return artists
    except musicbrainzngs.MusicBrainzError as e:
        print(f"An error occurred while accessing MusicBrainz: {e}")
        return []
    
def fetch_similar_artists(artist_name, limit=5):
    try:
        # Search for the artist
        result = musicbrainzngs.search_artists(artist=artist_name, limit=1)
        if result["artist-count"] == 0:
            print(f"No artist found for '{artist_name}'")
            return []

        artist_id = result["artist-list"][0]["id"]

        # Fetch related artists (use tags for similarity)
        artist_data = musicbrainzngs.get_artist_by_id(artist_id, includes=["tags"])
        tags = [tag["name"] for tag in artist_data["artist"].get("tag-list", [])]

        # Use the top tag to find similar artists
        if not tags:
            return []
        top_tag = tags[0]
        result = musicbrainzngs.search_artists(tag=top_tag, limit=limit)
        similar_artists = [artist["name"] for artist in result["artist-list"] if artist["name"] != artist_name]
        return similar_artists
    except musicbrainzngs.MusicBrainzError as e:
        print(f"Error fetching similar artists for {artist_name}: {e}")
        return []

def fetch_songs_by_artist(artist_name, limit=10):
    try:
        # Search for the artist
        result = musicbrainzngs.search_artists(artist=artist_name, limit=1)
        if result["artist-count"] == 0:
            print(f"No artist found for '{artist_name}'")
            return []

        artist_id = result["artist-list"][0]["id"]

        # Fetch recordings (songs) for the artist
        recordings = musicbrainzngs.browse_recordings(artist=artist_id, limit=limit)
        songs = [rec["title"] for rec in recordings["recording-list"]]
        return songs
    except musicbrainzngs.MusicBrainzError as e:
        print(f"Error fetching songs for {artist_name}: {e}")
        return []

# Example usage
artist_name = "kendrick Lamar"
genres = fetch_artist_genres(artist_name)
print(f"Genres for {artist_name}:", genres)

similar = fetch_similar_artists(artist_name)
print(f"Artists similar to {artist_name}: {similar}")
