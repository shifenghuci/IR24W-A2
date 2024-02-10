from bs4 import BeautifulSoup
import requests
from requests import Response
from tokenizer import yieldToken,printFrequencies
from urllib.parse import urlparse, urlunparse
from domainCheck import is_url_allowed

# Given a response object, return a generator that yield all valid hyperlink(has correct scheme and not a fragment) found from the soup_obj
def extract_hrefs(resp:Response):
  soup = BeautifulSoup(resp.text,'html.parser')
  for tag in soup.find_all('a'):
    href = tag.get('href')
    # yield links that has valid schemes and within the allowed domain
    if urlparse(href).scheme in ['http', 'https'] and is_url_allowed(href, allowed_domain):
      clean_url = urlunparse(urlparse(href)._replace(fragment= "")) #remove the fragment part
      yield(clean_url)

#Given a soup object adn a dictionary about word frequencies, update the word frequencies by word token found in the soup
def update_word_frequencies(resp: Response, freq_dict)-> None:
  soup = BeautifulSoup(resp.text,'html.parser')
  tokens = list(yieldToken(soup.get_text()))
  for token in tokens:
        freq_dict[token] = freq_dict.get(token, 0) + 1 # if new to dict, assign 1, if not, increment


# test case
seed_urls = "https://www.ics.uci.edu,https://www.cs.uci.edu,https://www.informatics.uci.edu,https://www.stat.uci.edu"
allowed_domain = {urlparse(seed_url).netloc.replace("www.", "") for seed_url in seed_urls.split(sep=",")}
downloaded_resps = {requests.get(url) for url in seed_urls.split(",")} # make polite request by asking every 0.05 seconds

word_frequency = dict()
visited_url = list()


for resp in downloaded_resps:
  #update word dict
  update_word_frequencies(resp, word_frequency)
  print(f'From {resp.url}, extracted valid links:')
  for link in extract_hrefs(resp):
    print(link)

print(f'Visited url: {seed_urls.split(",")}')
printFrequencies(word_frequency)
