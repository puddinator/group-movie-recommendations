import time 
from requests import get
from bs4 import BeautifulSoup
import re
# Needs LXML
from comparison import merge_for_comparison

def get_url(username):
    url = 'https://www.letterboxd.com/{}/films/'.format(username)

    # add page query
    url += 'page/{}/'

    return url

def extract_single_record(movie_container):
    if movie_container.p.span is not None:
        if (movie_container.p.span.text != ''):
            # ^No rating but a heart
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

def scrape_letterboxd(username):
    url = get_url(username)

    # Default max number of pages
    page = 1
    last_page = 1

    reviewed_movies = []

    while page <= last_page:
        response = get(url.format(page))
        html_soup = BeautifulSoup(response.text, 'lxml')
        if last_page == 1:
            try:
                last_page = int(html_soup.find('div', class_ = 'paginate-pages').ul.find_all("li")[-1].text)
            except:
                pass

        movie_containers = html_soup.find_all('li', class_='poster-container')
        if movie_containers == []:
            return
        for movie_container in movie_containers:
            reviewed_movie = extract_single_record(movie_container)
            if reviewed_movie is not None:
                reviewed_movies.append(reviewed_movie)
        page += 1
    # print(reviewed_movies)
    return reviewed_movies
    
def scrape_imdb(link, fast):
    # eg. https://www.imdb.com/user/ur3728510/ratings
    id = link.split("ur")[1].split("/")[0]
    next_page_url = "https://www.imdb.com/user/ur" + id + '/ratings'
    headers = {"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"}

    reviewed_movies = []

    while next_page_url != '':
        response = get(next_page_url, headers=headers)
        html_soup = BeautifulSoup(response.text, 'lxml')

        try:
            next_page_url = html_soup.find('a', class_="next-page")["href"]
            if (next_page_url == '#'):
                # print(reviewed_movies)
                return reviewed_movies
            next_page_url = "https://www.imdb.com" + next_page_url
        except:
            pass

        movie_containers = html_soup.find_all('div', class_='lister-item-content')
        if movie_containers == []:
            return
        for movie_container in movie_containers:
            reviewed_movie = extract_single_record_imdb(movie_container)
            if reviewed_movie is not None:
                reviewed_movies.append(reviewed_movie)
        
        print(next_page_url)
        if (fast == True):
            return reviewed_movies

def extract_single_record_imdb(movie_container):
    reviewed_movie = {}
    reviewed_movie['imdb_id'] = movie_container.find('input', class_='ipl-rating-interactive__state')['data-tconst']
    rating = movie_container.find('div', class_='ipl-rating-star--other-user').find('span', class_='ipl-rating-star__rating').text
    reviewed_movie['rating'] = int(rating) * 10
    return reviewed_movie

def scrape_many(self, usernames, number_of_accounts, fast):
    reviewed_movies_all = []
    deleted = 0
    is_imdb = False

    for i in range (0, number_of_accounts):
        
        if 'imdb' in usernames[i - deleted]:
            is_imdb = True
            self.update_state(state='PROGRESS', meta={'status': 'Gathering ur' + usernames[i - deleted].split("ur")[1].split("/")[0] + "'s user data"})
            reviewed_movies = scrape_imdb(usernames[i - deleted], fast)
        else:
            self.update_state(state='PROGRESS', meta={'status': 'Gathering ' + usernames[i - deleted] + "'s user data"})
            reviewed_movies = scrape_letterboxd(usernames[i - deleted])
        if reviewed_movies == None:
            # Kill the app!!
            if number_of_accounts == 1:
                return None
            # Skip current username
            self.update_state(state='PROGRESS', meta={'status': 'User data for ' + usernames[i - deleted] + " could not be found, did you spell it correctly? Skipping..."})
            time.sleep(10)
            usernames.pop(i - deleted)
            number_of_accounts -= 1
            deleted += 1
        else:
            reviewed_movies_all.append(reviewed_movies)
        
    # print(reviewed_movies_all)
    return merge_for_comparison(self, reviewed_movies_all, usernames, number_of_accounts, fast, is_imdb)

# scrape_letterboxd('abrokepcbuilder')