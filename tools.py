import numpy as np
import random

def postprocessing(obja, vertices):
    res = obja.split("\n")
    for line in res:
        if line[0] == 'v':
            a = 1
    return a

def preprocessing(obj_path):
    # Variables
    faces = []
    vertices = []
    gates = {}
    valences = {}
    patches = {}
    active_vertices = set()
    current_vertex = 1

    # Retrieve the data from the obj file
    with open(obj_path) as file:
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

    to_edit = {}
    # Order the edges in the patches
    for vertex, edges in patches.copy().items():
        start, end = edges.pop(0)
        chained_list = [start, end]

        while len(edges) > 1:
            for edge in edges:
                if edge[0] == end:
                    end = edge[1]
                    chained_list.append(end)
                    break
            else:
                # Go out the while
                break
            edges.remove(edge)

        if len(edges) > 1:
            if chained_list[0] == chained_list[-1]:
                chained_list.pop()

            # Add a new point
            vertices.append(vertices[vertex-1])
            active_vertices.add(current_vertex)

            # Modify the gates
            for gate in edges:
                gates[gate] = current_vertex

            # Modify the valences
            valences[vertex] -= len(edges)
            valences[current_vertex] = len(edges)

            start, end = edges.pop(0)
            new_chain = [start, end]
            while len(edges) > 1:
                for edge in edges:
                    if edge[0] == end:
                        end = edge[1]
                        new_chain.append(end)
                        break
                edges.remove(edge)

            # Add the new patch
            patches[current_vertex] = np.array(new_chain)

            # Replace the interior gates
            for point in new_chain:
                gates[(point, current_vertex)] = gates.pop((point, vertex))
                gates[(current_vertex, point)] = gates.pop((vertex, point))

            to_edit[vertex] = (new_chain, current_vertex)

            current_vertex += 1
            print('Multiple chains detected: {} -> {} & {}'.format(
                vertex, chained_list, new_chain))

        patches[vertex] = np.array(chained_list)

    # Update the patches
    for vertex, (chain, new) in to_edit.items():
        for point in chain:
            patches[point][np.where(patches[point] == vertex)[0]] = new

    return gates, valences, patches, active_vertices, vertices, faces

def decimating_conquest(gates, valences, patches, active_vertices, it, vertices, faces , obja, count_v, obj_to_obja):

    faces_status = {}
    vertices_status = {}
    plus_minus = {}
    print(obja)

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
            for gate in zip(chain[1:], chain[:-1]):
                fifo.append(gate)
                faces_status[(gate[-1], gate[0])] = 'conquered'

            # Remove the front vertex
            active_vertices.remove(front)
            obja += f"v {vertices[front-1][0]}  {vertices[front-1][1]}  {vertices[front-1][2]}\n"
            obj_to_obja[count_v] = front
            count_v += 1
            # Remove the old gates
            for vertex in chain:
                gates.pop((front, vertex))
                gates.pop((vertex, front))

            # Retriangulation
            valences, patches, gates, vertices, faces , obja, count_v = retriangulation(chain, valences, left, right,
                                                                                        gates, patches, front, plus_minus, it, vertices, faces , obja,  count_v, obj_to_obja)

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

        else:
            print("ERROR: ELSE (decimating conquest)")

    return obja, count_v

