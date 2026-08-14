import streamlit as st
import requests 
from sidebar import sidebar_construct

# displays and customizes the sidebar
sidebar_construct()

# verifies if the user is logged
if "access_token" not in st.session_state or st.session_state["access_token"] == None:
    st.warning("You need to login on the dashboard first.")
    st.stop()

access_token = st.session_state["access_token"]

st.markdown("# Your top tracks")
st.write("")


# displays more options of date to choose from
time_range_choice = st.radio("",
    options=["4 weeks", "6 months", "All time"],
    horizontal=True
)

time_map = {
    "4 weeks":"short_term",
    "6 months":"medium_term",
    "All time":"long_term"
}

time_range = time_map[time_range_choice]

response = requests.get(
    "https://api.spotify.com/v1/me/top/tracks",
    headers={"Authorization": f"Bearer {access_token}"},
    params={"limit": 20, "time_range": time_range}
)
data = response.json()
top_tracks = data["items"]

# puts in a list all 20 or less top tracks found
# until then a loading ui is displayed
with st.spinner("Loading..."):
    found_tracks = []
    for track in top_tracks:
        if track["album"]["images"] != []:
            image_url = track["album"]["images"][0]["url"]
        else:
            image_url = "default.png"
        link = track["external_urls"]["spotify"]
        artist = track["artists"][0]["name"]
        found_tracks.append((track["name"], image_url, link, artist))

# displays the tracks and their data
for i, (name, image_url, link, artist) in enumerate(found_tracks, start = 1):
    col1,col2 = st.columns([1, 5])
    col1.image(image_url, width = 120)
    # makes the name look better and green and displays it
    col2.markdown(
        f"### {i}. <a href='{link}' target='_blank' style='color:#0D5C33; text-decoration:none;'>{name}</a>",
        unsafe_allow_html=True
    )
    # makes the caption look better and green and displays it
    col2.markdown(
    f"<p style='font-size:16px; color:#0D5C33; margin-top:-10px;'>{artist}</p>",
    unsafe_allow_html=True
    )
    st.divider()