"""
BracketNode - Represents knockout bracket structure
"""

from .match import MatchResult


class BracketNode:
    def __init__(self, match=None):
        self.match = match  # Match that produces winner for this node
        self.left = None  # Child node (earlier round)
        self.right = None  # Child node (earlier round)
        self.winner = None  # Team reference set after match is played

    def compute_winner(self):
        """Returns winner once match is played"""
        if self.match and self.match.result:
            if self.match.result == MatchResult.A_WIN:
                self.winner = self.match.team_a
            elif self.match.result == MatchResult.B_WIN:
                self.winner = self.match.team_b
            elif self.match.penalties_result:
                self.winner = self.match.penalties_result[2]
        return self.winner
