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

def is_valid_seq(seq: List[Card]):
    if len(seq) == 1:
        return True
    
    for i in range(len(seq)-1):
        curr_card=seq[i]
        next_card =seq[i+1]
        if RANK_VALUES[curr_card.rank] - RANK_VALUES[next_card.rank] != 1:
            return False
        # if curr_card.suit != next_card.suit:
        #     return False
    return True
        

class GameBoard:

    def __init__(self,screen_width,screen_height,deck):
        self.screen_width=screen_width
        self.screen_height=screen_height
        self.card_width=80
        self.card_height=120    
        self.padding=24
        self.column_spacing=self.card_width + self.padding

        self.dragged_cards = []    
        self.drag_offset = (0, 0)     
        self.original_col_index = None 


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
            if self.dragged_cards:
                
                mouse_x, mouse_y = event.pos
                self.dragged_cards[0].rect.x = mouse_x - self.drag_offset[0]
                self.dragged_cards[0].rect.y = mouse_y - self.drag_offset[1]
            
            # Update positions of remaining cards (stacked below)
                for i in range(1, len(self.dragged_cards)):
                    self.dragged_cards[i].rect.x = self.dragged_cards[0].rect.x
                    self.dragged_cards[i].rect.y = self.dragged_cards[0].rect.y + (i * self.padding)
    
    def handle_drag_start(self,pos):
        for col_idx,col_cards in enumerate(self.gameCards):
            if not col_cards: #means if empty 
                continue
            
            for card_idx in range(len(col_cards)-1,-1,-1):
                card = col_cards[card_idx]
                if not card.face_up:
                    continue

                if card.rect.collidepoint(pos):
                    seq=col_cards[card_idx:]

                    if is_valid_seq(seq):
                        self.dragged_cards = seq
                        self.original_col_index=col_idx
                        self.drag_offset = (pos[0]-card.rect.x,pos[1]-card.rect.y)
                    
                        for _ in range(len(seq)):
                            col_cards.pop()
                        return




    def handle_drag_end(self, pos):
        if not self.dragged_cards:
            return
    
        dropped_successfully = False
        first_card = self.dragged_cards[0]  # The top card of the sequence

        for i, tableau_pos in enumerate(self.tableau_positions):
            dest_col_cards = self.gameCards[i]
            empty_slot_rect = pygame.Rect(tableau_pos[0], tableau_pos[1], self.card_width, self.card_height)

            if not dest_col_cards:
            # Empty column - only Kings can go here
                if empty_slot_rect.collidepoint(pos):
                    if first_card.rank == 'K':
                        dest_col_cards.extend(self.dragged_cards)
                        dropped_successfully = True
                        break
            else:
            # Non-empty column - check if valid move
                top_card = dest_col_cards[-1]
                if top_card.rect.collidepoint(pos):
                    if is_valid_spider_move(first_card, top_card):
                        dest_col_cards.extend(self.dragged_cards)
                        dropped_successfully = True
                        break
    
        if dropped_successfully:
        # Flip the new top card of source column
            source_col = self.gameCards[self.original_col_index]
            if source_col and not source_col[-1].face_up:
                source_col[-1].face_up = True
        else:
        # Snap back to original column
            self.gameCards[self.original_col_index].extend(self.dragged_cards)
    
        self.dragged_cards = []
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
        
        if self.dragged_cards:
            for card in self.dragged_cards:
                screen.blit(card.front_face, card.rect)



