import streamlit as st
import requests
from config import Id, Client, Redirect

Scope = "user-top-read"

st.title("Stats for Spotify")

# gets the code from the url
CODE = st.query_params.get("code")

if not CODE:
    Url = (
        "https://accounts.spotify.com/authorize" +
        f"?client_id={Id}" + "&response_type=code" + 
        f"&redirect_uri={Redirect}" + f"&scope={Scope}"
    )
    st.link_button("Login with Spotify",Url)
else:
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

    data = requests.get("https://api.spotify.com/v1/me/top/tracks",
               headers={"Authorization": f"Bearer {access_token}"})
    data = data.json()
    print(data)

    k = 1
    for item in data["items"]:
        track_name = item["name"]
        artist_name = item["artists"][0]["name"]

        st.markdown(f"{k} *{track_name}* - {artist_name}")
        k += 1