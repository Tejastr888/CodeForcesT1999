import pygame
from assets_manager import load_image
RANK_NAME = {"A": "ace", "J": "jack", "Q": "queen", "K": "king"}
class Card:
    def __init__(self, suit, rank,faces,back_img):
        self.suit = suit
        self.rank = rank
        self.face_up = False
        self.rect = pygame.Rect(0, 0, 80, 120)
        self.front_face=faces[self.image_key()]
        self.back_img = back_img

    def image_key(self):
        return f"{RANK_NAME.get(self.rank, self.rank)}_of_{self.suit}"

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        image_to_draw = self.front_face if self.face_up else self.back_img
        image = pygame.transform.smoothscale(image_to_draw, (80, 120))
        screen.blit(image, self.rect)
        