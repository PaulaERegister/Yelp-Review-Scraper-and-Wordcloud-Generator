"""

"""
import matplotlib.pyplot as plt
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
from wordcloud import WordCloud, STOPWORDS

default_url = 'https://www.yelp.com/search?find_desc=Restaurants&find_loc='
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def request_city():
    """

    :return:
    """
    city_string = input("Please enter the city and state that you want to search for: (Ex: San Jose, CA).\n")
    city = [x.strip() for x in city_string.split(',')]
    if len(city[0].split()) > 1:
        city[0] = '+'.join(city[0].split())
    return city, city_string


def read_page(location):
    """

    :param location:
    :return:
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

    :param soup:
    :return:
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

    :param soup:
    :return:
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


def get_reviews(restaurant_links, restaurant_names):
    """

    :param restaurant_links:
    :param restaurant_names:
    :return:
    """
    for i in range(len(restaurant_links)):
        link = 'https://yelp.com'+restaurant_links[i]
        restaurant_links[i] = link
    # df = pd.DataFrame(data={'Link':restaurant_links, 'Name': restaurant_names})

    reviews = {}
    for i in range(len(restaurant_links)):
        print(f"Gathering top reviews on {restaurant_names[i]} now...")
        review_text = []
        url = restaurant_links[i]
        uh = urllib.request.urlopen(url, context=ctx)
        html = uh.read()
        soup = BeautifulSoup(html, 'html.parser')
        for p in soup.find_all('p'):
            if 'itemprop' in p.attrs:
                if p.attrs['itemprop'] == 'description':
                    text = p.get_text().strip()
                    review_text.append(text)
        reviews[str(restaurant_names[i])] = review_text
    return reviews


def print_reviews(reviews, restaurant_names):
    """

    :param reviews:
    :param restaurant_names:
    :return:
    """
    for restaurant in restaurant_names:
        if restaurant in reviews:
            for review in reviews[restaurant]:
                print(review)
                print('='*100)
        else:
            print("No reviews for", restaurant)


def soup_parser(html):
    """

    :param html:
    :return:
    """
    soup = BeautifulSoup(html, 'html.parser')

    restaurant_links = get_restaurant_links(soup)
    restaurant_names = get_restaurant_names(soup)
    reviews = get_reviews(restaurant_links, restaurant_names)
    return restaurant_names, restaurant_links, reviews


def wordcloud_text(text):
    """

    :param text:
    :return:
    """
    stopwords = set(STOPWORDS)
    more_stopwords = ['food','good','bad','came','place','restaurant','really','much','less','more']
    for word in more_stopwords:
        stopwords.add(word)
    wc = WordCloud(background_color='white',max_words=50, stopwords=stopwords,max_font_size=40)
    _=wc.generate(text)
    plt.figure(figsize=(10, 7))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()


def wordcloud_reviews(review_dict):
    """

    :param review_dict:
    :return:
    """
    stopwords = set(STOPWORDS)
    more_stopwords = ['food', 'good', 'bad', 'came', 'place', 'restaurant', 'really', 'much', 'less', 'more']
    for word in more_stopwords:
        stopwords.add(word)

    wc = WordCloud(background_color="white", max_words=50, stopwords=stopwords, max_font_size=40)

    for restaurant in review_dict:
        text = '\n'.join(review_dict[restaurant])
        _ = wc.generate(text)

        plt.figure(figsize=(10, 7))
        plt.title(f"Wordcloud for {restaurant}\n", fontsize=20)
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
    plt.show()


def wordcloud_from_city(review_dict, place=None,num_restaurant=10,num_reviews=20,stopword_list=None,
                   disable_default_stopwords=False,verbosity=0):
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
    # if place == None:
    #     review_dict = get_reviews_place(num_restaurant=num_restaurant, num_reviews=num_reviews, verbosity=verbosity)
    # else:
    #     review_dict = get_reviews_place(num_restaurant=num_restaurant, num_reviews=num_reviews,
    #                                     place=place, verbosity=verbosity)

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

    return wc


def main():
    """

    """
    location, location_str = request_city()
    html = read_page(location)
    x, y, z = soup_parser(html)
    wordcloud_from_city(z, place=location_str, num_restaurant=20)


main()

