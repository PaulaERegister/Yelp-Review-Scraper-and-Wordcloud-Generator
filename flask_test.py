"""
Given a location, crawls through Yelp's results for that city, scraping the top restaurant
name and their links from the HTML using BeautifulSoup. Allows the user to view reviews by
restaurant before generating a wordcloud for a particular restaurant or for the location,
using the WordCloud library.
Derived from work done by Dr. Tirthajyoti Sarkar.
"""

from flask import Flask, render_template, request, flash, redirect, url_for, send_file, Response
import matplotlib.pyplot as plt
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
from dataclasses import dataclass
import ssl
from wordcloud import WordCloud, STOPWORDS
import io
from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


@dataclass
class Restaurant:
    name: str
    reviews: []

    def __init__(self, name, reviews):
        self.name = name
        self.reviews = reviews

    def __repr__(self):
        return "name"


app = Flask(__name__)
default_url = 'https://www.yelp.com/search?find_desc=Restaurants&find_loc='
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


@app.route('/', methods=['GET', 'POST'])
@app.route('/yelp_wordcloud', methods=['GET', 'POST'])
def index():
    """

    :return:
    """
    if request.method == 'POST':
        try:
            location = request.form['location']
            city, city_string = request_city(location)
            num_reviews = request.form['num_reviews']
            html = read_page(city)
            restaurant_names, restaurant_links, reviews, reviews_to_display = soup_parser(html, int(num_reviews))
            wordcloud_from_city(reviews, place=city_string, num_restaurant=20)
            wordcloud_reviews(reviews)
            print(reviews_to_display)
            return render_template('yelp_wordcloud.html', reviews=reviews_to_display)
        except:
            flash("Could not gather rviews for that location. Please try again.")
            return redirect(url_for('index'))
    reviews = {"None to Display": "N/A"}
    return render_template('yelp_wordcloud.html', reviews=reviews)


def request_city(city_string):
    """
    Asks the user for a city and state to use as input.
    :return:
        city: a list of [city, state]
        city_string: the original string input by the user
    """
    city = [x.strip() for x in city_string.split(',')]
    if len(city[0].split()) > 1:
        city[0] = '+'.join(city[0].split())
    return city, city_string


def read_page(location):
    """
    Generates the html from the location and default url in order to scrape data from it
    :param location: The [city, state] list for the location
    :return: HTML results for the default url + location
    """
    url = default_url + location[0] + ',+' + location[1]
    print("Opening ", url)
    page = urllib.request.urlopen(url,context=ctx)
    print("HTTP status", page.getcode())
    html = page.read()
    print(f"Reading finished. {len(html)} characters read.")
    return html


def get_restaurant_links(soup):
    """
    Scrapes through the BeautifulSoup soup parameter to find all of the links for
    the restaurants. Uses a parallel 'seen' list to only include unique URLs.
    :param soup: BeautifulSoup generated by the url + location
    :return: A list of restaurant links
    """
    restaurant_links = []
    seen = []
    for a in soup.find_all('a'):
        if 'class' in a.attrs and'lemon' in a.attrs['class'][0]:
            if 'href' in a.attrs:
                href = a.attrs['href']
                if '/biz' in href:
                    if len(href.split(':')) != 1:
                        continue
                    if href in restaurant_links or href.split('?')[0] in seen:
                        continue
                    else:
                        seen.append(href.split('?')[0])
                        restaurant_links.append(href)
    return restaurant_links


def get_restaurant_names(soup):
    """
    Gets a list of restaurant names scraped from the BeautifulSoup result
    :param soup: BeautifulSoup generated by url + location
    :return: a list of restaurant names][
    """
    restaurant_names = []
    for a in soup.find_all('a'):
        if 'href' in a.attrs:
            if '/biz/' in a.attrs['href']:
                contents = a.contents[0]
                if 'read' in contents or len(contents) == 0 or len(contents) == 1:
                    continue
                else:
                    restaurant_names.append(contents)
    return restaurant_names


