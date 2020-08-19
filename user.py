import numpy as np


class User(object):
    def __init__(self, user_id, matches, user_vector_dict):
        self.user_id = user_id
        self.user_vector = user_vector_dict
        self.matches = matches

    def convert_to_vector(self):
        return np.fromiter(self.user_vector.values(), dtype=float)

    def check_zero_vector(self):
        for item in self.user_vector.values():
            if item == 0:
                continue
            else:
                return False
        return True
