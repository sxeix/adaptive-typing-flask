from flask import Flask, request
from flask_cors import CORS
import logging
from markov import Markov, calculate_error, find_focus_sets
from data_handling_tools import get_wordset, preprocess_user_results, load_user, get_data_lists, save_data, find_users

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

logging.basicConfig(level=logging.DEBUG)

def get_current_user(user):
    userAgent = Markov(user)
    expectedAgent = Markov("expected")
    data = load_user(user)
    if not data == None:
        userHistory, expectedHistory = get_data_lists(data)
        userAgent.train(userHistory)
        expectedAgent.train(expectedHistory)
    return userAgent, expectedAgent

@app.route("/basic")
def test_route():
    basicResponse = dict()
    basicResponse["string"] = "this is a test string"
    return basicResponse


@app.route("/rand-words")
def get_random_words():
    return get_wordset(40, [])


@app.route("/tailored-wordset", methods=["POST", "GET"])
def get_tailored_words():
    responseJson = request.get_json()
    user = responseJson.get("user")
    userAgent, expectedAgent = get_current_user(user)
    app.logger.info(f"Generating wordset for {user}")
    error = calculate_error(expectedAgent, userAgent)
    focus_set = find_focus_sets(expectedAgent, error)
    # Should be a good idea to ensure each combo in the focus_set certainly has a % more than 0
    valid_set = False
    if len(focus_set) == 3:
        valid_set = True
    for item in focus_set:
        if item[2] == 0:
            valid_set = False
    if valid_set:
        app.logger.info(focus_set)
        return get_wordset(30, focus_set)
    else:
        return get_wordset(30, [])


@app.route("/test-result", methods=["POST", "GET"])
def test_results():
    responseJson = request.get_json()
    testWords = responseJson.get("actual")
    typedWords = responseJson.get("typed")
    user = responseJson.get("user")
    userAgent, expectedAgent = get_current_user(user)
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
    response["user"] = user
    response["typedWords"] = userSet
    response["testWords"] = expectedSet
    response["focus-sets"] = focus_set
    
    save_data(user, userAgent.get_history(), expectedAgent.get_history())
    
    return response

@app.route("/change-user", methods=["POST", "GET"])
def change_user():
    responseJson = request.get_json()
    user = responseJson.get("user")
    get_current_user(user)
    response = dict()
    response["message"] = f"current user changed to{user}"
    response["status"] = True
    
    return response
    
@app.route("/get-users")    
def get_users():
    userList = find_users()
    app.logger.info(userList)
    response = dict()
    response["users"] = userList
    return response

@app.before_first_request
def startup():
    get_current_user("testuser")

if __name__ == '__main__':
    print(app.before_first_request_funcs)
    app.run()