"""dealer.py - the ONE AI dealer, built as a LangChain agent (`create_agent`).

Players (the user and the AI players) never draw cards themselves. They send the dealer a
sentence like "deal me the next card". The dealer agent reads it and picks a tool:
    deal_card      -> the player wants a card
    player_stands  -> the player wants to stop
Plain Python then follows the rules (max 3 cards, no cards after bust) and calls draw_card().
The dealer is the ONLY place in the program that calls draw_card().
"""
import re

from langchain.agents import create_agent
from langchain_core.tools import tool

from . import cards
from .models import MAX_CARDS, DealResult, Hand

DEAL, STAND = "deal_card", "player_stands"

SYSTEM_PROMPT = (
    "You are the dealer in a simplified Blackjack game. "
    "If the player wants a card (e.g. 'deal me', 'hit me', 'one more'), call deal_card. "
    "If the player wants to stop (e.g. 'stand', 'I'm good', 'pass'), call player_stands. "
    "Call at most one tool. If the message is unclear, call no tool."
)


class Dealer:
    def __init__(self, llm=None):
        self.llm = llm                  # None => offline mode (keyword matching instead of the agent)
        self.intent = None              # what the agent chose for the current request
        self.agent = self._build_agent() if llm else None

    def _build_agent(self):
        """The agent's tools only RECORD its choice; the dealing itself is done in plain Python."""
        @tool
        def deal_card() -> str:
            """The player wants one more card."""
            self.intent = self.intent or DEAL       # keep only the first choice
            return "ok"

        @tool
        def player_stands() -> str:
            """The player wants to stop taking cards."""
            self.intent = self.intent or STAND
            return "ok"

        return create_agent(self.llm, tools=[deal_card, player_stands], system_prompt=SYSTEM_PROMPT)

    # ---- main entry point: called by the game for every player request ------------------
    def handle_request(self, player_name: str, hand: Hand, message: str) -> DealResult:
        intent = self._understand(message)
        return self._apply_rules(intent, player_name, hand)

    def _understand(self, message: str) -> str | None:
        """Work out what the player wants: DEAL, STAND or None (unclear)."""
        if self.agent:
            self.intent = None
            try:
                self.agent.invoke({"messages": [("user", message)]}, config={"recursion_limit": 6})
                return self.intent
            except Exception:
                pass                                 # LLM/API problem -> fall back to keywords
        return self._keyword_intent(message)

    @staticmethod
    def _keyword_intent(message: str) -> str | None:
        """Offline fallback. 'Stop' words are checked first so 'no more cards' means stand."""
        if re.search(r"\b(stand|stay|stop|pass|enough|no more|good|done|fold)\b", message, re.I):
            return STAND
        if re.search(r"\b(deal|hit|card|draw|another|next|more|yes|give|one)\b", message, re.I):
            return DEAL
        return None

    @staticmethod
    def _apply_rules(intent: str | None, name: str, hand: Hand) -> DealResult:
        """The rules live in code, so the LLM can never hand out extra cards."""
        if intent == STAND:
            return DealResult(f"Dealer: {name} stands.", stood=True)
        if intent != DEAL:
            return DealResult(f"Dealer: sorry {name}, I didn't get that - ask for a card or say stand.")
        if hand.busted:
            return DealResult(f"Dealer: {name}, you are already bust - no more cards.", stood=True)
        if len(hand.cards) >= MAX_CARDS:
            return DealResult(f"Dealer: {name}, you've had your {MAX_CARDS} cards.", stood=True)

        card = cards.draw_card()                     # the single call to the card function
        hand.cards.append(card)
        return DealResult(f"Dealer deals {name} a {card}.  Hand: {hand}", card=card)
