# nav_algorithm.py
import math
import heapq

GRID_SIZE = 6 

def node_to_xy(node):
    """Convert node number to (x, y) coordinates."""
    x = node % GRID_SIZE
    y = node // GRID_SIZE
    return (x, y)

def xy_to_node(x, y):
    """Convert (x, y) coordinates back to node number."""
    return y * GRID_SIZE + x

def get_neighbors(node, barriers):
    """Return valid 8-directional neighbors avoiding barriers."""
    x, y = node_to_xy(node)
    neighbors = []
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                neighbor = xy_to_node(nx, ny)
                if neighbor not in barriers:
                    neighbors.append(neighbor)
    return sorted(neighbors)

def chebyshev_distance(node_a, node_b):
    """Chebyshev distance: max(|dx|, |dy|) - Good for 8-way movement."""
    x1, y1 = node_to_xy(node_a)
    x2, y2 = node_to_xy(node_b)
    return max(abs(x2 - x1), abs(y2 - y1))

def euclidean_distance(node_a, node_b):
    """Exact edge cost calculation."""
    x1, y1 = node_to_xy(node_a)
    x2, y2 = node_to_xy(node_b)
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def a_star_search(start, goal, barriers):
    """
    A* Algorithm simulating ROS 2 Global Path Planning.
    Returns: path, visited_nodes
    """
    # pq entries: (f_cost, node, current_g_cost)
    pq = [(chebyshev_distance(start, goal), start, 0.0)]
    
    # Track the exact cost from start to a given node
    g_costs = {start: 0.0}
    parent = {start: None}
    visited_log = []
    
    found = False

    while pq:
        f_cost, current, current_g = heapq.heappop(pq)
        
        # Skip if we found a strictly better path to this node already
        if current in g_costs and current_g > g_costs[current]:
            continue
            
        visited_log.append(current)

        if current == goal:
            found = True
            break

        for neighbor in get_neighbors(current, barriers):
            # Calculate exact cost to neighbor
            tentative_g_cost = current_g + euclidean_distance(current, neighbor)
            
            if neighbor not in g_costs or tentative_g_cost < g_costs[neighbor]:
                g_costs[neighbor] = tentative_g_cost
                f_cost = tentative_g_cost + chebyshev_distance(neighbor, goal)
                parent[neighbor] = current
                heapq.heappush(pq, (f_cost, neighbor, tentative_g_cost))

    final_path = []
    if found:
        node = goal
        while node is not None:
            final_path.append(node)
            node = parent[node]
        final_path.reverse()

    return final_path, visited_log