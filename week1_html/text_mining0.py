from bs4 import BeautifulSoup
from urllib import request
import nltk
import re

def main():
    # import page as html
    url = "https://www.hs.fi/"
    html = request.urlopen(url).read().decode('utf8')

    # create beatifulsoup element
    soup = BeautifulSoup(html, 'html.parser')

    # create a list of all the headers (all classes of headers contain "teaser-title-")
    list_headers = soup.findAll(class_=re.compile("teaser-title-"))

    """
    # APPROACH 1: Manually removes all html code and leaves only text
    for x in range(10): # the loop prints the first ten lines in the list
       l = str(list_headers[x]).split("<span>") # splits the line at "<span>"
       l = re.sub('[/<>]', '', l[1]) # removes all extra characters from the start and the end of the second item that is the actual text
       print(re.sub('spanh2', '', l)) # removes the 'spanh2' character string that appears at the end of the line
       print() # adds one empty line so the output looks neater
    """

    # APPROACH 2: Code-wise a bit simpler, uses BeautifulSoup's inbuilt get_text() method
    for header in list_headers: # the loop prints all (8) given headers
        l = header.get_text() # uses the get_text method to extract only the text portion of each header
        print(re.sub('.*\|', '', l)) # removes all of HS's tags from the start of headers, leaving only the headers themselves
        print() # adds one empty line so the output looks neater
main()
