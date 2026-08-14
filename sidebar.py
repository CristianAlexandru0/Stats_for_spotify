import streamlit as st
# displays and customizes the sidebar for every page
def sidebar_construct():
    # displays the title "stats for spotify"
    st.sidebar.markdown(
    "<h1 style='font-size: 45px; font-weight: bold; text-align: center;'>Stats for Spotify</h1>", 
    unsafe_allow_html=True
    )
    # sets the sidebar green
    st.markdown("<style>[data-testid='stSidebar']{background-color:#0D5C33;}</style>", unsafe_allow_html=True)

    #costumizes the pages links on the sidebar
    st.markdown(
        "<style>[data-testid='stSidebarNavLink']{font-size:28px !important; font-weight:bold !important;}</style>",
        unsafe_allow_html=True
    )

    st.sidebar.divider()
