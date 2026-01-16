import pygame
from deck import Deck
from cards import Card
from typing import List


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
        if self.dragged_card:
            # TODO: Add logic here to check if drop is valid (e.g., correct rank/suit)
            
            # For now, let's just snap it back to where it came from (testing)
            self.gameCards[self.original_col_index].append(self.dragged_card)
            
            # Reset drag state
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




