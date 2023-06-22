from CardUtility import Hand
from treys import Card, Evaluator


class PokerHand(Hand):
    def __init__(self, player_hand: Hand, board_cards: Hand) -> None:
        super().__init__()
        self.evaluator = Evaluator()

        hole = [Card.new(str(card.value()) + str(card.suit())) for card in player_hand.cards]
        board = [Card.new(str(card.value()) + str(card.suit())) for card in board_cards.cards]

        self.score = self.evaluator.evaluate(hole, board)

    def evaluateHand(self) -> float:
        return self.score
