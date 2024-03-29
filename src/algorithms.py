import logging
import numpy as np
import random

from vertex import *
from graph import *

from graph import Graph


# Partitioning Algorithms

# Breadth First Search (BFS)


def pa_bfs(graph, vertex_ith: int, threshold: int):
    """Algorithm description: We can use basic graph search algorithm to solve graph partition algorithm :)
    Basically, the well-known BFS (Breadth-First-Search) algorithm can be modified to help us divide graph into two
    parts. BFS algorithm traverses the graph level by level and marks each vertex with the level in which it was
    visited. After completion of the traversal, the set of vertices of the graph is portioned into two parts $V_1$
    and $V_2$ by putting all vertices with level less than or equal to a pre-determined threshold $L$ in the set V1
    and putting the remaining vertices (with level greater than $L$) in the set $V_2$. $L$ is so chosen that $|V1|$
    is close to $|V2|$.

    References: 
    [1] Graph Partitioning, https://patterns.eecs.berkeley.edu/?page_id=571#1_BFS
    """
    L1 = set()
    L2 = set()

    # get the vertex `vertex_ith`.
    vertex = graph.getVertex(vertex_ith)

    # checking if not exist `vertex_ith` in Graph then raise error.
    if not vertex:
        message = 'Invalid vertex id, could not found vertex id `' + \
                  str(vertex_ith) + '` in Graph'
        raise ValueError(get_log(message, log_type='ERROR'))

    # get the number of vertices.
    n = graph.numVertices

    # bool array for marking visited or not.
    visited = [False] * n

    # get the vertex_id for easy management.
    vertex_id = vertex.getId()

    # initializing a queue to handling which vertex is remaining.
    queue = [vertex_id]

    # marking the `vertex_id` is visited due to the beginning vertex.
    visited[vertex_id] = True

    path = []  # path to track the working state of BFS.

    level = 0
    while queue:
        # handling current vertex before removing out of queue.
        cur_pos = queue[0]

        # appending to path to track.
        path.append(cur_pos)

        # remove it out of queue
        queue.pop(0)

        # get all neighbors id of current vertex.
        neighbor_cur_pos = [
            x.id for x in graph.getVertex(cur_pos).getConnections()]

        # loop over the neighbor of current vertex.
        for neighborId in neighbor_cur_pos:
            # if not visited then push that vertex into queue.
            if not visited[neighborId]:
                visited[neighborId] = True
                graph.vertList[neighborId].level = level
                if level >= threshold:
                    L2.add(neighborId)
                else:
                    L1.add(neighborId)
                queue.append(neighborId)
        level += 1

    logging.info("Group A vertices: {}".format(L1))
    logging.info("Group B vertices: {}".format(L2))
    return L1, L2


