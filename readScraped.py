import pickle
if __name__ == "__main__":
  try:
    with open("data.pickle", 'rb') as f:
      urls = pickle.load(f)
      print(urls)
  except FileNotFoundError:
      print("File not found")