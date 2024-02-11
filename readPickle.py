import pickle

file_name = 'data.pickle'

with open(file_name, 'rb') as f:
  print(pickle.load(f))