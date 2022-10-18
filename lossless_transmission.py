# -*- coding: utf-8 -*-
"""
CSI Project.

@author: Pierre Barroso + Fabio + Amar
"""
from tools import (preprocessing, decimating_conquest, cleaning_conquest,
                   sew_conquest, write_obj)


OBJ_PATH = './OBJ/cow.obj'
NB_ITERATIONS = 7
# Preprocessing
gates, valences, patches, active_vertices, vertices = preprocessing(OBJ_PATH)

# Repeat the 3 steps of the algorithm
for current_it in range(NB_ITERATIONS):
    if len(active_vertices) > 3:
        print('\n')
        print(len(active_vertices))

        # decimating conquest + retriangulation
        valences, patches, gates = decimating_conquest(
            gates, valences, patches, active_vertices, -1)

        # Cleaning Conquest
        fifo = []
        cleaning_conquest(gates, patches, valences, active_vertices, fifo)
        sew_conquest(gates, patches, active_vertices, valences, vertices)

        path = '{}_{}.obj'.format(OBJ_PATH.split('.obj')[0], current_it)
        write_obj(path, active_vertices, gates, vertices)

        for front, chain in patches.items():
            if len(set(chain)) != len(chain):
                print(front)
                print(chain)
    else:
        break

print('\n')
print('Final vertices: {}'.format(len(active_vertices)))
