import streamlit as st
from app import scrape_etsy_reviews, save_reviews_to_csv
import pandas as pd
import os

st.set_page_config(
    page_title="Add Competitors", 
    page_icon="➕",
    layout="wide"
)

# Add a section to display existing competitors
st.title("Existing Competitors")

# Get list of CSV files in the data directory
data_dir = "results"
if os.path.exists(data_dir):
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if csv_files:
        # Create a list to store competitor data
        competitors_data = []
        
        for csv_file in csv_files:
            # Extract shop name from filename (remove 'etsy_' prefix and '_reviews.csv' suffix)
            shop_name = csv_file.replace('etsy_', '').replace('_reviews.csv', '')
            
            # Read the CSV file to get review count
            df = pd.read_csv(os.path.join(data_dir, csv_file))
            review_count = len(df)
            
            competitors_data.append({
                'Shop Name': shop_name,
                'Review Count': review_count,
                'Last Updated': pd.Timestamp(os.path.getmtime(os.path.join(data_dir, csv_file)), unit='s').strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Display the data in a table
        competitors_df = pd.DataFrame(competitors_data)
        st.dataframe(competitors_df, use_container_width=True)
    else:
        st.info("No competitors have been added yet.")
else:
    st.info("No data directory found.")

# Add a separator
st.markdown("---")

# Original content for adding new competitors
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