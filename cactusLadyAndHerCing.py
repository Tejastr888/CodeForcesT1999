import sys

# Increase recursion depth for deep trees
sys.setrecursionlimit(300000)

def solve():
    # Fast I/O
    input = sys.stdin.read
    data = input().split()
    iterator = iter(data)
    
    try:
        num_test_cases = int(next(iterator))
    except StopIteration:
        return

    out_buffer = []

    for _ in range(num_test_cases):
        try:
            n = int(next(iterator))
            m = int(next(iterator))
        except StopIteration:
            break

        adj = [[] for _ in range(n + 1)]
        edges = []
        for _ in range(m):
            u = int(next(iterator))
            v = int(next(iterator))
            adj[u].append(v)
            adj[v].append(u)
            edges.append((u, v))

        # 1. Quick Degree Check
        # Max degree in a ladder is 3.
        possible = True
        for i in range(1, n + 1):
            if len(adj[i]) > 3:
                possible = False
                break
        
        if not possible:
            out_buffer.append("No")
            continue

        # 2. Cycle Detection & Bipartite Check
        # We need to identify which nodes are in cycles and assign IDs to cycles.
        parent = [0] * (n + 1)
        depth = [0] * (n + 1)
        visited = [False] * (n + 1)
        node_cycle_id = [-1] * (n + 1)
        in_cycle = [False] * (n + 1)
        
        # We also need to map edges to cycles to distinguish multiple cycles touching a node?
        # Actually, in a cactus with max degree 3, a node can belong to at most one cycle 
        # (because cycle=2 edges, leaving 1 edge for tree connection).
        # Exception: A node could connect two cycles? Degree would be 4. Impossible.
        # So each node is in at most 1 cycle.
        
        cycles = [] # List of sets of nodes
        
        # DFS stack for cycle finding
        # Using iterative DFS to avoid recursion limits on pre-processing if possible,
        # but recursive is easier to write for logic. Given N=200k, sys.setrecursionlimit is needed.
        
        def find_cycles_dfs(u, p, d):
            nonlocal possible
            visited[u] = True
            depth[u] = d
            parent[u] = p
            
            for v in adj[u]:
                if v == p:
                    continue
                if visited[v]:
                    if depth[v] < depth[u]: # Back-edge found
                        cycle_len = depth[u] - depth[v] + 1
                        if cycle_len % 2 != 0:
                            possible = False # Odd cycle
                            return False
                        
                        # Mark cycle nodes
                        curr = u
                        new_cycle_id = len(cycles)
                        current_cycle_nodes = set()
                        
                        # We need to register the cycle
                        while curr != v:
                            if node_cycle_id[curr] != -1:
                                # Overlapping cycles (shouldn't happen with deg <=3 checks but logic must be safe)
                                possible = False
                                return False
                            node_cycle_id[curr] = new_cycle_id
                            in_cycle[curr] = True
                            current_cycle_nodes.add(curr)
                            curr = parent[curr]
                        
                        if node_cycle_id[v] != -1:
                             # This handles the case where v is already marked. 
                             # Since v is the "root" of this cycle discovery, it's okay if v connects to others,
                             # but with max deg 3, v cannot be INSIDE another cycle fully.
                             # Actually, v acts as the intersection. 
                             # If v is already in a cycle, that's fine as long as edges are distinct.
                             pass
                             
                        # Note: We don't mark 'v' with cycle_id here typically to allow traversal flow,
                        # but for "in_cycle" check it's useful.
                        # However, 'v' is the anchor. Let's mark it specially or handle carefully.
                        # Let's just mark it.
                        # Wait, if v is in cycle A, and we find cycle B closing at v.
                        # v has 2 edges in A, 2 edges in B -> Degree 4. Impossible.
                        # So v cannot be in a previous cycle.
                        node_cycle_id[v] = new_cycle_id
                        in_cycle[v] = True
                        current_cycle_nodes.add(v)
                        cycles.append(current_cycle_nodes)
                        
                else:
                    if not find_cycles_dfs(v, u, d + 1):
                        return False
            return True

        # Find root (leaf preference)
        root = 1
        for i in range(1, n + 1):
            if len(adj[i]) == 1:
                root = i
                break

        if not find_cycles_dfs(root, 0, 0):
            out_buffer.append("No")
            continue

        if not possible:
            out_buffer.append("No")
            continue

        # 3. Embedding DFS
        ans = {} # Map node -> (x, y)
        
        # Helper to check if a subtree is a simple line
        # Returns (is_line, list_of_nodes)
        memo_line = {}
        
        def get_line(u, p):
            if (u, p) in memo_line: return memo_line[(u, p)]
            
            if in_cycle[u]: 
                return (False, [])
            
            children = [v for v in adj[u] if v != p]
            
            if len(children) > 1:
                return (False, [])
            
            if len(children) == 0:
                res = (True, [u])
                memo_line[(u, p)] = res
                return res
            
            is_l, nodes = get_line(children[0], u)
            if not is_l:
                return (False, [])
            
            res = (True, [u] + nodes)
            memo_line[(u, p)] = res
            return res

        # Main solver function
        # Returns True/False
        visited_solve = [False] * (n + 1)
        
        def dfs_solve(u, p, r, c):
            ans[u] = (r, c)
            visited_solve[u] = True
            
            children = [v for v in adj[u] if v != p]
            
            # Check if u initiates a cycle traversal
            # u is in a cycle, and one of its children is in the SAME cycle.
            cycle_child = -1
            cid = node_cycle_id[u]
            
            if cid != -1:
                for v in children:
                    if node_cycle_id[v] == cid:
                        cycle_child = v
                        break
            
            if cycle_child != -1:
                # --- PROCESS CYCLE ---
                # u is the entry point.
                # Identify the two cycle neighbors of u: v1 (cycle_child) and v2 (the other one)
                # One of these must be 'visited_solve' (the one we came from? No, we came from p).
                # Wait, u has 2 cycle neighbors.
                # If u is the root of the tree, both are unvisited.
                # If u is not root, one might be p?
                # No, if p is in the cycle, then u was visited as part of the cycle block processing
                # and we wouldn't be in this generic function call.
                # Therefore, if we are here, u is the "entry" to the cycle.
                
                # Find the two neighbors in the cycle
                cycle_neighbors = []
                for v in adj[u]:
                    if node_cycle_id[v] == cid:
                        cycle_neighbors.append(v)
                
                if len(cycle_neighbors) != 2:
                    return False # Should not happen in a valid cycle
                
                v1, v2 = cycle_neighbors
                
                # Logic: One neighbor must be the "vertical partner" at (1-r, c).
                # This partner is immediately blocked by the cycle loop, so it cannot have other children.
                # It must have degree 2 (only cycle edges).
                
                v_vert, v_horiz = -1, -1
                
                if len(adj[v1]) == 2:
                    v_vert, v_horiz = v1, v2
                elif len(adj[v2]) == 2:
                    v_vert, v_horiz = v2, v1
                else:
                    # Both have external branches -> Impossible to map to ladder start
                    return False
                
                # Trace the cycle path starting from v_horiz, ending at v_vert
                # Path: u -> v_horiz -> ... -> v_vert -> u
                # We need the ordered list of nodes from v_horiz to v_vert (excluding u)
                
                path = []
                curr = v_horiz
                prev = u
                
                while curr != v_vert:
                    path.append(curr)
                    visited_solve[curr] = True
                    # Find next
                    found = False
                    for nxt in adj[curr]:
                        if nxt != prev and node_cycle_id[nxt] == cid:
                            prev = curr
                            curr = nxt
                            found = True
                            break
                    if not found: return False # Broken cycle structure?
                
                path.append(v_vert)
                visited_solve[v_vert] = True
                
                # Cycle Geometry
                # Nodes: u + path. Total = 1 + len(path). Must be even.
                total_len = 1 + len(path)
                width = total_len // 2
                
                # Map Vertical Partner
                ans[v_vert] = (1-r, c)
                
                # Map Top Row: u -> ... (width nodes)
                # Map Bottom Row: v_vert <- ... (width nodes)
                # The path list corresponds to the loop around.
                # u is at (r, c).
                # Top row (excluding u): path[0] to path[width-2]
                # Turnaround Top: path[width-2]
                # Turnaround Bottom: path[width-1]
                # Bottom row (excluding v_vert): path[width] to path[end]
                
                # Indices in 'path' (0-based):
                # Top row nodes: path[0] ... path[width-2]
                # Bottom row nodes: path[width-1] ... path[len-1]
                
                # Example: Size 6. Width 3.
                # u(0,0). v_vert(1,0).
                # Top: u->p[0]->p[1]. (Coords: 0,1 and 0,2)
                # Bot: v_vert<-p[3]<-p[2]. (Coords: 1,1 and 1,2)
                # path = [p0, p1, p2, p3]
                # width=3. width-2 = 1. p[0]..p[1]. Correct.
                # top_turn = p[1]. bot_turn = p[2].
                
                # Assign coords
                # Top Row
                for i in range(width - 1):
                    node = path[i]
                    ans[node] = (r, c + 1 + i)
                    # Constraint: Internal nodes cannot branch.
                    # Internal nodes are p[0]...p[width-3].
                    # p[width-2] is the turnaround, can branch.
                    if i < width - 2:
                        if len(adj[node]) > 2: return False
                
                # Bottom Row
                # The list continues from width-1 to end.
                # These fill columns from width-1 down to 1.
                # p[width-1] is at col c + width - 1 (Bottom Turn)
                for i in range(width - 1):
                    idx = (width - 1) + i
                    node = path[idx]
                    col_loc = c + (width - 1) - i
                    ans[node] = (1-r, col_loc)
                    
                    # Internal check
                    # Bottom Turn is at i=0 (idx width-1). Can branch.
                    # Others are internal.
                    if i > 0:
                        if len(adj[node]) > 2: return False

                # Recurse on Turnaround nodes
                top_turn = path[width - 2]
                bot_turn = path[width - 1]
                
                # Next column for recursion
                next_c = c + width
                
                # Collect valid children for recursion
                # Children of top_turn (excluding cycle neighbors)
                top_kids = [v for v in adj[top_turn] if not visited_solve[v]]
                bot_kids = [v for v in adj[bot_turn] if not visited_solve[v]]
                
                # We essentially have two potential branches starting at next_c.
                # This looks like the "Fork" logic.
                
                if len(top_kids) > 1 or len(bot_kids) > 1:
                    return False
                
                kid1 = top_kids[0] if top_kids else None
                kid2 = bot_kids[0] if bot_kids else None
                
                if kid1 and kid2:
                    # Parallel lines required
                    is_l1, nodes1 = get_line(kid1, top_turn)
                    is_l2, nodes2 = get_line(kid2, bot_turn)
                    if not (is_l1 and is_l2): return False
                    
                    # Fill lines
                    # kid1 goes to (r, next_c)
                    curr_c = next_c
                    for x in nodes1:
                        ans[x] = (r, curr_c)
                        curr_c += 1
                    
                    # kid2 goes to (1-r, next_c)
                    curr_c = next_c
                    for x in nodes2:
                        ans[x] = (1-r, curr_c)
                        curr_c += 1
                        
                elif kid1:
                    if not dfs_solve(kid1, top_turn, r, next_c): return False
                elif kid2:
                    if not dfs_solve(kid2, bot_turn, 1-r, next_c): return False
                
                return True

            else:
                # --- PROCESS TREE/FORK ---
                if len(children) == 0:
                    return True
                
                elif len(children) == 1:
                    return dfs_solve(children[0], u, r, c + 1)
                
                elif len(children) == 2:
                    # Fork: Must split into two simple lines
                    k1, k2 = children[0], children[1]
                    
                    l1_ok, nodes1 = get_line(k1, u)
                    l2_ok, nodes2 = get_line(k2, u)
                    
                    if not (l1_ok and l2_ok):
                        return False
                    
                    # Map k1 line to current row
                    curr_c = c + 1
                    for x in nodes1:
                        ans[x] = (r, curr_c)
                        curr_c += 1
                        
                    # Map k2 line to other row
                    # Note: k2 connects to u via vertical edge at c?
                    # u is at (r, c). Ladder vertical edge is (r,c)-(1-r,c).
                    # So k2 MUST be placed at (1-r, c).
                    # Is (1-r, c) free? 
                    # If u came from left (r, c-1), yes.
                    # If u came from vertical? No, p would be there.
                    # If p exists, we must check where p is.
                    # Input graph is a tree of cycles.
                    # DFS traversal: p is always visited.
                    # ans[p] check?
                    
                    # Coordinate check:
                    if (1-r, c) in ans.values():
                        # If the spot is taken (by parent), we cannot put k2 there.
                        # If p is at (1-r, c), then u was connected vertically.
                        # If u was connected vertically, u used the vertical rung.
                        # We cannot use it again for k2.
                        return False 
                    
                    # Place k2 at (1-r, c)
                    ans[k2] = (1-r, c)
                    # Remaining k2 nodes go to c+1...
                    # nodes2[0] is k2.
                    curr_c = c + 1
                    for x in nodes2[1:]:
                        ans[x] = (1-r, curr_c)
                        curr_c += 1
                        
                    return True
                
                else:
                    return False

        # Run Solver
        if dfs_solve(root, 0, 0, 0):
            out_buffer.append("Yes")
            results = [""] * (n + 1)
            for k, v in ans.items():
                results[k] = f"{v[0]} {v[1]}"
            out_buffer.extend(results[1:])
        else:
            out_buffer.append("No")

    print('\n'.join(out_buffer))

if __name__ == '__main__':
    solve()