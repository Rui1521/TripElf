__author__ = 'Zexi Han'
__date__ = 'January 25th, 2019'
"""
Web Scraper Step 1 for Yelp Business Listings
"""
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import requests
from lxml.html import fromstring
from itertools import cycle
import traceback
import argparse
import re
import codecs
import time
import random
import json

get_yelp_page = \
    lambda category, zipcode, page_num: \
        'https://www.yelp.com/search?cflt={0}&find_loc={1}' \
        '&start={2}'.format(category, zipcode, page_num)

ZIP_URL = "zipcodes_nyc.txt"
FIELD_DELIM = u'###'
LISTING_DELIM = u'((('

LOCAL_COUNTER = 0
GLOBAL_COUNTER = 0

PROXY = set()

def get_zips():
    f = open(ZIP_URL, 'r+')
    zips = [int(zz.strip()) for zz in f.read().split('\n') if zz.strip() ]
    f.close()
    return zips

def get_proxies():
    proxies = set()
    with open('./proxies.txt', 'r') as proxies_file:
        for proxy in proxies_file:
            proxies.add(proxy[:-1])
    return proxies

def crawl_page(category, zipcode, page_num, proxy, verbose=False):
    """
    This method takes a page number, yelp GET param, and crawls exactly
    one page. We expect 10 listing per page.
    """
    global LOCAL_COUNTER
    global GLOBAL_COUNTER
    global PROXY

    try:
        page_url = get_yelp_page(category, zipcode, page_num)
        response = requests.get(page_url, proxies={"http": proxy[:-3], "https": proxy[:-3]}, timeout=10.0)
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.Timeout as e:
        print("Time out!")
        return [], False, False
    except requests.RequestException as e:
        print(str(e))
        return [], False, False

    restaurants = soup.find_all('div', attrs={'class':re.compile(r'^searchResult')})

    extracted = []
    for r in restaurants:
        img = ''
        yelpPage = ''
        title = ''
        rating = ''
        reviewCount = ''
        addr = ''
        phone = ''
        district = ''
        dollarPrice = ''
        categories = ''

        try:
            img = r.find(
                'img', {'class': re.compile(r'^photo-box-img')})['src'].replace(',', ' ')
        except Exception as e:
            if verbose: print('img extract fail', str(e))
        
        try:
            title = r.find(
                'h3', {'class': re.compile(r'^heading')}).a.getText().replace(',', ' ')
        except Exception as e:
            if verbose: print('title extract fail', str(e))
        
        try:
            yelpPage = unquote('https://www.yelp.com' + r.find(
                'h3', {'class': re.compile(r'^heading')}).a['href'].replace(',', ' '))
            if 'ad_business_id' in yelpPage:
                continue
        except Exception as e:
            if verbose: print('yelp page link extraction fail', str(e))
            continue
        
        try:
            priceCategories = r.find(
                'div', {'class': re.compile(r'^priceCategory')}).contents
            if len(priceCategories) == 2:
                dollarPrice = priceCategories[0].getText().replace(',', ' ')
                categories = priceCategories[1].getText().replace(', ', ';').replace(',', ' ')
            else:
                categories = priceCategories[0].getText().replace(', ', ';').replace(',', ' ')
        except Exception as e:
            if verbose: print("priceCategories extract fail", str(e))
        
        try:
            rating = r.find(
                'div', {'class': re.compile(r'^i-stars')})['aria-label'][0]
        except Exception as e:
            if verbose: print('rating extract fail', str(e))
        
        try:
            reviewCount = r.find(
                'span', {'class': re.compile(r'^reviewCount')}).getText().replace(' reviews', '').replace(',', ' ')
        except Exception as e:
            if verbose: print('reviewCount extract fail', str(e))
        
        try:
            secondaryAttributes = r.find('div', {'class': re.compile(r'secondaryAttributes')}).div.contents
            if len(secondaryAttributes) == 3:
                phone = secondaryAttributes[0].getText().replace(',', ' ')
                addr = secondaryAttributes[1].getText().replace(',', ' ')
                district = secondaryAttributes[2].getText().replace(',', ' ')
            else:
                if secondaryAttributes[0].getText()[0] == '(':
                    phone = secondaryAttributes[0].getText().replace(',', ' ')
                    addr = secondaryAttributes[1].getText().replace(',', ' ')
                else:
                    addr = secondaryAttributes[0].getText().replace(',', ' ')
                    district = secondaryAttributes[1].getText().replace(',', ' ')
        except Exception as e:
            if verbose:
                print('secondaryAttributes extract fail', str(e))

        # if title: print('title:', title)
        # if categories: print('categories:', categories)
        # if dollarPrice: print('dollarPrice:', dollarPrice)
        # if rating: print('rating:', rating)
        # if reviewCount: print('reviewCount:', reviewCount)
        # if img: print('img:', img)
        # if yelpPage: print('yelpPage:', yelpPage)
        # if addr: print('address:', addr)
        # if district: print('district:', district)
        # if phone: print('phone:', phone)
        
        GLOBAL_COUNTER += 1
        LOCAL_COUNTER += 1

        PROXY.add(proxy[-2:])
        
        extracted.append(title+','+categories+','+dollarPrice+','+rating+','+reviewCount+','+img+','+yelpPage+','+addr+','+district+','+str(zipcode)+','+phone)
        
        
        # try:
        #     assert(extracted[-1].count(',') == 10)
        # except AssertionError as e:
        #     print("Assertion error!")
        #     return extracted, False, True
    
    time.sleep(random.randint(2, 3) * .493146729)
    
    try:
        assert(len(extracted) == 30) # restaurants: 30; shopping: 10; nightlife: 30
    except AssertionError as e:
        # False is a special flag, returned when quitting
        return extracted, False, True

    print('Global count: ' + str(GLOBAL_COUNTER) + ' Local count: ' + str(LOCAL_COUNTER) + ' Zipcode: ' + str(zipcode))
    print(PROXY)
    return extracted, True, True

def crawl():
    some_zipcodes = get_zips()
    
    global LOCAL_COUNTER

    proxies = get_proxies()
    proxy_pool = cycle(proxies)
    
    category = 'nightlife' # restaurants, shopping, nightlife

    print('\n**We are attempting to extract all ' + category + ' in NYC!**')
    
    with open('./yelp_'+category+'_listings.csv', 'w') as yelp_listings:
        yelp_listings.write('title,categories,dollarPrice,rating,reviewCount,img,yelpPage,address,district,zipcode,phone')
        for zipcode in some_zipcodes:
            proxy = next(proxy_pool) #Get a proxy from the pool
            page = 0
            flag = True
            proxy_flag = True
            LOCAL_COUNTER = 0
            print('\n===== Attempting extraction for zipcode <', zipcode, '>=====\n')
            while flag:
                extracted, flag, proxy_flag = crawl_page(category, zipcode, page, proxy)
                if not proxy_flag:
                    print('proxy not working, retry with the next one')
                    proxy = next(proxy_pool)
                    flag = True
                    continue
                if not flag:
                    if page > 30:
                        for listing in extracted:
                            yelp_listings.write('\n'+listing)
                        print('we have hit the end of the zip code, extraction stopped or broke at zipcode')
                        break
                    else:
                        print('proxy error, reconnect with the next proxy')
                        proxy = next(proxy_pool)
                        flag = True
                        continue
                for listing in extracted:
                    yelp_listings.write('\n'+listing)
                page += 30  # restaurants: 30; shopping: 10; nightlife: 30

if __name__ == '__main__':
    crawl()
