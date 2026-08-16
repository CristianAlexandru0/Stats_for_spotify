import requests
import streamlit as st
# requests from last.fm top 10 most listened artists global
def get_global_artists(api_key):
    response = requests.get(
        "http://ws.audioscrobbler.com/2.0/",
        params={
            "method": "chart.gettopartists",
            "api_key": api_key,
            "format": "json",
            "limit": 10
        }
    )
    data = response.json()
    try:
        return data["artists"]["artist"]
    except KeyError:
        return []

# requests from last.fm top 15 most listened tracks global
def get_global_tracks(api_key):
    response = requests.get(
        "http://ws.audioscrobbler.com/2.0/",
        params={
            "method": "chart.gettoptracks",
            "api_key": api_key,
            "format": "json",
            "limit": 15
        }
    )
    data = response.json()
    try:
        return data["tracks"]["track"]
    except KeyError:
        return []

# because last.fm doesn't give anymore photos to artist and song, i will use spotify api
# get the images from spotify for artists
@st.cache_data
def get_artist_image_spotify(artist_name, token):
    response = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": artist_name, "type": "artist", "limit": 5}
    )
    data = response.json()
    try:
        items = data["artists"]["items"]
        for item in items:
            if item["name"].lower() == artist_name.lower():
                image_url = item["images"][0]["url"]
                spotify_url = item["external_urls"]["spotify"]
                return image_url, spotify_url
        # if there is no match, the first image is taken
        return items[0]["images"][0]["url"], items[0]["external_urls"]["spotify"]
    except KeyError:
        return "assets/default.png", None
    except TypeError:
        return "assets/default.png", None

# get the images from spotify for tracks
@st.cache_data
def get_track_image_spotify(track_name, artist_name, access_token):
    response = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": f"{track_name} {artist_name}", "type": "track", "limit": 5}
    )
    data = response.json()
    try:
        items = data["tracks"]["items"]
        # searches for all the artists of the track and the first 5 tracks with this name
        for item in items:
            search_artists = []
            for artist in item["artists"]:
                search_artists.append(artist["name"].lower())
                if artist_name.lower() in search_artists:
                    image_url = item["album"]["images"][0]["url"]
                    spotify_url = item["external_urls"]["spotify"]
                    return image_url, spotify_url
            # if there is no match, the first image is taken, and it's url
        return items[0]["album"]["images"][0]["url"], items[0]["external_urls"]["spotify"]
    except KeyError:
        return "assets/default.png", None
    except TypeError:
        return "assets/default.png", None