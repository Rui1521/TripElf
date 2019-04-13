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
    nightlife = pd.read_csv('nightlife_no_dup_step1.csv')
    urls = nightlife['yelpPage'].tolist()
    return urls

def get_proxies():
    try:
        print("Request a new list of proxies")
        proxy_list_url = "" # define your proxy list url here
        proxy_res = requests.get(proxy_list_url, timeout=6.0)
        proxies = BeautifulSoup(proxy_res.text, 'html.parser').getText().split("\n")
    except Exception:
        print("proxy request failed")
        return [], False
    for i in range(len(proxies)):
        proxies[i] = proxies[i]
    return proxies, True

def crawl_page(url, proxy, verbose=False):

    global GLOBAL_COUNTER
    global PROXY

    latitude = ''
    longitude = ''
    priceRange = ''
    zipcode = ''
    
    try:
        response = requests.get(url.replace('https','http'), proxies={"http": proxy[:-3], "https": proxy[:-3]}, timeout=6.0)
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
        latitude = str(data['markers'][1]['location']['latitude']).replace(',', ' ')
        longitude = str(data['markers'][1]['location']['longitude']).replace(',', ' ')
    except Exception as e:
        if verbose: print('latitude/longitude extract fail', str(e))
    
    try:
        priceRange = r.find('dd', {'class': re.compile(r'price-description')}).getText().strip().replace(',', ' ')
    except Exception as e:
        if verbose: print('priceRange extract fail', str(e))

    try:
        zipcode = r.find('div', {'class': re.compile(r'map-box-address')}).strong.address.getText().strip()[-5:].replace(',', ' ')
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
        
    extracted = url+','+priceRange+','+zipcode+','+latitude+','+longitude
        
    if GLOBAL_COUNTER % 10 == 0:
        print(url.split("/")[-1])
        print('Global count: ' + str(GLOBAL_COUNTER))
        print(PROXY)

    return extracted, True

def crawl():
    
    urls = get_urls()

    proxies, proxy_flag = get_proxies()
    proxy_pool = cycle(proxies)
    
    print('\n**We are attempting to extract detailed nightlife information in NYC!**')
    
    with open('./nightlife_step2.csv', 'w') as nightlife_more:
        
        nightlife_more.write(
            'yelpPage,priceRange,exactZipcode,latitude,longitude')
        
        i = 0
        flag = True
        proxy = next(proxy_pool)

        while i < len(urls):  
            extracted, flag = crawl_page(urls[i], proxy)
            if not flag:
                print('proxy error, reconnect with the next proxy')
                proxies.remove(proxy)
                if len(proxies) == 10:
                    proxies, proxy_flag = get_proxies()
                    if not proxy_flag:
                        break
                proxy_pool = cycle(proxies)
                proxy = next(proxy_pool)
                print('proxy_pool:', len(proxies))
                flag = True
                continue
            i += 1
            nightlife_more.write('\n'+extracted)
            time.sleep(random.randint(1, 2) * .1931467298)

if __name__ == '__main__':
    crawl()
