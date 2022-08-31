
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

    if not update:
        plt.ion()
    else:
        plt.clf()

    nx.draw(NX, node_color=colors, with_labels=True)
    plt.pause(0.5)
    


def simulate(graph, adopted, gplot=True, maxTime=500):

    if gplot:
        NX = createNetworkX(graph)
        plotGraph(NX, adopted, update=False)
    
    for t in range(maxTime):
        
        if not simulateRound(graph, adopted):
            break

        if gplot:
            plotGraph(NX, adopted, update=True)



