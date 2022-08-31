import sys
import graphx as gx
from simulate import invert_p1


netw_size = 50
netw_type = 'moore'

if netw_type == 'lattice':
    maxr=netw_size*netw_size*4/2/2
else:
    maxr=netw_size*netw_size*8/2/2

print(sys.argv)

if len(sys.argv) == 1:
    rewires = 0
else:
    rewires = int(sys.argv[1])

if rewires >= maxr:
    print('the number of rewires is too high (max=%s)' % maxr)
    sys.exit()


nstart = 1
max_time = 1000
p1 = 0
p_si = 0
p_ri = 0
p_sw = 0
gprint = False

if netw_type == 'lattice':
    G = gx.Lattice(0)
else:
    G = gx.Moore(0)

G.populate(netw_size, netw_size, p1, p_si, p_ri, p_sw)
G.prepareForReWire()

for i in range(rewires):
    G.reWire()

print(G.simulate(max_time, nstart, gprint))
