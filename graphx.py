import os
import re
import sys
import time
import shutil
import json
import numpy as np
import networkx as nx


from copy import copy
from math import exp

from functools import wraps

#from agents import corr
from agents import SimpleAgent, ComplexAgent, logit
from basicGraph import copyGraph

from nodeIterator import NodeIterator

from collections import Counter

class ArgumentError(Exception):
    pass

class BaseGraph(object):

    def __init__(self):
        #self.agentType = {}
        self.keys = []
        self.agents = {}
        self.nEdges = 0

    def addNode(self, key, p1, p_si, p_ri, p_sw, agent_type):
        if key in self.agents:
            return
        self.keys.append(key)
        if agent_type == 'simple':
            self.agents[key] = SimpleAgent(key, p1, p_si, p_ri, p_sw)
        else:
            self.agents[key] = ComplexAgent(key, p1, p_si, p_ri, p_sw)

    def __len__(self):
        return len(self.keys)

    def __contains__(self, key):
        return key in self.agents

    def addEdges(self, edges):
        for key1, key2 in edges:
            self.addEdge(key1, key2)

    def addEdge(self, key1, key2):
        if key1 == key2:
            return
        self.addDirectedEdge(key1, key2)
        self.addDirectedEdge(key2, key1)


    def remEdge(self, key1, key2):
        self.remDirectedEdge(key1, key2)
        self.remDirectedEdge(key2, key1)

    def remDirectedEdge(self, key1, key2):
        self.agents[key1].remove(key2)

    def addDirectedEdge(self, key1, key2):
        for k in [key1, key2]:
            if k in self.agents:
                continue
            raise ArgumentError('%s needs to be added' % k)

        self.agents[key1].addFriend(key2)
        self.nEdges += 1

    def __str__(self):
        lines = []
        for key in self.keys:
            f = ' --> '.join(map(str, self.agents[key].friends))
            lines.append('%s: %s' % (key, f))
        return '\n'.join(lines)

    def __iter__(self):
        self.index = -1
        return self

    def next(self):
        if self.index == (len(self.keys)-1):
            raise StopIteration
        self.index += 1
        return self.keys[self.index]

    def __next__(self):
        return self.next()

    def __getitem__(self, key):
        return self.agents[key]


    def clean(self):
        for key in self.keys:
            #self.agents[key].curr_rep = 0
            #self.agents[key].nsenders = 0
            #self.agents[key].RD = np.random.RandomState(key)

            #for f in self.agents[key].memory:
            #    self.agents[key].memory[f] = 0

            self.agents[key].adopter_friends = 0
            self.agents[key].n_active = 0



