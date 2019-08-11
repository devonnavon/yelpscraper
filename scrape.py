import requests
import certifi
from bs4 import BeautifulSoup
from ast import literal_eval

def single(url):
    #Headers will make it look like you are using a web browser
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    reviews = []
    yelp = 'https://www.yelp.com/'
    final_url = yelp + url.split('?')[0] + '?start={}&sort_by=date_desc'

    for i in range(0,500,20):
        final_url.format(i)
        response = requests.get(url, headers=headers, verify=False).text
        page = BeautifulSoup(response, "lxml")
        #on the first request we get business data
        if i == 0:
            header = page.find('div',attrs={'class': 'content-container js-biz-details'})
            name = header.find_all('h1',attrs={'class': 'biz-page-title embossed-text-white shortenough'})[1].text
            price = header.find('span',attrs={'class':'business-attribute price-range'}).text
            ratings_raw = literal_eval(header.find('div', attrs={'id':"rating-details-modal-content"}).attrs['data-monthly-ratings'])
            ratings = {}
            for x in ratings_raw:
                ratings.update({int(x) : [y[1] for y in ratings_raw[x]]})
            hours = [dict([x.text.strip().split('\n\n')[0:2]]) for x in page.find('table',attrs={'class':'table table-simple hours-table'}).find_all('tr')]
            info_raw = page.find('div',attrs={'class':'short-def-list'})
            info = dict(zip([x.text.strip() for x in info_raw.find_all('dt')], [x.text.strip() for x in info_raw.find_all('dd')]))
        else: pass
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

    scrape = {
        'name':name,
        'price':price,
        'ratings':ratings,
        'hours':hours,
        'info':info,
        'reviews':reviews
    }
    return scrape
