# -*- coding: utf-8 -*-
"""
CSI Project.

@author: Pierre Barroso + Fabio + Amar
"""
from tools import (preprocessing, decimating_conquest, cleaning_conquest,
                   sew_conquest, write_obj)


OBJ_PATH = './OBJ/icosphere.obj'
NB_ITERATIONS = 5
obja = ""
count_face = 1
# Preprocessing
gates, valences, patches, active_vertices, vertices, faces = preprocessing(OBJ_PATH)

# Repeat the 3 steps of the algorithm
for current_it in range(NB_ITERATIONS):
    if len(active_vertices) >= 3:
        print('\n')
        print(len(active_vertices))

        # decimating conquest + retriangulation
        obja, count_face = decimating_conquest(
            gates, valences, patches, active_vertices, -1, vertices, faces, obja, count_face)

        # Cleaning Conquest
        fifo = []
        print(obja)
        obja, count_face = cleaning_conquest(gates, patches, valences, active_vertices, fifo, faces, obja, count_face)
        print(obja)
        obja, count_face = sew_conquest(gates, patches, active_vertices, valences, vertices, faces, obja, count_face)
        print(obja)
        path = '{}_{}.obj'.format(OBJ_PATH.split('.obj')[0], current_it)
        write_obj(path, active_vertices, gates, vertices)

        for front, chain in patches.items():
            if len(set(chain)) != len(chain):
                print(front)
                print(chain)
    else:
        break
    
f = open("./OBJ/test.obja", "w")
f.write(obja)
f.close()

print('\n')
print('Final vertices: {}'.format(len(active_vertices)))
