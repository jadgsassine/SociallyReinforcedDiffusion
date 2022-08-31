"""
Here we create a lighter version of Graph to pick 
the remaining edges as we perform the rewiring

In short, we don't want to pick the same edge twice, so 
everytime an edge is chosen, it is removed from the graph. 
Because we don't want to remove anything from the original 
graph, we make a copy. But since we only need this copy 
for edge picking, we don't need to store as much and so can 
make it much lighter
"""


import numpy as np
from copy import copy

class BasicAgent(object):
    def __init__(self, seed_state, friends=None):
        if not friends:
            self.friends = []
        else:
            self.friends = friends
        self.nFriends = len(friends)
        self.seed_state = seed_state

    def pickFriend(self):
        i = self.seed_state.choice(self.nFriends)
        return i, self.friends[i]

    def removeValue(self, value):
        i = self.friends.index(value)
        self.removeIndex(i)

    def removeIndex(self, i):
        switch(i, self.nFriends-1, self.friends)
        self.nFriends -= 1


    def hasFriends(self):
        return self.nFriends > 0

    def remaingFriends(self):
        return self.friends[:self.nFriends]
        


class BasicGraph(object):
    def __init__(self, seed_state):
        self.agents = {}
        self.keys = []
        self.remainKeys = len(self.keys)
        self.seed_state = seed_state
    
    def add(self, key, friends):
        self.agents[key] = BasicAgent(self.seed_state, friends)
        if self.remainKeys < len(self.keys):
            self.keys[self.remainKeys] = key
        else:
            self.keys.append(key)
        self.remainKeys += 1
    
    def pickNode(self):
        if self.remainKeys == 0:
            raise Exception('no more avail keys')
        i = self.seed_state.choice(self.remainKeys)
        return i, self.keys[i]
    


    def pickEdge(self):
        """
        pick an edge by first choosing a node, 
        then a friend of that node.

        this approach does not always give equal 
        weight to each edge. eg:

           0 - 1
            \
             2 - 3
        
        which can be represented as:

            0 --> 1 -- 2
            1 --> 0
            2 --> 0 --> 3
            3 --> 2
        
        the proba of choosing each edge is

            (0,1): (1/4)*(1/2) + (1/4)
            (0,2): (1/4)*(1/2) + (1/4)*(1/2)
            (2,3): (1/4)*(1/2) + (1/4)

        however, here we assume that the degree 
        is the same for each node, hence it works 
        because the proba of selecting any pair (a, b) 
        is equal to 2*(1/n)*(1/degree)

        """

        if len(self.keys) < 2:
            raise Exception('less than 2 avail keys')

        i, n = self.pickNode()
        j, f = self.agents[n].pickFriend()
        
        self.agents[n].removeIndex(j)
        self.agents[f].removeValue(n)
        
        if not self.agents[n].hasFriends():
            self.removeIndex(i)

        if not self.agents[f].hasFriends():
            self.removeValue(f)

        return n, f

            
    def removeValue(self, value):
        i = self.keys.index(value)
        self.removeIndex(i)

    def removeIndex(self, i):
        switch(i, self.remainKeys-1, self.keys)
        self.remainKeys -= 1

    def __str__(self):
        txt = ''
        for key, obj in self.agents.iteritems(): 
            f = '-->'.join(map(str, obj.remaingFriends()))
            txt += '%s: %s\n' % (key, f)
        return txt
        

def switch(i, j, array):
    keep = array[i]
    array[i] = array[j]
    array[j] = keep


def copyGraph(graph):
    g = BasicGraph(graph.seed_state)
    for key in graph:
        g.add(key, graph[key].friends[:])
    return g
