import requests
import csv
import time
from bs4 import BeautifulSoup
import random
from datetime import datetime
from tqdm import tqdm
import os

TAGS = {
    'shape': ['oval', 'round', 'marquise', 'princess', 'cushion', 'emerald', 'pear', 'radiant', 'asscher', 'heart', 'trillion', 'baguette'],
    'style': ['engagement', 'wedding', 'bridal', 'eternity', 'halo', 'solitaire', 'anniversary', 'proposal'],
    'type': ['ring', 'band', 'earrings', 'huggies', 'hoop']
}

def scrape_etsy_reviews(shop_name, number_of_pages=1000, page_size=10, pause_seconds=0, progress_bar=None):
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/119.0.6045.169 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 13; SM-S908U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:136.0) Gecko/20100101 Firefox/136.0",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.1023 YaBrowser/23.9.1.1023 Yowser/2.5 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.3124.85"
    ]

    headers = {
        "Host": "www.etsy.com",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": f"https://www.etsy.com/shop/{shop_name}",
        "X-Requested-With": "XMLHttpRequest",
        "X-Etsy-Protection": "1",
    }

    all_reviews = []
    consecutive_success = 0

    for page in range(1, number_of_pages + 1):
        if progress_bar:
            progress_bar.progress(page / number_of_pages)
            
        url = (
            "https://www.etsy.com/api/v3/ajax/bespoke/public/neu/specs/shop-reviews?"
            "log_performance_metrics=false"
            "&specs[shop-reviews][]=Shop2_ApiSpecs_Reviews"
            f"&specs[shop-reviews][1][shopname]={shop_name}"
            f"&specs[shop-reviews][1][page]={page}"
            f"&specs[shop-reviews][1][reviews_per_page]={page_size}"
            "&specs[shop-reviews][1][should_hide_reviews]=true"
            "&specs[shop-reviews][1][is_in_shop_home]=true"
            "&specs[shop-reviews][1][sort_option]=Relevancy"
        )

        response = requests.get(url, headers=headers)
        
        # Check response status
        if response.status_code == 200:
            consecutive_success += 1
            print(f"Page {page}: Success (Status: 200) - Consecutive successes: {consecutive_success}")
        else:
            consecutive_success = 0
            print(f"Page {page}: Failed (Status: {response.status_code})")
            continue

        data = response.json()
        soup = BeautifulSoup(data["output"]["shop-reviews"], 'html.parser')

        for li in soup.find_all('li', {'data-region': 'review'}):
            review_id = li.get('data-review-region', None)

            attrib_p = li.find('p', class_='shop2-review-attribution')
            if attrib_p:
                user_a = attrib_p.find('a')
                user = user_a.text.strip() if user_a else None
                parts = attrib_p.text.split(' on ')
                date = parts[-1].strip() if len(parts) > 1 else None
            else:
                user = None
                date = None

            rating_input = li.find('input', {'name': 'initial-rating'})
            rating = rating_input.get('value') if rating_input else None

            # Update the class name for finding review text
            review_p = li.find('p', class_='prose wt-break-word wt-m-xs-0')
            review_text = review_p.text.strip() if review_p else None

            listing_div = li.find('div', {'data-region': 'listing'})
            if listing_div:
                listing_a = listing_div.find('a')
                listing_title = listing_a.get('aria-label') if listing_a else None
                listing_url = listing_a.get('href') if listing_a else None
            else:
                listing_title = None
                listing_url = None

            img = li.find('img')
            avatar_url = img.get('src') if img else None
            try:
                # Try the original format first
                parsed_date = datetime.strptime(date, "%d %b, %Y")
            except ValueError:
                try:
                    # Try the alternative format (Month Day, Year)
                    parsed_date = datetime.strptime(date, "%b %d, %Y")
                except ValueError:
                    parsed_date = None

            # Get tags for the listing
            tags = get_tags_from_title(listing_title)

            all_reviews.append({
                'review_id': review_id,
                'user': user,
                'date': parsed_date,
                'rating': rating,
                'review_text': review_text,
                'listing_title': listing_title,
                'listing_url': "https://www.etsy.com/"+listing_url if listing_url else None,
                'avatar_url': avatar_url,
                'shape_tags': tags.get('shape', None) if tags else None,
                'style_tags': tags.get('style', None) if tags else None,
                'type_tags': tags.get('type', None) if tags else None
            })

        time.sleep(pause_seconds)

    return all_reviews

def save_reviews_to_csv(reviews, shop_name):
    if not reviews:
        return None
    
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    
    filename = f'results/etsy_{shop_name}_reviews.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reviews[0].keys())
        writer.writeheader()
        writer.writerows(reviews)
    
    return filename

def get_tags_from_title(title):
    if not title:
        return None
    
    title_lower = title.lower()
    found_tags = {}
    
    for category, tags in TAGS.items():
        for tag in tags:
            if tag.lower() in title_lower:
                if category not in found_tags:
                    found_tags[category] = []
                found_tags[category].append(tag)
    
    return found_tags
