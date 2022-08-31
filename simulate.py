import os
import json

import itertools

import time
import graphx as gx

import numpy as np

from multiprocessing import Process

from settings import params

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def compute_nrewires(n, k, netw_type, intervals=5):
    if netw_type == 'lattice':
        #maxr=n*n*4/2/2
        maxr=n*n*k/2/2
    elif netw_type == 'moore':
        #maxr=n*n*8/2/2
        maxr=n*n*k/2/2
    elif netw_type == 'hexagonal':
        maxr=n*(n/2)*6/2/2

    #return [0, int(0.01*maxr),int(0.1*maxr), maxr]
    #return [0, maxr]

    return [
        0,
        0.0001*maxr,
        0.001*maxr,
        0.01*maxr,
        0.1*maxr,
        0.2*maxr,
        0.3*maxr,
        0.35*maxr,
        0.4*maxr,
        0.45*maxr,
        0.5*maxr,
        maxr
    ]


    step = int(maxr/intervals)
    end_rewires = np.arange(step, maxr,
        int((maxr-step)/(intervals-1))).tolist()
    start_rewires = [0]
    new_rewires = 10
    while  new_rewires < end_rewires[0]:
        start_rewires.append(new_rewires)
        new_rewires *= 10
    return start_rewires + end_rewires


def compute_nrewires_robust(n, p):
    maxr=n*n*8/2/2
    return [int(p*maxr), int((1-p)*maxr)]


def process_input(foutput):
    (netw_type, max_time, n_start, netw_size, p1, p_si, p_ri, p_sw, k, agent_type) = foutput.split('-')
    return (netw_type, int(max_time), int(n_start), int(netw_size),
        float(p1), float(p_si), float(p_ri), float(p_sw), int(k), agent_type)


#def run_single(folder_output, lock):
def run_single(foutput):
    (netw_type, max_time, n_start, netw_size, p1, p_si, p_ri, p_sw, k, agent_type) = process_input(foutput)

    if netw_type == 'lattice':
        G = gx.Lattice(0)
    else:
        G = gx.Moore(0)

    #G.populate(netw_size, netw_size, p1, p_si, p_ri, p_sw, k)
    G.populate(netw_size, netw_size, p1, p_si, p_ri, p_sw, k, agent_type)

    G.prepareForReWire()

    soFar = 0

    times = range(max_time)

    rewires = [int(r) for r in  compute_nrewires(netw_size, k, netw_type)]

    for nr in [rewires[0], rewires[len(rewires)-1]]:
    #for nr in rewires:
    #for nr in [rewires[len(rewires)-1]]:
        for i in range(nr-soFar):
            G.reWire()

        out = G.simulate(max_time, n_start)

        path_output = os.path.join(params['path'], foutput, '%s.txt' % nr)
        with open(path_output, 'a') as w:
            w.write('%s\n' % json.dumps(out))

        #writeHash(lock, path_output, out)

        soFar = nr


def newLock(func):
    def wrapper(lock, *args):
        lock.acquire()
        res = func(*args)
        lock.release()
        return res
    return wrapper


@newLock
def writeHash(path_output, out):
    with open(path_output, 'a') as w:
        w.write('%s\n' % json.dumps(out))



#def simulateQueue(nWorker, queue, lock):
def simulateQueue(nWorker, queue):
    jobs = 0
    for foutput in queue:
        t0=time.time()
        # print('worker %s processing %s' % (nWorker, foutput))
        run_single(foutput)
        run_time = time.time() - t0
        jobs += 1
        logger.info('worker %s processed %s jobs (t_last = %s)' % (
            nWorker, jobs, run_time))
    logger.info('ending worker: %s' % nWorker)


def runMulti(queues, nProcesses):
    jobs = []
    #lock = Lock()
    try:
        for i in range(nProcesses):
            #args = (i, queues[i], lock)
            args = (i, queues[i])
            p = Process(target=simulateQueue, args=args)
            jobs.append(p)

            logger.info('starting worker: %s' % i)

            p.start()

        for p in jobs:
            p.join()

    except (KeyboardInterrupt, SystemExit):

        for p in jobs:
            if not p.is_alive():
                continue
            p.terminate()

        raise


def randeven(low, high):
    potential = np.random.randint(low=low, high=high)
    if potential % 2 == 0:
        return potential
    if potential == low:
        return potential + 1
    if potential == high:
        return potential - 1
    if np.random.random() > 0.5:
        return potential + 1
    return potential - 1



def run_random(total_samples=1000):

    if params['path'] == '':
        raise Exception('Please specify a path where data will be stored')

    print('data will be stored at %s' % params['path'] )

    if not os.path.exists(params['path']):
        os.makedirs(params['path'])

    netw_type = 'moore'
    agent_type = 'complex'
    for i in range(total_samples):
        netw_size = randeven(low=10, high=100)
        p1 = np.random.uniform(low=0, high=1)
        p_si = np.random.uniform(low=0, high=1)
        p_ri = np.random.uniform(low=0, high=1)
        p_sw = np.random.uniform(low=0, high=1)

        if netw_type == 'lattice':
            k = np.random.choice([2,3,4,5])
            if k == 5 and netw_size == 10:
                continue
        else:
            k = np.random.choice([4,8])

        foutput = '%s-%s-%s-%s-%s-%s-%s-%s-%s-%s' % (
            netw_type, 5000, 1, netw_size, p1, p_si, p_ri, p_sw, k, agent_type
        )



        path_folder = os.path.join(params['path'], foutput)
        if not os.path.exists(path_folder):
            os.makedirs(path_folder)

        print(i)
        run_single(foutput)



def run_simulation():

    if params['path'] == '':
        raise Exception('Please specify a path where data will be stored')

    print('data will be stored at %s' % params['path'] )

    if not os.path.exists(params['path']):
        os.makedirs(params['path'])

    queues = {i: [] for i in range(params['nProcesses'])}

    logger.info('spreading the work accros %s workers' % params['nProcesses'])

    input = [
                params['netw_type'],
                params['max_time'],
                params['n_start'],
                params['netw_size'],
                params['p1'],
                params['p_si'],
                params['p_ri'],
                params['p_sw'],
                params['k'],
                params['agent_type']
    ]

    for param in itertools.product(*input):

        foutput = '-'.join(['%s' % p for p in param])

        path_folder = os.path.join(params['path'], foutput)
        if not os.path.exists(path_folder):
            os.makedirs(path_folder)

        choice = np.random.choice(params['nProcesses'])
        for sample in range(params['nsamples']):
            queues[choice].append(foutput)


    runMulti(queues, params['nProcesses'])
