# -*- coding: utf-8 -*-
import numpy as np
"""
CSI Project.

@author: Pierre Barroso + Fabio + Amar + Younes
"""
from tools import (preprocessing, decimating_conquest, cleaning_conquest,
                   sew_conquest, write_obj, postprocessing)


OBJ_PATH = './OBJ/icosphere.obj'
NB_ITERATIONS = 4
obja = ""
obj_to_obja = {}

# Preprocessing
gates, valences, patches, active_vertices, vertices, faces = preprocessing(OBJ_PATH)
nb_vertex = len(vertices)
count_v = nb_vertex +1

# Repeat the 3 steps of the algorithm
for current_it in range(NB_ITERATIONS):
    obja_iter = ""
    count_v_iter = 1

    if len(active_vertices) >= 10 and current_it < NB_ITERATIONS-1:
        obj_to_obja_iter = {}

        # decimating conquest + retriangulation
        obja_iter, count_v_iter = decimating_conquest(
            gates, valences, patches, active_vertices, -1, vertices, faces, obja_iter, count_v_iter, obj_to_obja_iter )

        # Cleaning Conquest
        fifo = []
        obja_iter, count_v_iter = cleaning_conquest(gates, patches,
                                             valences, active_vertices, fifo, vertices, faces,
                                             obja_iter, count_v_iter, obj_to_obja_iter)
        obja_iter, count_v_iter = sew_conquest(gates, patches, 
                                        active_vertices, valences, 
                                        vertices, faces, obja_iter, count_v_iter, obj_to_obja_iter)
        obja = obja_iter + obja
        a = {}
        for k in range(1,count_v_iter):
            a[count_v - k] = obj_to_obja_iter[count_v_iter -k]
        obj_to_obja.update(a)
        count_v -= count_v_iter -1

    else:
        a = {}
        path = '{}_{}.obj'.format(OBJ_PATH.split('.obj')[0], current_it)
        obj_f = write_obj(active_vertices, gates, vertices,  count_v_iter, a)
        obj_to_obja.update(a)
        obja = obj_f + obja
        break

# Postprocessing
a = postprocessing(obja, vertices)
f = open("./OBJ/test.obja", "w")
f.write(obja)
f.close()

print('\n')
print('Final vertices: {}'.format(len(active_vertices)))
