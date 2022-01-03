import requests
from bs4 import BeautifulSoup
from bs4 import Tag

import pandas as pd

import time
import random

import os

def parsify_url(URL):
    page = requests.get(URL)
    html = BeautifulSoup(page.content, "html.parser")
    return html

def extract_links(html):
    links = html.find_all("h3")
    proper_links = [link.contents[0].get("href") for link in links if link.contents[0].has_attr("id")]
    return proper_links

def extract_page(html):
    dark_texts = html.find_all("span", {"class": "dark_text"})
    data = {}
    
    # I take to my list descriptions without links
    for dark_text in dark_texts:
        if dark_text.next_sibling.strip(): # If not-empty then it doesn't have links
            key = delete_colon(dark_text.contents[0])
            element = dark_text.next_sibling.strip()
            data[key] = element
    
    # I take to my list descriptions with links
    for dark_text in dark_texts:
        if not dark_text.next_sibling.strip():
            key = delete_colon(dark_text.contents[0])
            element = []
            iterator = dark_text.next_siblings
            for iterable in iterator:
                if (isinstance(iterable, Tag) and iterable.name == 'a'): # I want to get rid of line breaks
                    element.append(iterable.contents[0])
            data[key] = element
            
    # I add separately Score data, because above methods don't work in this case
    data.pop('Score')
    ratingValue = html.find('span', itemprop = 'ratingValue')
    if ratingValue is not None:
        ratingValue = ratingValue.contents[0]
        data['Score'] = ratingValue
    ratingCount = html.find('span', itemprop = 'ratingCount')
    if ratingCount is not None:
        ratingCount = ratingCount.contents[0]
        data['Score Count'] = ratingCount
    
    return data

# Every content of dark_text tag which points at data we want to scrap has colon in the end and we want to get rid of it.
def delete_colon(text):
    text_list = list(text)
    text_list = text_list[:-1]
    return "".join(text_list)

page_number = 19100
URL = "https://myanimelist.net/topanime.php?limit={}".format(page_number)
html = parsify_url(URL)

find_next = html.find_all('a', class_="link-blue-box next")
table = []

while True:
    # Test tracking
    os.system('clear')
    print(page_number)

    URL = "https://myanimelist.net/topanime.php?limit={}".format(page_number)
    html = parsify_url(URL)

    links = extract_links(html)
    htmls = [parsify_url(URL) for URL in links]
    data = [extract_page(html) for html in htmls]
    table.extend(data)

    time_delay = random.randrange(2, 10)
    time.sleep(time_delay)

    page_number += 50
    find_next = html.find_all('a', class_="link-blue-box next")
    if not find_next:
        break

df = pd.DataFrame(table)
df.to_csv('out.csv', index=False)