# Kerninghan-Lin (KL) algorithm
def pa_kl(graph):
    """Algorithm description: The KL algorithm is a heuristic algorithm for partitioning a graph into two disjoint
    sets of vertices with roughly equal sizes, while minimizing the total weight of the edges between the two sets.
    The algorithm works by iteratively swapping vertices between the two sets in a way that reduces the total weight
    of the cut.

    The algorithm starts by dividing the vertices into two sets, A and B, with roughly equal sizes. 
    Then, it iteratively performs the following steps:
        Step 1: Compute the net gain for moving each vertex from set A to set B, and vice versa. 
        The net gain is defined as the difference between the sum of the weights of the edges 
        that connect the vertex to its current set and the sum of the weights of the edges 
        that connect the vertex to the other set.

        Step 2: Select the pair of vertices with the highest net gain, one from set A and one from set B, and swap them.

        Step 3: Update the net gains for the affected vertices, and repeat the process until no more swaps can be made.

    The algorithm terminates when no more swaps can be made that improve the total weight of the cut. 
    The final partitioning is the one that results in the minimum cut.

    References: 
    [1] Graph Partitioning, https://patterns.eecs.berkeley.edu/?page_id=571#1_BFS
    """
    # Partition the vertices into two equal-sized groups A and B.

    half = graph.numVertices // 2
    for ind in range(half):
        graph.vertList[ind].partition_label = 'A'
        graph.vertList[ind + half].partition_label = 'B'

    total_gain = 0

    # Keep track of the total gain in each iteration.
    for _ in range(half):
        # Get the vertices in groups A and B and their D values.
        group_a = [v.id for k, v in graph.vertList.items()
                   if v.partition_label == "A"]
        group_b = [v.id for k, v in graph.vertList.items()
                   if v.partition_label == "B"]

        D_values = {}

        for idx, vertex in graph.vertList.items():
            for neighbor in vertex.connectedTo:
                if vertex.partition_label == neighbor.partition_label:
                    vertex.internal_cost += vertex.getWeight(neighbor)
                else:
                    vertex.external_cost -= vertex.getWeight(neighbor)

            D_values.update(
                {idx: graph.vertList[idx].external_cost + graph.vertList[idx].internal_cost})

        # Compute the gains for all possible vertex swaps between groups A and B.
        gains = []
        for a in group_a:
            for b in group_b:
                c_ab = graph.vertList[a].getWeight(graph.vertList[b])
                gain = D_values[a] + D_values[b] - (2 * c_ab)
                gains.append([[a, b], gain])

        # Sort the gains in descending order and get the maximum gain.
        gains = sorted(gains, key=lambda x: x[1], reverse=True)
        max_gain = gains[0][1]

        if max_gain <= 0:
            break

        # Get the pair of vertices with the maximum gain and swap their partition labels.
        pair = gains[0][0]
        group_a.remove(pair[0])
        group_b.remove(pair[1])

        graph.vertList[pair[0]].partition_label = "B"
        graph.vertList[pair[1]].partition_label = "A"

        # Update the D values of the vertices in groups A and B.
        for x in group_a:
            c_xa = graph.vertList[x].getWeight(graph.vertList[pair[0]])
            c_xb = graph.vertList[x].getWeight(graph.vertList[pair[1]])
            D_values[x] += 2 * c_xa - 2 * c_xb

        for y in group_b:
            c_ya = graph.vertList[y].getWeight(graph.vertList[pair[0]])
            c_yb = graph.vertList[y].getWeight(graph.vertList[pair[1]])
            D_values[x] += 2 * c_ya - 2 * c_yb

        # Update the total gain.
        total_gain += max_gain

        # break

    # Get the cutset size and the vertex IDs in groups A and B.
    cutset_size = graph.compute_partition_cost()
    group_a = [v.id for k, v in graph.vertList.items()
               if v.partition_label == "A"]
    group_b = [v.id for k, v in graph.vertList.items()
               if v.partition_label == "B"]

    # Print the results
    logging.info("Cut size: {}".format(cutset_size))
    logging.info("Group A vertices: {}".format(group_a))
    logging.info("Group B vertices: {}".format(group_b))

    return cutset_size, group_a, group_b


"""
The KL algorithm is a fast and effective heuristic for graph partitioning, and is widely used in practice. 
However, it is not guaranteed to find the optimal partitioning, and can get stuck in local minima. 
As a result, it is often used in combination with other algorithms or as a preprocessing step 
for more sophisticated partitioning algorithms.
"""


#########################################################################################################
# Fiduccia-Mattheyses (FM) algorithm


