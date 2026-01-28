
from typing import List
from cards import Card

class GameState:
    def __init__(self, columns, stockpile):
        self.columns = columns
        self.stockpile = stockpile

    def copy(self):
        return GameState(
            columns=[col[:] for col in self.columns],
            stockpile=self.stockpile[:]
        )
    
    def apply_move(self, move):
        """Mutate state by applying a move"""
        cards = self.columns[move.from_col][-move.num_cards:]
        self.columns[move.from_col] = self.columns[move.from_col][:-move.num_cards]
        self.columns[move.to_col].extend(cards)
        
        # Flip card if needed
        if self.columns[move.from_col] and not self.columns[move.from_col][-1].face_up:
            self.columns[move.from_col][-1].face_up = True

