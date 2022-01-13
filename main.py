from flask import Flask, request
from flask_cors import CORS
import random
import logging
from difflib import SequenceMatcher
import re
from markov import Markov, calculate_error, find_focus_sets


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins":"*"}})

logging.basicConfig(level=logging.DEBUG)

userAgent = Markov('user')
expectedAgent = Markov('expected')
  
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

  userSet, expectedSet = preprocess_user_results(typedWords, testWords)
  
  # app.logger.info(userSet)
  # app.logger.info(expectedSet)
  
  userAgent.train(userSet)
  expectedAgent.train(expectedSet)

  error = calculate_error(expectedAgent, userAgent)
  focus_set = find_focus_sets(expectedAgent, error)
  # app.logger.info(error)
  # app.logger.info(focus_set)

  response = dict()
  response['result'] = 'success'
  response['typedWords'] = userSet
  response['testWords'] = expectedSet
  response['focus-sets'] = focus_set
  return response


def preprocess_user_results(typed: list, expected: list):
  expectedFormatted = list()
  userFormatted = list()
  for i, tWord in enumerate(typed):
    typedWord = tWord.lower()
    expectedWord = expected[i].lower()
    if typedWord == expectedWord:
      expectedFormatted.append(expectedWord)
      userFormatted.append(typedWord)
    elif typedWord != expectedWord:
      # caluclate similarity of two strings
      # only cater if they are more than 70% similar
      # might need to improve this
      # also checks that there's no integers in the word
      similarity = SequenceMatcher(None, typedWord, expectedWord).ratio()
      containsIntegers = re.search('\d', typedWord)
      containsSpecialChars = any(char in "!@#$%^&*()-+?_=,<>/" for char in typedWord)
      if similarity >= 0.7 and not (containsIntegers or containsSpecialChars):
        expectedFormatted.append(expectedWord)
        userFormatted.append(typedWord)

  return userFormatted, expectedFormatted

app.run()