def get_reviews(restaurant_links, restaurant_names, num_reviews):
    """
    Using the restaurant links and restaurant names, generates a dictionary of reviews
    :param restaurant_links: A list of URLs for all of the restaurants
    :param restaurant_names: A list of Names for all of the restaurants
    :param num_reviews A number provided by the users of the number of restaurants
        to gather reviews on.
    :return: a dictionary of reviews
    """
    for i in range(len(restaurant_links)):
        link = 'https://yelp.com'+restaurant_links[i]
        restaurant_links[i] = link

    reviews = {}
    reviews_to_display = {}
    num_reviews = min(num_reviews, len(restaurant_links), len(restaurant_names))

    for i in range(num_reviews):
        print(f"Gathering top reviews on {restaurant_names[i]} now...")
        review_text = []
        review_display = []
        url = restaurant_links[i]
        uh = urllib.request.urlopen(url, context=ctx)
        html = uh.read()
        soup = BeautifulSoup(html, 'html.parser')

        for p in soup.find_all('p'):
            if 'itemprop' in p.attrs:
                if p.attrs['itemprop'] == 'description':
                    text = p.get_text().strip()
                    review_text.append(text)
                    review_display.append([text])
        reviews[str(restaurant_names[i])] = review_text
        reviews_to_display[str(restaurant_names[i])] = review_display

    return reviews, reviews_to_display


def print_reviews(reviews, restaurant_names):
    """
    Allows the user to print a certain number of reviews or print all of them
    :param reviews: A dictionary of reviews
    :param restaurant_names: A list of restaurant names
    :return: None
    """
    prompt = "Displaying reviews: How many restaurant's reviews would you like to see?\n" \
             "\tThere are " + str(len(restaurant_names)) + " restaurants. " \
                                                           "Type 'print' to print out a list of the available" \
                                                           " restaurants. " \
                                                           "\nEnter a number or the restaurant name. Press enter to " \
                                                           "view all.\n"
    result = input(prompt)

    while not result.isdigit():

        if result == 'print':
            print_restaurant_names(restaurant_names)
            result = input(prompt)

        if result == '':
            for restaurant in restaurant_names:
                if restaurant in reviews:
                    for review in reviews[restaurant]:
                        print(review)
                        print('=' * 100)
                else:
                    print("No reviews for", restaurant)
            result = 0
            break

        else:
            if result in reviews:
                for review in reviews[result]:
                    print(review)
                    print('=' * 100)

            else:
                print("Sorry, I didn't understand that input. Try again.")
            result = input(prompt)

    for i in range(int(result)):
        if restaurant_names[i] in reviews:
            for review in reviews[restaurant_names[i]]:
                print(review)
                print('=' * 100)
        else:
            print("No reviews for", restaurant_names[i])


def print_restaurant_names(restaurant_names):
    """
    Prints out all of the restaurant names
    :param restaurant_names: a list of restaurant names
    :return: None
    """
    for i in range(len(restaurant_names)):
        print(restaurant_names[i])


def soup_parser(html, num_reviews):
    """
    This function gets the restaurant links, names, and then prompts the user for a number
    of restaurants to gather the reviews on.
    :param html: html generated by default url + location
    :param num_reviews: the number of restaurants to gather reviews on. If 0, default to all
    :return:
        restaurant_names: a list of restaurant names generated by get_restaurant_names
        restaurant_links: a list of restaurant links generated by get_restaurant_links
        reviews: a dictionary of reviews generated by get_reviews
    """
    soup = BeautifulSoup(html, 'html.parser')

    restaurant_links = get_restaurant_links(soup)
    restaurant_names = get_restaurant_names(soup)

    if num_reviews == 0:
        num_reviews = len(restaurant_links)

    reviews, reviews_to_display = get_reviews(restaurant_links, restaurant_names, num_reviews)
    print(reviews)
    return restaurant_names, restaurant_links, reviews, reviews_to_display


def wordcloud_text(text):
    """
    Creates a wordcloud from the given text, with some commonly used words being ignored
    :param text:
    :return: None
    """
    stopwords = set(STOPWORDS)
    more_stopwords = ['food', 'good', 'bad', 'came', 'place', 'restaurant', 'really', 'much', 'less', 'more']
    for word in more_stopwords:
        stopwords.add(word)
    wc = WordCloud(background_color='white', max_words=50, stopwords=stopwords, max_font_size=40)
    _ = wc.generate(text)
    plt.figure(figsize=(10, 7))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()


