__author__ = 'Zexi Han'
__date__ = 'January 25th, 2019'
"""
Web Scraper Step 2 for Yelp Business Listings
"""
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from lxml.html import fromstring
from itertools import cycle
import pandas as pd
import requests
import traceback
import argparse
import re
import codecs
import time
import random
import json

GLOBAL_COUNTER = 0
PROXY = set()

def get_urls():
    restaurants = pd.read_csv('restaurants_nyc.csv')
    urls = restaurants['yelpPage'].tolist()
    return urls

def get_ids():
    restaurants = pd.read_csv('restaurants_nyc.csv')
    ids = restaurants['business_id'].tolist()
    return ids

def get_proxies():
    proxies = set()
    with open('./proxies.txt', 'r') as proxies_file:
        for proxy in proxies_file:
            proxies.add(proxy[:-1])
    return proxies

def crawl_page(id, url, proxy, verbose=False):

    global GLOBAL_COUNTER
    global PROXY

    latitude = ''
    longitude = ''
    priceRange = ''
    zipcode = ''
    
    try:
        response = requests.get(url.replace('https','http'), proxies={"http": proxy[:-3], "https": proxy[:-3]}, timeout=10.0)
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.Timeout as e:
        print("Time out!")
        return [], False
    except requests.RequestException as e:
        print(str(e))
        return [], False
    
    
    r = soup.find('div', {'class': 'main-content-wrap--full'})
    if not r:
        return [], False

    try:
        json_text = r.find('div', {'class': re.compile(r'lightbox-map')})['data-map-state']
        data = json.loads(json_text)
        latitude = str(data['markers'][1]['location']['latitude']).replace('，', ' ')
        longitude = str(data['markers'][1]['location']['longitude']).replace('，', ' ')
    except Exception as e:
        if verbose: print('latitude/longitude extract fail', str(e))
    
    try:
        priceRange = r.find('dd', {'class': re.compile(r'price-description')}).getText().strip().replace('，', ' ')
    except Exception as e:
        if verbose: print('priceRange extract fail', str(e))

    try:
        zipcode = r.find('div', {'class': re.compile(r'map-box-address')}).strong.address.getText().strip()[-5:].replace('，', ' ')
    except Exception as e:
        if verbose: print('zipcode extract fail', str(e))
    
    # print(id)
    # if zipcode: print('zipcode:', zipcode)
    # if priceRange: print('priceRange:', priceRange)
    # if latitude: print('latitude: ', latitude)
    # if longitude: print('longitude: ', longitude)
    # print('----------')

    PROXY.add(proxy[-2:])
        
    GLOBAL_COUNTER += 1
        
    extracted = id+','+priceRange+','+zipcode+','+','+latitude+','+longitude
        
    if GLOBAL_COUNTER % 10 == 0:
        print('Global count: ' + str(GLOBAL_COUNTER))
        print(PROXY)

    return extracted, True

def crawl():
    
    ids = get_ids()
    urls = get_urls()

    if len(ids) != len(urls):
        raise AssertionError

    proxies = get_proxies()
    proxy_pool = cycle(proxies)
    
    print('\n**We are attempting to extract detailed business information in NYC!**')
    
    with open('./shopping_more.csv', 'w') as shopping_more:
        
        shopping_more.write(
            'businessId,priceRange,zipcode,latitude,longitude')
        
        i = 0
        flag = True
        proxy = next(proxy_pool)

        while i < len(ids):  
            extracted, flag = crawl_page(ids[i], urls[i], proxy)
            if not flag:
                print('proxy error, reconnect with the next proxy')
                proxy = next(proxy_pool)
                flag = True
                continue
            i += 1
            shopping_more.write('\n'+extracted)
            time.sleep(random.randint(0, 1) * .931467298)

if __name__ == '__main__':
    crawl()
