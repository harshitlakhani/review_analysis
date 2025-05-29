import requests
import re
import logging
from urllib.parse import urlencode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_and_log_reviews(
    shop_name: str,
    page: int = 1,
    reviews_per_page: int = 10,
    sort_option: str = "Relevancy",
    should_hide_reviews: bool = True,
    is_in_shop_home: bool = True,
):
    # build the query-string parameters
    specs = {
        "log_performance_metrics": "false",
        "specs[shop-reviews][]": "Shop2_ApiSpecs_Reviews",
        "specs[shop-reviews][1][shopname]": shop_name,
        "specs[shop-reviews][1][page]": str(page),
        "specs[shop-reviews][1][reviews_per_page]": str(reviews_per_page),
        "specs[shop-reviews][1][should_hide_reviews]": str(should_hide_reviews).lower(),
        "specs[shop-reviews][1][is_in_shop_home]": str(is_in_shop_home).lower(),
        "specs[shop-reviews][1][sort_option]": sort_option,
    }
    url = "https://www.etsy.com/api/v3/ajax/bespoke/public/neu/specs/shop-reviews?" + urlencode(specs)

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) " +
                      "AppleWebKit/537.36 (KHTML, like Gecko) " +
                      "Chrome/134.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    payload = resp.json()

    # extract the HTML block
    html = payload["output"]["shop-reviews"]
    match = re.search(r"<ul.*?>(.*?)</ul>", html, re.DOTALL)
    if not match:
        logger.warning("No <ul>…</ul> block found in shop-reviews payload")
        return

    ul_content = match.group(0)  # includes the <ul> tags
    logger.info("Extracted <ul> block:\n%s", ul_content)


if __name__ == "__main__":
    # example usage
    fetch_and_log_reviews("DiamondrensuLabgrown", page=1, reviews_per_page=10)