def retriangulation(chain, valences, left, right, gates, patches, front, plus_minus, it, vertices, faces , obja, count_v, obj_to_obja):
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
                
        # Update obja
        obja += f"f {front}  {chain[0]}  {chain[1]}\n"
        obja += f"f {front}  {chain[1]}  {chain[2]}\n"
        obja += f"f {front}  {chain[2]}  {chain[0]}\n"
        obja += f"df {chain[0]}  {chain[1]}  {chain[2]}\n"


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
            
            # Update obja
            obja += f"f {front}  {chain[0]}  {chain[1]}\n"
            obja += f"f {front}  {chain[1]}  {chain[2]}\n"
            obja += f"f {front}  {chain[2]}  {chain[3]}\n"
            obja += f"f {front}  {chain[3]}  {chain[0]}\n"
            obja += f"df {left}  {chain[1]}  {chain[2]}\n"
            obja += f"df {left}  {chain[1]}  {right}\n"

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

            # Update obja
            obja += f"f {front}  {chain[0]}  {chain[1]}\n"
            obja += f"f {front}  {chain[1]}  {chain[2]}\n"
            obja += f"f {front}  {chain[2]}  {chain[3]}\n"
            obja += f"f {front}  {chain[3]}  {chain[0]}\n"
            obja += f"df {right}  {chain[2]}  {left}\n"
            obja += f"df {chain[2]}  {right}  {chain[1]}\n"

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

            # Update obja
            obja += f"f {front}  {chain[0]}  {chain[1]}\n"
            obja += f"f {front}  {chain[1]}  {chain[2]}\n"
            obja += f"f {front}  {chain[2]}  {chain[3]}\n"
            obja += f"f {front}  {chain[3]}  {chain[4]}\n"
            obja += f"f {front}  {chain[4]}  {chain[0]}\n"
            obja += f"df {left}  {right}  {chain[1]}\n"
            obja += f"df {chain[1]}  {left}  {chain[3]}\n"
            obja += f"df {chain[1]}  {chain[2]}  {chain[3]}\n"

            
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
            
            # Update obja
            obja += f"f {front}  {chain[0]}  {chain[1]}\n"
            obja += f"f {front}  {chain[1]}  {chain[2]}\n"
            obja += f"f {front}  {chain[2]}  {chain[3]}\n"
            obja += f"f {front}  {chain[3]}  {chain[4]}\n"
            obja += f"f {front}  {chain[4]}  {chain[0]}\n"
            obja += f"df {left}  {right}  {chain[3]}\n"
            obja += f"df {chain[1]}  {right}  {chain[3]}\n"
            obja += f"df {chain[1]}  {chain[2]}  {chain[3]}\n"

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

            # Update obja
            obja += f"f {front}  {chain[0]}  {chain[1]}\n"
            obja += f"f {front}  {chain[1]}  {chain[2]}\n"
            obja += f"f {front}  {chain[2]}  {chain[3]}\n"
            obja += f"f {front}  {chain[3]}  {chain[4]}\n"
            obja += f"f {front}  {chain[4]}  {chain[0]}\n"
            obja += f"df {left}  {right}  {chain[2]}\n"
            obja += f"df {chain[1]}  {right}  {chain[2]}\n"
            obja += f"df {left}  {chain[2]}  {chain[3]}\n"

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

            # Update obja
            obja += f"f {front}  {chain[0]}  {chain[1]}\n"
            obja += f"f {front}  {chain[1]}  {chain[2]}\n"
            obja += f"f {front}  {chain[2]}  {chain[3]}\n"
            obja += f"f {front}  {chain[3]}  {chain[4]}\n"
            obja += f"f {front}  {chain[4]}  {chain[5]}\n"
            obja += f"f {front}  {chain[5]}  {chain[0]}\n"
            obja += f"df {left}  {right}  {chain[1]}\n"
            obja += f"df {chain[1]}  {left}  {chain[2]}\n"
            obja += f"df {chain[1]}  {left}  {chain[2]}\n"            
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
            
            # Update obja
            obja += f"f {front}  {chain[0]}  {chain[1]}\n"
            obja += f"f {front}  {chain[1]}  {chain[2]}\n"
            obja += f"f {front}  {chain[2]}  {chain[3]}\n"
            obja += f"f {front}  {chain[3]}  {chain[4]}\n"
            obja += f"f {front}  {chain[4]}  {chain[5]}\n"
            obja += f"f {front}  {chain[5]}  {chain[0]}\n"
            obja += f"df {chain[2]}  {right}  {chain[1]}\n"
            obja += f"df {chain[2]}  {chain[3]}  {chain[4]}\n"
            obja += f"df {chain[5]}  {left}  {right}\n"  
          
    return valences, patches, gates, vertices, faces , obja, count_v

def cleaning_conquest(gates, patches, valences, active_vertices, fifo, vertices, faces, obja,  count_v, obj_to_obja):
    # Cleaning Conquest
    faces_status = {}
    vertices_status = {}
    done = set()

    # Choose a random gate
    for vertex in active_vertices:
        if valences[vertex] == 3:
            chain = patches[vertex]
            break
    else:
        return

    first_gate = (chain[0], chain[1])

    # Create the fifo
    fifo.append(first_gate)

    # Loop over the model
    while len(fifo) > 0:
        # Retrieve the first element of the fifo
        gate = fifo.pop(0)
        if gate in done:
            continue
        else:
            done.add(gate)

        # Retrieve the front vertex
        front = gates[gate]
        chain = patches[front]
        left, right = gate

        # conquered or null
        if faces_status.get(gate) is not None:
            print('*', end='')
            continue

        elif valences[front] == 3 and vertices_status.get(front) is None:
            print('.', end='')

            # Remove the vertex
            active_vertices.remove(front)

            for left, right in fifo.copy():
                if left == front or right == front:
                    fifo.remove((left, right))
                    
            # Update obja
            obja += f"v {vertices[front-1][0]}  {vertices[front-1][1]}  {vertices[front-1][2]}\n"
            obj_to_obja[count_v] = front
            count_v += 1
            
            # Update the valences
            for point in chain:
                valences[point] -= 1
                # Remove the old gates
                gates.pop((front, point))
                gates.pop((point, front))

            # Update the faces
            gates[(chain[0], chain[1])] = chain[2]
            gates[(chain[1], chain[2])] = chain[0]
            gates[(chain[2], chain[0])] = chain[1]

            # Update the patches
            for point in chain:
                patches[point] = patches[point][patches[point] != front]
                vertices_status[point] = 'conquered'

            # Update face status
            faces_status[(chain[1], chain[0])] = 'conquered'
            faces_status[(chain[2], chain[1])] = 'conquered'

            # Update fifo
            front_1 = gates[(chain[1], chain[0])]
            front_2 = gates[(chain[2], chain[1])]
            fifo.append((front_1, chain[0]))
            fifo.append((chain[1], front_1))
            fifo.append((front_2, chain[1]))
            fifo.append((chain[2], front_2))
            
            # Update obja
            obja += f"f {front}  {chain[0]}  {chain[1]}\n"
            obja += f"f {front}  {chain[1]}  {chain[2]}\n"
            obja += f"f {front}  {chain[2]}  {chain[0]}\n"
            obja += f"df {chain[0]}  {chain[1]}  {chain[2]}\n"
 

        elif valences[front] <= 6 and vertices_status.get(front) is None:
            print("-", end='')
            try:
                i = np.where(chain == right)[0][0]
            except IndexError:
                print(chain)
                print(right)
                print(front)
            chain = np.append(chain[i:], chain[:i])
            for gate in zip(chain[1:], chain[:-1]):
                fifo.append(gate)
                faces_status[(gate[-1], gate[0])] = 'conquered'

        elif (vertices_status.get(front) is None and valences[front] > 6) or (
                vertices_status.get(front) == 'conquered'):
            print('o', end='')

            # Set the front face to null
            faces_status[gate] = 'null'

            # Add the other edges to the fifo
            fifo.append((front, right))
            fifo.append((left, front))
    return obja, count_v

