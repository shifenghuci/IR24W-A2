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
   #for url in d.values():
    #print(url)

with shelve.open('stats/word_freq') as db:
  print("Below is the 50 most common words found in the scrapped urls:")
  printFrequencies(dict(db))

try:
  with open('stats/longest_page.txt', 'r') as f:
    #longest_page = pickle.load(f)
    lines = f.readlines()
    maxLen = int(lines[1].strip())
    maxUrl = lines[0].strip()
    print(f'The longest page found in url is {maxUrl}, it has {maxLen} tokens')
except FileNotFoundError:
   print("NO RECORD")
   with open('stats/longest_page.txt', 'w') as f:
      f.write("None\n")
      f.write(str(0))

#with open('stats/ics_domain.txt', 'r') as d:
  #lines = d.readlines()
  #for url in lines:
    #print(url)


