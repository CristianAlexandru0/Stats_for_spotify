import numpy as np
import requests
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from normalize_genres import normalize_lastfm_genres
# because executing one by one the api requests take a long time
# this function will help with executing the requests simultaneous
def get_all_genres_simultaneous(artists, api_key):
    # executor is a manager that can simultaneous execute 10 functions
    executor = ThreadPoolExecutor(max_workers=10)
    tasks = []
    # submit sends every artist to a thread
    # submit doesn't wait for the function to return (it will execute in the background)
    for artist in artists:
        task = executor.submit(get_genres_lastfm, artist["name"], api_key)
        tasks.append(task)
    # waits for all the threads to finish and syncs the result of the function (task.result) in the artist genres
    # zip function asociates every artist with his task in order
    for artist, task in zip(artists, tasks):
        artist["genres"] = task.result()
    # free the resources
    executor.shutdown()


# requests the data of an artist from last.fm 
# and adds the genres of the artist to a list
@st.cache_data
def get_genres_lastfm(artist_name, api_key):
    response = requests.get(
         "http://ws.audioscrobbler.com/2.0/",
        params={
            "method": "artist.getTopTags",
            "artist": artist_name,
            "api_key": api_key,
            "format": "json"
        }
    )
   
    data = response.json()
    genres = []
    try:
        tags = data["toptags"]["tag"]
        #gets the most important 3 genres
        top_3_tags = tags[:3]
        for tag in top_3_tags:
            genre_name = tag["name"].lower().replace("-", " ").strip()
            genres.append(genre_name)
    except KeyError:
        return []
    except TypeError:
        return []
    return normalize_lastfm_genres(genres)
    
# collects all the genres from the user's top artists
def collect_genres(top_artists):
    genres = []
    for artist in top_artists:
        for genre in artist.get("genres",[]):
            if genre not in genres:
                genres.append(genre)
    return list(genres)

# the sum of all vectors of the user's top artists
def build_profile(top_artists, all_user_genres):
    profile = np.zeros(len(all_user_genres))
    for artist in top_artists:
        artist_genres = artist.get("genres", [])
        profile = profile + transfrom_to_vector(artist_genres, all_user_genres)
    return profile

# compare the artists genres with the users genres
# if the genres are the same it puts in a vector 1 else 0
# with the help of numpy, it creates an array
def transfrom_to_vector(artist_genres, user_genres):
    vector = []
    for genre in user_genres:
        if genre in artist_genres:
            vector.append(1)
        else:
            vector.append(0)
    return np.array(vector)

 # calculates the likness of the two vectors to be similar
def cosinus_affinity(vector1, vector2):
    # calculates the norm of the two vectors
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)

    if norm_vector1 == 0 or norm_vector2 == 0:
        return 0
    
    # calculates the dot product of the vectors
    dot_product = np.dot(vector1, vector2)

    affinity = dot_product / (norm_vector1 * norm_vector2)
    return affinity

    
    