import pickle

with open('longest_page', 'rb') as f:
  longest_page = pickle.load(f)
  print(longest_page)