def pa_fm(graph):
    """Algorithm description: The FM algorithm is another popular heuristic algorithm for partitioning a graph into
    two disjoint sets of vertices with roughly equal sizes, while minimizing the total weight of the edges between
    the two sets. The algorithm works by iteratively moving vertices between the two sets in a way that reduces the
    total weight of the cut.

    The algorithm starts by dividing the vertices into two sets, A and B, with roughly equal sizes. 
    Then, it iteratively performs the following steps:
        Step 1: Compute the net gain for moving each vertex from set A to set B, and vice versa. 
        The net gain is defined as the difference between the sum of the weights of the edges 
        that connect the vertex to its current set and the sum of the weights of the edges 
        that connect the vertex to the other set.

        Step 2:  select one node according to some criterion, remove it from its present partition and put it to the
        other partition

        Step 3: Update the gains of the affected vertices, and repeat the process until no more vertices can be moved
        that result in a decrease in the total weight of the cut.

    The algorithm terminates when no more vertices can be moved that result in a decrease in the total weight of the
    cut. The final partitioning is the one that results in the minimum cut.

    References: 
    [1] Graph Partitioning, https://patterns.eecs.berkeley.edu/?page_id=571#1_BFS
    """

    # Partition the vertices into two equal-sized groups A and B.
    half = graph.numVertices // 2
    for ind in range(half):
        graph.vertList[ind].partition_label = 'A'
        graph.vertList[ind + half].partition_label = 'B'

    total_gain = 0

    # Keep track of the total gain in each iteration.
    for _ in range(half):
        # Get the vertices in groups A and B and their D values.
        group_a = [v.id for k, v in graph.vertList.items()
                   if v.partition_label == "A"]
        group_b = [v.id for k, v in graph.vertList.items()
                   if v.partition_label == "B"]

        D_values = {}

        for idx, vertex in graph.vertList.items():
            for neighbor in vertex.connectedTo:
                if vertex.partition_label == neighbor.partition_label:
                    vertex.internal_cost += vertex.getWeight(neighbor)
                else:
                    vertex.external_cost -= vertex.getWeight(neighbor)

            D_values.update(
                {idx: graph.vertList[idx].external_cost + graph.vertList[idx].internal_cost})

        # Compute the gains for all possible vertex swaps between groups A and B.
        gains = []
        for a in group_a:
            for b in group_b:
                c_ab = graph.vertList[a].getWeight(graph.vertList[b])
                gain = D_values[a] + D_values[b] - (2 * c_ab)
                gains.append([[a, b], gain])

        # Sort the gains in descending order and get the maximum gain.
        gains = sorted(gains, key=lambda x: x[1], reverse=True)
        min_gain = gains[-1][1]

        if min_gain <= 0:
            break

        # Get the pair of vertices with the maximum gain and swap their partition labels.
        pair = gains[0][0]


        # Random locked vertex
        locked_vertex = random.randint(0, 1)

        if locked_vertex == 0:
             graph.vertList[pair[0]].partition_label = "B"
        else:
            graph.vertList[pair[1]].partition_label = "A"

        # Update the D values of the vertices in groups A and B.
        for x in group_a:
            c_xa = graph.vertList[x].getWeight(graph.vertList[pair[0]])
            c_xb = graph.vertList[x].getWeight(graph.vertList[pair[1]])
            D_values[x] += 2 * c_xa - 2 * c_xb

        for y in group_b:
            c_ya = graph.vertList[y].getWeight(graph.vertList[pair[0]])
            c_yb = graph.vertList[y].getWeight(graph.vertList[pair[1]])
            D_values[x] += 2 * c_ya - 2 * c_yb

        # Update the total gain.
        total_gain += min_gain

        # break

    # Get the cutset size and the vertex IDs in groups A and B.
    cutset_size = graph.compute_partition_cost()
    group_a = [v.id for k, v in graph.vertList.items()
               if v.partition_label == "A"]
    group_b = [v.id for k, v in graph.vertList.items()
               if v.partition_label == "B"]

    # Print the results
    logging.info("Cut size: {}".format(cutset_size))
    logging.info("Group A vertices: {}".format(group_a))
    logging.info("Group B vertices: {}".format(group_b))

    return cutset_size, group_a, group_b


"""The FM algorithm is a fast and effective heuristic for graph partitioning, and is often used in combination with 
other algorithms or as a preprocessing step for more sophisticated partitioning algorithms. Like the KL algorithm, 
it is not guaranteed to find the optimal partitioning, and can get stuck in local minima. However, it is often faster 
and more scalable than the KL algorithm, making it a popular choice for large-scale graph partitioning problems."""


#########################################################################################################
# Spectral Bisection


