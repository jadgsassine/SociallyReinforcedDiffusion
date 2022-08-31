
import graphx as gx
import networkx as nx
import matplotlib.pyplot as plt


def createNetworkX(graph):
    g = nx.Graph()
    for key in graph:
        for f in graph[key].friends:
            g.add_edge('%s' % key,'%s' % f)
    return g


def plotGraph(NX, adopted, update=True):

    colors = [
        'blue' if int(node) in adopted else 'red'
        for node in NX.nodes()
    ]


    #if not update:
    #    plt.ion()
    #else:
    #    plt.clf()

    nx.draw(NX, node_color=colors, with_labels=False)
    #plt.pause(0.5)


netw_size = 16
p1=0
p_si=0
p_ri=0
p_sw=0

nrewires=0

G = gx.Lattice(0)
G.populate(netw_size, netw_size, p1, p_si, p_ri, p_sw)
G.prepareForReWire()
for i in range(nrewires):
    G.reWire()

adopted = G.init_adoption(1)

NX = createNetworkX(G)
plotGraph(NX, adopted)
print(adopted)
plt.show()
