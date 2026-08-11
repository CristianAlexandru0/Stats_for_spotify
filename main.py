import streamlit as st
import requests
from config import Id, Client, Redirect

Scope = "user-top-read user-read-private"

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
    st.success("You are connected")