class Graph(BaseGraph):

    def __init__(self, seed=0):
        super(Graph, self).__init__()
        self.seed_state = np.random.RandomState(seed)
        self.avail = None
        self.adopted = set()
        self.initial_adopters = set()

    def prepareForReWire(self):
        # copy the graph into a lighter version of itself
        self.avail = copyGraph(self)


    def reWire(self):
        """
        we first add edges between a-b  and fa-fb
        and then we remove 'bad' edges, i.e. edges where
        both nodes have increased by 1.

        the ideal case is

          k       k         k+1      k+1       k       k
        -- a -- fa --      -- a -- fa --     -- a    fa --
                       ->     |    |      ->    |    |
        -- b -- fb --      -- b -- fb --     -- b    fb --
          k       k         k+1      k+1       k       k


        if there is an edge betwen a and b already, or
        if they are the same node, then we won't be able
        to remove any edge for 'free': some nodes will
        have one more degree than the others


          k       k         k+1      k
        -- a -- fa --      -- a -- fa --
                 |     ->     |    |
        -- b -- fb --      -- b -- fb --
          k       k         k+1      k

        or

          k      k           k      k+1
        -- a -- fa --      -- a -- fa --
            \         ->       \    |
              \                  \  |
             -- fb --           -- fb --
                  k                 k+1

        when this happens, we remove 'bad' edges
        with probability 1/2 such that, in expectation,
        all nodes have degree k.

        in any case, this is not important, since their
        number is so small (<1% of nodes when we rewire
        all edges) that we did not need to do that

        """
        if not self.avail:
            raise Exception('should prepare for rewire first')

        a, fa = self.avail.pickEdge()
        b, fb = self.avail.pickEdge()

        if a == fb:
            b, fb = fb, b

        k = {i:self.agents[i].degree() for i in [a,fa,b,fb]}

        self.addEdge(a, b)
        self.addEdge(fa, fb)

        # we take the set in case both a and b are the same
        potentiallyBad = set([(a, fa), (a, fb), (b, fa), (b, fb)])

        for i, fi in potentiallyBad:

            if not fi in self.agents[i].friends:
                continue

            if self.agents[i].degree() > k[i]:
                if self.agents[fi].degree() > k[fi]:
                    self.remEdge(i, fi)
                #elif self.seed_state.random_sample() < 0.5:
                elif np.random.random() < 0.5:
                    self.remEdge(i, fi)


    # def reWire(self):
    #
    #     keep_going = True
    #
    #     while keep_going:
    #         a = self.keys[np.random.choice(len(self.keys))]
    #         b = self.agents[a].friends[np.random.choice(len(self.agents[a].friends))]
    #         c = self.keys[np.random.choice(len(self.keys))]
    #         d = self.agents[c].friends[np.random.choice(len(self.agents[c].friends))]
    #
    #         if a != c and c not in self.agents[a].friends and d not in self.agents[b].friends:
    #             keep_going = False
    #
    #     self.addEdge(a, c)
    #     self.addEdge(b, d)
    #     self.remEdge(a, b)
    #     self.remEdge(c, d)



    def shareAdopted(self):
        return len(self.adopted)/float(len(self.keys))


    def init_adoption(self, nstart=1):
        focal = np.random.choice(range(len(self)), nstart, replace=False)
        adopted = set(focal)
        for node in focal:
            for f in self.agents[node].friends:
                adopted.add(f)
        return adopted


    # def simulate(
    #                 self,
    #                 times,
    #                 seedAdopt=0,
    #                 seedUpdate=0,
    #                 nstart=1,
    #                 asynch='asynch',
    #                 p_inactive=1e-1,
    #                 p_re_active=1e-3,
    #                 p_lose_consid=1e-1,
    #                 p_re_consid =1e-1,
    #                 p_drop_link=1e-1,
    #                 gprint=False
    #     ):
    #
    #     self.adopted = set()
    #     self.active = NodeIterator(len(self))
    #     self.inactive = NodeIterator(len(self))
    #     self.susceptible = NodeIterator(len(self))
    #     self.not_susceptible = NodeIterator(len(self))
    #
    #
    #     if gprint:
    #         curr = 0
    #         self.position = {}
    #         for j in range(self.height):
    #             for i in range(self.width):
    #                 self.position[curr] = (j, i)
    #                 curr += 1
    #
    #
    #     self.pending_messages = {key: [] for key in self.keys}
    #     #RD = np.random.RandomState(seedAdopt)
    #     #initial_adopters = set(RD.choice(range(len(self)), nstart, replace=False))
    #     if len(self.initial_adopters) == 0:
    #         self.initial_adopters = self.init_adoption(seedAdopt, nstart)
    #         #self.initial_adopters = set(np.random.choice(range(len(self)), nstart, replace=False))
    #
    #     for node in self.initial_adopters:
    #         self.active.add(node)
    #         self.adopted.add(node)
    #
    #     for node in self.initial_adopters:
    #         for f in self.agents[node].friends:
    #             if f not in self.adopted:
    #                 self.susceptible.add(f)
    #                 self.pending_messages[f].append(node)
    #
    #     if gprint:
    #         print('time: 0 (%s adopted)' % self.shareAdopted())
    #         self.printAdoption()
    #
    #     freq = [self.shareAdopted()]
    #
    #     self.friends_of_adopters = []
    #     self.scores_of_adopters = []
    #
    #     for t in times:
    #         self.friends_counter = Counter()
    #         if asynch == 'asynch':
    #             self.run_asynch(t, p_inactive, p_re_active, p_lose_consid,
    #                 p_re_consid, p_drop_link, gprint)
    #
    #         else:
    #             self.run_synch(t, p_inactive, p_re_active, p_lose_consid,
    #                 p_re_consid, p_drop_link, gprint)
    #
    #         self.friends_of_adopters.append(self.friends_counter)
    #         newFreq = self.shareAdopted()
    #         freq.append(newFreq)
    #
    #         if gprint:
    #             time.sleep(0.5)
    #             os.system('clear')
    #             print('time: %s (%s adopted)' % (t+1, newFreq))
    #             self.printAdoption()
    #
    #         if len(self.active) == 0 or len(self.susceptible) == 0:
    #             break
    #
    #         if newFreq == 1:
    #             break
    #
    #     self.clean()
    #
    #     return t+1, freq + [newFreq]*(len(times)-len(freq))
    #
    #
    #
    # def run_synch(
    #                     self,
    #                     seedUpdate,
    #                     p_inactive,
    #                     p_re_active,
    #                     p_lose_consid,
    #                     p_re_consid,
    #                     p_drop_link,
    #                     gprint=False
    #     ):
    #
    #     #adopters = set()
    #
    #     #for s in self.susceptible:
    #     #    for f in self.agents[s].friends:
    #     #        if f in self.active:
    #     #            adopters.add(f)
    #
    #     #adopters = [a for a in adopters]
    #
    #     #np.random.shuffle(adopters)
    #
    #     receivers = {}
    #
    #     #for key in adopters:
    #     for key in self.active:
    #         #if not self.agents[key].send():
    #         #    continue
    #
    #         all_friends = self.agents[key].friends
    #         #friends = np.random.choice(all_friends, int(len(all_friends)/2), replace=False)
    #         friends = np.random.choice(all_friends, int(len(all_friends)), replace=False)
    #         for f in friends:
    #             if f not in self.susceptible:
    #                 continue
    #             if f in self.adopted:
    #                 continue
    #
    #             self.agents[f].memory[key] += 1
    #
    #             if f not in receivers:
    #                 receivers[f] = []
    #             receivers[f].append(key)
    #
    #     add_to_active = []
    #     add_to_susceptible = []
    #     drop_susceptible = []
    #
    #     # TO REMOVE ???
    #     #for s in self.susceptible:
    #     #    if s in receivers:
    #     #        continue
    #     #    if np.random.random() < self.agents[s].attention:
    #     #        receivers[s] = []
    #
    #     for r in receivers:
    #         if self.agents[r].adopt():
    #             self.adopted.add(r)
    #             self.susceptible.drop(r)
    #
    #             add_to_active.append(r)
    #
    #             self.friends_counter.update([sum([1 for f in self.agents[r].friends if f in self.active])])
    #
    #             for f in self.agents[r].friends:
    #                 if f in self.adopted:
    #                     continue
    #                 if f not in self.susceptible:
    #                     add_to_susceptible.append(f)
    #
    #         else:
    #             for sender in receivers[r]:
    #                 if np.random.random() < self.agents[r].forget_rate:
    #                     self.agents[r].memory[sender] -= 1
    #
    #     drop_active = []
    #     if p_inactive > 0:
    #         for a in self.active:
    #             if not self.agents[a].becomeInactive(p_inactive):
    #                 continue
    #             drop_active.append(a)
    #
    #     if p_lose_consid > 0:
    #         for a in self.susceptible:
    #             if not self.agents[a].loseConsideration(p_lose_consid):
    #                 continue
    #             drop_susceptible.append(a)
    #
    #     for key in add_to_active:
    #         self.active.add(key)
    #
    #     for key in drop_active:
    #         self.active.drop(key)
    #
    #     for key in add_to_susceptible:
    #         self.susceptible.add(key)
    #
    #     for key in drop_susceptible:
    #         self.susceptible.drop(key)
    #
    #
    #
    #
    #
    #
    #
    #
    #
    # def run_asynch(
    #                     self,
    #                     seedUpdate,
    #                     p_inactive,
    #                     p_re_active,
    #                     p_lose_consid,
    #                     p_re_consid,
    #                     p_drop_link,
    #                     gprint=False
    #     ):
    #
    #
    #     susceptibles = [s for s in self.susceptible]
    #     np.random.shuffle(susceptibles)
    #
    #     scam_thrs = 5
    #
    #     for s in susceptibles:
    #         if np.random.random() > self.agents[s].attention:
    #             continue
    #
    #         if len(self.pending_messages[s]) > scam_thrs:
    #             self.susceptible.drop(s)
    #             continue
    #
    #         while len(self.pending_messages[s]) > 0:
    #             self.pending.update([len(self.pending_messages[s])])
    #             sender = self.pending_messages[s].pop()
    #             self.agents[s].memory[sender] += 1
    #
    #         if not self.agents[s].adopt():
    #             continue
    #
    #         self.adopted.add(s)
    #         self.susceptible.drop(s)
    #
    #         for f in self.agents[s].friends:
    #             if f in self.adopted:
    #                 continue
    #             if f in self.not_susceptible:
    #                 continue
    #             self.susceptible.add(f)
    #             self.pending_messages[f].append(s)
    #
    #
    #
    # def simulate(
    #                 self,
    #                 max_time,
    #                 nstart=1,
    #                 gprint=False
    #     ):
    #
    #     self.adopted = set()
    #
    #     if len(self.initial_adopters) == 0:
    #         self.initial_adopters = self.init_adoption(nstart)
    #
    #     for node in self.initial_adopters:
    #         self.adopted.add(node)
    #
    #     freq = [len(self.adopted)/float(len(self.keys))]
    #
    #     inactive_sender = set()
    #     inactive_receiver = set()
    #
    #     for t in range(max_time-1):
    #         to_add = []
    #         to_remove = []
    #         to_become_inactive = []
    #
    #         for key in self.keys:
    #
    #             if key in self.adopted:
    #                 continue
    #             if key in inactive_receiver:
    #                 continue
    #
    #             n_adopters = 0
    #             n_active_adopters = 0
    #             for f in self.agents[key].friends:
    #                 if f not in self.adopted:
    #                     continue
    #                 n_adopters += 1
    #                 if f not in inactive_sender:
    #                     n_active_adopters += 1
    #
    #             if n_active_adopters > 0:
    #                 if self.agents[key].adopt(n_adopters):
    #                     to_add.append(key)
    #                 elif self.agents[key].become_receiver_inactive():
    #                     inactive_receiver.add(key)
    #
    #         for key in self.adopted:
    #             n_adopters = [f for f in self.agents[key].friends if f not in self.adopted]
    #             if self.agents[key].unadopt(n_adopters):
    #                 to_remove.append(key)
    #                 if key in inactive_sender:
    #                     inactive_sender.remove(key)
    #             elif self.agents[key].become_sender_inactive():
    #                 inactive_sender.add(key)
    #
    #         for key in to_add:
    #             self.adopted.add(key)
    #
    #         for key in to_remove:
    #             self.adopted.remove(key)
    #
    #         newFreq = len(self.adopted)/float(len(self.keys))
    #         freq.append(newFreq)
    #
    #         if newFreq == 1:
    #             break
    #
    #     self.clean()
    #
    #     return t+1, freq + [newFreq]*(max_time-len(freq))



    def simulate(
                    self,
                    max_time,
                    nstart=1,
                    gprint=False
        ):


        if gprint:
            curr = 0
            self.position = {}
            for j in range(self.height):
                for i in range(self.width):
                    self.position[curr] = (j, i)
                    curr += 1

        nodes = {
            'potential': set(),
            'active_sender': set(),
            'inactive_sender': set(),
            'active_receiver': set(),
            'inactive_receiver': set()
        }

        for key in self.keys:
            nodes['potential'].add(key)

        if len(self.initial_adopters) == 0:
            self.initial_adopters = self.init_adoption(nstart)

        for key in self.initial_adopters:
            nodes['potential'].remove(key)
            nodes['active_sender'].add(key)

        for key in self.initial_adopters:
            for f in self.agents[key].friends:
                self.agents[f].change_adopter_count(1)
                self.agents[f].change_n_active_count(1)
                if f in nodes['potential']:
                    nodes['potential'].remove(f)
                    nodes['active_receiver'].add(f)

        if gprint:
            print('time: 0 (%s adopted)' % self.shareAdopted())
            self.printAdoption()

        freq = [len(nodes['active_sender'])/float(len(self.keys))]

        self.ones = []
        self.twos = []

        for t in range(max_time-1):

            one = 0
            two = 0

            move = set()

            for key in nodes['active_receiver']:

                if self.agents[key].n_active == 0:
                    continue

                if self.agents[key].adopt():
                    move.add((key, 'active_receiver', 'active_sender'))
                    if self.agents[key].adopter_friends == 1:
                        one += 1
                    else:
                        two += 1

                else:
                    if self.agents[key].become_receiver_inactive():
                        move.add((key, 'active_receiver', 'inactive_receiver'))


            for key in nodes['active_sender']:
                if self.agents[key].unadopt():
                    move.add((key, 'active_sender', 'active_receiver'))
                else:
                    if self.agents[key].become_sender_inactive():
                        move.add((key, 'active_sender', 'inactive_sender'))

            for key in nodes['inactive_sender']:
                if self.agents[key].unadopt():
                    move.add((key, 'inactive_sender', 'active_receiver'))

            for (key, from_, to) in move:
                nodes[from_].remove(key)
                nodes[to].add(key)

                if from_ == 'active_receiver' and to == 'active_sender':
                    for f in self.agents[key].friends:
                        self.agents[f].change_adopter_count(1)
                        self.agents[f].change_n_active_count(1)
                        if f in nodes['potential']:
                            nodes['potential'].remove(f)
                            nodes['active_receiver'].add(f)

                elif from_ == 'active_sender' and to == 'active_receiver':
                    for f in self.agents[key].friends:
                        self.agents[f].change_adopter_count(-1)
                        self.agents[f].change_n_active_count(-1)

                elif from_ == 'active_sender' and to == 'inactive_sender':
                    for f in self.agents[key].friends:
                        self.agents[f].change_n_active_count(-1)

                elif from_ == 'inactive_sender' and to == 'active_receiver':
                    for f in self.agents[key].friends:
                        self.agents[f].change_adopter_count(-1)


            newFreq = (len(nodes['active_sender']) + len(nodes['inactive_sender']))/float(len(self.keys))
            freq.append(newFreq)

            self.ones.append(one)
            self.twos.append(two)

            if newFreq == 1:
                break

            #if len(nodes['active_receiver']) == 0:
            #    break

        self.clean()

        return t+1, freq + [newFreq]*(max_time-len(freq))




