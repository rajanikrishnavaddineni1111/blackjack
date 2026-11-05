"""players.py - the human player and the AI player agents.

Players never touch cards.py. Each turn they only produce a sentence for the dealer.

AI players use LangChain: a prompt template piped into an LLM that must answer in a fixed
format (action + a short line to say). That "prompt | llm" pipe is a LangChain chain.
"""
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from .models import LIMIT, MAX_CARDS, Hand


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand = Hand()

    def next_message(self, others: dict[str, int]) -> str:
        raise NotImplementedError


class HumanPlayer(Player):
    """The user types free text such as 'deal me the next card' or 'I'll stand'."""

    def next_message(self, others):
        print(f"\n>>> Your hand: {self.hand}   (cards used: {len(self.hand.cards)}/{MAX_CARDS})")
        print("    Other players' totals: " + ", ".join(f"{n}={t}" for n, t in others.items()))
        return input("    What do you say to the dealer? ").strip()


class Decision(BaseModel):
    """The fixed answer format we force the LLM to use."""
    action: str = Field(description="Exactly 'draw' or 'stand'")
    say: str = Field(description="One short, in-character sentence")


PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are {name}, a Blackjack player. Personality: {persona}\n"
     "Goal: finish with the highest total that stays UNDER {limit}. {limit} or more = bust = you lose.\n"
     "Cards are random numbers from 2 to 11. You can hold at most {max_cards} cards."),
    ("human",
     "Your cards: {cards} (total {total}). Other players' totals: {others}.\n"
     "Do you 'draw' another card or 'stand'? Answer with the action and one short line to say."),
])


class AIPlayer(Player):
    """An AI agent with a personality that decides whether to draw another card."""

    def __init__(self, name: str, persona: str, risk_limit: int, llm=None):
        super().__init__(name)
        self.persona = persona
        self.risk_limit = risk_limit       # offline mode: keep drawing while total is below this
        # LangChain chain: fill the prompt, send to the LLM, get a Decision back
        self.chain = (PROMPT | llm.with_structured_output(Decision)) if llm else None

    def next_message(self, others):
        action, speech = self.decide(others)
        print(f"{self.name} thinks: \"{speech}\"")
        # The dealer always gets a clear request, whatever the AI "says" for flavour
        return "I'll stand." if action == "stand" else "Dealer, deal me another card."

    def decide(self, others) -> tuple[str, str]:
        """Return ('draw' or 'stand', a short line)."""
        if self.chain:
            try:
                answer = self.chain.invoke({
                    "name": self.name, "persona": self.persona, "limit": LIMIT, "max_cards": MAX_CARDS,
                    "cards": self.hand.cards, "total": self.hand.total, "others": others,
                })
                action = answer.action.strip().lower()
                if action in ("draw", "stand"):
                    return action, answer.say.strip()
            except Exception:
                pass                                   # LLM problem -> use the simple rule below
        if self.hand.total < self.risk_limit:
            return "draw", "Deal me a card, dealer."
        return "stand", "I'm good."
