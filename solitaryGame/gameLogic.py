from dataclasses import dataclass
from typing import List
from constants import RANK_VALUE
from cards import Card
from gameState import GameState

@dataclass
class Move:
    from_col: int
    to_col: int    
    num_cards: int
    card_rank: str
    
    def is_deal(self) -> bool:
        return self.from_col == -1 and self.card_rank == "DEAL"
    
    def __repr__(self):
        if self.is_deal():
            return f"Move(DEAL from stockpile)"
        return f"Move({self.num_cards}x {self.card_rank} from col{self.from_col} to col{self.to_col})"
    
class GameLogic:
    @staticmethod
    def is_valid_move(card_to_drop, target_card, strict_suit=False):
        card_val = RANK_VALUE[card_to_drop.rank]
        target_val = RANK_VALUE[target_card.rank]
        rank_match = (target_val - card_val == 1)
        
        if not rank_match:
            return False
            
        return True

    @staticmethod
    def is_valid_seq(seq: List[Card]) -> bool:
        if len(seq)==0:
            return False
        if len(seq)==1:
            return seq[0].face_up
        if not all(card.face_up for card in seq):
            return False
        for i in range(len(seq) - 1):
            curr_card = seq[i]
            next_card = seq[i + 1]
            if RANK_VALUE[curr_card.rank] - RANK_VALUE[next_card.rank] != 1:
                return False
        
        return True
        

    @staticmethod
    def check_complete_seq(column: List[Card]) -> bool:
        """
        Check if column contains a complete K→A sequence and remove it
        
        A complete sequence is:
        - 13 cards (K, Q, J, 10, 9, 8, 7, 6, 5, 4, 3, 2, A)
        - All same suit (for Spider Solitaire completion)
        - All face-up
        - In correct descending order
        
        Args:
            column: List of cards in a column
        
        Returns:
            True if sequence was found and removed, False otherwise
        """
        if len(column) < 13:
            return False
        
        # Check from different starting positions in case multiple sequences
        for start_idx in range(len(column) - 12):
            seq = column[start_idx:start_idx + 13]
            
            # Must be exactly 13 cards
            if len(seq) != 13:
                continue
            
            # Must start with King and end with Ace
            if seq[0].rank != 'K' or seq[-1].rank != 'A':
                continue
            
            # All must be face-up
            if not all(card.face_up for card in seq):
                continue
            
            # Must be same suit (Spider Solitaire rule for completion)
            first_suit = seq[0].suit
            if not all(card.suit == first_suit for card in seq):
                continue
            
            # Must match exact rank order
            expected_ranks = ['K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2', 'A']
            if not all(seq[i].rank == expected_ranks[i] for i in range(13)):
                continue
            
            # Found complete sequence! Remove it
            for _ in range(13):
                column.pop(start_idx)
            
            # Flip newly exposed card if needed
            if column and start_idx <= len(column):
                if start_idx > 0 and not column[start_idx - 1].face_up:
                    column[start_idx - 1].face_up = True
                elif start_idx == 0 and column and not column[-1].face_up:
                    column[-1].face_up = True
            
            return True
        
        return False

    @staticmethod
    def get_all_possible_moves(state: GameState) -> List[Move]:
        moves = []
        for from_col in range(10):
            col = state.columns[from_col]
            if not col:
                continue
        
            max_seq_len = GameLogic._find_movable_sequence(col)
            
            if max_seq_len == 0:
                continue  # No movable cards
            
            # Try moving sequences of different lengths
            for num_cards in range(1, max_seq_len + 1):
                cards_to_move = col[-num_cards:]
                top_card = cards_to_move[0]
                
                # Try each destination column
                for to_col in range(10):
                    if from_col == to_col:
                        continue  # Can't move to same column
                    
                    dest_col = state.columns[to_col]
                    
                    # Case 1: Empty column - only Kings allowed
                    if not dest_col:
                        if top_card.rank == 'K':
                            moves.append(Move(
                                from_col=from_col,
                                to_col=to_col,
                                num_cards=num_cards,
                                card_rank=top_card.rank
                            ))
                    
                    # Case 2: Non-empty column - check if valid move
                    else:
                        if GameLogic.is_valid_move(top_card, dest_col[-1]):
                            moves.append(Move(
                                from_col=from_col,
                                to_col=to_col,
                                num_cards=num_cards,
                                card_rank=top_card.rank
                            ))
        
        return moves
    
    @staticmethod
    def _find_movable_sequence(column: List[Card]) -> int:
        if not column:
            return 0
        
        if not column[-1].face_up:
            return 0
        
        length = 1
        
        # Walk backwards up the column
        for i in range(len(column) - 1, 0, -1):
            curr_card = column[i]
            prev_card = column[i - 1]
            
            # Must be face-up
            if not prev_card.face_up:
                break
            if RANK_VALUE[prev_card.rank] - RANK_VALUE[curr_card.rank] != 1:
                break
            
            length += 1
        return length
    
    @staticmethod
    def check_and_remove_complete_sequence(column: List['Card']) -> bool:
        """
        Alias for check_complete_seq for backwards compatibility
        """
        return GameLogic.check_complete_seq(column)



