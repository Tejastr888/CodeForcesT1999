import pygame
from deck import Deck
from cards import Card
from typing import List
from constants import RANK_VALUE as RANK_VALUES
from gameState import GameState
from spiderSolver import SpiderSolver
from gameLogic import Move


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
        self.column_spacing = self.card_width + self.padding

        self.dragged_cards = []    
        self.drag_offset = (0, 0)     
        self.original_col_index = None 

        self.dealing_cards = []
        self.deal_animation_speed = 15


        self.stockpile_pos = (self.screen_width - self.card_width - self.padding, self.screen_height-self.card_height-self.padding)

        self.tableau_positions = []
        tableau_start_y = self.padding * 2
        for i in range(10):
            self.tableau_positions.append((self.padding + i * self.column_spacing, tableau_start_y))

        self.stockpile = []
        self.gameCards: List[List[Card]] = [[] for _ in range(10)]
        self.stockpile = []
        self.setup_game(deck)

        self.solve_button_rect = pygame.Rect(
            self.screen_width - 200,
            20,
            150,
            40
        )

        self.is_solving = False
        self.solution_moves = []
        self.current_move_index = 0
        self.move_animation_timer = 0
        self.move_animation_delay = 30 
        self.solving_cards = []  
        self.solver_status = "Ready" 
    
    def start_auto_solve(self):
        if self.is_solving:
            print("Already solving!")
            return
        
        print("Starting auto-solve...")
        self.solver_status = "Solving..."

        game_state = GameState(
            columns=[col[:] for col in self.gameCards],
            stockpile=self.stockpile[:]
        )

        solver = SpiderSolver(game_state)
        self.solution_moves = solver.solve()
        
        if self.solution_moves:
            print(f"✓ Solution found! {len(self.solution_moves)} moves")
            self.solver_status = f"Solving: {len(self.solution_moves)} moves"
            self.is_solving = True
            self.current_move_index = 0
            self.move_animation_timer = 0
        else:
            print("✗ No solution found")
            self.solver_status = "No solution found"
    
    def update_auto_solve(self):
        if self.solving_cards:
            self.update_solve_animation()
            return
        
        # Check if we're done
        if self.current_move_index >= len(self.solution_moves):
            self.is_solving = False
            self.solver_status = "Solved!"
            print("✓ Solution complete!")
            return
        
        # Wait before next move
        self.move_animation_timer += 1
        
        if self.move_animation_timer >= self.move_animation_delay:
            # Execute next move
            move = self.solution_moves[self.current_move_index]
            print(f"Executing move {self.current_move_index + 1}/{len(self.solution_moves)}: {move}")
            self._animate_solve_move(move)
            self.current_move_index += 1
            self.move_animation_timer = 0
            self.solver_status = f"Move {self.current_move_index}/{len(self.solution_moves)}"
    
    def _animate_solve_move(self, move: Move):
        if move.is_deal():
            self.deal_from_stockpile()
        else:
            # Regular move: animate cards from one column to another
            cards_to_move = self.gameCards[move.from_col][-move.num_cards:]
            
            # Remove from source column
            for _ in range(move.num_cards):
                self.gameCards[move.from_col].pop()
            
            # Flip exposed card in source
            if self.gameCards[move.from_col]:
                if not self.gameCards[move.from_col][-1].face_up:
                    self.gameCards[move.from_col][-1].face_up = True
            
            # Setup animation data
            source_x, source_y = self.tableau_positions[move.from_col]
            target_x, target_y = self.tableau_positions[move.to_col]
            dest_col_len = len(self.gameCards[move.to_col])
            
            for i, card in enumerate(cards_to_move):
                self.solving_cards.append({
                    'card': card,
                    'target_col_index': move.to_col,
                    'current_x': source_x,
                    'current_y': source_y + i * self.padding,
                    'target_x': target_x,
                    'target_y': target_y + (dest_col_len + i) * self.padding
                })
    
    def update_solve_animation(self):
        if not self.solving_cards:
            return
        
        cards_to_remove = []
        
        for solve_data in self.solving_cards:
            card = solve_data['card']
            
            # Calculate direction to target
            dx = solve_data['target_x'] - solve_data['current_x']
            dy = solve_data['target_y'] - solve_data['current_y']
            
            # Calculate distance
            distance = (dx**2 + dy**2) ** 0.5
            
            if distance < self.deal_animation_speed:
                # Reached destination
                self.gameCards[solve_data['target_col_index']].append(card)
                cards_to_remove.append(solve_data)
            else:
                # Move towards target
                ratio = self.deal_animation_speed / distance
                solve_data['current_x'] += dx * ratio
                solve_data['current_y'] += dy * ratio
                
                # Update card rect for drawing
                card.rect.x = int(solve_data['current_x'])
                card.rect.y = int(solve_data['current_y'])
        
        # Remove finished animations
        for solve_data in cards_to_remove:
            self.solving_cards.remove(solve_data)
        
        # After all cards reach destination, check for complete sequences
        if not self.solving_cards and cards_to_remove:
            # Check the destination column for complete sequences
            dest_col = cards_to_remove[0]['target_col_index']
            self.check_and_remove_complete_seq(dest_col)
    
    def deal_from_stockpile(self):
        if len(self.stockpile) == 0:
            print("STOCKPILE IS EMPTY!")
            return
        
        for col in self.gameCards:
            if len(col) == 0:
                print("Cannot deal - all columns must have at least one card!")
                return
        
        cards_to_deal = min(10, len(self.stockpile))

        for i in range(cards_to_deal):
            card:Card = self.stockpile.pop()
            card.face_up = True
            target_col = self.gameCards[i]
            start_x,start_y = self.tableau_positions[i]
            target_y = start_y + (len(target_col) * self.padding)
            self.dealing_cards.append({
                'card': card,
                'target_col_index': i,
                'current_x': self.stockpile_pos[0],
                'current_y': self.stockpile_pos[1],
                'target_x': start_x,
                'target_y': target_y
            })

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
                if self.solve_button_rect.collidepoint(event.pos):
                    self.start_auto_solve()
                    return
                stockpile_rect = pygame.Rect(
                    self.stockpile_pos[0],
                    self.stockpile_pos[1],
                    self.card_width,
                    self.card_height
                )
                if stockpile_rect.collidepoint(event.pos):
                    if not self.is_solving:
                        self.deal_from_stockpile()
                else:
                    if not self.is_solving:
                        self.handle_drag_start(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if not self.is_solving:
                    self.handle_drag_end(event.pos)
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragged_cards and not self.is_solving:
                
                mouse_x, mouse_y = event.pos
                self.dragged_cards[0].rect.x = mouse_x - self.drag_offset[0]
                self.dragged_cards[0].rect.y = mouse_y - self.drag_offset[1]
            
            # Update positions of remaining cards (stacked below)
                for i in range(1, len(self.dragged_cards)):
                    self.dragged_cards[i].rect.x = self.dragged_cards[0].rect.x
                    self.dragged_cards[i].rect.y = self.dragged_cards[0].rect.y + (i * self.padding)
    
    def deal_from_stockpile(self):
        if len(self.stockpile) == 0:
            print("STOCKPILE IS EMPTY!")
            return
        
        for col in self.gameCards:
            if len(col) == 0:
                print("Cannot deal - all columns must have at least one card!")
                return
        
        cards_to_deal = min(10, len(self.stockpile))

        for i in range(cards_to_deal):
            card:Card = self.stockpile.pop()
            card.face_up = True
            target_col = self.gameCards[i]
            start_x,start_y = self.tableau_positions[i]
            target_y = start_y + (len(target_col) * self.padding)
            self.dealing_cards.append({
                'card': card,
                'target_col_index': i,
                'current_x': self.stockpile_pos[0],
                'current_y': self.stockpile_pos[1],
                'target_x': start_x,
                'target_y': target_y
            })

    def update_animations(self):
        """Update positions of cards being dealt"""
        if not self.dealing_cards:
            return
        
        cards_to_remove = []
        
        for deal_data in self.dealing_cards:
            card = deal_data['card']
            
            # Calculate direction to target
            dx = deal_data['target_x'] - deal_data['current_x']
            dy = deal_data['target_y'] - deal_data['current_y']
            
            # Calculate distance
            distance = (dx**2 + dy**2) ** 0.5
            
            if distance < self.deal_animation_speed:
                # Reached destination
                self.gameCards[deal_data['target_col_index']].append(card)
                cards_to_remove.append(deal_data)
            else:
                # Move towards target
                ratio = self.deal_animation_speed / distance
                deal_data['current_x'] += dx * ratio
                deal_data['current_y'] += dy * ratio
                
                # Update card rect for drawing
                card.rect.x = int(deal_data['current_x'])
                card.rect.y = int(deal_data['current_y'])
        
        # Remove finished animations
        for deal_data in cards_to_remove:
            self.dealing_cards.remove(deal_data)
    
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

    def check_and_remove_complete_seq(self,col_idx):
        col = self.gameCards[col_idx]

        if len(col)<13:
            return False
        
        for start_idx in range(len(col)-12):
            seq = col[start_idx:start_idx + 13]
            if len(seq) == 13 and seq[0].rank == 'K' and seq[-1].rank == 'A':
                # first_suit = seq[0].suit
                # if all(card.suit == first_suit for card in seq):
                if all(card.face_up for card in seq):
                    expected_ranks = ['K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2', 'A']
                    if all(seq[i].rank == expected_ranks[i] for i in range(13)):
                        for _ in range(13):
                            col.pop(start_idx)
                        if col and not col[-1].face_up:
                            col[-1].face_up = True
                        
                        return True
                    
        return False
                
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
                        self.check_and_remove_complete_seq(i)
                        dropped_successfully = True
                        break
            else:
            # Non-empty column - check if valid move
                top_card = dest_col_cards[-1]
                if top_card.rect.collidepoint(pos):
                    if is_valid_spider_move(first_card, top_card):
                        dest_col_cards.extend(self.dragged_cards)
                        self.check_and_remove_complete_seq(i)
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
        for deal_data in self.dealing_cards:
            card = deal_data['card']
            screen.blit(card.front_face, card.rect)
        
        for solve_data in self.solving_cards:
            card = solve_data['card']
            screen.blit(card.front_face, card.rect)
        
        # Draw dragged cards
        if self.dragged_cards:
            for card in self.dragged_cards:
                screen.blit(card.front_face, card.rect)
        
        if self.dragged_cards:
            for card in self.dragged_cards:
                screen.blit(card.front_face, card.rect)
        
        self.draw_solve_button(screen)

    def draw_solve_button(self, screen):
        """Draw the solve button"""
        # Button background
        button_color = (0, 150, 0) if not self.is_solving else (150, 150, 150)
        pygame.draw.rect(screen, button_color, self.solve_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.solve_button_rect, 2)
        
        # Button text
        font = pygame.font.Font(None, 32)
        text = "Solving..." if self.is_solving else "Solve"
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.solve_button_rect.center)
        screen.blit(text_surface, text_rect)
        
        # Status text below button
        if self.solver_status:
            status_font = pygame.font.Font(None, 24)
            status_surface = status_font.render(self.solver_status, True, (255, 255, 255))
            status_rect = status_surface.get_rect(
                centerx=self.solve_button_rect.centerx,
                top=self.solve_button_rect.bottom + 5
            )
            screen.blit(status_surface, status_rect)