def pa_sb(graph):
    """Algorithm description:

    The Spectral Bisection algorithm is a graph partitioning algorithm that is based on the eigenvalues and
    eigenvectors of the graph Laplacian matrix. The algorithm works by iteratively bisecting the graph into two
    disjoint sets of vertices with roughly equal sizes, while minimizing the total weight of the edges between the
    two sets.

    The algorithm starts by computing the eigenvectors corresponding to the smallest eigenvalues of the graph
    Laplacian matrix. The eigenvectors are then used to partition the graph into two sets of vertices, A and B,
    by assigning each vertex to the set that corresponds to the sign of the corresponding eigenvector component. This
    initial partitioning is not guaranteed to be balanced, but is usually close to it.

    Then, the algorithm iteratively improves the partitioning by performing the following steps: Step 1: Compute the
    cut size of the current partitioning. Step 2: Compute the eigenvectors corresponding to the second-smallest
    eigenvalues of the graph Laplacian matrix. Step 3: Compute the projection of the current partitioning onto the
    space spanned by the eigenvectors corresponding to the smallest and second-smallest eigenvalues. This projection
    is used to determine a new partitioning by assigning each vertex to the set that corresponds to the sign of the
    projection. Step 4: Compute the cut size of the new partitioning, and select it if it has a smaller cut size than
    the current partitioning. Otherwise, discard the new partitioning and continue with the current one.

    The algorithm terminates when no more improvements can be made, or when a desired balance ratio between the two
    sets is achieved. The final partitioning is the one that results in the minimum cut.

    References: 
    [1] Graph Partitioning, https://patterns.eecs.berkeley.edu/?page_id=571#1_BFS
    """
    laplacian_matrix = graph.compute_laplacian_matrix()
    logging.info('Computing the eigenvectors and eigenvalues')
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian_matrix)

    # Index of the second eigenvalue
    index_fnzev = np.argsort(eigenvalues)[1]
    logging.info('Eigenvector for #{} eigenvalue ({}): '.format(
        index_fnzev, eigenvalues[index_fnzev]), eigenvectors[:, index_fnzev])

    # Partition on the sign of the eigenvector's coordinates
    partition = [val >= 0 for val in eigenvectors[:, index_fnzev]]

    # Compute the edges in between
    logging.info('Compute the edges in between two groups.')
    a = [idx for (idx, group_label) in enumerate(partition) if group_label]
    b = [idx for (idx, group_label) in enumerate(partition) if not group_label]

    group_a = [v.id for k, v in graph.vertList.items()
               if v.id in a]
    group_b = [v.id for k, v in graph.vertList.items()
               if v.id in b]

    logging.info("Group A vertices: {}".format(group_a))
    logging.info("Group B vertices: {}".format(group_b))
    return group_a, group_b


"""The Spectral Bisection algorithm is a powerful graph partitioning algorithm that can produce high-quality 
partitions for a wide range of graph types. However, it can be computationally expensive, especially for large 
graphs, due to the need to compute the eigenvalues and eigenvectors of the Laplacian matrix."""
#########################################################################################################
def pa_scc_kl(graph):
    # Identify the connected components in the graph using DFS
    scc_lst = graph.find_strongly_connected_components()

    # Compute the weight of each component
    weights = [abs(len(c) - graph.numVertices/2) for c in scc_lst]

    # Sort the components by weight in descending order
    sorted_scc_lst = [c for _,c in sorted(zip(weights, scc_lst), reverse=True)]

    # Initialize the partition as an empty list
    partition = {}

    # Iterate over each connected component and attempt to partition it
    for component in sorted_scc_lst:
        print(component)
        subgraph = Graph()
    
        for vertex in component:
            subgraph.addVertex(vertex)
            for neighbor in graph.vertList[vertex].connectedTo:
                if neighbor.getId() not in component:
                    subgraph.addVertex(neighbor.getId())
                    subgraph.addEdge(vertex, neighbor.getId(), graph.vertList[vertex].getWeight(neighbor))

        
        # Partition the subgraph using a heuristic algorithm
        # such as Kernighan-Lin or Fiduccia-Mattheyses
        # Here we'll use Kernighan-Lin
        cutset_size, partition_1, partition_2 = pa_kl(subgraph)

        # Add the partitions to the overall partition
        partition.setdefault('partition_1', []).append(partition_1)
        partition.setdefault('partition_2', []).append(partition_2)

    return partition



#########################################################################################################
# Recursive Bisection
"""
this is the description

"""


