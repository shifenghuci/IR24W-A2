import shelve
import pickle
#report the 50 most common words and number of url crawled
def printFrequencies(frequencies):
    counter = 0
    for (token, count) in sorted(frequencies.items(), key=lambda item: item[1],reverse=True):  # sort each pair by value
        print(f'{token}\t{count}')
        counter = counter + 1
        if(counter == 50):
           break

with shelve.open('stats/scraped_urls') as d:
   print(f'Number of url crawled: {len(d.keys())}')

with shelve.open('stats/word_freq') as db:
  print("Below is the 50 most common words found in the scrapped urls:")
  printFrequencies(dict(db))

try:
  with open('stats/longest_page', 'rb') as f:
    longest_page = pickle.load(f)
    print(f'The longest page found in url is {longest_page[0]}, it has {longest_page[1]} tokens')
except FileNotFoundError:
   print("NO RECORD")
   with open('stats/longest_page', 'wb') as f:
        pickle.dump((None,0), f)


