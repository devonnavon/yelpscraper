import requests
from bs4 import BeautifulSoup
from ast import literal_eval

def get_yelp_page(url, format=''):
    '''
    url doesn't include yelp.com prefix
    '''
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    yelp_url = 'https://www.yelp.com/'
    url = yelp_url + url
    response = requests.get(url.format(format), headers=headers, verify=True).text
    page = BeautifulSoup(response, "lxml")
    return page

def get_city(search, city, state, page_limit = 1):
    url =  'search?find_desc=' + search + '&find_loc=' + city + '%2C%20' + state + '&start={}'
    for i in range(0,page_limit*30,30):
        page = get_yelp_request(url, i)
        if i == 0:
            links = []
            names = []
        #iterate through list of links within <h3> tags
        for y in [x.select_one('a[href*=/biz/]') for x in page.find_all('h3')]:
            if y is not None: #filter out h3s that don't have links
                links.append(y.attrs['href']) #append link attribute
                names.append(y.text.strip())
    return {'names': names,'links':links}

def get_header(page):
    return page.find('div',attrs={'class': 'content-container js-biz-details'})

def get_name(page):
    name_raw = page.find_all('h1',attrs={'class': 'biz-page-title embossed-text-white shortenough'})
    if len(name_raw) == 0:
        name_raw = page.find_all('h1',attrs={'class': 'biz-page-title embossed-text-white'})
    else:
        pass
    name = ' '.join([x.text for x in name_raw]).strip()
    return name

def get_price(header):
    try: #some places don't have a price
        price = header.find('span',attrs={'class':'business-attribute price-range'}).text
    except AttributeError:
        price = None
    return price

def get_ratings(header):
    ratings_raw = literal_eval(header.find('div', attrs={'id':"rating-details-modal-content"}).attrs['data-monthly-ratings'])
    ratings = {}
    for x in ratings_raw:
        ratings.update({int(x) : [y[1] for y in ratings_raw[x]]})
    return ratings

def get_hours(page):
    try: #some places don't have hours
        hours = [dict([x.text.strip().split('\n\n')[0:2]]) for x in page.find('table',attrs={'class':'table table-simple hours-table'}).find_all('tr')]
    except AttributeError:
        hours = None
    return hours

def get_info(page):
    info_raw = page.find('div',attrs={'class':'short-def-list'})
    info = dict(zip([x.text.strip() for x in info_raw.find_all('dt')], [x.text.strip() for x in info_raw.find_all('dd')]))
    return info

def get_reviews(page):
    reviews = []
    for p in page.find_all("div", attrs={'class': 'review-content'}):
        date = p.find('span', attrs={'class': 'rating-qualifier'}).text.strip()
        rating = float(p.find('img').attrs['alt'][:3])
        content = p.find('p', attrs={'lang': 'en'}).text
        review = {
            'date' : date,
            'rating' : rating,
            'content' : content
        }
        reviews.append(review)
    return reviews

def get_business(url, page_limit = 1, show_loader=False):
    '''
    url is shorthand yelp business url
    url = /biz/the-roosevelt-room-austin'
    page_limit = number of requests to iterate through reviews
                 number of reviews = page_limit * 20
    '''
    #headers will make it look like you are using a web browser
    reviews = []
    if show_loader:
        print('Loading Reviews: [',end='=')
        loader = '='*int(110/page_limit)
    url = url + '?start={}&sort_by=date_desc'
    for i in range(0,page_limit*20,20):
        page = get_yelp_request(url, i)
        if show_loader: print(loader,end='')
        #on the first request we get business data
        if i == 0:
            name = get_name(page)
            header = get_header(page)
            price = get_price(header)
            ratings = get_ratings(header)
            hours = get_hours(page)
            info = get_info(page)
        else:
            pass
        #on all page requests we get reviews
        reviews+=get_reviews(page)
    if show_loader: print(']')
    business = {
        'name':name,
        'price':price,
        'ratings':ratings,
        'hours':hours,
        'info':info,
        'reviews':reviews
    }
    return business
