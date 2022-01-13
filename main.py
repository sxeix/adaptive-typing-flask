from flask import Flask, request
from flask_cors import CORS
import logging
from markov import Markov, calculate_error, find_focus_sets
from data_handling_tools import get_wordset, preprocess_user_results, load_user, get_data_lists, save_data

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

logging.basicConfig(level=logging.DEBUG)

userAgent = Markov("user")
expectedAgent = Markov("expected")

current_user = 'testuser'

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
    valid_set = True
    for item in focus_set:
        if item[2] == 0:
            valid_set = False
    if valid_set:
        return get_wordset(30, focus_set)
    else:
        return get_wordset(40, [])


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
    
    save_data(current_user, userAgent.get_history(), expectedAgent.get_history())
    
    return response


@app.before_first_request
def startup():
    data = load_user(current_user)
    userHistory, expectedHistory = get_data_lists(data)
    userAgent.train(userHistory)
    expectedAgent.train(expectedHistory)
    

if __name__ == '__main__':
    print(app.before_first_request_funcs)
    app.run()