class Lattice(Graph):
    def __init__(self, seed):
        super(Lattice, self).__init__(seed)
        self.seqForPrint = None


    def createSeq(self):
        nNodes = len(self.keys)
        if nNodes % 2 != 0:
            raise Exception('nNodes % 2 != 0')
        perimeter = int(nNodes/2)
        nodes = []
        for i in range(perimeter-1):
            nodes += [i, i+perimeter+1]
        return nodes + [i+1, i+2]


    def printAdoption(self):

        if len(self.keys) == 0:
            raise Exception('graph is empty')

        if not self.seqForPrint:
            self.seqForPrint = self.createSeq()

        rows = {0: '', 1: ' '}

        #nodes = ''
        for key, i in enumerate(self.seqForPrint):
            word = ''
            if i in self.adopted:
                word += '+'
            else:
                p = int(self.agents[i].pAdopt()*10)
                if p == 0:
                    word += ' '
                elif p == 10:
                    word += '9'
                else:
                    word += '%s' % p

            rows[key % 2] += '%s ' % word


        #print nodes
        print(rows[1])
        print(rows[0])


    #def populate(self, width, height, send_rate, forget_rate, w, thrs, slope, attention):
    def populate(self, width, height, p1, p_si, p_ri, p_sw):

        """
        creates a ring lattice by iteratively
        connecting the following nodes

            a -- b
                \  /
                c -- d
        """

        self.width = width
        self.height = height

        nNodes = width*height

        if nNodes % 2 != 0:
            raise Exception('nNodes % 2 != 0')

        perimeter = int(nNodes/2)

        for i in range(nNodes):
            #self.addNode(i, send_rate, forget_rate, w, thrs, slope, attention)
            self.addNode(i, p1, p_si, p_ri, p_sw)


        for i in range(perimeter):
            c = i
            a = i + perimeter
            if i == perimeter-1:
                b = i + 1
                d = 0
            else:
                b = i+perimeter+1
                d = i + 1


            self.addEdges([(c,d),(c,a),(c,b),(a,b)])


