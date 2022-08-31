
import numpy as np
from math import exp
from collections import Counter, deque


class Agent(object):
    def __init__(self, key, p1, p_si, p_ri, p_sw):
        self.key = key
        self.friends = []

        self.p1 = p1
        self.p_si = p_si
        self.p_ri = p_ri
        self.p_sw = p_sw
        self.adopter_friends = 0
        self.n_active = 0
        self.hold = True

    def degree(self):
        return len(self.friends)

    def addFriend(self, key):
        if key in self.friends:
            return
        self.friends.append(key)
        #self.memory[key] = 0

    def replace(self, key, newKey):
        self.remove(key)
        self.addFriend(newKey)

    def remove(self, key):
        del self.friends[self.friends.index(key)]
        #del self.memory[key]

    def become_sender_inactive(self):
        return np.random.random() < self.p_si

    def become_receiver_inactive(self):
        if self.hold:
            self.hold = False
            return False
        return np.random.random() < self.p_ri

    # def p_adopt(self, score=None):
    #     if score is None:
    #         score = self.adopter_friends
    #     if score == 0:
    #         return 0
    #     return logit(score - 2, invert_p1(self.p1))

    def p_adopt(self, score=None):
        pass

    def adopt(self, score=None):
        return np.random.random() < self.p_adopt(score)

    def unadopt(self, score=None):
        return np.random.random() < (1-self.p_adopt(score))*self.p_sw

    def change_adopter_count(self, by):
        self.adopter_friends += by
        if self.adopter_friends < 0:
            raise Exception('adopter count < 0')

    def change_n_active_count(self, by):
        self.n_active += by
        if self.n_active < 0:
            raise Exception('n active count < 0')


class SimpleAgent(Agent):
    def p_adopt(self, score=None):
        if score is None:
            score = self.adopter_friends
        print((self.p1, score, 1-(1-self.p1)**score))
        return 1-(1-self.p1)**score


class ComplexAgent(Agent):
    def p_adopt(self, score=None):
        if score is None:
            score = self.adopter_friends
        if score == 0:
            return 0
        elif score == 1:
            return self.p1
        else:
            return 1

def invert_p1(p1):
    return np.log(1/p1 - 1)


def logit(x, slope=1):
    return (1./(1.+ exp(-slope*x)))
