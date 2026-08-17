# translates most popular genres from Last.fm to Spotify genres
def normalize_lastfm_genres(lastfm_genres):
    genre_mapp = {
        "hip-hop": "hip hop",
        "rnb": "r&b",
        "r and b": "r&b",
        "r'n'b": "r&b",
        "rock and roll": "rock",
        "rock n roll": "rock",
        "alternative": "alternative rock", 
        "alt rock": "alternative rock",
        "post punk": "post-punk",
        "heavy metal": "metal",
        "electronic": "edm",
        "electronica": "edm",
        "dnb": "drum and bass",
        "drum & bass": "drum and bass",
        "chillout": "chill",
        "synthpop": "synth-pop",
        "indie": "indie pop",
        "kpop": "k-pop",
        "korean pop": "k-pop",
        "jpop": "j-pop",
        "japanese pop": "j-pop",
        "romanian": "romanian pop", 
        "romanian hip-hop": "romanian hip hop",
        "ro rap": "romanian rap",
        "ro trap": "romanian trap",
        "romanian house": "romanian electronic",
        "ost": "soundtrack",
        "soundtracks": "soundtrack",
        "singer songwriter": "singer-songwriter",
        "singer/songwriter": "singer-songwriter"
    }

    normalized_genres = []
    for genre in lastfm_genres:
        gen = genre.lower().strip()

        # if it is not in the dictionary then it returns the genre without modifying it
        transf_genre = genre_mapp.get(gen, gen)

        # if the genre not in the list it adds it
        if transf_genre not in normalized_genres:
            normalized_genres.append(transf_genre)

    # returns the list
    return normalized_genres