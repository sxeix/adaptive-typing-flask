import random
from difflib import SequenceMatcher
import re
import json
import os
from this import d
from xml.dom.minidom import CharacterData

def get_wordset(length: int, focus_set: list):
    response = dict()
    words = read_words()
    selectedWords = []
    if not focus_set:
        random.shuffle(words)
        selectedWords = words[0:length]
    elif focus_set:
        response["focus_set"] = focus_set
        selectedWords = get_tailored_words(focus_set, length)
    response["words"] = {}
    for i, word in enumerate(selectedWords):
        response["words"][i] = word
    return response


def get_tailored_words(focus_set: list, length: int):
    characterCombos = []
    containsThree = []
    containsTwo = []
    containsOne = []
    for tup in focus_set:
        characterCombos.append(tup[0] + tup[1])
    words = read_words()
    random.shuffle(words)
    if len(characterCombos != 3):
        return get_wordset(length, [])
    a, b, c = characterCombos
    for word in words:
        wordContainsCombo = [a in word, b in word, c in word]
        containsCount = 0
        for x in wordContainsCombo:
            if x == True:
                containsCount += 1
        if containsCount == 3:
            containsThree.append(word)
        elif containsCount == 2:
            containsTwo.append(word)
        elif containsCount == 1:
            containsOne.append(word)
    totalContains = containsThree + containsTwo + containsOne
    if len(totalContains) > length:
        totalContains = totalContains[0:length]
    elif len(totalContains) < length:
        neededWords = length - len(totalContains)
        while neededWords > 0:
            if not words[neededWords] in totalContains:
                totalContains.append(word[neededWords])
                neededWords -= 1
    random.shuffle(totalContains)
    return totalContains


def read_words():
    words = []
    with open("words.txt", "r") as f:
        words = f.readlines()
        words = [word.rstrip() for word in words]
    return words


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
            containsIntegers = re.search("\d", typedWord)
            containsSpecialChars = any(
                char in "!@#$%^&*()-+?_=,<>/" for char in typedWord
            )
            if similarity >= 0.7 and not (containsIntegers or containsSpecialChars):
                expectedFormatted.append(expectedWord)
                userFormatted.append(typedWord)
    return userFormatted, expectedFormatted

def load_user(username: str):
    path = os.path.expanduser('~/Documents') + f"/AdaptiveTyping/{username}.json"
    file = open(path)
    data = json.load(file)
    return data

def save_data(username: str, typedHistory: list, expectedHistory: list):
    path = os.path.expanduser('~/Documents') + f"/AdaptiveTyping/{username}.json"
    
    data = dict()
    data['typed'] = typedHistory
    data['expected'] = expectedHistory
    
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)

def get_data_lists(savedata):
    userHistory = savedata['typed']
    expectedHistory = savedata['expected']
    return userHistory, expectedHistory