def get_subgraphs(partition):
    group_a, group_b = [], []
    for k, v in partition.items():
        if v == 'A':
            group_a.append(k)
        else:
            group_b.append(k)
    return group_a, group_b


def save_partition(graph: Graph, partition: dict, condition: str, subgraph1=None):
    for vertex in graph.getVertices():
        if eval(condition):
            partition[vertex] = "A"
        else:
            partition[vertex] = "B"

    return partition


def partition_vertices(graph):
    # Partition the vertices into two equal-sized groups A and B.
    half = graph.numVertices // 2
    total_gain = 0
    # Keep track of the total gain in each iteration.
    for _ in range(half):
        # Get the vertices in groups A and B and their D values.
        group_a = [v.id for k, v in graph.vertList.items()
                   if v.partition_label == "A"]
        group_b = [v.id for k, v in graph.vertList.items()
                   if v.partition_label == "B"]

        D_values = {}

        for idx, vertex in graph.vertList.items():
            for neighbor in vertex.getConnections():
                if vertex.partition_label == neighbor.partition_label:
                    vertex.internal_cost += vertex.getWeight(neighbor)
                else:
                    vertex.external_cost -= vertex.getWeight(neighbor)

            D_values.update(
                {idx: graph.vertList[idx].external_cost + graph.vertList[idx].internal_cost})

        # Compute the gains for all possible vertex swaps between groups A and B.
        gains = []
        for a in group_a:
            for b in group_b:
                c_ab = graph.vertList[a].getWeight(graph.vertList[b])
                gain = D_values[a] + D_values[b] - (2 * c_ab)
                gains.append([[a, b], gain])

        # Sort the gains in descending order and get the maximum gain.
        max_gain = 0
        if len(gains):
            gains = sorted(gains, key=lambda x: x[1], reverse=True)
            max_gain = gains[0][1]

        if max_gain <= 0:
            break

        # Get the pair of vertices with the maximum gain and swap their partition labels.
        pair = gains[0][0]
        group_a.remove(pair[0])
        group_b.remove(pair[1])

        graph.vertList[pair[0]].partition_label = "B"
        graph.vertList[pair[1]].partition_label = "A"

        # Update the D values of the vertices in groups A and B.
        for x in group_a:
            c_xa = graph.vertList[x].getWeight(graph.vertList[pair[0]])
            c_xb = graph.vertList[x].getWeight(graph.vertList[pair[1]])
            D_values[x] += 2 * c_xa - 2 * c_xb

        for y in group_b:
            c_ya = graph.vertList[y].getWeight(graph.vertList[pair[0]])
            c_yb = graph.vertList[y].getWeight(graph.vertList[pair[1]])
            D_values[x] += 2 * c_ya - 2 * c_yb

        # Update the total gain.
        total_gain += max_gain

    group_a = [v.id for k, v in graph.vertList.items()
               if v.partition_label == "A"]
    group_b = [v.id for k, v in graph.vertList.items()
               if v.partition_label == "B"]
    subgraph1 = Graph()
    subgraph2 = Graph()
    for vertex in graph:
        if vertex.partition_label == "A":
            subgraph1.addVertex(vertex.id, vertex.partition_label)
            for neighbor in vertex.getConnections():
                if neighbor.id in group_a:
                    subgraph1.addEdge(vertex.id, neighbor.id, vertex.getWeight(neighbor))
        else:
            subgraph2.addVertex(vertex.id, vertex.partition_label)
            for neighbor in vertex.getConnections():
                if neighbor.id in group_b:
                    subgraph2.addEdge(vertex.id, neighbor.id, vertex.getWeight(neighbor))

    return subgraph1, subgraph2


def partition_graph(graph: Graph, partition, max_levels: int, min_size: int, weight_threshold: float):
    if graph.numVertices <= min_size or max_levels == 0:
        partition = save_partition(graph, partition, "len(partition) % 2 == 0")
        return partition

    subgraph1, subgraph2 = partition_vertices(graph)

    # Check if the sub-graphs are balanced by using the weight proportion
    balance_byWeight = abs(subgraph1.compute_total_weight() - subgraph2.compute_total_weight()) \
                       / graph.compute_total_weight()

    if balance_byWeight < weight_threshold:
        partition = save_partition(graph, partition, "vertex in subgraph1.getVertices()", subgraph1)
        return partition

    # Recursively partition the sub-graphs
    partition_graph(subgraph1, partition, max_levels - 1, min_size, weight_threshold)
    partition_graph(subgraph2, partition, max_levels - 1, min_size, weight_threshold)


