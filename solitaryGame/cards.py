import pygame

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.face_up = False
        self.rect = pygame.Rect(0, 0, 80, 120)
        
    def draw(self, screen, x, y):
        self.rect.x = x
        self.rect.y = y
        
        if self.face_up:
            pygame.draw.rect(screen, "white", self.rect)
            pygame.draw.rect(screen, "black", self.rect, 2)
            
            font = pygame.font.Font(None, 24)
            text = font.render(f"{self.rank}{self.suit[0]}", True, 
                             "red" if self.suit in ["hearts", "diamonds"] else "black")
            screen.blit(text, (x + 5, y + 5))
        else:
            pygame.draw.rect(screen, "blue", self.rect)
            pygame.draw.rect(screen, "white", self.rect, 2)