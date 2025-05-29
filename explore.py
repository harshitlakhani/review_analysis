import pandas as pd

data = pd.read_csv("results/etsy_MesmoraJewelry_reviews.csv")

# Convert 'date' column to datetime format
data['date'] = pd.to_datetime(data['date'])

# Print the date column
print(data["date"])