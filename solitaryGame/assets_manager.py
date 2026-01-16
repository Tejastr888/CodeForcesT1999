import pygame
from constants import BASE

ASSETS_DIR = BASE / "assets"

CARD_FACES_DIR = ASSETS_DIR/"card_pngs"/"card_faces"
CARD_BACKS_DIR = ASSETS_DIR/"card_pngs"/"card_backs"

def load_image(path, size=None):
    image = pygame.image.load(path).convert_alpha()
    if size:
        image = pygame.transform.smoothscale(image, size)
    return image

def load_card_faces():
    faces = {}
    for p in CARD_FACES_DIR.glob("*.png"):
        faces[p.stem] = load_image(p)
    return faces

def load_card_backs():
    return [load_image(p) for p in CARD_BACKS_DIR.glob("*.png")]