def recursive_bisection(graph: Graph, max_levels=3, min_size=1, weight_threshold=0.02):
    partition = {}
    partition_graph(graph, partition, max_levels, min_size, weight_threshold)
    group_a, group_b = get_subgraphs(partition)
    logging.info("Group A vertices: {}".format(group_a))
    logging.info("Group B vertices: {}".format(group_b))
    return group_a, group_b


def greedyColoring(graph):
    # Initialize a color map for the vertices
    color_map = {}

    # Sort vertices by their degree
    vertices = sorted(graph.vertList.values(), key=lambda vertex: len(vertex.getConnections()), reverse=True)

    # Iterate over vertices and assign a color
    for vertex in vertices:
        used_colors = set()
        v_id = vertex.getId()
        for neighbor in vertex.getConnections():
            n_id = neighbor.getId()
            if n_id in color_map:
                used_colors.add(color_map[n_id])
        for color in range(graph.numVertices):
            if color not in used_colors:
                color_map[v_id] = color
                break
    color_group = {}
    for v_id, color in color_map.items():
        if not color_group.get(color):
            color_group[color] = []
        color_group[color].append(v_id)

    for color, group in color_group.items():
        logging.info("Color {}: {}".format(color, group))
    # Return the color map
    return color_map


def get_closest_centroid( graph: Graph, node, centroids):
    dist_arr = []
    for c_id in centroids:
        distance = graph.get_edge_weight_bfs(node, c_id)
        dist_arr.append(distance)

    return np.argmin(dist_arr), np.min(dist_arr)


def recompute_new_centroid(graph: Graph, samples):
    dist_toOthers = np.array(list(map(lambda p: sum(map(lambda other: graph.get_edge_weight_bfs(p, other), samples)),
                                      samples)))
    return samples[np.argmin(dist_toOthers)]


def update_centroids(graph: Graph, c_ids, cur_centroids, thredshold, total_dist, optimal_total_dist):
    has_converged = True
    old_total = optimal_total_dist.copy()
    new_total = total_dist.copy()
    result = new_total

    d = sum(map(lambda i: abs(new_total[i]) / old_total[i],[i for i in range(len(old_total))]))

    if d > thredshold:
        has_converged = False
        result = optimal_total_dist
        c_ids = cur_centroids

    return has_converged, c_ids, result


def k_medois(graph: Graph, k=3, thredshold=2, max_iter=500):

    # init centroids and parameters
    c_ids = random.sample(graph.getVertices(), k)
    has_converged = False
    groups_data = [[] for _ in range(k)]
    optimal_total_dist = [math.inf for _ in range(k)]
    # Looping until converged
    for _ in range(max_iter):
        cur_centroids = []
        total_dist = []
        # Clustering samples has the same centroid `c_id`
        for i, c_id in enumerate(c_ids):
            samples = []
            d_min = []
            for v_id in graph.getVertices():
                c, min_c = get_closest_centroid(graph, v_id, c_ids)
                if c == i:
                    samples.append(v_id)
                    d_min.append(min_c)

            # Compute new centroid
            new_centroid = recompute_new_centroid(graph, samples)
            cur_centroids.append(new_centroid)
            total_dist.append(sum(d_min))
            groups_data[i] = samples.copy()
        has_converged, c_ids, optimal_total_dist = update_centroids(graph, c_ids, cur_centroids, thredshold, total_dist,
                                                                    optimal_total_dist)
        if has_converged:
            print(optimal_total_dist)
            break

    # Returned k clusters with its elements
    for c_id, dist, group in zip(c_ids, optimal_total_dist, groups_data):
        logging.info("Group {} has minimum distance {} with samples: {}".format(c_id, dist, group))
    return c_ids, groups_data
