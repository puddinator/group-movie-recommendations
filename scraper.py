from requests import get
from bs4 import BeautifulSoup

from comparison import merge_for_comparison

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
        return reviewed_movie

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

    reviewed_movies = []

    while page <= last_page:
        response = get(url.format(page))
        html_soup = BeautifulSoup(response.text, 'html.parser')
        if last_page == 1000:
            last_page = int(html_soup.find('div', class_ = 'paginate-pages').ul.find_all("li")[-1].text)
        movie_containers = html_soup.find_all('li', class_='poster-container')
        for movie_container in movie_containers:
            reviewed_movie = extract_single_record(movie_container)
            if reviewed_movie is not None:
                reviewed_movies.append(reviewed_movie)
        page += 1
    
    return reviewed_movies
    

def scrape_many(self, usernames, number_of_accounts):
    reviewed_movies_all = []
    
    for i in range (1, int(number_of_accounts) + 1):
        self.update_state(state='PROGRESS', meta={'status': 'Gathering ' + usernames['username_' + str(i)] + "'s user data"})
        reviewed_movies = scrape(usernames['username_' + str(i)])
        reviewed_movies_all.append(reviewed_movies)
        self.update_state(state='PROGRESS', meta={'status': "Gathered!"})

    # print(reviewed_movies_all)
    return merge_for_comparison(self, reviewed_movies_all, number_of_accounts, usernames)

# scrape('abrokepcbuilder')