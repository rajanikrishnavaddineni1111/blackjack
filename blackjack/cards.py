"""cards.py - the ONLY place that touches the random card source.

The task provides a local function that "draws a card" (random 2..11).
Players must never import/call this directly; only the Dealer does.
"""
import random


def draw_card() -> int:
    """Simulate drawing one card: a random integer between 2 and 11 (inclusive)."""
    return random.randint(2, 11)
