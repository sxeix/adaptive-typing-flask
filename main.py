"""
Flask application for controlling communication to and from the UI of the AdaptiveTyping app
"""
import logging

from flask import Flask, request
from flask_cors import CORS

from data_handling_tools import (find_users, get_data_lists, get_wordset,
                                 load_user, preprocess_user_results, save_data,
                                 load_stats)
from markov import Markov, calculate_error, find_focus_sets

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

logging.basicConfig(level=logging.DEBUG)


def get_current_user(user):
    user_agent = Markov(user)
    expected_agent = Markov("expected")
    data = load_user(user)
    if not data is None:
        user_history, expected_history = get_data_lists(data)
        user_agent.train(user_history)
        expected_agent.train(expected_history)
    return user_agent, expected_agent


@app.route("/basic")
def test_route():
    basic_response = {}
    basic_response["string"] = "this is a test string"
    return basic_response


@app.route("/rand-words")
def get_random_words():
    return get_wordset(40, [])


@app.route("/tailored-wordset", methods=["POST", "GET"])
def get_tailored_words():
    response_json = request.get_json()
    user = response_json.get("user")
    user_agent, expected_agent = get_current_user(user)
    app.logger.info(f"Generating wordset for {user}")
    error = calculate_error(expected_agent, user_agent)
    focus_set = find_focus_sets(expected_agent, error)
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
    return get_wordset(30, [])


@app.route("/test-result", methods=["POST", "GET"])
def test_results():
    response_json = request.get_json()
    test_words = response_json.get("actual")
    typed_words = response_json.get("typed")
    user = response_json.get("user")
    stats = response_json.get("stats")
    user_agent, expected_agent = get_current_user(user)
    user_set, expected_set = preprocess_user_results(typed_words, test_words)

    # app.logger.info(user_set)
    # app.logger.info(expected_set)

    user_agent.train(user_set)
    expected_agent.train(expected_set)

    error = calculate_error(expected_agent, user_agent)
    focus_set = find_focus_sets(expected_agent, error)
    # app.logger.info(error)
    # app.logger.info(focus_set)

    response = {}
    response["result"] = "success"
    response["user"] = user
    response["typed_words"] = user_set
    response["test_words"] = expected_set
    response["focus-sets"] = focus_set

    app.logger.info(stats)
    save_data(user, user_agent.get_history(), expected_agent.get_history(), stats)

    return response


@app.route("/change-user", methods=["POST", "GET"])
def change_user():
    response_json = request.get_json()
    user = response_json.get("user")
    get_current_user(user)
    response = {}
    response["message"] = f"current user changed to{user}"
    response["status"] = True

    return response


@app.route("/get-users")
def get_users():
    user_list = find_users()
    app.logger.info(user_list)
    response = {}
    response["users"] = user_list
    return response

@app.route("/get-user-stats", methods=["POST", "GET"])
def get_user_stats():
    response_json = request.get_json()
    user = response_json.get('user')
    user_stats = load_stats(user)
    response = {}
    response['user'] = user
    response['stats'] = user_stats
    return response

@app.before_first_request
def startup():
    get_current_user("testuser")


if __name__ == '__main__':
    print(app.before_first_request_funcs)
    app.run()
