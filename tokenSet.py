def get_tokenSet(url:str) -> set():
  #return a set of all token in the url
  return frozenset({x for x in url.split('/')})

with shelve.open('scraped_urls') as d:
  d[url] = get_tokenSet[url]

  
tokenSets = set()

url = "https://www.ics.uci.edu/community/about"

tokenSets.add(get_tokenSet(url))

# for link in hyperlinks:
#   if get_tokenSet(link) in tokenSets:
#     print("Exist token set, do not crawl")

print(get_tokenSet(url))
print(tokenSets)