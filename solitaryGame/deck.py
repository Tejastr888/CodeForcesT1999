import random
from cards import Card
from assets_manager import load_card_faces,load_card_backs



class Deck:
    def __init__(self):
        self.faces = load_card_faces()
        self.back_images= load_card_backs()
        suits = ["hearts", "diamonds", "clubs", "spades"]
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        self.cards = [Card(suit, rank,self.faces,self.back_images[0]) for suit in suits for rank in ranks]
        
    def shuffle(self):
        random.shuffle(self.cards)
        
    def deal(self):
        return self.cards.pop() if self.cards else None