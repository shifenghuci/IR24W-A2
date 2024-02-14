import shelve
import pickle
from urllib.parse import urlparse
#report the 50 most common words and number of url crawled
def printFrequencies(frequencies):
    counter = 0
    for (token, count) in sorted(frequencies.items(), key=lambda item: item[1],reverse=True):  # sort each pair by value
        print(f'{token}\t{count}')
        counter = counter + 1
        if(counter == 50):
           break

with shelve.open('stats/scraped_urls') as d:
   domain = "www.ics.uci.edu"
   urls = list(d.keys())
   sub_domains = []
   for url in urls:
       if urlparse(url).netloc.endswith(domain):
           sub_domains.append(url)
   print(f'Number of url crawled: {len(urls)}')

with shelve.open('stats/word_freq') as db:
  print("Below is the 50 most common words found in the scrapped urls:")
  printFrequencies(dict(db))


with shelve.open('stats/longest_page') as longest_page:
  url = longest_page['url']
  num = longest_page['num']
  print(f'The longest page is {url}, which has {num} tokens')




