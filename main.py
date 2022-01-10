from flask import Flask, request
from flask_cors import CORS
import random
import logging
import sys


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins":"*"}})

logging.basicConfig(level=logging.DEBUG)

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

@app.route("/test-result", methods=['POST', 'GET'])
def test_results():
  responseJson = request.get_json()
  testWords = responseJson.get('actual')
  typedWords = responseJson.get('typed')
  app.logger.info(testWords)
  response = dict()
  response['result'] = 'success'
  response['testWords'] = testWords
  response['typedWords'] = typedWords
  return response
  
    

app.run()