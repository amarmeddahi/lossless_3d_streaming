# -*- coding: utf-8 -*-
"""
CSI Project.

@author: Pierre Barroso + Fabio + Amar
"""
import random
import numpy as np
from tools import *
import sys


OBJ_PATH = sys.argv[1]
NB_ITERATIONS = int(sys.argv[2])
# Preprocessing
gates, valences, patches, active_vertices, vertices = preprocessing(OBJ_PATH)

# Repeat the 3 steps of the algorithm
for current_it in range(NB_ITERATIONS):
    print('')
    print(len(active_vertices))

    # decimating conquest + retriangulation
    valences, patches, gates = decimating_conquest(gates, valences, patches, active_vertices)

    # Cleaning Conquest
    fifo = []
    cleaning_conquest(gates, patches, valences, active_vertices, fifo)

    path = '{}_{}.obj'.format(OBJ_PATH.split('.obj')[0], current_it)
    write_obj(path, active_vertices, gates, vertices)
