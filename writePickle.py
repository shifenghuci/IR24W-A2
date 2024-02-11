import pickle

scrapped_urls = {"www.google.com": ["Google", 12345]}

with open('data.pickle','wb') as f:
  pickle.dump(scrapped_urls, f)
