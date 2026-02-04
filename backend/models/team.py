"""
Team - Persistent object representing a country across the tournament
"""

from .stats import Stats


class Team:
    def __init__(self, name, elo, group):
        self.name = name
        self.elo = elo
        self.group = group
        self.stats = Stats()

        # Meta
        self.eliminated = False
        self.seed = None
        self.user_prediction = None

        # Group stage tracking
        self.points = 0
        self.goal_diff = 0

    def add_goal(self, n=1):
        """Increment goals for"""
        self.stats.GF += n

    def concede_goal(self, n=1):
        """Increment goals against"""
        self.stats.GA += n

    def add_minutes(self, minutes):
        """Add minutes played"""
        self.stats.minutes_played += minutes

    def reset_match_state(self):
        """Reset transient per-match fields (cards, temp mods)"""
        pass
