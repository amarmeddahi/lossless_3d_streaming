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
    for vertex in active_vertices.copy():
        if valences[vertex] == 3:
            # Remove the vertex
            active_vertices.remove(vertex)

            # Update the valences
            chain = patches[vertex]
            for point in chain:
                valences[point] -= 1
                # Remove the old gates
                gates.pop((vertex, point))
                gates.pop((point, vertex))

            # Update the faces
            gates[(chain[0], chain[1])] = chain[2]
            gates[(chain[1], chain[2])] = chain[0]
            gates[(chain[2], chain[0])] = chain[1]

            # Update the patches
            for point in chain:
                patches[point] = patches[point][patches[point] != vertex]

    path = '{}_{}.obj'.format(OBJ_PATH.split('.obj')[0], current_it)
    write_obj(path, active_vertices, gates, vertices)
