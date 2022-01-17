"""
Markov model implementation that is used to observe a user's typing.
What is learnt can then be compared to what their Markov transition model should have looked like and highlight errors.
"""
import pandas as pd
import numpy as np
import sys

np.set_printoptions(threshold=sys.maxsize)

class Markov:

    __name = ""
    __model = {}
    __history = []
    __matrix = np.zeros((26, 26))
    __matrix_arr = []
    __states = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
    ]

    def __init__(self, markov_name):
        self.__name = markov_name
        self.__matrix = np.zeros((26, 26))
        self.__history = []
        self.__model = {}
        self.__matrix_arr = []

    def train(self, word_array):
        self.__history.extend(word_array)
        for word in self.__history:
            for i in range(0, len(word) - 1):
                if i != len(word) - 1:
                    if self.__model.get(word[i]):
                        if self.__model[word[i]].get(word[i + 1]):
                            self.__model[word[i]][word[i + 1]]["count"] = (
                                int(self.__model[word[i]][word[i + 1]]["count"]) + 1
                            )
                        else:
                            self.__model[word[i]][word[i + 1]] = {"count": 1}
                    else:
                        self.__model[word[i]] = {word[i + 1]: {"count": 1}}
        self.__calculate_probabilities()

    def get_model_dict(self):
        return self.__model

    def __calculate_probabilities(self):
        for first_char, val in self.__model.items():
            total_count = 0
            for _, character in val.items():
                total_count += character["count"]
            for second_char, second_char_count_dict in val.items():
                P = float(second_char_count_dict["count"]) / float(total_count)
                self.__model[first_char][second_char]["P"] = P
        self.__calculate_current_transition_matrix()

    def __calculate_current_transition_matrix(self):
        self.__matrix_arr.clear()
        for char_state in self.__states:
            if not self.__model.get(char_state):
                zeros = [0] * 26
                self.__matrix_arr.append(zeros)
            else:
                transitions = []
                first_char = self.__model[char_state]
                for c in self.__states:
                    if not first_char.get(c):
                        transitions.append(0)
                    else:
                        transitions.append(first_char[c]["P"])
                self.__matrix_arr.append(transitions)
        self.__update_matrix()

    def __update_matrix(self):
        self.__matrix = np.array(self.__matrix_arr)

    def get_history(self):
        return self.__history

    def get_matrix(self):
        return self.__matrix

    def get_name(self):
        return self.__name

    def print_matrix(self):
        df = pd.DataFrame(self.__matrix, columns=self.__states, index=self.__states)
        print("\n" + self.__name.upper())
        print(df)

    def get_states(self):
        return self.__states

    def get_model(self):
        return self.__model


def compare_matrices(m1, m2):
    difference_matrix = np.subtract(m1.get_matrix(), m2.get_matrix())
    # print('\n' + 'DIFFERENCE')
    print_matrix(difference_matrix, m1.get_states())


def calculate_error(m1, m2):
    # print("\n CALCULATED ERROR")
    sub = np.subtract(m1.get_matrix(), m2.get_matrix())
    divided = np.divide(
        sub, m1.get_matrix(), out=np.zeros_like(sub), where=m1.get_matrix() != 0
    )
    result = np.multiply(
        divided, 100
    )  # This occurs to create a percent out of 100 - might be easier to leave as decimal
    # print_matrix(result, m1.get_states())
    return result


def print_matrix(m, s):
    df = pd.DataFrame(m, columns=s, index=s)
    print(df)


def find_focus_sets(markov, matrix):
    # Find the transitions in the matrix which have the highest probability of being spelt wrong
    # also take into account the number of times that set has been typed in the past
    error_list = matrix.tolist()
    model = markov.get_model()
    states = markov.get_states()
    by_error = []
    for row in range(0, 25):
        for item in range(0, 25):
            # Count currently does nothing when it comes to being used in this case
            # Consider dropping values completely if their count is under '3' for example
            if model.get(states[row]):
                if model.get(states[row]).get(states[item]):
                    if int(model[states[row]][states[item]]["count"]) > 10:
                        by_error.append(
                            (states[row], states[item], error_list[row][item])
                        )
    sorted_by_error = sorted(by_error, key=lambda x: x[2], reverse=True)
    # print(sorted_by_error[0:3])
    return sorted_by_error[0:3]
