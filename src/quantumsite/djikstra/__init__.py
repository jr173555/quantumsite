# TODO: Phase 1 (Planer): first implement a Ground Truth Planner (perfekte Route) (A*, D*Lite, (Djikstra)), Phase 2 collect data,
# Phase 3 (Optimizer): the reinforcement learning algorithm um möglichst nah an A* Lösung zu kommen

import random
import networkx as nx
import matplotlib.pyplot as plt


def random_graph(n=12, extra_p=0.25, wmin=1, wmax=9, seed=None):
    """
    Create a random, connected, undirected, weighted graph and a layout for plotting.

    This function produces:
      1) A NetworkX Graph `G` with nodes labeled 0..n-1
      2) A 2D position dictionary `pos` (node -> (x, y)) for plotting
      3) A random start node and a random target node (distinct)

    Connectivity guarantee:
      - First, it builds a random spanning tree by connecting each node i (from 1..n-1)
        to a random earlier node j in [0, i-1]. This ensures the graph is connected.
      - Then it adds additional random edges (non-duplicates) with probability `extra_p`.

    Edge weights:
      - Each edge gets an integer weight in [wmin, wmax].
      - Dijkstra requires non-negative weights; this function always uses positive integers.

    Plot layout (less crowded):
      - Uses NetworkX spring_layout, which is a force-directed layout.
      - Parameters k, scale, and iterations are chosen to spread nodes further apart.

    Parameters
    ----------
    n : int
        Number of nodes (nodes will be 0..n-1).
    extra_p : float
        Probability of adding any potential extra edge (i, j) not already present.
        Higher values create denser graphs.
    wmin, wmax : int
        Minimum and maximum integer edge weights (inclusive).
    seed : int or None
        If given, random generator is seeded for reproducible graphs and layout.

    Returns
    -------
    G : nx.Graph
        Connected, undirected, weighted graph.
    pos : dict[int, tuple[float, float]]
        Node positions for plotting.
    start : int
        Random start node.
    target : int
        Random target node.
    """
    if seed is not None:
        random.seed(seed)

    G = nx.Graph()
    G.add_nodes_from(range(n))

    # Build a spanning tree to guarantee connectivity
    for i in range(1, n):
        j = random.randrange(0, i)
        G.add_edge(i, j, weight=random.randint(wmin, wmax))

    # Add extra edges to increase density
    for i in range(n):
        for j in range(i + 1, n):
            if not G.has_edge(i, j) and random.random() < extra_p:
                G.add_edge(i, j, weight=random.randint(wmin, wmax))

    # Choose start/target
    start, target = random.sample(list(G.nodes), 2)

    # Spread-out layout
    pos = nx.spring_layout(G, seed=seed, k=2.2, iterations=300, scale=4.0)

    return G, pos, start, target


def pick_min(unvisited, dist):
    """
    Pick the node with the smallest distance from a list of unvisited nodes.

    This is the key operation that replaces a priority queue (heap):
    - In classic Dijkstra with a heap, you can get the min-distance node in O(log V).
    - With a simple list, we scan all candidates, which costs O(V) per selection.

    Parameters
    ----------
    unvisited : list[int]
        Nodes not settled yet (still candidates).
    dist : list[float]
        dist[v] is the current best-known distance from the start to v.

    Returns
    -------
    m : int
        The node in `unvisited` with minimal dist[m].
    """
    m = unvisited[0]
    for v in unvisited[1:]:
        if dist[v] < dist[m]:
            m = v
    return m


