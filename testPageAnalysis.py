from bs4 import BeautifulSoup
import requests
from tokenizer import yieldToken,updateWordFrequencies,printFrequencies
from urllib.parse import urlparse
seed_urls = "https://www.ics.uci.edu,https://www.cs.uci.edu,https://www.informatics.uci.edu,https://www.stat.uci.edu"
downloaded_resps = {requests.get(url) for url in seed_urls.split(",")} # make polite request by asking every 0.05 seconds

word_frequency = dict()
visited_url = list()
# return a generator that yield all valid hyperlink(has correct scheme and not a fragment) found from the soup_obj
def extract_hrefs(soup):
  for tag in soup.find_all('a'):
    href = tag.get('href')
    if urlparse(href).scheme in ['http', 'https']:
      print(href)
      yield(href)

for resp in downloaded_resps:
  html_doc = resp.text
  soup = BeautifulSoup(html_doc, 'html.parser')
  #all_text = soup.get_text()
  all_link = list(extract_hrefs(soup))
  #tokens = list(yieldToken(all_text))
  #updateWordFrequencies(tokens,word_frequency)
  visited_url.append(resp.url)

#printFrequencies(word_frequency)
print(f'list of visited urls:{visited_url}')