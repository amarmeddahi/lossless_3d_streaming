# -*- coding: utf-8 -*-
"""
CSI Project.

@author: Pierre Barroso + Fabio + Amar
"""
import random
import numpy as np
from functions import preprocessing, write_obj
import sys


OBJ_PATH = sys.argv[1]
NB_ITERATIONS = int(sys.argv[2])
# Preprocessing
gates, valences, patches, active_vertices, vertices = preprocessing(OBJ_PATH)

# Repeat the 3 steps of the algorithm
for current_it in range(NB_ITERATIONS):
    print('')
    print(len(active_vertices))

    faces_status = {}
    vertices_status = {}
    plus_minus = {}

    # Choose a random gate
    first_gate = random.choice(list(gates.keys()))
    left, right = first_gate
    plus_minus[left] = '+'
    plus_minus[right] = '-'

    # Create the fifo
    fifo = [first_gate]

    # Loop over the model
    while len(fifo) > 0:

        # Retrieve the first element of the fifo
        gate = fifo.pop(0)
        left, right = gate
        vertices_status[left] = 'conquered'
        vertices_status[right] = 'conquered'

        # Retrieve the front vertex
        front = gates[gate]

        # conquered or null
        if faces_status.get(gate) is not None:
            print('*', end='')
            continue

        elif valences[front] <= 6 and vertices_status.get(front) is None:
            print('.', end='')

            # Retrieve the border of the patch
            chain = patches[front]

            # Tag all the vertices as conquered
            for vertex in chain:
                vertices_status[vertex] = 'conquered'

            # Add the following gates to the fifo
            # and tag the inner faces as conquered
            i = np.where(chain == right)[0][0]
            chain = np.append(chain[i:], chain[:i])
            # print(chain)
            for gate in zip(chain[1:], chain[:-1]):
                # print(gate)
                fifo.append(gate)
                faces_status[(gate[-1], gate[0])] = 'conquered'
            # print("stop")

            # Remove the front vertex
            # print(front)
            active_vertices.remove(front)

            # Remove the old gates
            for vertex in chain:
                gates.pop((front, vertex))
                gates.pop((vertex, front))

            # Retrieve the information to start the retriangulation
            valence = valences[front]
            left_sign = plus_minus[left]
            right_sign = plus_minus[right]

            # Select the right case
            if valence == 3:
                # Update the valences
                for vertex in chain:
                    valences[vertex] -= 1

                # Update the faces
                new_front = chain[1]
                gates[(left, right)] = new_front
                gates[(right, new_front)] = left
                gates[(new_front, left)] = right

                # Update the patches
                for vertex in chain:
                    patches[vertex] = patches[vertex][patches[vertex] != front]

                # Update the signs
                if plus_minus.get(new_front) is None:
                    if left_sign == '+' and right_sign == '+':
                        plus_minus[new_front] = '-'
                    else:
                        plus_minus[new_front] = '+'

            elif valence == 4:
                if right_sign == '-':
                    # Update the signs
                    if plus_minus.get(chain[1]) is None:
                        plus_minus[chain[1]] = '+'
                    if plus_minus.get(chain[2]) is None:
                        plus_minus[chain[2]] = '-'

                    # Update the faces
                    gates[(left, right)] = chain[1]
                    gates[(right, chain[1])] = left
                    gates[(chain[1], chain[2])] = left
                    gates[(chain[2], left)] = chain[1]

                    # Add the new gates
                    gates[(left, chain[1])] = chain[2]
                    gates[(chain[1], left)] = right

                    # Update the valences
                    valences[right] -= 1
                    valences[chain[2]] -= 1

                    # Update the patches
                    patches[right] = patches[right][patches[right] != front]
                    patches[chain[2]] = patches[chain[2]][patches[chain[2]] != front]
                    patches[left][np.where(patches[left] == front)[0]] = chain[1]
                    patches[chain[1]][np.where(patches[chain[1]] == front)[0]] = left

                else:
                    # Update the signs
                    if plus_minus.get(chain[1]) is None:
                        plus_minus[chain[1]] = '-'
                    if plus_minus.get(chain[2]) is None:
                        plus_minus[chain[2]] = '+'

                    # Update the faces
                    gates[(left, right)] = chain[2]
                    gates[(right, chain[1])] = chain[2]
                    gates[(chain[1], chain[2])] = right
                    gates[(chain[2], left)] = right

                    # Add the new gates
                    gates[(right, chain[2])] = left
                    gates[(chain[2], right)] = chain[1]

                    # Update the valences
                    valences[left] -= 1
                    valences[chain[1]] -= 1

                    # Update the patches
                    patches[left] = patches[left][patches[left] != front]
                    patches[chain[1]] = patches[chain[1]][patches[chain[1]] != front]
                    patches[right][np.where(patches[right] == front)[0]] = chain[2]
                    patches[chain[2]][np.where(patches[chain[2]] == front)[0]] = right

            elif valence == 5:
                if right_sign == '-':
                    # Update the signs
                    if plus_minus.get(chain[1]) is None:
                        plus_minus[chain[1]] = '+'
                    if plus_minus.get(chain[2]) is None:
                        plus_minus[chain[2]] = '-'
                    if plus_minus.get(chain[3]) is None:
                        plus_minus[chain[3]] = '+'

                    # Update the faces
                    gates[(left, right)] = chain[1]
                    gates[(right, chain[1])] = left
                    gates[(chain[1], chain[2])] = chain[3]
                    gates[(chain[2], chain[3])] = chain[1]
                    gates[(chain[3], left)] = chain[1]

                    # Add the new gates
                    gates[(left, chain[1])] = chain[3]
                    gates[(chain[1], left)] = right
                    gates[(chain[3], chain[1])] = chain[2]
                    gates[(chain[1], chain[3])] = left

                    # Update the valences
                    valences[right] -= 1
                    valences[chain[1]] += 1
                    valences[chain[2]] -= 1

                    # Update the patches
                    patches[right] = patches[right][patches[right] != front]

                    patch = patches[chain[1]]
                    i = np.where(patch == front)[0][0]
                    patch = patch[patch != front]
                    patches[chain[1]] = np.insert(patch, [i, i], [chain[3], left])

                    patches[chain[2]] = patches[chain[2]][patches[chain[2]] != front]
                    patches[chain[3]][np.where(patches[chain[3]] == front)[0]] = chain[1]
                    patches[left][np.where(patches[left] == front)[0]] = chain[1]

                elif left_sign == '-':
                    # Update the signs
                    if plus_minus.get(chain[1]) is None:
                        plus_minus[chain[1]] = '+'
                    if plus_minus.get(chain[2]) is None:
                        plus_minus[chain[2]] = '-'
                    if plus_minus.get(chain[3]) is None:
                        plus_minus[chain[3]] = '+'

                    # Update the faces
                    gates[(left, right)] = chain[3]
                    gates[(right, chain[1])] = chain[3]
                    gates[(chain[1], chain[2])] = chain[3]
                    gates[(chain[2], chain[3])] = chain[1]
                    gates[(chain[3], left)] = right

                    # Add the new gates
                    gates[(right, chain[3])] = left
                    gates[(chain[3], right)] = chain[1]
                    gates[(chain[3], chain[1])] = chain[2]
                    gates[(chain[1], chain[3])] = right

                    # Update the valences
                    valences[chain[2]] -= 1
                    valences[chain[3]] += 1
                    valences[left] -= 1

                    # Update the patches
                    patches[right][np.where(patches[right] == front)[0]] = chain[3]
                    patches[chain[1]][np.where(patches[chain[1]] == front)[0]] = chain[3]
                    patches[chain[2]] = patches[chain[2]][patches[chain[2]] != front]

                    patch = patches[chain[3]]
                    i = np.where(patch == front)[0][0]
                    patch = patch[patch != front]
                    patches[chain[3]] = np.insert(patch, [i, i], [right, chain[1]])

                    patches[left] = patches[left][patches[left] != front]

                else:
                    # Update the signs
                    if plus_minus.get(chain[1]) is None:
                        plus_minus[chain[1]] = '-'
                    if plus_minus.get(chain[2]) is None:
                        plus_minus[chain[2]] = '+'
                    if plus_minus.get(chain[3]) is None:
                        plus_minus[chain[3]] = '-'

                    # Update the faces
                    gates[(left, right)] = chain[2]
                    gates[(right, chain[1])] = chain[2]
                    gates[(chain[1], chain[2])] = right
                    gates[(chain[2], chain[3])] = left
                    gates[(chain[3], left)] = chain[2]

                    # Add the new gates
                    gates[(right, chain[2])] = left
                    gates[(chain[2], right)] = chain[1]
                    gates[(chain[2], left)] = right
                    gates[(left, chain[2])] = chain[3]

                    # Update the valences
                    valences[chain[1]] -= 1
                    valences[chain[2]] += 1
                    valences[chain[3]] -= 1

                    # Update the patches
                    patches[right][np.where(patches[right] == front)[0]] = chain[2]
                    patches[chain[1]] = patches[chain[1]][patches[chain[1]] != front]

                    patch = patches[chain[2]]
                    i = np.where(patch == front)[0][0]
                    patch = patch[patch != front]
                    patches[chain[2]] = np.insert(patch, [i, i], [left, right])

                    patches[chain[3]] = patches[chain[3]][patches[chain[3]] != front]
                    patches[left][np.where(patches[left] == front)[0]] = chain[2]

            elif valence == 6:

                if right_sign == '-':
                    # Update the signs
                    if plus_minus.get(chain[1]) is None:
                        plus_minus[chain[1]] = '+'
                    if plus_minus.get(chain[2]) is None:
                        plus_minus[chain[2]] = '-'
                    if plus_minus.get(chain[3]) is None:
                        plus_minus[chain[3]] = '+'
                    if plus_minus.get(chain[4]) is None:
                        plus_minus[chain[4]] = '-'

                    # Update the faces
                    gates[(left, right)] = chain[1]
                    gates[(right, chain[1])] = left
                    gates[(chain[1], chain[2])] = chain[3]
                    gates[(chain[2], chain[3])] = chain[1]
                    gates[(chain[3], chain[4])] = left
                    gates[(chain[4], left)] = chain[3]

                    # Add the new gates
                    gates[(left, chain[1])] = chain[3]
                    gates[(chain[1], left)] = right
                    gates[(chain[3], chain[1])] = chain[2]
                    gates[(chain[1], chain[3])] = left
                    gates[(left, chain[3])] = chain[4]
                    gates[(chain[3], left)] = chain[1]

                    # Update the valences
                    valences[right] -= 1
                    valences[chain[1]] += 1
                    valences[chain[2]] -= 1
                    valences[chain[3]] += 1
                    valences[chain[4]] -= 1
                    valences[left] += 1

                    # Update the patches
                    patches[right] = patches[right][patches[right] != front]

                    patch = patches[chain[1]]
                    i = np.where(patch == front)[0][0]
                    patch = patch[patch != front]
                    patches[chain[1]] = np.insert(patch, [i, i], [chain[3], left])

                    patches[chain[2]] = patches[chain[2]][patches[chain[2]] != front]

                    patch = patches[chain[3]]
                    i = np.where(patch == front)[0][0]
                    patch = patch[patch != front]
                    patches[chain[3]] = np.insert(patch, [i, i], [left, chain[1]])

                    patches[chain[4]] = patches[chain[4]][patches[chain[4]] != front]

                    patch = patches[left]
                    i = np.where(patch == front)[0][0]
                    patch = patch[patch != front]
                    patches[left] = np.insert(patch, [i, i], [chain[1], chain[3]])

                else:
                    # Update the signs
                    if plus_minus.get(chain[1]) is None:
                        plus_minus[chain[1]] = '-'
                    if plus_minus.get(chain[2]) is None:
                        plus_minus[chain[2]] = '+'
                    if plus_minus.get(chain[3]) is None:
                        plus_minus[chain[3]] = '-'
                    if plus_minus.get(chain[4]) is None:
                        plus_minus[chain[4]] = '+'

                    # Update the faces
                    gates[(left, right)] = chain[4]
                    gates[(right, chain[1])] = chain[2]
                    gates[(chain[1], chain[2])] = right
                    gates[(chain[2], chain[3])] = chain[4]
                    gates[(chain[3], chain[4])] = chain[2]
                    gates[(chain[4], left)] = right

                    # Add the new gates
                    gates[(right, chain[4])] = left
                    gates[(chain[4], right)] = chain[2]
                    gates[(chain[4], chain[2])] = chain[3]
                    gates[(chain[2], chain[4])] = right
                    gates[(right, chain[2])] = chain[4]
                    gates[(chain[2], right)] = chain[1]

                    # Update the valences
                    valences[right] += 1
                    valences[chain[1]] -= 1
                    valences[chain[2]] += 1
                    valences[chain[3]] -= 1
                    valences[chain[4]] += 1
                    valences[left] -= 1

                    # Update the patches
                    patch = patches[right]
                    i = np.where(patch == front)[0][0]
                    patch = patch[patch != front]
                    patches[right] = np.insert(patch, [i, i], [chain[2], chain[4]])

                    patches[chain[1]] = patches[chain[1]][patches[chain[1]] != front]

                    patch = patches[chain[2]]
                    i = np.where(patch == front)[0][0]
                    patch = patch[patch != front]
                    patches[chain[2]] = np.insert(patch, [i, i], [chain[4], right])

                    patches[chain[3]] = patches[chain[3]][patches[chain[3]] != front]

                    patch = patches[chain[4]]
                    i = np.where(patch == front)[0][0]
                    patch = patch[patch != front]
                    patches[chain[4]] = np.insert(patch, [i, i], [right, chain[2]])

                    patches[left] = patches[left][patches[left] != front]

        elif (vertices_status.get(front) is None and valences[front] > 6) or (
                vertices_status.get(front) == 'conquered'):
            print('o', end='')

            # Set the front face to null
            faces_status[gate] = 'null'

            if plus_minus.get(front) is None:
                plus_minus[front] = '+'

            # Add the other edges to the fifo
            fifo.append((front, right))
            fifo.append((left, front))

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
