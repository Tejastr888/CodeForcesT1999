import pygame
from deck import Deck
from cards import Card
from typing import List
from constants import RANK_VALUE as RANK_VALUES

def is_valid_spider_move(card_to_drop, target_card, strict_suit=False):
    # 1. Rank Check: Must always be one less (e.g., 5 on 6)
    card_val = RANK_VALUES[card_to_drop.rank]
    target_val = RANK_VALUES[target_card.rank]
    rank_match = (target_val - card_val == 1)
    
    if not rank_match:
        return False
        
    # 2. Suit Check: If strict_suit is True, suits must match
    if strict_suit:
        return card_to_drop.suit == target_card.suit
        
    return True # If not strict, any suit on any suit is fine


class GameBoard:
    def __init__(self,screen_width,screen_height,deck):
        self.screen_width=screen_width
        self.screen_height=screen_height
        self.card_width=80
        self.card_height=120    
        self.padding=24
        self.column_spacing=self.card_width + self.padding

        self.dragged_card = None       # The card object currently being dragged
        self.drag_offset = (0, 0)      # Distance between mouse click and card corner
        self.original_col_index = None # Where the card came from (to snap back)


        self.stockpile_pos = (self.screen_width - self.card_width - self.padding, self.screen_height-self.card_height-self.padding)

        self.tableau_positions = []
        tableau_start_y = self.padding * 2
        for i in range(10):
            self.tableau_positions.append((self.padding + i * self.column_spacing, tableau_start_y))

        self.stockpile = []
        self.gameCards: List[List[Card]] = [[] for _ in range(10)]
        self.stockpile = []
        self.setup_game(deck)
    
    def setup_game(self,deck:Deck):
        deck.shuffle()
        for i in range(4):
            for col in range(10):
                card = deck.deal()
                if card:
                    if i==3:
                        card.face_up = True
                    self.gameCards[col].append(card)
        
        while len(deck.cards)>0:
            self.stockpile.append(deck.deal())
    
    def handle_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.handle_drag_start(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.handle_drag_end(event.pos)
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragged_card:
                # Move the card's rect based on mouse position + offset
                mouse_x, mouse_y = event.pos
                self.dragged_card.rect.x = mouse_x - self.drag_offset[0]
                self.dragged_card.rect.y = mouse_y - self.drag_offset[1]
    
    def handle_drag_start(self,pos):
        for col_idx, col_cards in enumerate(self.gameCards):
            if not col_cards:
                continue
            top_card = col_cards[-1]
            if top_card.rect.collidepoint(pos):
                self.dragged_card = top_card
                self.original_col_index = col_idx
                self.drag_offset = (pos[0] - top_card.rect.x, pos[1] - top_card.rect.y)

                col_cards.pop() 
                break
    def handle_drag_end(self, pos):
        if not self.dragged_card:
            return
        dropped_successfully = False

        for i, tableau_pos in enumerate(self.tableau_positions):
            dest_col_cards = self.gameCards[i]
            empty_slot_rect = pygame.Rect(tableau_pos[0],tableau_pos[1],self.card_width,self.card_height)

            if not dest_col_cards:
                if empty_slot_rect.collidepoint(pos):
                    if self.dragged_card.rank == 'K':
                        dest_col_cards.append(self.dragged_card)
                        dropped_successfully = True
                        break
            else:
                top_card = dest_col_cards[-1]
                if top_card.rect.collidepoint(pos):
                    if is_valid_spider_move(self.dragged_card, top_card):
                        dest_col_cards.append(self.dragged_card)
                        dropped_successfully = True
                        break
            
        
        if dropped_successfully:
            source_col = self.gameCards[self.original_col_index]
            if source_col:
                source_col[-1].face_up = True
        else:
            # Invalid move (or dropped in empty space). Snap back to original column.
            self.gameCards[self.original_col_index].append(self.dragged_card)
        self.dragged_card = None
        self.original_col_index = None
            
            

    def draw(self, screen):
        for pos in self.tableau_positions:
            pygame.draw.rect(screen, "darkgreen", (pos[0], pos[1], self.card_width, self.card_height), 2)
        pygame.draw.rect(screen, "darkgreen", (self.stockpile_pos[0], self.stockpile_pos[1], self.card_width, self.card_height), 2)

        for i,col_cards in enumerate(self.gameCards):
            start_x,start_y= self.tableau_positions[i]
            for j,card in enumerate(col_cards):
                card_y = start_y + (j*self.padding)
                card.draw(screen,start_x,card_y)
        
        for i, card in enumerate(self.stockpile):
            card.draw(screen, self.stockpile_pos[0], self.stockpile_pos[1])
        
        if self.dragged_card:
            # We don't recalculate X/Y here; we use the rect updated by MOUSEMOTION
            screen.blit(self.dragged_card.front_face, self.dragged_card.rect)




