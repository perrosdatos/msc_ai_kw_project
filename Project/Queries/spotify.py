import requests

# Spotify API credentials
CLIENT_ID = 'fc19e8277188449795d08758c50b76ed'
CLIENT_SECRET = '1f3ffb7277ed444c8b194772ed8e383c'

def get_spotify_token(client_id, client_secret):
    """
    Get an access token from the Spotify API.
    """
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def search_artist(artist_name, token):
    """
    Search for an artist on Spotify and return their ID.
    """
    url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 3
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    if data["artists"]["items"]:
        return data["artists"]["items"]
    return None

def get_artist_songs(artist_id, limit=5):
    """
    Get top tracks for an artist.
    """
    token = get_spotify_token(CLIENT_ID, CLIENT_SECRET)
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "market": "US"  # Specify the market to localize the results
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return [track for track in data["tracks"][:limit]]

# Example usage
def fetch_songs_by_artist(artist_name, limit=10):
    try:
        token = get_spotify_token(CLIENT_ID, CLIENT_SECRET)
        response = search_artist(artist_name, token)
        artist_id = response[0]["id"]
        if not artist_id:
            print(f"Artist '{artist_name}' not found.")
            return []
        songs = get_artist_songs(artist_id, token, limit=limit)
        return songs
    except requests.RequestException as e:
        print(f"Error fetching songs for artist '{artist_name}': {e}")
        return []
    
def fetch_artist(artist_name):
    try:
        token = get_spotify_token(CLIENT_ID, CLIENT_SECRET)
        artists = search_artist(artist_name, token)
        if not artists:
            print(f"Artist '{artist_name}' not found.")
            return []
        return artists
    except requests.RequestException as e:
        print(f"Error fetching songs for artist '{artist_name}': {e}")
        return []

# Example
#liked_artist = "Coldplay"
#songs = fetch_songs_by_artist(liked_artist, limit=1)
#print(f"Top songs by {liked_artist}: {songs}")
