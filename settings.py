import os
import numpy as np

PATH_KEEPER = ''

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
#PATH_KEEPER = os.path.join(CURR_DIR, '..', '..','data', 'diffusion_random_moore')
PATH_KEEPER = os.path.join(CURR_DIR, '..', '..','data', 'complementary')


params = {
    'path': PATH_KEEPER,
    'nProcesses': 1,
    'netw_size': np.arange(10, 100, 10).tolist(),
    #'netw_size': [200],
    #'p1': np.arange(0.006, 0.5, 0.005),
    'p1': [0.001],
    'nsamples': 100,
    #'nsamples': 100,
    'max_time': [5000],
    'n_start': [1],
    'netw_type': ['lattice'],
    #'netw_type': ['moore'],
    'p_si': [0],
    'p_ri': [0],
    'p_sw': [0],
    'k': [2],
    #'k': [4],
    'agent_type': ['complex']
}
