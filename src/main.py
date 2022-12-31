# -*- coding: utf-8 -*-
import numpy as np

"""
CSI Project

This code is a mesh simplification algorithm that reduces the number of vertices in a mesh while preserving its overall shape. It works by repeating the following three steps: decimating conquest, cleaning conquest, and sew conquest. The algorithm is designed to be iterative, with each iteration reducing the number of vertices by a small amount.

@author: Pierre Barroso (MystW) + Fabio PEREIRA DE ARAUJO (fabiopereira59) + Amar Meddahi (amarmeddahi) + Younes Boutiyarzist (younesBoutiyarzist)

"""

from tools import (preprocessing, decimating_conquest, cleaning_conquest,
                   sew_conquest, write_obj, postprocessing, write_last_obja)

def simplify_mesh(obj_path: str, nb_iterations: int) -> str:
    """
    Simplify a mesh by iteratively applying the decimating conquest, cleaning conquest, and sew conquest algorithms.

    Parameters:
        obj_path (str): the path to the input OBJ file
        nb_iterations (int): the number of times to repeat the simplification process

    Returns:
        str: the resulting OBJ file in string format
    """
    # Preprocessing
    gates, valences, patches, active_vertices, vertices, faces = preprocessing(obj_path)
    nb_vertex = len(vertices)
    count_v = nb_vertex + 1
    obja = ""
    obj_to_obja = {}

    # Repeat the 3 steps of the algorithm
    for current_it in range(nb_iterations):
        if len(active_vertices) >= 10 and current_it < nb_iterations - 1:
            # Decimating conquest + retriangulation
            obj_to_obja_iter = {}
            obja_iter = ""
            count_v_iter = 1
            obja_iter, count_v_iter = decimating_conquest(
                gates, valences, patches, active_vertices, -1, vertices, faces, obja_iter, count_v_iter, obj_to_obja_iter)

            # Update obja
            a = {}
            for k in range(1, count_v_iter):
                a[count_v - k] = obj_to_obja_iter[count_v_iter - k]
            obj_to_obja.update(a)
            count_v -= count_v_iter - 1
            obja = obja_iter + obja

            # Cleaning conquest
            fifo = []
            obj_to_obja_iter = {}
            obja_iter = ""
            count_v_iter = 1
            obja_iter, count_v_iter = cleaning_conquest(gates, patches,
                                                         valences, active_vertices, fifo, vertices, faces,
                                                         obja_iter, count_v_iter, obj_to_obja_iter)
            # Update obja
            a = {}
            for k in range(1, count_v_iter):
                a[count_v - k] = obj_to_obja_iter[count_v_iter - k]
            obj_to_obja.update(a)
            count_v -= count_v_iter - 1
            obja = obja_iter + obja

            # Sew conquest
            obj_to_obja_iter = {}
            obja_iter = ""
            count_v_iter = 1
            obja_iter, count_v_iter = sew_conquest(gates, patches, 
                                            active_vertices, valences, 
                                            vertices, faces, obja_iter, count_v_iter, obj_to_obja_iter)
            # Update obja
            a = {}
            for k in range(1, count_v_iter):
                a[count_v - k] = obj_to_obja_iter[count_v_iter - k]
            obj_to_obja.update(a)
            count_v -= count_v_iter - 1        
            obja = obja_iter + obja

            # Create current obj
            path = '{}_{}.obj'.format(obj_path.split('.obj')[0], current_it)
            write_obj(path, active_vertices, gates, vertices)

        else:
            a = {}
            path = '{}_{}.obj'.format(obj_path.split('.obj')[0], current_it)
            write_obj(path, active_vertices, gates, vertices)
            obj_f = write_last_obja(active_vertices, gates, vertices,  1, a)
            obj_to_obja.update(a)
            obja = obj_f + obja
            break

    # Postprocessing
    obja = postprocessing(obja, vertices, obj_to_obja)

    return obja

OBJ_PATH = './OBJ/icosphere.obj'
NB_ITERATIONS = 6
obja = ""
obj_to_obja = {}

if __name__ == '__main__':
    obja = simplify_mesh(OBJ_PATH, NB_ITERATIONS)
    f = open(OBJ_PATH + "a", "w")
    f.write(obja)
    f.close()