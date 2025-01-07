from Queries.musicBrainz import fetch_artist_genres

favorite_artists = ["Kendrick Lamar", "Jermaine Lamarr Cole", "Drake"]
genres = []
for artist in favorite_artists:
    genre = fetch_artist_genres(artist)
    genres.append(genre)
    print(f"Genres for {artist}:", genre)