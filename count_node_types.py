import sys
import graphx as gx
from agents import SimpleAgent
from simulate import compute_nrewires
import matplotlib.pyplot as plt


netw_size = 20
netw_type = 'lattice'

nstart = 1
max_time = 1000
p1 = 0.01
p_si = 0
p_ri = 0
p_sw = 0
k=2
agent_type='complex'
gprint = False

rewires = [int(r) for r in  compute_nrewires(netw_size, k, netw_type)]


G = gx.Lattice(0)
G.populate(netw_size, netw_size, p1, p_si, p_ri, p_sw, k, agent_type)
G.prepareForReWire()

t, freqs = G.simulate(max_time, nstart, gprint)

fig, ax = plt.subplots(1,3, figsize=(12, 4))

ones = [0]
twos = [0]
for o, t in zip(G.ones,G.twos):
    ones.append(o + ones[len(ones)-1])
    twos.append(t + twos[len(twos)-1])

ax[0].plot(ones[1:], color=u'#1f77b4', linestyle='--', label='n=1')
ax[0].plot(twos[1:], color=u'#1f77b4', linestyle='-', label='n=2+')
ax[0].legend(loc = 'lower right')

for i in range(rewires[len(rewires)-1]):
    G.reWire()

t, freqs = G.simulate(max_time, nstart, gprint)

ones = [0]
twos = [0]
for o, t in zip(G.ones,G.twos):
    ones.append(o + ones[len(ones)-1])
    twos.append(t + twos[len(twos)-1])

ax[1].plot(ones[1:], color=u'#ff7f0e', linestyle='--', label='n=1')
ax[1].plot(twos[1:], color=u'#ff7f0e', linestyle='-', label='n=2+')
ax[1].legend(loc='lower right')



ax[0].set_title('Clustered')
ax[1].set_title('Random')

ax[0].set_ylabel('Cummulative Adopters')


ax[2].plot([int(f*400) for f in freqs], label='complex', color='black', linestyle='-')
for key in G:
    new_agent = SimpleAgent(key, p1, p_si, p_ri, p_sw)
    new_agent.friends = G.agents[key].friends
    G.agents[key] = new_agent
t, freqs = G.simulate(max_time, nstart, gprint)
ax[2].plot([int(f*400) for f in freqs], label='simple', color='black', linestyle='--')
ax[2].legend(loc='lower right')
ax[2].set_title('Complex vs Simple Contagion\non Random Network')

for i in range(3):
    ax[i].set_xlim(0, 400)
    ax[i].set_ylim(0, 405)
    ax[i].set_xlabel('Time')

fig.subplots_adjust(left  = 0.1, right = 0.95, bottom = 0.15, top = 0.85, wspace = 0.3, hspace=0.5)

plt.show()
