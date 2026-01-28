from gameState import GameState
from gameLogic import GameLogic,Move
from typing import List, Set

class SpiderSolver:
    def __init__(self, gameState: GameState):
        self.initial_state = gameState.copy()
        self.solutionMoves = []
        self.visited_states: Set[str] = set()
        self.states_explored = 0
        self.max_depth = 150 
    
    def solve(self):
        print("Starting spidersolver...")
        self.solutionMoves = []
        self.visited_states.clear()
        self.states_explored = 0
        
        state = self.initial_state.copy()
        
        if self._backtrack(state, [] , 0):
            print(f"Solution found! {len(self.solutionMoves)} moves")
            return self.solutionMoves
        print(f"No solution found. Explored {self.states_explored} states")
        return None
    
    def _backtrack(self, state: GameState, moves_so_far: List[Move], depth: int):
        self.states_explored += 1
        if depth >= self.max_depth:
            return False
        
        if self._is_solved(state):
            self.solutionMoves = moves_so_far[:]
            return True
        
        state_hash = self._hash_state(state)
        if state_hash in self.visited_states:
            return False
        
        self.visited_states.add(state_hash)
        
        possible_moves = GameLogic.get_all_possible_moves(state)
        possible_moves.sort(key=lambda m: self._evaluate_move(state, m), reverse=True)
        
        # Try each tableau move
        for move in possible_moves:
            new_state = state.copy()
            new_state.apply_move(move)
            
            if self._backtrack(new_state, moves_so_far + [move], depth + 1):
                return True
        
        # **NEW: If no valid tableau moves OR all failed, try dealing from stockpile**
        if len(state.stockpile) > 0 and self._can_deal_from_stockpile(state) and self._should_try_stockpile(state):
            # Create special "DEAL" move
            deal_move = Move(
                from_col=-1,  # Special indicator for stockpile
                to_col=-1,
                num_cards=10,  # Dealing 10 cards
                card_rank="DEAL"
            )
            
            new_state = state.copy()
            self._deal_from_stockpile(new_state)
            
            if self._backtrack(new_state, moves_so_far + [deal_move], depth + 1):
                return True
        
        return False
    
    def _can_deal_from_stockpile(self, state: GameState) -> bool:
        """
        Check if we can deal from stockpile
        Rule: All columns must have at least one card
        """
        if len(state.stockpile) == 0:
            return False
        
        # Check all columns have at least 1 card
        for col in state.columns:
            if len(col) == 0:
                return False
        
        return True
    
    def _deal_from_stockpile(self, state: GameState):
        """
        Deal one row from stockpile (up to 10 cards, one per column)
        Modifies state in-place
        """
        cards_to_deal = min(10, len(state.stockpile))
        
        for i in range(cards_to_deal):
            card = state.stockpile.pop()
            card.face_up = True
            state.columns[i].append(card)
        
        # After dealing, check each column for complete sequences
        for col_idx in range(cards_to_deal):
            removed = GameLogic.check_and_remove_complete_sequence(
                state.columns[col_idx]
            )
            if removed:
                state.sequences_removed += 1
                # Flip newly exposed card
                if state.columns[col_idx]:
                    if not state.columns[col_idx][-1].face_up:
                        state.columns[col_idx][-1].face_up = True
    
    def _hash_state(self, state: GameState) -> str:
        hash_parts = []
        for col in state.columns:
            col_str = "|".join(
                f"{card.rank}{card.suit}{'U' if card.face_up else 'D'}"
                for card in col
            )
            hash_parts.append(col_str)
        
        hash_parts.append(f"STOCK:{len(state.stockpile)}")
        
        return "::".join(hash_parts)
    
    def _is_solved(self, state: GameState) -> bool:
        """Game is solved when all columns are empty"""
        return all(len(col) == 0 for col in state.columns)
    
    def _evaluate_move(self, state: GameState, move: Move) -> float:
        """
        Heuristic scoring - guide search toward better moves
        """
        score = 0.0
        
        from_col = state.columns[move.from_col]
        to_col = state.columns[move.to_col]
        
        # 1. Expose face-down cards (highest priority!)
        if len(from_col) > move.num_cards:
            card_below = from_col[-(move.num_cards + 1)]
            if not card_below.face_up:
                score += 50
        
        # 2. Prefer moving longer sequences
        score += move.num_cards * 3
        
        # 3. Build toward complete sequences
        if len(to_col) + move.num_cards >= 13:
            score += 20
        
        # 4. Prefer suited builds
        cards_to_move = from_col[-move.num_cards:]
        if to_col and cards_to_move:
            if cards_to_move[0].suit == to_col[-1].suit:
                score += 10
        
        # 5. Penalize moves to empty columns unless King
        if len(to_col) == 0:
            if move.card_rank == 'K':
                score += 5
            else:
                score -= 30
        
        # 6. Avoid short fragmented columns
        if len(to_col) > 0 and len(to_col) < 3:
            score -= 5
        
        # 7. Penalize potential undo moves
        if len(to_col) > 0 and len(from_col) > move.num_cards:
            if len(state.columns[move.to_col]) < len(state.columns[move.from_col]):
                score -= 10
        
        return score
    def _should_try_stockpile(self, state: GameState) -> bool:
        """
        Only deal from stockpile if we're REALLY stuck
        Don't deal prematurely - it makes the game harder!
        """
        possible_moves = GameLogic.get_all_possible_moves(state)
        
        # If we have ANY moves available, don't deal yet
        if len(possible_moves) > 0:
            return False  # Let backtracking try all moves first
        
        # Only deal when truly stuck (no moves possible)
        return True