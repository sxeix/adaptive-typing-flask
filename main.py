from flask import Flask, request
from flask_cors import CORS
import logging
from markov import Markov, calculate_error, find_focus_sets
from data_handling_tools import get_wordset, preprocess_user_results

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

logging.basicConfig(level=logging.DEBUG)

userAgent = Markov("user")
expectedAgent = Markov("expected")


@app.route("/basic")
def test_route():
    basicResponse = dict()
    basicResponse["string"] = "this is a test string"
    return basicResponse


@app.route("/rand-words")
def get_random_words():
    return get_wordset(40, [])


@app.route("/tailored-wordset")
def get_tailored_words():
    error = calculate_error(expectedAgent, userAgent)
    focus_set = find_focus_sets(expectedAgent, error)
    # Should be a good idea to ensure each combo in the focus_set certainly has a % more than 0
    return get_wordset(30, focus_set)


@app.route("/test-result", methods=["POST", "GET"])
def test_results():
    responseJson = request.get_json()
    testWords = responseJson.get("actual")
    typedWords = responseJson.get("typed")

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
    response["result"] = "success"
    response["typedWords"] = userSet
    response["testWords"] = expectedSet
    response["focus-sets"] = focus_set
    return response



app.run()
