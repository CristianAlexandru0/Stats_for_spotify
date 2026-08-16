import streamlit as st
# displays and customizes the sidebar for every page
def sidebar_construct():
    # displays the title "stats for spotify"
    st.sidebar.markdown(
    "<h1 style='font-size: 45px; font-weight: bold; text-align: center;'>Stats for Spotify</h1>", 
    unsafe_allow_html=True
    )

    st.sidebar.divider()

    # sets the sidebar green
    st.markdown("<style>[data-testid='stSidebar']{background-color:#0D5C33;}</style>", unsafe_allow_html=True)

    #costumizes the pages links on the sidebar
    st.markdown(
        "<style>[data-testid='stBaseButton-secondary'],[data-testid='stBaseButton-secondary'] *{color:white !important;}</style>",
        unsafe_allow_html=True
    )

    # sets the costumization of the buttons
    st.markdown(
        """
        <style>
        [data-testid='stSidebar'] .stButton button, [data-testid='stSidebar'] .stLinkButton a {
            background: transparent !important; border: 1px solid white !important;
        }
        [data-testid='stSidebar'] .stButton button *, [data-testid='stSidebar'] .stLinkButton a * {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # displays the loggout button and logs out of account
    if st.sidebar.button("Logout", width="stretch"):
        st.session_state["access_token"] = None
        st.query_params.clear()
        st.switch_page("Dashboard.py")

    # displays the refresh data button and refreshes the app
    if st.sidebar.button("Refresh Data",width="stretch"):
        st.cache_data.clear()
        st.query_params.clear()
        st.rerun()

    # displays a button that when pressed it redirect the user to the github repo
    st.sidebar.link_button(
        "GitHub Source", 
        "https://github.com/CristianAlexandru0/Stats_for_spotify", 
        width=True
    )
   
    st.sidebar.caption("Made with Streamlit + Spotify and Last.fm API ")

    
