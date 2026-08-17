import streamlit as st
import requests
from src.sidebar import sidebar_construct

# gets the api keys and secrets from streamlit secrets
Id = st.secrets["Id"]
Client = st.secrets["Client"]
Redirect = st.secrets["Redirect"]
LastFmKey = st.secrets["LastFmKey"]

# displays and customizes the sidebar
sidebar_construct()

Scope = "user-top-read user-read-private"
st.set_page_config(layout="wide")



if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

if st.session_state["access_token"] == None:
    # gets the code from the url
    CODE = st.query_params.get("code")

    if not CODE:
        # creates the authorization link
        Url = (
            "https://accounts.spotify.com/authorize" +
            f"?client_id={Id}" + "&response_type=code" + 
            f"&redirect_uri={Redirect}" + f"&scope={Scope}"
        )
        st.link_button("Login with Spotify",Url)
    else:
        # requests the acces_token from spotify with the help of the code
        token_response = requests.post(
            "https://accounts.spotify.com/api/token", 
            data ={
                "grant_type": "authorization_code",
                "code": CODE,
                "redirect_uri": Redirect,
                "client_id": Id,
                "client_secret": Client
                }
        )
        token_json = token_response.json()
        access_token = token_json["access_token"]

        # adds the access token in the session_state to save the token between the files
        if "access_token" in token_json:
            st.session_state["access_token"] = access_token

            st.query_params.clear()
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Login failed")
else:
    access_token = st.session_state["access_token"]
    # requests the profile data from spotify
    profile_response = requests.get(
        "https://api.spotify.com/v1/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    profile_data = profile_response.json()

    # saves the name
    account_name = profile_data["display_name"].title()
    # saves the followers
    account_followers = profile_data["followers"]["total"]
    # saves the subscription type
    account_sub = profile_data["product"].title()

    # creates the table
    first_column, second_column, third_column = st.columns([1,2,1])
    st.divider()

    # extracts the image
    if profile_data["images"] != []:
        image_url = profile_data["images"][0]["url"]
        first_column.image(image_url, width = 180)
    else:
        # if there is no image it will put a default one
       first_column.image("assets/default.png",width = 180)

    # puts the data in the second column
    second_column.markdown(f"## Hello, {account_name}!")
    st.write("")
    first_subcol, second_subcol = second_column.columns(2)
    first_subcol.metric(label = "Spotify Subscription", value = account_sub)
    second_subcol.metric(label = "Followers", value = account_followers)

    # RECOMANDATIONS    
    from src.recomandation import get_genres_lastfm, get_all_genres_simultaneous, collect_genres
    from src.recomandation import build_profile, transfrom_to_vector, cosinus_affinity 
    # 'spinner' adds a loading bar while the program is finding the artists
    with st.spinner("Loading..."):
        artists_response = requests.get(
            "https://api.spotify.com/v1/me/top/artists",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        # all user's top artists
        top_artists = artists_response.json()["items"]

        # adds more genres to the artist from last.fm (requesting simultaneous for 10 artist at a time)
        
        get_all_genres_simultaneous(top_artists, LastFmKey)

        # creates a list with all the genres from the top artists
        all_user_genres = collect_genres(top_artists)
        # adds the genres of the top artist to build a profile
        user_profile = build_profile(top_artists, all_user_genres)

        from collections import Counter

        all_top_artists_genres = []
        # adds all the top artists genres to a list
        for artist in top_artists:
            all_top_artists_genres.extend(artist.get("genres",[]))
        # returns a dictionary like variable 
        count = Counter(all_top_artists_genres)

        # gets the top 4 most listened genres in pairs like "name":"count"
        top_7_pairs = count.most_common(7)

        # displays a genre chart
        from src.genre_graphic import show_graph

        show_graph(top_7_pairs, third_column)

        top_7_genres = []
        # gets the top 4 most listened genres names
        for pair in top_7_pairs:
            genre_name = pair[0]
            top_7_genres.append(genre_name)

        found_artists = []
        # extacts 10 artists from each most listened genre
        for genre in top_7_genres: 
            response = requests.get(
                "https://api.spotify.com/v1/search",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"q": f'genre:"{genre}"', "type": "artist", "limit": 10}
            )
            data = response .json()
            try:
                items = data["artists"]["items"]
            except KeyError:
                items = []
            found_artists.extend(items)

        # adds more genres to the artist from last.fm (requesting simultaneous for 10 artist at a time)
        get_all_genres_simultaneous(found_artists, LastFmKey)

        recomended_artist = []
        seen_artists = []
        top_artists_id = []
        for artist in top_artists:
            top_artists_id.append(artist["id"])

        for artist in found_artists:
            id = artist["id"]
            if id not in top_artists_id and id not in seen_artists:
                # mark the artist as already seen
                seen_artists.append(id)
                # transform the genres of the artist in a vector
                vector_artist = transfrom_to_vector(artist.get("genres",[]),all_user_genres)
                # caculate the similarity score
                affinity_score = cosinus_affinity(vector_artist, user_profile)
                if affinity_score > 0:
                    if artist["images"]:
                        image_url = artist["images"][0]["url"]
                    else:
                        image_url = "assets/default.png"
                    # appends to a list of dictionaries the data of the artist
                    recomended_artist.append({
                        "name": artist["name"],
                        "image": image_url,
                        "link": artist["external_urls"]["spotify"],
                        "score": affinity_score
                    })
    # returns the score of an artist 
    def extract_score(artist):
        return artist["score"]
    # sorts the artists by the score in descending order
    recomended_artist.sort(key = extract_score, reverse = True)

    st.markdown("Our recomandation for you")
    # displays the top 10 recomandation artists in a 10-column layout
    if recomended_artist:
         with st.spinner("Loading..."):
            recomendation_row = st.columns(10)
            for i, recomendation in enumerate(recomended_artist[:10]):
                recomendation_row[i].image(recomendation["image"], width="stretch")
                recomendation_row[i].markdown(f"[{recomendation['name']}]({recomendation['link']})")
                recomendation_row[i].caption(f"Similarity:{int(recomendation['score'] * 100)}%")
    else:
        st.info("We didn t find enough recomandations for you")

    from src.global_artists_tracks import get_global_artists, get_global_tracks
    from src.global_artists_tracks import get_artist_image_spotify, get_track_image_spotify
    #returns top 10 most listened artists
    top_global_artists = get_global_artists(LastFmKey)
    # returns top 10 most listened songs
    top_global_tracks = get_global_tracks(LastFmKey)

    # for the results to not be shown imediatly after they are found, and to show them all at the same time
    # first it collects the data and puts a loading string and after display it
    if top_global_artists:
        found_artists = []
        with st.spinner("Loading..."):
            for i, artist in enumerate(top_global_artists[:10]):
                image_url, spotify_url = get_artist_image_spotify(artist["name"], access_token)
                # adds a tuple to the list
                found_artists.append((artist["name"], image_url, spotify_url))

        st.markdown("Trending artist")
        # displays the top 10 global artists in a 10-column layout
        artists_row = st.columns(10)
        for i, (name, image_url, spotify_url) in enumerate(found_artists):
            artists_row[i].image(image_url, width="stretch")
            artists_row[i].markdown(f"[{name}]({spotify_url})")

    # searches top trending tracks
    if top_global_tracks:
        with st.spinner("Loading..."):
            found_tracks = []
            for i, track in enumerate(top_global_tracks[:10]):
                image_url, spotify_url = get_track_image_spotify(track["name"],track["artist"]["name"] ,access_token)
                found_tracks.append((track["name"], image_url, spotify_url, track['artist']['name']))

        st.markdown("Trending tracks")
        # displays the top 10 global tracks in a 10-column layout
        track_row = st.columns(10)
        for i, (name, image_url, spotify_url, artist) in enumerate(found_tracks):
            track_row[i].image(image_url, width="stretch")
            track_row[i].markdown(f"[{name}]({spotify_url})")
            track_row[i].caption(f"{artist}")
        
