import shelve
import pickle

english_stopwords = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", 
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", 
    "can", "couldn't", "d", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", 
    "each", "few", "for", "from", "further", 
    "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", 
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", 
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", 
    "let's", 
    "me", "more", "most", "mustn't", "my", "myself", 
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", 
    "out", "over", "own", 
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", 
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", 
    "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", 
    "under", "until", "up", 
    "very", 
    "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", 
    "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", 
    "would", "wouldn't", 
    "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}
#report the 50 most common words and number of url crawled
def printFrequencies(frequencies):
    counter = 0
    for (token, count) in sorted(frequencies.items(), key=lambda item: item[1],reverse=True):  # sort each pair by value
        if (token not in english_stopwords):
          #print(f'{token}\t{count}')
          counter = counter + 1
        if(counter == 50):
           break

with shelve.open('stats/scraped_urls') as d:
  print(f'Number of url crawled: {len(d.keys())}')
  urlCount = 0
  hasTag = False
  for url in d.values():
    for s in url:
      if "#" in s:
        hasTag = True
    if hasTag:
      hasTag = False
    else:
      urlCount+=1
  print(urlCount)

with shelve.open('stats/word_freq') as db:
  #print("Below is the 50 most common words found in the scrapped urls:")
  printFrequencies(dict(db))

try:
  with open('stats/longest_page.txt', 'r') as f:
    #longest_page = pickle.load(f)
    lines = f.readlines()
    maxLen = int(lines[1].strip())
    maxUrl = lines[0].strip()
    #print(f'The longest page found in url is {maxUrl}, it has {maxLen} tokens')
except FileNotFoundError:
   print("NO RECORD")
   with open('stats/longest_page.txt', 'w') as f:
      f.write("None\n")
      f.write(str(0))

#with open('stats/ics_domain.txt', 'r') as d:
  #lines = d.readlines()
  #for url in lines:
    #print(url)


