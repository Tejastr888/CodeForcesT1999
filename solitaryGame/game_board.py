import pygame
class GameBoard:
    def __init__(self,screen_width,screen_height):
        self.screen_width=screen_width
        self.screen_height=screen_height
        self.card_width=80
        self.card_height=120    
        self.padding=20
        self.column_spacing=self.card_width + self.padding

        self.stockpile_pos = (self.screen_width - self.card_width - self.padding, self.screen_height-self.card_height-self.padding)

        self.tableau_positions = []
        tableau_start_y = self.padding * 2
        for i in range(10):
            self.tableau_positions.append((self.padding + i * self.column_spacing, tableau_start_y))

        self.stockpile = []

    def draw(self, screen):
        print("Drawing Game Board")
        print("Tableau Positions:", self.tableau_positions)
        for pos in self.tableau_positions:
            pygame.draw.rect(screen, "darkgreen", (pos[0], pos[1], self.card_width, self.card_height), 2)

        pygame.draw.rect(screen, "darkgreen", (self.stockpile_pos[0], self.stockpile_pos[1], self.card_width, self.card_height), 2)

