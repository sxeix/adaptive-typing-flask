import random

def get_wordset(length: int, tailored: list):
  response = dict()
  words = []
  with open('words.txt', 'r') as f:
    words = f.readlines()
    words = [word.rstrip() for word in words]
  selectedWords = []
  if not tailored:
    random.shuffle(words)
    selectedWords = words[0:length]
  elif tailored:
    # insert code here to select appropriate words
    pass
  for i, word in enumerate(selectedWords):
    response[i] = word
  return response
