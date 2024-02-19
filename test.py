from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urlparse
from tokenizer import yieldToken
import shelve
import pickle
from utils.response import Response
import scraper

def get_hrefs(resp):
    #return all hyperlink found from the url
    soup = BeautifulSoup(resp.text, 'html.parser')
    return [tag.get('href') for tag in soup.find_all('a')]

def get_hrefs(url):
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        hrefs = []
        for tag in soup.find_all('a'):
            hrefs.append(tag.get('href'))
        return hrefs
def get_tokenSet(url:str):
  #return a set of all token in the url
  return frozenset({x for x in url.split('/')})

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

def detectedTrap(url):
    path_token = urlparse(url).path.split('/')
    path_depth = len(path_token)
    DEPTH_THRESHOLD = 6
    calendar_words = {'events', 'schedule', 'news', 'page', 'appointments', 'date'}
    if path_depth > DEPTH_THRESHOLD:
        return True
    elif any((token in calendar_words) for token in path_token):
        return True
    else:
        return False

def yieldToken(text:str):
    # return a generator of token to lower case from a generator of file
    pattern = re.compile(r'[a-zA-Z0-9]+', re.IGNORECASE)  # pattern being any sequence of alphanumeric character
    return (token.lower() for token in pattern.findall(text) if len(token) > 1) 

def extract_next_links(url, resp):
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    '''
    Expected cases & handle:
        1.absolute url: append directly to links
        2.relative url: convert to absolute and append to links
        3.fragment: ignore, don't append
        5.None: ignore, don't append
        6.Non website scheme: ignore, don't append
        7.url lacking scheme: apply scheme and append to links
    '''

    # update dict of scraped urls
    with shelve.open('stats/scraped_urls') as d:
        d[url] = get_tokenSet(url)

    absoluteLinks = []
    hyperlinks = []
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    for hrefs in soup.find_all('a'):
        hyperlinks.append(hrefs.get('href'))

    # updates longest page
    tokens = list(yieldToken(soup.get_text()))
    num_words = len(tokens)
    with shelve.open('stats/longest_page') as longest_page:
        #update longest_page
        if 'num' in longest_page:
            if num_words > longest_page['num']:
                longest_page['url'] = url
                longest_page['num'] = num_words
        else:
            longest_page['num'] = 0
            longest_page['url'] = url

    # updates frequency of each word from url
    with shelve.open('stats/word_freq') as word_freq:
        for token in tokens:
            word_freq[token] = word_freq.get(token, 0) + 1
 
    # converts links to absolute links if needed and adds to absoluteLinks to be returned
    for link in set(hyperlinks):
        if not link:
            continue #skip None
        if link.startswith('http') or link.startswith('https'):
            #is complete url
            absoluteLinks.append(link)
        if link.startswith('//'):
            #missing scheme
            absoluteLinks.append(f'{urlparse(url).scheme}:{link}') #Give it the same scheme as the original url
        elif link.startswith('/'):
            #is relative
            if url[-1] == '/':
                url = url[:-1] #normalize self-directing page, ie: http://www.ics.uci.edu/ -> http://www.ics.uci.edu
            absolute_url = f'{url}{link}'
            absoluteLinks.append(absolute_url)
        else:
            # The fragment, mailto, tel got ignored
            continue
    return absoluteLinks


url = "https://www.cs.uci.edu/sangeetha-abdu-jyothi-named-a-rising-star-in-networking-and-communications/#more-3900/event/2017-computer-science-research-showcase/event/2017-computer-science-research-showcase/event/2017-computer-science-research-showcase/event/2017-computer-science-research-showcase"

testingLink = "https://ics.uci.edu/community/news/notes/index#dechter_2010_uai_challenge"

u = "https://www.ics.uci.edu/~saeed/index.html/community/alumni/grad/forms_policies/index/accessibility-statement/academics/course-updates/research-areas"

t = "hello 1 2 3 a a a b b b"

web = "https://www.stat.uci.edu/qu-named-2024-ims-medallion-lecturer"

web2 = "https://www.cs.uci.edu"

ics = "https://ics.uci.edu"
response1 = requests.get(web)
response2 = requests.get(ics)
response3 = requests.get(web2)
#print(response1)
#content = response.text
respd = {"url": "https://www.stat.uci.edu/qu-named-2024-ims-medallion-lecturer", "status": 200, "response": response1}
respd2 = {"url": "https://ics.uci.edu", "status": 200, "response": response2}
respd3 = {"url": "https://www.cs.uci.edu", "status": 200, "response": response3}
ob = Response(respd)
ob.raw_response = response1
ob2 = Response(respd2)
ob2.raw_response = response2
ob3 = Response(respd3)
ob3.raw_response = response3
#print(ob)
#print(extract_next_links(web,ob))
#print(web)
#links = scraper.extract_next_links(web, ob)
#print(links)
#links.append("https://www.stat.uci.edu/qu-named-2024-ims-medallion-lecturer")
#links.append("https://www.stat.uci.edu/qu-named-2024-ims-medallion-lecturer/1/2/3/4/5/6/7")
#for l in links:
    #print(l)
    #print(scraper.is_valid(l))

with open('stats/longest_page.txt', 'w') as t:
            print("RESETTING LONGEST PAGE")
            #pickle.dump((None,0),t)
            t.write("None\n")
            t.write("0")

with open('stats/ics_domain.txt', 'w') as u:
            u.write("")


print(scraper.scraper("https://www.stat.uci.edu/qu-named-2024-ims-medallion-lecturer",ob))
print(scraper.scraper("https://vision.ics.uci.edu",ob2))
print(scraper.scraper("https://www.cs.uci.edu",ob3))

#page = requests.get(u)
#soup = BeautifulSoup(page.text)
#tokens = list(yieldToken(soup.get_text()))
#print(list(yieldToken(t)))
#print(tokens)
#print(detectedTrap(u))
#print(get_hrefs(testingLink))

#print("hello")
#print(scraper.detectedTrap("https://www.stat.uci.edu/qu-named-2024-ims-medallion-lecturer/hello/hello"))


#print(urlparse(url).path)
#print(urlparse(url).fragment)
#print(exceedRepeatedThreshold(url))

