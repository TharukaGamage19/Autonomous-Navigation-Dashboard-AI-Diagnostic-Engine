import heapq

def get_heuristic(a, b):
    """Calculate Manhattan distance between two points."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def calculate_path(grid, start, end):
    """
    A* Pathfinding Algorithm.
    grid: 2D list where 0 is open space, 1 is an obstacle.
    start: Tuple (row, col)
    end: Tuple (row, col)
    Returns a list of tuples representing the path, or None if blocked.
    """
    rows = len(grid)
    cols = len(grid[0])
    
    # Priority queue to explore the lowest cost nodes first
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    # Dictionary to reconstruct the path later
    came_from = {}
    
    # Cost from start to the current node
    g_score = {start: 0}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        # If we reached the end, reconstruct the path backwards
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
            
        # Explore neighbors: Right, Down, Left, Up
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            # Ensure neighbor is within grid boundaries
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols:
                # Ensure neighbor is not an obstacle (1)
                if grid[neighbor[0]][neighbor[1]] == 1:
                    continue 
                    
                # The distance between adjacent nodes is exactly 1
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    # f_score = cost from start + estimated cost to end
                    f_score = tentative_g_score + get_heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score, neighbor))
                    
    return None # No valid path found
