"""
Stats - Value object for team statistics
"""


class Stats:
    def __init__(self):
        self.GF = 0  # Goals For
        self.GA = 0  # Goals Against
        self.minutes_played = 0
        self.matches_played = 0
        self.clean_sheets = 0
        self.yellow_count = 0
        self.red_count = 0
        self.xG = 0.0  # Optional

    def per_90(self, stat_name):
        """Get any stat per 90 minutes"""
        if self.minutes_played == 0:
            return 0.0
        value = getattr(self, stat_name, 0)
        return (value / self.minutes_played) * 90
