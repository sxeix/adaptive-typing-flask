from flask import Flask, request
from flask_cors import CORS
import random
import logging
from difflib import SequenceMatcher
import re


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
  # Need to preprocess the words to remove anomalies
  testWords = responseJson.get('actual')
  typedWords = responseJson.get('typed')
  app.logger.info(testWords)
  userSet, expectedSet = preprocess_user_results(typedWords, testWords)
  response = dict()
  response['result'] = 'success'
  # response['typedWords'] = typedWords
  # response['testWords'] = testWords
  response['typedWords'] = userSet
  response['testWords'] = expectedSet
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
        app.logger.info('has ran here ' + typedWord)
        expectedFormatted.append(expectedWord)
        userFormatted.append(typedWord)

  return userFormatted, expectedFormatted

app.run()