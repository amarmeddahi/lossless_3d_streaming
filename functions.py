import numpy as np
import random


def preprocessing(obj_path):
    faces = []
    vertices = []
    gates = {}
    valences = {}
    patches = {}
    active_vertices = set()
    # Retrieve the data from the obj file
    with open(obj_path) as file:
        current_vertex = 1
        # Loop over the lines of the obj file
        for line in file:
            # Case of a vertex
            if line[0] == 'v':
                # Store the coordinates x, y, z
                x, y, z = line.split(' ')[1:]
                vertices.append([float(x), float(y), float(z)])
                active_vertices.add(current_vertex)
                current_vertex += 1

            # Case of a face
            elif line[0] == 'f':
                # The indices of the face vertices
                a, b, c = line.split(' ')[1:]
                a, b, c = int(a), int(b), int(c)
                faces.append([a, b, c])

                # Add the different gates
                gates[(a, b)] = c
                gates[(b, c)] = a
                gates[(c, a)] = b

                # Update the valences
                if valences.get(a) is None:
                    valences[a] = 1
                else:
                    valences[a] += 1

                if valences.get(b) is None:
                    valences[b] = 1
                else:
                    valences[b] += 1

                if valences.get(c) is None:
                    valences[c] = 1
                else:
                    valences[c] += 1

                # Add the patches
                if patches.get(a) is None:
                    patches[a] = [(b, c)]
                else:
                    patches[a].append((b, c))

                if patches.get(b) is None:
                    patches[b] = [(c, a)]
                else:
                    patches[b].append((c, a))

                if patches.get(c) is None:
                    patches[c] = [(a, b)]
                else:
                    patches[c].append((a, b))

    # Order the edges in the patches
    for vertex, edges in patches.items():
        start, end = edges.pop(0)
        chained_list = [start, end]

        while len(edges) > 1:
            for edge in edges:
                if edge[0] == end:
                    end = edge[1]
                    chained_list.append(end)
                    break
            edges.remove(edge)

        patches[vertex] = np.array(chained_list)

    return gates, valences, patches, active_vertices, vertices

def decimating_conquest(gates, valences, patches, active_vertices):

    faces_status = {}
    vertices_status = {}
    plus_minus = {}

    # Choose a random gate
    first_gate = random.choice(list(gates.keys()))
    left, right = first_gate
    plus_minus[left] = '-'
    plus_minus[right] = '+'

    # Create the fifo
    fifo = [first_gate]

    # Loop over the model
    while len(fifo) > 0:

        # Retrieve the first element of the fifo
        gate = fifo.pop(0)
        left, right = gate
        vertices_status[left] = 'conquered'
        vertices_status[right] = 'conquered'

    return

# def retriangulation()

def write_obj(path, active_vertices, gates, vertices):
    new_indices = {}
    local_copy = gates.copy()
    with open(path, 'w') as file:
        for k, vertex in enumerate(active_vertices):
            x, y, z = vertices[vertex-1]
            file.write('v {} {} {}\n'.format(x, y, z))
            new_indices[vertex] = k + 1

        for gate in gates.copy():
            left, right = gate
            try:
                front = local_copy[gate]
                local_copy.pop(gate)
                local_copy.pop((right, front))
                local_copy.pop((front, left))
                file.write('f {} {} {}\n'.format(
                    new_indices[left], new_indices[right], new_indices[front]))
            except KeyError:
                continue
