from bs4 import BeautifulSoup
from urllib import request
import nltk, re

def main():
    # import page as html
    url = "https://www.hs.fi/"
    html = request.urlopen(url).read().decode('utf8')
    # create beatifulsoup element
    soup = BeautifulSoup(html, 'html.parser')

    # create a list of all the headers (caption in HS html)
    list_headers = soup.findAll(True, {'caption'})

main()
