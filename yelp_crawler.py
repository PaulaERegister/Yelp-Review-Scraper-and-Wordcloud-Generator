import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import requests
import os
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl

default_url = 'https://www.yelp.com/search?find_desc=Restaurants&find_loc='
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def read_page(location):

    url = default_url + location[0] + ',+' + location[1]
    print("Opening ", url)
    page = urllib.request.urlopen(url,context=ctx)
    print("HTTP status", page.getcode())
    html = page.read()
    print(f"Reading finished. {len(html)} characters read.")
    return html

def request_city():
    city = input("Please enter the city and state that you want to search for: (Ex: San Jose, CA).\n")
    city = [x.strip() for x in city.split(',')]
    if len(city[0].split()) > 1:
        city[0] = '+'.join(city[0].split())
    return city

def soup_parser(html):
    soup = BeautifulSoup(html, 'html.parser')
    restaurant_names = []
    restaurant_links = []
    seen = []
    for a in soup.find_all('a'):
        if 'class' in a.attrs:
            if 'lemon' in a.attrs['class'][0]:
                if 'href' in a.attrs:
                    if '/biz' in a.attrs['href']:
                        # if len(a.attrs['href'].split(':')) != 1:
                        #     continue
                        if a.attrs['href'] in restaurant_links or a.attrs['href'].split('-')[0] in seen:
                            continue
                        else:
                            seen.append(a.attrs['href'].split('-')[0])
                            restaurant_links.append(a.attrs['href'])
    for a in soup.find_all('a'):
        if 'href' in a.attrs:
            if '/biz/' in a.attrs['href']:
                if 'read' in a.contents[0] or len(a.contents[0]) == 0 or len(a.contents[0]) == 1:
                    continue
                else:
                    restaurant_names.append(a.contents[0])
    print(restaurant_links)
    print(restaurant_names)
    for i in range(len(restaurant_links)):
        link = 'https://yelp.com'+restaurant_links[i]
        restaurant_links[i] = link
    # df = pd.DataFrame(data={'Link':restaurant_links, 'Name': restaurant_names})
    reviews = {}
    for i in range(1):
        print(f"Gathering top reviews on {restaurant_names[i]} now...")
        review_text = []
        url = restaurant_links[i]
        uh = urllib.request.urlopen(url, context=ctx)
        html = uh.read()
        soup = BeautifulSoup(html, 'html.parser')
        for p in soup.find_all('p'):
            if 'itemprop' in p.attrs:
                if p.attrs['itemprop']=='description':
                    text = p.get_text().strip()
                    review_text.append(text)
        reviews[str(restaurant_names[i])] = review_text
    for restaurant in restaurant_names:
        if restaurant in reviews:
            for review in reviews[restaurant]:
                print(review)
                print('='*100)
        else:
            print("No reviews for ", restaurant)


def main():
    location = request_city()
    print(location)
    html = read_page(location)
    soup_parser(html)
main()
