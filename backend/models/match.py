"""
Match simulation classes - EventType, MatchEvent, MatchState, MatchResult, Match
"""

from enum import Enum
import random
import time


# ============================================================================
# EventType Enum - Types of match events
# ============================================================================
class EventType(Enum):
    GOAL = "GOAL"
    ATTEMPT = "ATTEMPT"
    YELLOW = "YELLOW"
    RED = "RED"
    SUB = "SUB"
    PENALTY_TAKEN = "PENALTY_TAKEN"
    EXTRA_TIME_START = "EXTRA_TIME_START"
    EXTRA_TIME_END = "EXTRA_TIME_END"


# ============================================================================
# MatchEvent Class - Represents timeline events in a match
# ============================================================================
class MatchEvent:
    def __init__(self, minute, event_type, team, player=None, meta=None):
        self.minute = minute
        self.type = event_type
        self.team = team  # Reference to Team object
        self.player = player  # Optional string
        self.meta = meta or {}  # e.g., {'shot_xg': 0.3, 'assist': 'Player X'}

    def apply_to(self, match_state):
        """Update transient match state"""
        if self.type == EventType.GOAL:
            if match_state.team_a == self.team:
                match_state.score_a += 1
            else:
                match_state.score_b += 1
        elif self.type == EventType.YELLOW:
            # Update yellow cards
            if match_state.team_a == self.team:
                match_state.yellow_a += 1
            else:
                match_state.yellow_b += 1
        elif self.type == EventType.RED:
            # Update red cards and modifiers
            if match_state.team_a == self.team:
                match_state.red_cards_a += 1
                match_state.attack_mod_a -= 0.1
            else:
                match_state.red_cards_b += 1
                match_state.attack_mod_b -= 0.1

    def undo(self):
        """Optional for testing or rewind UI"""
        pass


# ============================================================================
# MatchState Class - Transient value object used during match simulation
# ============================================================================
class MatchState:
    def __init__(self, team_a, team_b):
        self.team_a = team_a
        self.team_b = team_b
        self.current_minute = 0
        self.score_a = 0
        self.score_b = 0

        # Transient modifiers (influenced by events)
        self.attack_mod_a = 0
        self.def_mod_a = 0
        self.attack_mod_b = 0
        self.def_mod_b = 0

        # Cards
        self.red_cards_a = 0
        self.red_cards_b = 0
        self.yellow_a = 0
        self.yellow_b = 0

        # Optional
        self.momentum = 0.5  # 0-1 scale

    def update_on_event(self, event):
        """Mutate the state based on event"""
        event.apply_to(self)


# ============================================================================
# MatchResult Enum - Match outcomes
# ============================================================================
class MatchResult(Enum):
    A_WIN = "A_WIN"
    B_WIN = "B_WIN"
    DRAW = "DRAW"


# ============================================================================
# Match Class - Manages match simulation and events
# ============================================================================
class Match:
    def __init__(self, team_a, team_b, is_group=True):
        self.team_a = team_a
        self.team_b = team_b
        self.is_group = is_group
        self.scheduled_minute_range = 90

        self.events = []
        self.final_score = None  # (int, int)
        self.result = None  # MatchResult enum
        self.penalties_result = None  # Optional (score_a, score_b, winner)

        self.match_state = None  # Created during play

    def generate_timeline(self, sim_params=None):
        #Generate events based on team ELOs - preserves original scoring formula
        score_a = int(6 * random.random() * self.team_a.elo / 100)
        score_b = int(6 * random.random() * self.team_b.elo / 100)

        # Apply ELO swing logic from original (upset avoidance)
        if score_a == score_b and self.team_b.elo - self.team_a.elo > 20:
            if random.random() > 0.01:
                score_a = int(6 * random.random() * self.team_a.elo / 100)
        if score_a > score_b and self.team_b.elo - self.team_a.elo > 20:
            if random.random() > 0.01:
                score_a, score_b = score_b, score_a

        # Create goal events at random minutes
        self.events = []
        for i in range(score_a):
            minute = int(random.random() * 90)
            self.events.append(MatchEvent(minute, EventType.GOAL, self.team_a))
        for i in range(score_b):
            minute = int(random.random() * 90)
            self.events.append(MatchEvent(minute, EventType.GOAL, self.team_b))

        # Add cards
        yellow_count = random.randint(0, 4)
        for _ in range(yellow_count):
            minute = random.randint(1, 90)
            team = random.choice([self.team_a, self.team_b])
            self.events.append(MatchEvent(minute, EventType.YELLOW, team))

        # Red card logic (FIXED: indentation bug from line 202)
        red_chance = random.random()
        if red_chance < 0.08:  # ~8% of matches have a red
            minute = random.randint(20, 85)
            team = random.choice([self.team_a, self.team_b])
            self.events.append(MatchEvent(minute, EventType.RED, team))

        self.events.sort(key=lambda e: e.minute)
        return self.events

    def play(self, replay_mode=True, delay=0.1):
        """Replay events minute by minute or finalize immediately"""
        # Create transient match state
        self.match_state = MatchState(self.team_a, self.team_b)

        # Replay events
        if replay_mode:
            for event in self.events:
                event.apply_to(self.match_state)
                time.sleep(delay)
        else:
            # Immediate finalization
            for event in self.events:
                event.apply_to(self.match_state)

        self.final_score = (self.match_state.score_a, self.match_state.score_b)

        # Determine result
        if self.match_state.score_a > self.match_state.score_b:
            self.result = MatchResult.A_WIN
        elif self.match_state.score_b > self.match_state.score_a:
            self.result = MatchResult.B_WIN
        else:
            self.result = MatchResult.DRAW

        # Print match result (preserve original format)
        print(f"{self.team_a.name} - {self.team_b.name} {self.final_score[0]} - {self.final_score[1]}")

    def play_penalties(self, delay=0.1):
        """Preserve original penalty logic"""
        print(" play penalties")
        i = 0
        pen_a = 0
        pen_b = 0
        pen_diff = 0

        while pen_diff < 1 or i < 5:
            pen_a = int(0.92 + random.random() * self.team_a.elo / 100) + pen_a
            pen_b = int(0.92 + random.random() * self.team_b.elo / 100) + pen_b
            pen_diff = abs(pen_a - pen_b)
            i += 1
            time.sleep(delay)
            print(pen_a, pen_b, i)

        winner = self.team_a if pen_a > pen_b else self.team_b
        print(f"Penalty score {self.team_a.name} {pen_a} {self.team_b.name} {pen_b}")

        self.penalties_result = (pen_a, pen_b, winner)
        return winner

    def update_team_stats(self):
        """Final step: increment Team.stats with GF, GA, minutes_played, etc."""
        # Update persistent team stats
        self.team_a.add_goal(self.final_score[0])
        self.team_a.concede_goal(self.final_score[1])
        self.team_a.add_minutes(90)
        self.team_a.stats.matches_played += 1

        self.team_b.add_goal(self.final_score[1])
        self.team_b.concede_goal(self.final_score[0])
        self.team_b.add_minutes(90)
        self.team_b.stats.matches_played += 1

        # Update group stage specific tracking
        if self.is_group:
            if self.result == MatchResult.A_WIN:
                self.team_a.points += 3
            elif self.result == MatchResult.B_WIN:
                self.team_b.points += 3
            else:
                self.team_a.points += 1
                self.team_b.points += 1

            self.team_a.goal_diff += (self.final_score[0] - self.final_score[1])
            self.team_b.goal_diff += (self.final_score[1] - self.final_score[0])
