from requests import get
from bs4 import BeautifulSoup

from comparison import merge_for_comparison

# Data list to store the scraped data in
reviewed_movies = []

def get_url(username):
    url = 'https://www.letterboxd.com/{}/films/'.format(username)

    # add page query
    url += 'page/{}/'

    return url

def extract_single_record(movie_container):
    if movie_container.p.span is not None:
        reviewed_movie = {} 
        reviewed_movie['movie_id'] = movie_container.div['data-target-link'][6:][:-1] 
        reviewed_movie['rating'] = convert_rating(movie_container.p.span.text)
        reviewed_movies.append(reviewed_movie)

def convert_rating(rating):
    if rating == '½':
        return 10
    elif rating == '★': 
        return 20
    elif rating == '★½': 
        return 30
    elif rating == '★★': 
        return 40
    elif rating == '★★½': 
        return 50
    elif rating == '★★★': 
        return 60
    elif rating == '★★★½': 
        return 70
    elif rating == '★★★★': 
        return 80
    elif rating == '★★★★½': 
        return 90
    elif rating == '★★★★★': 
        return 100

def scrape(username):
    url = get_url(username)

    # Default max number of pages
    page = 1
    last_page = 1000

    while page <= last_page:
        response = get(url.format(page))
        html_soup = BeautifulSoup(response.text, 'html.parser')
        if last_page == 1000:
            last_page = int(html_soup.find('div', class_ = 'paginate-pages').ul.find_all("li")[-1].text)
        movie_containers = html_soup.find_all('li', class_='poster-container')
        for movie_container in movie_containers:
            extract_single_record(movie_container)
        page += 1

    return merge_for_comparison(reviewed_movies)
    