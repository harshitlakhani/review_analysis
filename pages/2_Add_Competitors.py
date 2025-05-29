import streamlit as st
from app import scrape_etsy_reviews, save_reviews_to_csv

st.set_page_config(
    page_title="Add Competitors", 
    page_icon="➕",
    layout="wide"
)

st.title("Add New Competitor")

# Input fields
shop_name = st.text_input("Shop Name", placeholder="Enter Etsy shop name")
number_of_pages = st.number_input("Number of Pages", min_value=1, max_value=1000, value=10)

if st.button("Scrape Reviews"):
    if not shop_name:
        st.error("Please enter a shop name")
    else:
        # Create a progress container
        progress_bar = st.progress(0)
        status_container = st.empty()
        
        with st.spinner("Scraping reviews... This may take a while."):
            status_container.text("Starting scrape...")
            
            # Scrape reviews with progress bar
            reviews = scrape_etsy_reviews(shop_name, number_of_pages, progress_bar=progress_bar)
            
            if reviews:
                # Save to CSV
                filename = save_reviews_to_csv(reviews, shop_name)
                
                # Display success message
                st.success(f"Successfully scraped {len(reviews)} reviews!")
                
                # Download button
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="Download CSV",
                        data=f,
                        file_name=f'etsy_{shop_name}_reviews.csv',
                        mime='text/csv'
                    )
            else:
                st.error("No reviews found or an error occurred during scraping.") 