def wordcloud_reviews(review_dict):
    """
    Creates a wordcloud from the reviews of restaurants in the review_dict, allowing the
    user to choose the restaurant to view a wordcloud for.
    :param review_dict: A dictionary of restaurants and their reviews
    :return: None
    """
    stopwords = set(STOPWORDS)
    more_stopwords = ['food', 'good', 'bad', 'came', 'place', 'restaurant', 'really', 'much', 'less', 'more']
    for word in more_stopwords:
        stopwords.add(word)

    wc = WordCloud(background_color="white", max_words=50, stopwords=stopwords, max_font_size=40)
    prompt = "Building wordcloud from reviews! Press enter to view a wordcloud for each, or enter a " \
             "restaurant name to build one from. Enter 0 to stop.\n"
    result = input(prompt)

    while result != 0:
        if result == '':
            for restaurant in review_dict:
                wordcloud(wc, review_dict[restaurant], restaurant)
            break
        if result in review_dict:
            wordcloud(wc, review_dict[result], result)
            result = input(prompt)
        else:
            print("I didn't understand that.")
            result = input(prompt)


def wordcloud(wc, restaurant, restaurant_name):
    """

    :param wc:
    :param restaurant:
    :param restaurant_name:
    :return:
    """
    text = '\n'.join(restaurant)
    _ = wc.generate(text)

    plt.figure(figsize=(10, 7))
    plt.title(f"Wordcloud for {restaurant_name}\n", fontsize=20)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()


def plot_wc(wc, place=None, restaurant=None):
    """

    :param wc:
    :param place:
    :param restaurant:
    :return:
    """
    plt.figure(figsize=(12, 8))

    if place is not None:
        plt.title("{}\n".format(place), fontsize=20)

    if restaurant is not None:
        plt.title("{}\n".format(restaurant), fontsize=20)

    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    img = BytesIO()
    wc.to_image().save(img, 'PNG')
    img.seek(0)
    return send_file(img, mimetype='image/png')
    plt.show()


@app.route('/wc.png')
def wordcloud_from_city(review_dict, place=None, num_restaurant=10, num_reviews=20, stopword_list=None,
                        disable_default_stopwords=False, verbosity=0):
    """

    :param review_dict:
    :param place:
    :param num_restaurant:
    :param num_reviews:
    :param stopword_list:
    :param disable_default_stopwords:
    :param verbosity:
    :return:
    """
    text = ""

    for restaurant in review_dict:
        text_restaurant = '\n'.join(review_dict[restaurant])
        text += text_restaurant

    # Add custom stopwords to the default list
    stopwords = set(STOPWORDS)
    more_stopwords = ['food', 'good', 'bad', 'best', 'amazing', 'go', 'went', 'came', 'come', 'back', 'place',
                      'restaurant',
                      'really', 'much', 'less', 'more', 'order', 'ordered', 'great', 'time', 'wait', 'table',
                      'everything',
                      'take', 'definitely', 'sure', 'recommend', 'recommended', 'delicious', 'taste', 'tasty',
                      'menu', 'service', 'meal', 'experience', 'got', 'night', 'one', 'will', 'made', 'make',
                      'bit', 'dish', 'dishes', 'well', 'try', 'always', 'never', 'little', 'big', 'small', 'nice',
                      'excellent']
    if not disable_default_stopwords:
        for word in more_stopwords:
            stopwords.add(word)

    if stopword_list is not None:
        for word in stopword_list:
            stopwords.add(word)

    wc = WordCloud(background_color="white", max_words=50, stopwords=stopwords, max_font_size=40, scale=3)
    _ = wc.generate(text)

    plot_wc(wc, place=place)
    img = BytesIO()
    wc.to_image().save(img, 'PNG')
    img.seek(0)
    return send_file(img, mimetype='image/png')


def main():
    """

    """
    app.secret_key = 'super secret key'
    app.run(debug=True)


main()
