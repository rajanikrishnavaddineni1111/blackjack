"""main.py - start the game:  python -m blackjack.main   (options: --offline, --auto, --seed N)"""
import argparse
import os
import random
import warnings

from .dealer import Dealer
from .game import Game
from .llm import get_llm
from .players import AIPlayer, HumanPlayer

# Harmless noise from langchain-anthropic + pydantic; results are correct
warnings.filterwarnings("ignore", message="Pydantic serializer warnings")


def main() -> None:
    parser = argparse.ArgumentParser(description="Blackjack with AI agents")
    parser.add_argument("--offline", action="store_true", help="no LLM, simple rule-based agents")
    parser.add_argument("--auto", action="store_true", help="the 'You' player is a bot too (demo)")
    parser.add_argument("--seed", type=int, help="fixed random seed for repeatable cards")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
    if args.offline:
        os.environ["BLACKJACK_OFFLINE"] = "1"

    llm = get_llm()                                   # None => offline mode
    print("Blackjack | mode:", "LLM agents (online)" if llm else "OFFLINE (no API key, simple rules)")
    print("Rules: up to 3 cards each. Highest total under 21 wins (21 or more is a bust).")
    print("Talk to the dealer in plain English, e.g. 'deal me the next card' or 'I'll stand'.")

    dealer = Dealer(llm)                              # the one AI dealer agent
    ai_players = [                                    # three AI player agents
        AIPlayer("Alice", "cautious; hates busting", 14, llm),
        AIPlayer("Bob", "reckless gambler; loves risk", 18, llm),
        AIPlayer("Carol", "calm and calculating; plays the odds", 16, llm),
    ]
    you = AIPlayer("You", "balanced", 16, llm) if args.auto else HumanPlayer("You")

    Game(dealer, [you, *ai_players]).run()


if __name__ == "__main__":
    main()
