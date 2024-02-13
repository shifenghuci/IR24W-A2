import shelve

def printFrequencies(frequencies):
    counter = 0
    for (token, count) in sorted(frequencies.items(), key=lambda item: item[1],reverse=True):  # sort each pair by value
        print(f'{token}\t{count}')
        counter = counter + 1
        if(counter == 50):
           break

with shelve.open('url_stat') as db:
  printFrequencies(dict(db))


