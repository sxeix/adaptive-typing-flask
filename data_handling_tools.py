import random

def get_wordset(length: int, focus_set: list):
  response = dict()
  words = []
  with open('words.txt', 'r') as f:
    words = f.readlines()
    words = [word.rstrip() for word in words]
  selectedWords = []
  if not focus_set:
    random.shuffle(words)
    selectedWords = words[0:length]
  elif focus_set:
    # insert code here to select appropriate words
    # replace random.shuffle
    response["focus_set"] = focus_set
    random.shuffle(words)
    selectedWords = words[0:length]
  response["words"] = {}
  for i, word in enumerate(selectedWords):
    response["words"][i] = word
  return response
