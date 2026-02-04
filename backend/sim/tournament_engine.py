"""
TournamentEngine - Orchestrates entire tournament simulation
"""

import json
from models import Team, Group, Match, MatchResult



class TournamentEngine:
    def __init__(self, delay=0.1):
        self.teams = []
        self.groups = []
        self.bracket_root = None
        self.sim_params = {
            'delay': delay,
            'base_goal_rate': 6,  # From original formula
            'use_elos': True
        }
        self.user_predictions = {}

    def load_data(self, source='data/teams_2018.json'):
        """Load tournament data from JSON file or hardcoded fallback"""
        if source.endswith('.json'):
            # Load from JSON file
            with open(source, 'r') as f:
                data = json.load(f)

            team_data = [(t['name'], t['elo'], t['group']) for t in data['teams']]
        else:
            # Fallback: hardcoded data
            team_data = [
                ("Russia", 18, "A"), ("Saudi Arabia", 10, "A"),
                ("Uruguay", 54, "A"), ("Egypt", 42, "A"),
                ("Portugal", 57, "B"), ("Spain", 58, "B"),
                ("Morroco", 20, "B"), ("Iran", 8, "B"),
                ("France", 83, "C"), ("Peru", 34, "C"),
                ("Denmark", 42, "C"), ("Australia", 15, "C"),
                ("Argentina", 57, "D"), ("Iceland", 40, "D"),
                ("Croatia", 45, "D"), ("Nigeria", 38, "D"),
                ("Brazil", 87, "E"), ("Switzerland", 40, "E"),
                ("Costa Rica", 38, "E"), ("Serbia", 33, "E"),
                ("Germany", 85, "F"), ("Mexico", 40, "F"),
                ("Sweden", 41, "F"), ("South Korea", 38, "F"),
                ("Belgium", 70, "G"), ("Panama", 35, "G"),
                ("Tunisia", 24, "G"), ("England", 65, "G"),
                ("Poland", 50, "H"), ("Colombia", 60, "H"),
                ("Senegal", 45, "H"), ("Japan", 38, "H")
            ]

        for name, elo, group_name in team_data:
            team = Team(name, elo, group_name)
            self.teams.append(team)

        # Create groups
        for group_letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            group_teams = [t for t in self.teams if t.group == group_letter]
            group = Group(f"Group {group_letter}", group_teams)
            self.groups.append(group)

    def simulate_group_stage(self):
        """Simulate all group matches and return qualifiers"""
        qualifiers = []
        for group in self.groups:
            group.schedule_matches()
            for match in group.matches:
                match.generate_timeline(self.sim_params)
                match.play(delay=self.sim_params['delay'])
                match.update_team_stats()

            top_2 = group.compute_standings()
            qualifiers.extend(top_2)

            # Print group results (preserve original output)
            print("Games finished!")
            points_list = [t.points for t in group.teams]
            gd_list = [t.goal_diff for t in group.teams]
            print(points_list)
            print(gd_list)
            print(f"winner {top_2[0].name}")
            print(f"Runner-up {top_2[1].name}")

        return qualifiers

    def simulate_knockout_round(self, teams, round_name):
        """Simulate a knockout round (R16, QF, SF, F)"""
        print(f" knockout {round_name} stage")
        winners = []

        for i in range(0, len(teams), 2):
            match = Match(teams[i], teams[i+1], is_group=False)
            match.generate_timeline(self.sim_params)
            match.play(delay=self.sim_params['delay'])

            # Handle draw in knockout
            if match.result == MatchResult.DRAW:
                winner = match.play_penalties(delay=self.sim_params['delay'])
            else:
                winner = match.team_a if match.result == MatchResult.A_WIN else match.team_b

            match.update_team_stats()
            winner.eliminated = False
            winners.append(winner)

            # Mark loser as eliminated
            loser = match.team_b if winner == match.team_a else match.team_a
            loser.eliminated = True

        return winners

    def simulate_tournament(self):
        """Orchestrates entire flow: group stage → knockout rounds → champion"""
        # Group stage
        qualifiers = self.simulate_group_stage()

        # Round of 16 (preserve original bracket structure)
        # 0-A, 1-B, 2-C, 3-D, 4-E, 5-F, 6-G, 7-H
        # Winner positions: [0,1]=A, [2,3]=B, [4,5]=C, etc.
        r16_matchups = [
            (qualifiers[0], qualifiers[3]),   # A1 vs B2
            (qualifiers[4], qualifiers[7]),   # C1 vs D2
            (qualifiers[8], qualifiers[11]),  # E1 vs F2
            (qualifiers[12], qualifiers[15]), # G1 vs H2
            (qualifiers[2], qualifiers[1]),   # B1 vs A2
            (qualifiers[6], qualifiers[5]),   # D1 vs C2
            (qualifiers[10], qualifiers[9]),  # F1 vs E2
            (qualifiers[14], qualifiers[13])  # H1 vs G2
        ]

        r16_teams = []
        for t1, t2 in r16_matchups:
            r16_teams.extend([t1, t2])

        quarter_finalists = self.simulate_knockout_round(r16_teams, "16")
        semi_finalists = self.simulate_knockout_round(quarter_finalists, "8")
        finalists = self.simulate_knockout_round(semi_finalists, "4")

        print("final")
        champion = self.simulate_knockout_round(finalists, "final")

        return champion[0]
