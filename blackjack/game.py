"""game.py - runs the turns and decides the winner."""
from .dealer import Dealer
from .models import LIMIT, MAX_CARDS
from .players import Player


def pick_winners(players: list[Player]) -> list[Player]:
    """Highest total UNDER 21. Players at 21 or over are bust and cannot win. Equal totals = tie."""
    valid = [p for p in players if not p.hand.busted]
    if not valid:
        return []
    best = max(p.hand.total for p in valid)
    return [p for p in valid if p.hand.total == best]


class Game:
    def __init__(self, dealer: Dealer, players: list[Player]):
        self.dealer = dealer
        self.players = players

    def play_turn(self, player: Player) -> None:
        """One player's turn: talk to the dealer until they stand, bust or reach 3 cards."""
        print(f"\n=== {player.name}'s turn ===")
        while len(player.hand.cards) < MAX_CARDS and not player.hand.busted:
            others = {p.name: p.hand.total for p in self.players if p is not player}
            message = player.next_message(others)
            if not message:
                continue
            print(f"{player.name}: \"{message}\"")
            result = self.dealer.handle_request(player.name, player.hand, message)  # only way to get a card
            print(result.message)
            if result.stood:
                break
        if player.hand.busted:
            print(f"*** {player.name} BUSTS with {player.hand.total}! ***")

    def run(self) -> list[Player]:
        for player in self.players:                  # everyone plays one turn, in order
            self.play_turn(player)

        print("\n" + "=" * 40 + "\n FINAL RESULTS\n" + "=" * 40)
        for p in self.players:
            status = "BUST" if p.hand.busted else "ok"
            print(f" {p.name:<8} {str(p.hand):<22} [{status}]")

        winners = pick_winners(self.players)
        if not winners:
            print(f"\n Nobody finished under {LIMIT}. No winner!")
        elif len(winners) == 1:
            print(f"\n WINNER: {winners[0].name} with {winners[0].hand.total}!")
        else:
            print(f"\n TIE between {', '.join(w.name for w in winners)} with {winners[0].hand.total}!")
        return winners