def dijkstra_steps(G, start, target):
    """
    Dijkstra's algorithm (without heapq) as a step-by-step generator.

    IMPORTANT:
      - This implementation uses only simple Python lists/sets.
      - It is intended for learning / step visualization rather than performance.

    Algorithm overview:
      - dist[v] = best-known distance from `start` to v
      - prev[v] = predecessor of v on the shortest path found so far
      - unvisited = list of nodes not "settled" yet
      - visited = set of settled nodes (final shortest distance is known)

    Per iteration:
      1) Select u = node in unvisited with smallest dist[u]
      2) If dist[u] == infinity, no remaining reachable nodes -> stop
      3) Remove u from unvisited, add to visited
      4) For each neighbor v of u not in visited:
           if dist[u] + w(u,v) < dist[v], update dist[v] and prev[v]
      5) Yield state for visualization

    Yielded state:
      - current node u that was just settled
      - visited set
      - frontier set (unvisited nodes that already have a finite dist)
      - dist list
      - prev list

    Complexity (with lists):
      - Selecting the minimum each step: O(V)
      - Done V times: O(V^2)
      - Relaxation over edges total: O(E)
      => Overall: O(V^2 + E)

    Preconditions / assumptions:
      - Nodes are labeled 0..n-1 (true for random_graph()) so we can use lists.
      - Edge weights are non-negative.

    Parameters
    ----------
    G : nx.Graph
        Weighted graph. Each edge must have attribute "weight" (non-negative).
    start : int
        Start node (source).
    target : int
        Target node (destination). Algorithm stops early once target is settled.

    Yields
    ------
    u : int
        Node that got settled in this step.
    visited : set[int]
        All settled nodes so far.
    frontier : set[int]
        Nodes that are not yet settled but already have finite distance estimates.
    dist : list[float]
        Current best-known distance values.
    prev : list[int|None]
        Predecessor pointers for path reconstruction.
    """
    n = G.number_of_nodes()
    INF = float("inf")

    dist = [INF] * n
    prev = [None] * n
    dist[start] = 0

    unvisited = list(G.nodes)
    visited = set()

    while unvisited:
        u = pick_min(unvisited, dist)

        # If the best remaining node is unreachable, stop.
        if dist[u] == INF:
            return

        unvisited.remove(u)
        visited.add(u)

        # Relax outgoing edges from u
        for v in G.neighbors(u):
            if v in visited:
                continue
            w = G[u][v]["weight"]
            nd = dist[u] + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u

        # "Frontier" = currently discovered but not yet settled nodes
        frontier = {v for v in unvisited if dist[v] < INF}

        yield u, visited, frontier, dist, prev

        if u == target:
            return


def build_path(prev, start, target):
    """
    Reconstruct the shortest path using a predecessor array.

    The predecessor array `prev` encodes a shortest-path tree:
      - prev[v] = the node right before v on the best known path from `start` to v
      - prev[start] is typically None

    Reconstruction:
      - Start from `target`, repeatedly follow prev[] backwards until `start`.
      - Reverse the collected list to get start->target order.

    Edge cases:
      - If start == target, path is [start].
      - If target is unreachable, prev[target] may be None => return [].

    Parameters
    ----------
    prev : list[int|None]
        Predecessor pointers.
    start : int
        Start node.
    target : int
        Target node.

    Returns
    -------
    path : list[int]
        Node sequence from start to target (inclusive), or [] if unreachable.
    """
    if start == target:
        return [start]
    if prev[target] is None:
        return []

    out = [target]
    while out[-1] != start:
        p = prev[out[-1]]
        if p is None:
            return []
        out.append(p)

    out.reverse()
    return out


