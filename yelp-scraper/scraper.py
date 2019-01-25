__author__ = 'Zexi Han'
__date__ = 'January 25th, 2019'
"""
Web scraper for Yelp listings
"""
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests import get
import argparse
import re
import codecs
import time
import random

get_yelp_page = \
    lambda zipcode, cflt, page_num: \
        'http://www.yelp.com/search?find_desc=&find_loc={0}' \
        '&ns=1{1}&start={2}'.format(zipcode, cflt, page_num)

ZIP_URL = "zipcodes_nyc.txt"
FIELD_DELIM = u'###'
LISTING_DELIM = u'((('

def get_zips():
    """
    """
    f = open(ZIP_URL, 'r+')
    zips = [int(zz.strip()) for zz in f.read().split('\n') if zz.strip() ]
    f.close()
    return zips


def crawl_page(zipcode, cflt, page_num, global_counter, verbose=False):
    """
    This method takes a page number, yelp GET param, and crawls exactly
    one page. We expect 10 listing per page.
    """
    try:
        page_url = get_yelp_page(zipcode, cflt, page_num)
        response = get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(str(e))
        return [], False

    restaurants = soup.find_all('div', attrs={'class':re.compile
            (r'^searchResult')})
    try:
        assert(len(restaurants) == 10)
    except AssertionError as e:
        # We make a dangerous assumption that yelp has 10 listing per page,
        # however this can also be a formatting issue, so watch out
        print('we have hit the end of the zip code', str(e))
        # False is a special flag, returned when quitting
        return [], global_counter, False

    extracted = []
    local_counter = 0
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
                'img', {'class': re.compile(r'^photo-box-img')})['src']
        except Exception as e:
            if verbose: print('img extract fail', str(e))
        
        try:
            title = r.find(
                'h3', {'class': re.compile(r'^heading')}).a.getText()
        except Exception as e:
            if verbose: print('title extract fail', str(e))
        
        try:
            yelpPage = 'https://www.yelp.com' + r.find(
                'h3', {'class': re.compile(r'^heading')}).a['href']
        except Exception as e:
            if verbose: print('yelp page link extraction fail', str(e))
            continue
        
        try:
            priceCategories = r.find(
                'div', {'class': re.compile(r'^priceCategory')}).contents
            if len(priceCategories) == 2:
                dollarPrice = priceCategories[0].getText()
                categories = priceCategories[1].getText().replace(', ', ';')
            else:
                categories = priceCategories[0].getText().replace(', ', ';')
        except Exception as e:
            if verbose: print("priceCategories extract fail", str(e))
        
        try:
            rating = r.find(
                'div', {'class': re.compile(r'^i-stars')})['aria-label'][0]
        except Exception as e:
            if verbose: print('rating extract fail', str(e))
        
        try:
            reviewCount = r.find(
                'span', {'class': re.compile(r'^reviewCount')}).getText().replace(' reviews', '')
        except Exception as e:
            if verbose: print('reviewCount extract fail', str(e))
        
        try:
            secondaryAttributes = r.find('div', {'class': re.compile(
                r'secondaryAttributes')}).div.contents
            if len(secondaryAttributes) == 3:
                phone = secondaryAttributes[0].getText()
                addr = secondaryAttributes[1].getText()
                district = secondaryAttributes[2].getText()
            else:
                if secondaryAttributes[0].getText()[0] == '(':
                    phone = secondaryAttributes[0].getText()
                    addr = secondaryAttributes[1].getText()
                else:
                    addr = secondaryAttributes[0].getText()
                    district = secondaryAttributes[1].getText()
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
        
        local_counter += 1
        global_counter += 1
        if local_counter % 10 == 0: 
            print('Global count: ' + str(global_counter) + ' Local count: ' + str(local_counter) + ' Zipcode: ' + str(zipcode))
        
        extracted.append(title+','+categories+','+dollarPrice+','+rating+','+reviewCount+','+img+','+yelpPage+','+addr+','+district+','+str(zipcode)+','+phone)
        
        time.sleep(random.randint(1, 2) * .931467298)

        if extracted[-1].count(',') != 10:
            return extracted, global_counter, False
        
    return extracted, global_counter, True

def crawl(zipcode=None):
    some_zipcodes = [zipcode] if zipcode else get_zips()
    global_counter = 0

    if zipcode is None:
        print('\n**We are attempting to extract all zipcodes in America!**')
    
    with open('./yelp_restaurants_listings.csv', 'w') as yelp_listings:
        yelp_listings.write('title,categories,dollarPrice,rating,reviewCount,img,yelpPage,address,district,zipcode,phone')
        for zipcode in some_zipcodes:
            page = 0
            cflt = '#cflt=restaurants'
            flag = True
            print('\n===== Attempting extraction for zipcode <', zipcode, '>=====\n')
            while flag:
                extracted, global_counter, flag = crawl_page(zipcode, cflt, page, global_counter)
                if not flag:
                    print('extraction stopped or broke at zipcode')
                    break
                for listing in extracted:
                    yelp_listings.write('\n'+listing)
                cflt = ''
                page += 10
                time.sleep(random.randint(1, 2) * .931467298)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extracts all yelp restaurant \
        data from a specified zip code (or all American zip codes if nothing \
        is provided)')
    parser.add_argument('-z', '--zipcode', type=int, help='Enter a zip code \
        you\'t like to extract from.')
    args = parser.parse_args()
    crawl(args.zipcode)
