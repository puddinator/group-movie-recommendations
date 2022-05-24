import os
import requests

from flask import redirect, render_template, request, session
from functools import wraps

from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions
from webdriver_manager.chrome import ChromeDriverManager
from operator import itemgetter

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"



#Scraper stuff
def get_url(search_text):
    """Generate a url from search text"""
    url = 'https://www.amazon.sg/s?k={}&ref=nb_sb_noss_1'.format(search_text)
    
    # add page query
    url += '&page={}'
        
    return url

def get_product_url(url):
    """Generate the generic url"""
    url = url[:url.rfind('/')]

    return url

def get_img_url(imageurl):
    """Generate the high quality image from url"""
    imageurl = imageurl.replace("320", "")

    return imageurl


def extract_record(single_record):
    """Extract and return data from a single record"""
    
    # Title
    title_tag = single_record.h2.a
    title = title_tag.text.strip()
    url = 'https://www.amazon.sg' + title_tag.get('href')
    
    # because some products dont have prices we have to use try-except block to catch AttributeError
    try:
        # product price
        price_parent = single_record.find('span', 'a-price')
        price = price_parent.find('span', 'a-offscreen').text
        price = float(price.replace("$", "").replace(',',"").replace('S',""))
    except AttributeError:
        return

    try:
        rating = single_record.i.text
    except AttributeError:
        rating = "-"

    try:
        review_count = single_record.find('span', {'class': 'a-size-base s-underline-text'}).text
    except AttributeError:
        review_count = "-"

    try:
        # image url
        imageurl = single_record.img['src']
    except AttributeError:
        return

    return {
        "title": title,
        "price": float(price),
        "rating": rating,
        "review_count": review_count,
        "url": get_product_url(url),
        "imageurl": get_img_url(imageurl)
    }

    return result

def lookup(search_term):
    """Run main program routine"""

    # startup the webdriver
    options=Options()
    
    options.headless = True #choose if we want the web browser to be open when doing the crawling 
    # options.use_chromium = True
    driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)

    records = []
    url = get_url(search_term)
    
    for page in range(1, 2):
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', {'data-component-type': 's-search-result'})

        for item in results:
            record = extract_record(item)
            if record:
                records.append(record)
    sortedrecords = sorted(records, key=itemgetter('price'), reverse=True)
    return sortedrecords
