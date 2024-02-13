from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
def get_hrefs(resp):
    #return all hyperlink found from the url
    soup = BeautifulSoup(resp.text, 'html.parser')
    return [tag.get('href') for tag in soup.find_all('a')]

def exceedRepeatedThreshold(url)-> True|False:
    #return true indicating if the url's path contain repeated pattern that exceed a certain threshold
    THRESHOLD = 1
    d = {}
    non_domain = urlparse(url).path + urlparse(url).fragment + urlparse(url).query
    tokens = non_domain.split('/')
    for x in tokens:
        if x != '': #skipping empty space
          d[x] = d.get(x,0) + 1
    return any(value > THRESHOLD for value in d.values())


url = "https://www.cs.uci.edu/sangeetha-abdu-jyothi-named-a-rising-star-in-networking-and-communications/#more-3900/event/2017-computer-science-research-showcase/event/2017-computer-science-research-showcase/event/2017-computer-science-research-showcase/event/2017-computer-science-research-showcase"

print(urlparse(url).path)
print(urlparse(url).fragment)
print(exceedRepeatedThreshold(url))

