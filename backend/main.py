"""
Main entry point for tournament simulation
"""

from sim import TournamentEngine
from config import DEFAULT_DELAY, DEFAULT_TEAMS_FILE


if __name__ == "__main__":
    # Create tournament engine
    engine = TournamentEngine(delay=DEFAULT_DELAY)

    # Load team data
    engine.load_data(DEFAULT_TEAMS_FILE)

    # Run tournament simulation
    champion = engine.simulate_tournament()

    # Print champion
    print(f"\nChampion: {champion.name}")