class Lattice(Graph):
    def __init__(self, seed):
        super(Lattice, self).__init__(seed)

    def populate(self, width, height, p1, p_si, p_ri, p_sw, k, agent_type):

        nNodes = width*height

        if nNodes <= 2*k:
            raise Exception('nNodes is too small')

        for i in range(nNodes):
            self.addNode(i, p1, p_si, p_ri, p_sw, agent_type)

        edges_to_add = []
        for i in range(nNodes):
            for j in range(1, k+1):
                edges_to_add.append([i, (i+j) % nNodes])
                edges_to_add.append([i, (nNodes + (i-j)) % nNodes])

        self.addEdges(edges_to_add)



class RandomRegular(Graph):

    def __init__(self, seed, degree):
        super(RandomRegular, self).__init__(seed)
        self.degree = degree

    def populate(self, width, height, send_rate, forget_rate, w, thrs, slope, sd, auto_corr, attention):
        corr = {}
        value = 0
        g = nx.random_regular_graph(self.degree, width*height)
        for tuple in g.nodes:
            self.addNode(value, send_rate, forget_rate, w, thrs, slope, sd, auto_corr, attention)
            corr[tuple] = value
            value += 1

        for tuple1 in g:
            for tuple2 in g.neighbors(tuple1):
                self.addEdge(corr[tuple1], corr[tuple2])


