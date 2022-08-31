
import graphx as gx
import networkx as nx
import matplotlib.pyplot as plt


def createNetworkX(graph):
    g = nx.Graph()
    for key in graph:
        for f in graph[key].friends:
            g.add_edge('%s' % key,'%s' % f)
    return g


netw_size = 6
k = 8

p1=0
p_si=0
p_ri=0
p_sw=0


G = gx.Moore(0)
G.populate(netw_size, netw_size, p1, p_si, p_ri, p_sw, k)
for key in G:
    print(len(G.agents[key].friends))
NX = createNetworkX(G)
nx.draw(NX)
plt.show()
