import sys
import graphx as gx
from simulate import compute_nrewires
from agents import SimpleAgent
import matplotlib.pyplot as plt


netw_size = 20
netw_type = 'lattice'

nstart = 1
max_time = 1000
p1 = 0.01
p_si = 0
p_ri = 0
p_sw = 0
k = 2
agent_type='complex'
gprint = False

rewires = [int(r) for r in  compute_nrewires(netw_size, k, netw_type)]

G = gx.Lattice(0)
G.populate(netw_size, netw_size, p1, p_si, p_ri, p_sw, k, agent_type)
G.prepareForReWire()

for i in range(rewires[len(rewires)-1]):
    G.reWire()

fig, ax = plt.subplots(1,1)

t, freqs = G.simulate(max_time, nstart, gprint)

ax.plot(freqs, label='complex')


for key in G:
    new_agent = SimpleAgent(key, p1, p_si, p_ri, p_sw)
    new_agent.friends = G.agents[key].friends
    G.agents[key] = new_agent

t, freqs = G.simulate(max_time, nstart, gprint)

ax.plot(freqs, label='simple')

print(freqs)

ax.set_xlim(0, 1000)
ax.legend()
plt.show()