class Hexagonal(Graph):

    def __init__(self, seed):
        super(Hexagonal, self).__init__(seed)

    def populate(self, width, height, send_rate, forget_rate, w, thrs, slope, sd, auto_corr, attention):
        #g = nx.triangular_lattice_graph(14, 14, periodic=True) #98
        #g = nx.triangular_lattice_graph(16, 16, periodic=True) #128

        corr = {}
        value = 0
        g = nx.triangular_lattice_graph(width, height, periodic=True)
        for tuple in g.nodes:
            self.addNode(value, send_rate, forget_rate, w, thrs, slope, sd, auto_corr, attention)
            corr[tuple] = value
            value += 1

        for tuple1 in g:
            for tuple2 in g.neighbors(tuple1):
                self.addEdge(corr[tuple1], corr[tuple2])


class Moore(Graph):

    """

      0  -  1  - 2 --
      |  \/ | \/ | \/
      |  /\ | /\ | /\
      4  -  5 -  6 --
      |  \/ | \/ | \/
      |  /\ | /\ | /\
      7   - 8  - 9 --
      |  \/ | \/ | \

    """


    def __init__(self, seed):
        super(Moore, self).__init__(seed)


    def printAdoption(self):
        curr = 0
        final = ''
        word = ''
        for j in range(self.height):
            for i in range(self.width):
                if curr in self.adopted:
                    if curr in self.active:
                        word += ' + '
                    else:
                        word += ' - '
                else:
                    #p = int(self.agents[curr].pAdopt()*10)

                    p = sum([1 for f in self.agents[curr].friends if f in self.active])
                    #p = int(self.agents[curr].score())
                    #if p == 0:
                    #    word += '   '
                    #elif p == 10:
                    #    word += ' 9 '
                    #else:
                    #    word += ' %s ' % p
                    word += ' %s ' % p
                curr += 1
            final += '%s|\n' % word
            word = ''
        final += '-'*self.width
        print(final)
        #sys.stdout.write("\r%s" % final)
        #sys.stdout.flush()


    def populate(self, width, height, p1, p_si, p_ri, p_sw, k, agent_type):

        if k != 4 and k != 8:
            raise Exception('k should be 4 or 8')

        self.width = width
        self.height = height

        for i in range(width*height):
            self.addNode(i, p1, p_si, p_ri, p_sw, agent_type)


        curr = 0

        for j, i in loop(width, height):

            if j > 0 and k == 8:

                if i > 0 and i < width-1:

                    #  | uppLeft uppRight
                    #  |      \  /
                    #  |   -- curr --
                    self.addEdge(curr,curr-width-1)
                    self.addEdge(curr,curr-width+1)

                elif i == 0:

                    #  |    uppRight
                    #  |   /
                    #  |curr --

                    self.addEdge(curr,curr-width+1)


                elif i == width-1:

                    #     uppLeft   |
                    #            \  |
                    #        -- curr|

                    self.addEdge(curr,curr-width-1)

            if i < width-1:

                #   curr - right

                self.addEdge(curr, curr+1)

            if j < height-1:

                #   curr
                #    |
                #   bottom

                self.addEdge(curr, curr+width)

            curr += 1


        #return
        # link the right part of the page to the left
        curr = 2*width - 1
        i = width-1
        for j in range(1, height-1):
            self.addEdge(curr, curr-width+1)
            if k == 8:
                self.addEdge(curr, curr-2*width+1)
                self.addEdge(curr, curr+1)
            curr += width


        # link the top part of the page to the bottom
        last = width*height-1
        curr = 1
        for i in range(1, width-1):
            self.addEdge(curr, last-width+i+1)
            if k == 8:
                self.addEdge(curr, last-width+i)
                self.addEdge(curr, last-width+i+2)
            curr += 1

        # link the corners
        self.addEdge(0, last-width+1)
        self.addEdge(0, width-1)

        if k == 8:
            self.addEdge(0, last-width+2)
            self.addEdge(0, last)

        self.addEdge(width-1, last)
        if k == 8:
            self.addEdge(width-1, last-1)
            self.addEdge(width-1, width)
            self.addEdge(width-1, last-width+1)

        self.addEdge(last, last-width+1)
        if k == 8:
            self.addEdge(last, last-2*width+1)



def loop(width, height):
    idx = []
    for j in range(height):
        for i in range(width):
            idx.append((j,i))
    return idx
