import pickle

with open('longest_page', 'rb') as f:
  longest_page = pickle.load(f)
  print(longest_page)

with open('scraped_urls', 'rb') as f:
  scraped_urls = pickle.load(f)
  print(f'number of pages crawled: {len(scraped_urls)}')