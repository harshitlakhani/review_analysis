import streamlit as st
from app import scrape_etsy_reviews, save_reviews_to_csv
import pandas as pd
import glob
import os

st.set_page_config(
    page_title="Add Competitors", 
    page_icon="➕",
    layout="wide"  # Added wide layout
)

st.title("Add New Competitor")

# Function to get latest review date for a shop
def get_latest_review_date(shop_name):
    csv_files = glob.glob(f'results/etsy_{shop_name}_reviews.csv')
    if not csv_files:
        return None
    
    latest_date = None
    for file in csv_files:
        df = pd.read_csv(file)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            file_latest = df['date'].max()
            if latest_date is None or file_latest > latest_date:
                latest_date = file_latest
    
    return latest_date

# Input fields
shop_name = st.text_input("Shop Name", placeholder="Enter Etsy shop name")
number_of_pages = st.number_input("Number of Pages", min_value=1, max_value=1000, value=10)

col1, col2 = st.columns(2)

with col1:
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

with col2:
    if st.button("Refresh Reviews"):
        if not shop_name:
            st.error("Please enter a shop name")
        else:
            latest_date = get_latest_review_date(shop_name)
            if latest_date is None:
                st.error("No existing reviews found for this shop")
            else:
                progress_bar = st.progress(0)
                status_container = st.empty()
                
                with st.spinner("Refreshing reviews... This may take a while."):
                    # Convert timestamp to date string in YYYY-MM-DD format
                    start_date = latest_date.strftime('%Y-%m-%d')
                    status_container.text(f"Starting refresh from {start_date}...")
                    
                    # Scrape reviews with progress bar and start date
                    reviews = scrape_etsy_reviews(
                        shop_name, 
                        number_of_pages
                    )
                    
                    if reviews:
                        # Save to CSV
                        filename = save_reviews_to_csv(reviews, shop_name)
                        
                        # Display success message
                        st.success(f"Successfully scraped {len(reviews)} new reviews!")
                        
                        # Download button
                        with open(filename, 'rb') as f:
                            st.download_button(
                                label="Download CSV",
                                data=f,
                                file_name=f'etsy_{shop_name}_reviews.csv',
                                mime='text/csv'
                            )
                    else:
                        st.error("No new reviews found or an error occurred during scraping.") 