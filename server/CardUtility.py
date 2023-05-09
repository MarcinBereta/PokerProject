from enum import Enum
import random
from functools import reduce

class CardValue(Enum):
    ACE =   14, 'A'
    DEUCE = 2 , '2'
    THREE = 3 , '3'
    FOUR =  4 , '4'
    FIVE =  5 , '5'
    SIX =   6,  '6'
    SEVEN = 7,  '7'
    EIGHT = 8,  '8'
    NINE =  9,  '9'
    TEN =   10, 'T'
    JACK =  11, 'J'
    QUEEN = 12, 'Q'
    KING =  13, 'K'

    def __int__(self):
        return self.value[0]
    
    def __str__(self):
        return self.value[1]
    

class CardSuit(Enum):
    CLUB = 1, 'c'
    HEART = 2, 'h'
    DIAMOND = 3 , 'd'
    SPADE = 4 , 's'

    def __int__(self):
        return self.value[0]
    
    def __str__(self):
        return self.value[1]
    
class Card(tuple):
    def __new__(self, value: CardValue, suit: CardSuit):
        return tuple.__new__(self, (value, suit))
    
    def value(self) -> CardValue:
        return self[0]

    def suit(self) -> CardSuit:
        return self[1]
    
    def get_path(self) -> str:
        return  (self.value().name + "_of_" + self.suit().name + "s.png").lower()
     
    def __str__(self) -> str:
        return f"{self.value().name} of {self.suit().name}"
    
    def __hash__(self) -> int:
        return hash(self)


class Hand():
    def __init__(self) -> None:
        self.cards = []

    def add_card(self, card: Card) -> None:
        self.cards.append(card);

    def __str__(self) -> str:
        return reduce(lambda x, y: str(x) + " " + str(y) + "\n", self.cards, "")
    
    def get_cards_path_name(self):
        paths = []
        for i in self.cards:
            paths.append(i.get_path())
        return paths
    

class Deck(object):
    def __init__(self) -> None:
        self._cards = [ Card(value, suit) for value in CardValue for suit in CardSuit]
        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self._cards)

    def add_card(self, card: Card) -> None:
        if card in self._cards:
            raise LookupError("This card is already in deck!")
        self._cards.append(card);
    
    def remove_card(self, card: Card) -> None:
        if card not in self._cards:
            raise LookupError("Cannot find this card in deck!")
        self._cards.remove(card);

    def pop_top_card(self, i = -1) -> Card:
        if not self._cards:
            raise KeyError("Cannot pop from empty array!")
        return self._cards.pop(i)

    def sort(self) -> None:
        self.sort(self._cards)

    def give_cards(self, hand: Hand, numberOfCards) -> None:
        
        if numberOfCards > len(self._cards):
            raise LookupError("Number of cards to draw is greater than number of cards in deck!")

        for _ in range(numberOfCards):
            hand.add_card(self.pop_top_card())