def draw(
    G,
    pos,
    start,
    target,
    visited,
    frontier,
    dist,
    current=None,
    final_path=None,
    ax=None,
):
    """
    Draw the graph with visual states for Dijkstra.

    Coloring rules (in order of precedence):
      - If final_path is provided: nodes on final_path get a special color
      - start node: green
      - target node: red
      - current settled node: orange
      - visited (settled): blue-ish
      - frontier (discovered but not settled): pink-ish
      - others: light gray

    Labels:
      - Each node shows:
            node_id
            current distance estimate (∞ if unknown/unreachable so far)

    Edges:
      - Each edge is labeled with its integer weight.

    Notes:
      - No plot title (as requested).
      - Node positions are provided externally (pos), so you can control spacing via
        the layout function that produced `pos`.

    Parameters
    ----------
    G : nx.Graph
        The graph to draw.
    pos : dict[int, tuple[float, float]]
        Node positions (layout coordinates).
    start : int
        Start node.
    target : int
        Target node.
    visited : set[int]
        Settled nodes.
    frontier : set[int]
        Discovered but unsettled nodes.
    dist : list[float]
        Distance estimates for labeling.
    current : int or None
        The node settled in the current step (highlighted).
    final_path : list[int] or None
        If provided, highlight these nodes as the final shortest path.
    ax : matplotlib.axes.Axes or None
        Axes to draw on. If None, uses current axes.
    """
    if ax is None:
        ax = plt.gca()
    ax.clear()

    def node_color(v):
        if final_path and v in final_path:
            return "#a78bfa"  # path
        if v == start:
            return "#22c55e"  # start
        if v == target:
            return "#ef4444"  # target
        if v == current:
            return "#f59e0b"  # current
        if v in visited:
            return "#60a5fa"  # visited
        if v in frontier:
            return "#fb7185"  # frontier
        return "#d1d5db"  # unknown

    labels = {}
    for v in G.nodes:
        labels[v] = f"{v}\n∞" if dist[v] == float("inf") else f"{v}\n{dist[v]}"

    nx.draw_networkx(
        G,
        pos,
        ax=ax,
        with_labels=True,
        labels=labels,
        node_color=[node_color(v) for v in G.nodes],
        node_size=750,
        font_size=8,
    )

    edge_labels = {(u, v): G[u][v]["weight"] for u, v in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)

    ax.set_axis_off()


def main():
    """
    Run a step-by-step demo of Dijkstra on a random weighted graph.

    Behavior:
      - Creates a random connected graph and a spread-out layout.
      - Prints start/target in the console.
      - Runs Dijkstra step-by-step:
          - After each settled node, draws the current state.
          - Waits for user input:
              Enter -> next step
              'q'   -> quit early
      - After completion, reconstructs and draws the final shortest path.

    Tips:
      - Increase `n` for larger graphs.
      - Reduce `extra_p` for sparser graphs.
      - If your plot still feels crowded, increase:
          spring_layout k, scale, iterations
        inside random_graph().
    """
    G, pos, start, target = random_graph(n=12, extra_p=0.25, seed=None)

    print(f"Start:  {start}")
    print(f"Target: {target}")
    print("Press Enter for next step, or type 'q' then Enter to quit.\n")

    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 7))  # bigger figure => more space

    dist_last = [float("inf")] * G.number_of_nodes()
    prev_last = [None] * G.number_of_nodes()
    visited_last = set()
    frontier_last = set()

    for step, (cur, visited, frontier, dist, prev) in enumerate(
        dijkstra_steps(G, start, target), 1
    ):
        # Copy to keep a stable snapshot even if something changes later
        dist_last = dist[:]
        prev_last = prev[:]
        visited_last = set(visited)
        frontier_last = set(frontier)

        print(f"Step {step:03d}: settled={cur}, dist={dist_last[cur]}")
        draw(
            G,
            pos,
            start,
            target,
            visited_last,
            frontier_last,
            dist_last,
            current=cur,
            ax=ax,
        )
        plt.pause(0.001)

        cmd = input()
        if cmd.strip().lower() == "q":
            break
        if cur == target:
            print("\nReached target.")
            break

    final = build_path(prev_last, start, target)
    if final:
        print("Shortest distance:", dist_last[target])
        print("Path:", final)
    else:
        print("\nNo path found (target unreachable).")

    draw(
        G,
        pos,
        start,
        target,
        visited_last,
        frontier_last,
        dist_last,
        final_path=final,
        ax=ax,
    )
    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()
