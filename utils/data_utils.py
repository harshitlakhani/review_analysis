import pandas as pd
import glob
import os
import logging

def get_competitors():
    csv_files = glob.glob('results/etsy_*_reviews.csv')
    competitors = [os.path.basename(f).replace('etsy_', '').replace('_reviews.csv', '') for f in csv_files]
    return competitors

def load_competitor_data(competitor_name):
    try:
        df = pd.read_csv(f'results/etsy_{competitor_name}_reviews.csv')
        if 'date' in df.columns:
            # Handle date format with milliseconds
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date', ascending=False)
        return df
    except Exception as e:
        logging.error(f"Failed to load competitor data for {competitor_name}: {str(e)}")
        return None 