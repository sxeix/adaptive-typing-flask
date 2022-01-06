from flask import Flask
from flask_cors import CORS
import random


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins":"*"}})

@app.route("/basic")
def test_route():
  basicResponse = dict()
  basicResponse["string"] = "this is a test string"
  return basicResponse

@app.route("/rand-words")
def get_random_words():
  randWordResponse = dict()
  words = []
  with open('words.txt', 'r') as f:
    words = f.readlines()
    words = [word.rstrip() for word in words]
  random.shuffle(words)
  sizedWordsResponse = words[0:40]
  for i, word in enumerate(sizedWordsResponse):
    randWordResponse[i] = word
  return randWordResponse
    

app.run()