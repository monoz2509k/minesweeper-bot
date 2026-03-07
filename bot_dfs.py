### bot_dfs.py
class DFSAgent:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def get_neighbors(self, r, c):
        # get neightbours (8 cells around)
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    neighbors.append((nr, nc))
        return neighbors

    def get_frontier_cells(self, kb):
        # get all unrevealed cells adjacent to revealed numbers
        frontier = set()
        for (r, c), value in kb.items():
            if isinstance(value, int) and value > 0:
                for nr, nc in self.get_neighbors(r, c):
                    if kb.get((nr, nc)) == 'U':
                        frontier.add((nr, nc))
        return list(frontier)

    def is_valid_assignment(self, assignment, kb, component_cells):
        # check if the assignment is right
        relevant_numbers = set()
        for cell in component_cells:
            for nr, nc in self.get_neighbors(*cell):
                val = kb.get((nr, nc))
                if isinstance(val, int):
                    relevant_numbers.add((nr, nc))

        for r, c in relevant_numbers:
            target_mines = kb[(r, c)]
            neighbors = self.get_neighbors(r, c)
            confirmed_mines = sum(1 for n in neighbors if kb.get(n) == 'F' or assignment.get(n) == 'MINE')
            potential_space = sum(1 for n in neighbors if kb.get(n) == 'U' and n not in assignment)

            if confirmed_mines > target_mines: return False
            if confirmed_mines + potential_space < target_mines: return False
        return True

    def split_into_components(self, frontier_cells, kb):
        # split frontiers into connected components 
        components = []
        visited = set()
        for start_cell in frontier_cells:
            if start_cell in visited: continue
            comp = []
            queue = [start_cell]
            visited.add(start_cell)
            while queue:
                cell = queue.pop(0)
                comp.append(cell)
                adj_nums = [n for n in self.get_neighbors(*cell) if isinstance(kb.get(n), int)]
                for num_cell in adj_nums:
                    for neighbor in self.get_neighbors(*num_cell):
                        if neighbor in frontier_cells and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
            components.append(comp)
        components.sort(key=len)
        return components

    def solve_component(self, component_cells, kb):
        # traverse dfs in component to find all valid assignments
        def count_constraints(cell):
            return sum(1 for n in self.get_neighbors(*cell) if isinstance(kb.get(n), int))
        component_cells.sort(key=count_constraints, reverse=True)

        stack = [{}]
        valid_models = []
        max_iters = 5000 # limit iterations 
        iters = 0
        is_complete = True # revealed all possibilities

        while stack:
            iters += 1
            if iters > max_iters or len(valid_models) > 100:
                is_complete = False
                break
            
            curr_assignment = stack.pop()
            if len(curr_assignment) == len(component_cells):
                valid_models.append(curr_assignment)
                continue

            next_cell = component_cells[len(curr_assignment)]
            for val in ['SAFE', 'MINE']:
                new_assign = curr_assignment.copy()
                new_assign[next_cell] = val
                if self.is_valid_assignment(new_assign, kb, component_cells):
                    stack.append(new_assign)
        
        return valid_models, is_complete

    def evaluate(self, models, component_cells):
        # calculate probabilities for each cell based on available valid models
        if not models: return {}
        probs = {}
        total = len(models)
        for cell in component_cells:
            mine_count = sum(1 for m in models if m[cell] == 'MINE')
            p_mine = mine_count / total
            probs[cell] = {'SAFE': 1 - p_mine, 'MINE': p_mine}
        return probs

    def get_best_move(self, kb):
        frontier_cells = self.get_frontier_cells(kb)
        if not frontier_cells: return None, None
        
        components = self.split_into_components(frontier_cells, kb)
        all_stats = {} 
        # cell -> {'p': {'SAFE': x, 'MINE': y}, 'complete': bool} 
        # x : prob of being SAFE
        # y : prob of being MINE
        # complete: whether DFS fully traversed 

        # collect probabilities from each component 
        for comp in components:
            models, is_complete = self.solve_component(comp, kb)
            if not models: continue
            
            comp_probs = self.evaluate(models, comp)
            
            # if prob is 100% and dfs fully traversed, take action immediately
            if is_complete:
                for cell, p in comp_probs.items():
                    if p['MINE'] == 1.0:
                        return "MINE", cell

                for cell, p in comp_probs.items():
                    if p['SAFE'] == 1.0:
                        return "SAFE", cell

                # Không có cell chắc chắn → lưu để so sánh sau
                for cell, p in comp_probs.items():
                    all_stats[cell] = {'p': p, 'complete': True}
            # else store them
            else:
                for cell, p in comp_probs.items():
                    all_stats[cell] = {'p': p, 'complete': is_complete}

        # else pick the one with highest SAFE probs 
        if all_stats:
            best_guess = max(all_stats.keys(), key=lambda c: all_stats[c]['p']['SAFE'])
            prob_safe = all_stats[best_guess]['p']['SAFE']
            print(f"Bot guesses cell {best_guess} with SAFE confidence: {prob_safe*100:.1f}%")
            return "SAFE", best_guess

        return None, None