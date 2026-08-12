import streamlit as st
import requests
from config import Id, Client, Redirect, LastFmKey
Scope = "user-top-read user-read-private"
st.set_page_config(layout="wide")
st.sidebar.markdown(
    "<h1 style='font-size: 45px; font-weight: bold;'>Stats for Spotify</h1>", 
    unsafe_allow_html=True
)
st.sidebar.divider()

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
        token_response = requests.post("https://accounts.spotify.com/api/token", 
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
    first_column, second_column = st.columns([1,3])
    st.divider()

    # extracts the image
    if profile_data["images"] != []:
        image_url = profile_data["images"][0]["url"]
        first_column.image(image_url, width = 140)
    else:
        # if there is no image it will put a default one
       first_column.image("default.png",width = 140)

    # puts the data in the second column
    second_column.markdown(f"## Hello, {account_name}!")
    st.write("")
    first_subcol, second_subcol = second_column.columns(2)
    first_subcol.metric(label = "Spotify Subscription", value = account_sub)
    second_subcol.metric(label = "Followers", value = account_followers)

    # RECOMANDATIONS    
    from recomandation import get_genres_lastfm, get_all_genres_simultaneous, collect_genres
    from recomandation import build_profile, transfrom_to_vector, cosinus_affinity 

    artists_response = requests.get(
                "https://api.spotify.com/v1/me/top/artists",
                headers={"Authorization": f"Bearer {access_token}"}
    )
    # all user's top artists
    top_artists = artists_response.json()["items"]

    # adds more genres to the artist from last.fm
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
    top_4_pairs = count.most_common(4)

    top_4_genres = []
    # gets the top 4 most listened genres names
    for pair in top_4_pairs:
        genre_name = pair[0]
        top_4_genres.append(genre_name)

    found_artists = []
    # extacts 10 artists from each most listened genre
    for genre in top_4_genres: 
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

    # adds more genres to the artist from last.fm
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
                    image_url = "default.png"
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

    st.markdown("Our recomandation for you:")
    if recomended_artist:
        recomendation_row = st.columns(10)
        for i, recomendation in enumerate(recomended_artist[:10]):
            recomendation_row[i].image(recomendation["image"], use_container_width = True)
            recomendation_row[i].markdown(f"[{recomendation['name']}]({recomendation['link']})")
            recomendation_row[i].caption(f"Similarity:{int(recomendation['score'] * 100)}%")
    else:
        st.info("We didn t find enough recomandations for you")
    st.success("You are connected")
    