"""
Group - Manages group stage
"""

from .match import Match


class Group:
    def __init__(self, name, teams):
        self.name = name  # "Group A", etc.
        self.teams = teams  # List of 4 Team objects
        self.matches = []
        self.standings = None

    def schedule_matches(self):
        """Round-robin: all teams play each other"""
        for i in range(len(self.teams)):
            for j in range(i + 1, len(self.teams)):
                match = Match(self.teams[i], self.teams[j], is_group=True)
                self.matches.append(match)

    def compute_standings(self):
        """Sort teams by points, then goal diff"""
        sorted_teams = sorted(
            self.teams,
            key=lambda t: (t.points, t.goal_diff),
            reverse=True
        )
        self.standings = sorted_teams
        return sorted_teams[:2]  # Return top 2 qualifiers
