"""models.py - small data classes and constants shared by every module."""
from dataclasses import dataclass, field

MAX_CARDS = 3      # each player may draw at most three cards
LIMIT = 21         # a winning total must be UNDER this (as per the instructions)


@dataclass
class Hand:
    cards: list[int] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(self.cards)

    @property
    def busted(self) -> bool:
        return self.total >= LIMIT      # 21 or more is "bust": it cannot win

    def __str__(self) -> str:
        if not self.cards:
            return "(no cards)"
        return " + ".join(map(str, self.cards)) + f" = {self.total}"


@dataclass
class DealResult:
    """What the dealer tells a player after handling one request."""
    message: str                # text shown in the terminal
    card: int | None = None     # the card dealt, if any
    stood: bool = False         # True = this player's turn is over
