"""
Set of various functions that the main flask app depends on to function properly.
Mostly for generating wordsets & saving/loading data.
"""
import json
import os
import random
import re
from difflib import SequenceMatcher
from os import listdir


def get_wordset(length: int, focus_set: list):
    response = {}
    words = read_words()
    selected_words = []
    if not focus_set:
        random.shuffle(words)
        selected_words = words[0:length]
    elif focus_set:
        response["focus_set"] = focus_set
        selected_words = get_tailored_words(focus_set, length)
    response["words"] = {}
    for i, word in enumerate(selected_words):
        response["words"][i] = word
    return response


def get_tailored_words(focus_set: list, length: int):
    character_combos = []
    contains = {}
    contains['1']= []
    contains['2']= []
    contains['3']= []
    for tup in focus_set:
        character_combos.append(tup[0] + tup[1])
    words = read_words()
    random.shuffle(words)
    if len(character_combos) != 3:
        return get_wordset(length, [])
    char_a, char_b, char_c = character_combos # pylint: disable=unbalanced-tuple-unpacking
    for word in words:
        word_contains_combo = [char_a in word, char_b in word, char_c in word]
        countains_count = 0
        for char_combo in word_contains_combo:
            if char_combo is True:
                countains_count += 1
        if countains_count == 3:
            contains['3'].append(word)
        elif countains_count == 2:
            contains['2'].append(word)
        elif countains_count == 1:
            contains['1'].append(word)
    total_contains = contains['3'] + contains['2'] + contains['1']
    if len(total_contains) > length:
        total_contains = total_contains[0:length]
    elif len(total_contains) < length:
        needed_words = length - len(total_contains)
        while needed_words > 0:
            if not words[needed_words] in total_contains:
                total_contains.append(words[needed_words])
                needed_words -= 1
    random.shuffle(total_contains)
    return total_contains


def read_words():
    words = []
    with open("words.txt", "r", encoding='UTF-8') as file:
        words = file.readlines()
        words = [word.rstrip() for word in words]
    return words


def preprocess_user_results(typed: list, expected: list):
    expected_formatted_word = []
    user_formatted = []
    for i, pre_process_typed_word in enumerate(typed):
        typed_word = pre_process_typed_word.lower()
        expected_word = expected[i].lower()
        if typed_word == expected_word:
            expected_formatted_word.append(expected_word)
            user_formatted.append(typed_word)
        elif typed_word != expected_word:
            # caluclate similarity of two strings
            # only cater if they are more than 70% similar
            # might need to improve this
            # also checks that there's no integers in the word
            similarity = SequenceMatcher(None, typed_word, expected_word).ratio()
            contains_integers = re.search(r"\d", typed_word)
            contains_special_chars = any(
                char in "!@#$%^&*()-+?_=,<>/" for char in typed_word
            )
            if similarity >= 0.7 and not (contains_integers or contains_special_chars):
                expected_formatted_word.append(expected_word)
                user_formatted.append(typed_word)
    return user_formatted, expected_formatted_word


def load_user(username: str):
    path = os.path.expanduser('~/Documents') + \
        f"/AdaptiveTyping/{username}.json"
    if os.path.exists(path):
        with open(path, encoding='UTF-8') as file:
        # file = open(path, encoding='UTF-8')
            data = json.load(file)
        return data
    return None


def save_data(username: str, typed_history: list, expected_history: list, stats: dict):
    filename = f'/{username}.json'
    stats_filename = f'/{username}_stats.json'
    path = os.path.expanduser('~/Documents/AdaptiveTyping')
    if not os.path.exists(path):
        os.makedirs(path)
    data = {}
    data['typed'] = typed_history
    data['expected'] = expected_history
    with open(path+filename, 'w+', encoding='UTF-8') as file:
        json.dump(data, file, indent=4)
    # Use a second file for the statistics
    # Must only save if there is a focus-set involved in the test
    if not stats.get('focus-set'):
        return
    if not os.path.isfile(path+stats_filename):
        with open(path+stats_filename, mode='w+', encoding='UTF-8') as file:
            json.dump([stats], file, indent=4)
    else:
        with open(path+stats_filename, mode='r', encoding='UTF-8') as file:
            stat_history = json.load(file)
            stat_history.append(stats)
        with open(path+stats_filename, mode='w', encoding='UTF-8') as file:
            json.dump(stat_history, file, indent=4)


def get_data_lists(savedata):
    user_history = savedata['typed']
    expected_history = savedata['expected']
    return user_history, expected_history


def find_users():
    # Need to test that if the logic fixes the issue listed on Github
    path = os.path.expanduser('~/Documents/AdaptiveTyping')
    if os.path.exists(path) and len(listdir(path)) > 1:
        files = listdir(path)
        trimmed_files = []
        for file in files:
            trimmed_file = file[:len(file)-5]
            if not '_stats' in trimmed_file:
                trimmed_files.append(file[:len(file)-5])
        return trimmed_files
    return []

def load_stats(user: str):
    stats_filename = f'/{user}_stats.json'
    path = os.path.expanduser('~/Documents/AdaptiveTyping')
    history = {}
    if os.path.isfile(path+stats_filename):
        with open(path+stats_filename, mode='r', encoding='UTF-8') as file:
            stat_history = json.load(file)
            history = stat_history
    return history
