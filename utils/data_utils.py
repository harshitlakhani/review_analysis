import pandas as pd
import glob
import os

def get_competitors():
    csv_files = glob.glob('results/etsy_*_reviews.csv')
    competitors = [os.path.basename(f).replace('etsy_', '').replace('_reviews.csv', '') for f in csv_files]
    return competitors

def load_competitor_data(competitor_name):
    try:
        df = pd.read_csv(f'results/etsy_{competitor_name}_reviews.csv')
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date', ascending=False)
        return df
    except Exception as e:
        return None 