def write_obj(active_vertices, gates, vertices, count_v, obj_to_obja):
    obj_f = ""
    new_indices = {}
    local_copy = gates.copy()
    for k, vertex in enumerate(active_vertices):
        x, y, z = vertices[vertex-1]
        obj_f += f"v {x} {y} {z}\n"
        obj_to_obja[count_v] = vertex
        count_v += 1
        new_indices[vertex] = k + 1

    for gate in gates.copy():
        left, right = gate
        try:
            front = local_copy[gate]
            local_copy.pop(gate)
            if local_copy[(right, front)] == left:
                local_copy.pop((right, front))
            else:
                print('\t\t WTF \t\t')
                print('face: {}-{}-{}, th: {}, found: {}'.format(
                    right, front, left, left, local_copy[(right, front)]))
            if local_copy[(front, left)] == right:
                local_copy.pop((front, left))
            else:
                print('\t\t WTF \t\t')
                print('f: {}-{}-{}, th: {}, found: {}'.format(
                    front, left, right, right, local_copy[(front, left)]))
            obj_f += f"f {new_indices[left]} {new_indices[right]} {new_indices[front]}\n"
        except KeyError:
            continue
    return obj_f

def sew_conquest(gates, patches, active_vertices, valences, vertices, faces , obja, count_v, obj_to_obja):
    for vertex in active_vertices.copy():
        if valences[vertex] == 2:
            try:
                active_vertices.remove(vertex)
                chain = patches[vertex]
                gates.pop((chain[0], vertex))
                gates.pop((chain[1], vertex))
                gates.pop((vertex, chain[0]))
                gates.pop((vertex, chain[1]))
                
                # Update obja
                x, y, z = vertices[vertex-1]
                obja += f"v {x} {y} {z}\n"
                obj_to_obja[count_v] = vertex
                count_v += 1
                
                patch = patches[chain[0]]
                patches[chain[0]] = patch[patch != vertex]
                patch = patches[chain[0]]
                k = np.where(patch == chain[1])[0][0]
                patches[chain[0]] = patch[np.r_[0:k, k+1:len(patch)]]
                valences[chain[0]] -= 2

                patch = patches[chain[1]]
                patches[chain[1]] = patch[patch != vertex]
                patch = patches[chain[1]]
                k = np.where(patch == chain[0])[0][0]
                patches[chain[1]] = patch[np.r_[0:k, k+1:len(patch)]]
                valences[chain[1]] -= 2

                patch = patches[chain[0]]
                k = np.where(patch == chain[1])[0]
                if len(k) > 1:
                    print(patch)
                    k = k[0]
                gates[(chain[1], chain[0])] = int(patch[k-1])

                patch = patches[chain[1]]
                k = np.where(patch == chain[0])[0]
                if len(k) > 1:
                    print(patch)
                    k = k[0]
                gates[(chain[0], chain[1])] = int(patch[k-1])
            except KeyError:
                continue

    to_duplicate = {}
    for front, chain in patches.items():
        if len(set(chain)) != len(chain):
            copy = chain.copy()
            copy.sort()
            to_duplicate[front] = copy[np.where(np.diff(copy) == 0)[0]][0]
    while len(to_duplicate) > 0:
        left, right = to_duplicate.popitem()
        to_duplicate.pop(right)

        vertices.append(vertices[left-1])
        new_left = len(vertices)
        vertices.append(vertices[right-1])
        new_right = new_left + 1

        # TODO: do something to treat the shared edges
    return obja, count_v


