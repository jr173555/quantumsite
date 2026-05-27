import numpy as np
import networkx as nx


def unspec_grid(n: int) -> tuple[list[tuple[int, int, int]], list[tuple[int, int]]]:
    """Generate vertices and edges for an n×n 2D grid in the z=0 plane.

    Vertices are laid out row-by-row (y first, then x) and are represented as
    3-tuples ``(x, y, 0)``.  Edges connect each vertex to its right neighbor
    (``x+1``) and its upper neighbor (``y+1``), forming a regular lattice.

    Args:
        n: The number of vertices along each axis, producing an n×n grid.

    Returns:
        coords: A list of ``(x, y, 0)`` tuples — one per vertex, ordered
            row-by-row from ``(0, 0, 0)`` to ``(n-1, n-1, 0)``.
        edges: A list of ``(idx1, idx2)`` tuples where each value is an index
            into *coords*, representing an undirected edge between two
            adjacent vertices.

    Example:
        >>> coords, edges = unspec_grid(2)
        >>> coords
        [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)]
        >>> edges
        [(0, 1), (0, 2), (1, 3), (2, 3)]
    """
    coords: list[tuple[int, int, int]] = []
    for y in range(n):
        for x in range(n):
            # for z in range(6):  # 0 to 5
            coords.append((x, y, 0))

    edges: list[tuple[int, int]] = []
    for y in range(n):
        for x in range(n):
            coord1: tuple[int, int, int] = (x, y, 0)
            idx1: int = coords.index(coord1)
            if x < n - 1:
                coord2: tuple[int, int, int] = (x + 1, y, 0)
                idx2: int = coords.index(coord2)
                edges.append((idx1, idx2))
            if y < n - 1:
                coord3: tuple[int, int, int] = (x, y + 1, 0)
                idx3: int = coords.index(coord3)
                edges.append((idx1, idx3))

    return coords, edges


def grid_into_graph(
    coords: list[tuple[int, int, int]],
    edges: list[tuple[int, int]],
    distance_weight: bool = False,
) -> nx.Graph:
    """Convert grid vertices and edges into a NetworkX graph.

    The weights of the edges can be set to the Euclidean distance between vertices if
    `distance_weight` is True.  Otherwise, edges will have a default weight of 1.

    Args:
        coords: A list of vertex coordinates as (x, y, z) tuples.
        edges: A list of edges as (idx1, idx2) tuples where each index
            corresponds to a vertex in *coords*.
        distance_weight: Whether to use Euclidean distance as edge weights.

    Returns:
        A NetworkX graph where each vertex is labeled with its (x, y, z)
        coordinate and edges connect adjacent vertices as specified by *edges*.
    """
    graph = nx.Graph()
    for idx, coord in enumerate(coords):
        graph.add_node(idx, coord=coord)
    for idx1, idx2 in edges:
        graph.add_edge(idx1, idx2)
    if distance_weight:
        positions1 = np.array([coord[edge[0]] for edge in edges])
        positions2 = np.array([coord[edge[1]] for edge in edges])
        weights = np.linalg.norm(positions1 - positions2, axis=1)
    else:
        weights = np.ones(len(edges))
    for (idx1, idx2), weight in zip(edges, weights):
        graph.edges[idx1, idx2]["weight"] = weight
    return graph
