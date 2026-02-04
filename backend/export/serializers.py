"""
Serializers - JSON export functionality for tournament snapshots
"""


def export_snapshot(tournament_engine):
    """
    Export a JSON-serializable snapshot of the tournament state

    Args:
        tournament_engine: TournamentEngine instance

    Returns:
        dict: JSON-serializable tournament snapshot
    """
    snapshot = {
        'sim_params': tournament_engine.sim_params,
        'teams': [],
        'groups': [],
        'qualifiers': [],
    }

    # Export team data
    for team in tournament_engine.teams:
        snapshot['teams'].append({
            'name': team.name,
            'elo': team.elo,
            'group': team.group,
            'eliminated': team.eliminated,
            'points': team.points,
            'goal_diff': team.goal_diff,
            'stats': {
                'GF': team.stats.GF,
                'GA': team.stats.GA,
                'minutes_played': team.stats.minutes_played,
                'matches_played': team.stats.matches_played,
                'clean_sheets': team.stats.clean_sheets,
                'yellow_count': team.stats.yellow_count,
                'red_count': team.stats.red_count,
                'xG': team.stats.xG,
                'goals_per_90': team.stats.per_90('GF')
            }
        })

    # Export group data
    for group in tournament_engine.groups:
        group_data = {
            'name': group.name,
            'teams': [t.name for t in group.teams],
            'matches_played': len(group.matches),
            'standings': None
        }

        if group.standings:
            group_data['standings'] = [
                {
                    'team': t.name,
                    'points': t.points,
                    'goal_diff': t.goal_diff
                } for t in group.standings
            ]

        snapshot['groups'].append(group_data)

    return snapshot
