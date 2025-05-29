import streamlit as st

st.set_page_config(
    page_title="Etsy Review Analyzer",
    page_icon="🛍️",
    layout="wide"
)

st.title("Etsy Review Analyzer")
st.write("""
Welcome to the Etsy Review Analyzer! Use the sidebar to navigate between different features:

- **Explore**: View and analyze existing competitor reviews
- **Add Competitors**: Scrape new competitor data
""") 