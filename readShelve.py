import shelve
#report the 50 most common words and number of url crawled
def printFrequencies(frequencies):
    counter = 0
    for (token, count) in sorted(frequencies.items(), key=lambda item: item[1],reverse=True):  # sort each pair by value
        print(f'{token}\t{count}')
        counter = counter + 1
        if(counter == 50):
           break

with shelve.open('word_freq') as db:
  printFrequencies(dict(db))

with shelve.open('scraped_urls') as d:
   print(f'Number of url crawled: {len(d.keys())}')

