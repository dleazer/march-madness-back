.mode csv

CREATE TABLE seasons(
	season TEXT NOT NULL,
	date_start TEXT NOT NULL,
	region_w TEXT NOT NULL,
	region_x TEXT NOT NULL,
	region_y TEXT NOT NULL,
	region_z TEXT NOT NULL,
	date_end TEXT NOT NULL
);

.import data/MSeasons.csv seasons

CREATE TABLE teams(
	id TEXT NOT NULL,
	name TEXT NOT NULL,
	first_d1_season TEXT NOT NULL,
	last_d1_season TEXT NOT NULL
);

.import data/MTeams.csv teams

CREATE TABLE team_average_stats(
	season TEXT NOT NULL,
	team_id TEXT NOT NULL,
	points REAL NOT NULL,
	twos_att REAL NOT NULL,
	twos_made REAL NOT NULL,
	threes_att REAL NOT NULL,
	threes_made REAL NOT NULL,
	free_throws_att REAL NOT NULL,
	free_throws_made REAL NOT NULL,
	rebounds_off REAL NOT NULL,
	rebounds_def REAL NOT NULL,
	assists REAL NOT NULL,
	turnovers REAL NOT NULL,
	steals REAL NOT NULL,
	blocks REAL NOT NULL,
	personal_fouls REAL NOT NULL
);

.import data/AllGamesTeamAverageStats.csv team_average_stats

CREATE TABLE ncaa_tournament_seeds(
	season TEXT NOT NULL,
	seed TEXT NOT NULL,
	team_id TEXT NOT NULL
);

.import data/MNCAATourneySeeds.csv ncaa_tournament_seeds

CREATE TABLE ncaa_tournament_slots(
	season TEXT NOT NULL,
	slot TEXT NOT NULL,
	strong_seed TEXT NOT NULL,
	weak_seed TEXT NOT NULL
);

.import data/MNCAATourneySlots.csv ncaa_tournament_slots

CREATE TABLE ncaa_tournament_seed_round_slots(
	seed TEXT NOT NULL,
	round TEXT NOT NULL,
	slot TEXT NOT NULL,
	early_day_num INTEGER NOT NULL,
	late_day_num INTEGER NOT NULL
);

.import data/MNCAATourneySeedRoundSlots.csv ncaa_tournament_seed_round_slots

CREATE TABLE ncaa_tournament_predictions(
	season TEXT NOT NULL,
	team_a TEXT NOT NULL,
	team_b TEXT NOT NULL,
	team_a_win_prob REAL NOT NULL
);

CREATE TABLE regular_season_team_average_stats_scaled(
	season TEXT NOT NULL,
	team_id TEXT NOT NULL,
	points REAL NOT NULL,
	twos_att REAL NOT NULL,
	twos_made REAL NOT NULL,
	threes_att REAL NOT NULL,
	threes_made REAL NOT NULL,
	free_throws_att REAL NOT NULL,
	free_throws_made REAL NOT NULL,
	rebounds_off REAL NOT NULL,
	rebounds_def REAL NOT NULL,
	assists REAL NOT NULL,
	turnovers REAL NOT NULL,
	steals REAL NOT NULL,
	blocks REAL NOT NULL,
	personal_fouls REAL NOT NULL
);

.import data/RegularSeasonTeamAverageStatsScaled.csv regular_season_team_average_stats_scaled

CREATE TABLE conference_tournament_team_average_stats_scaled(
	season TEXT NOT NULL,
	team_id TEXT NOT NULL,
	points REAL NOT NULL,
	twos_att REAL NOT NULL,
	twos_made REAL NOT NULL,
	threes_att REAL NOT NULL,
	threes_made REAL NOT NULL,
	free_throws_att REAL NOT NULL,
	free_throws_made REAL NOT NULL,
	rebounds_off REAL NOT NULL,
	rebounds_def REAL NOT NULL,
	assists REAL NOT NULL,
	turnovers REAL NOT NULL,
	steals REAL NOT NULL,
	blocks REAL NOT NULL,
	personal_fouls REAL NOT NULL
);

.import data/ConferenceTournamentTeamAverageStatsScaled.csv conference_tournament_team_average_stats_scaled

CREATE TABLE ncaa_tournament_team_average_stats_scaled(
	season TEXT NOT NULL,
	team_id TEXT NOT NULL,
	points REAL NOT NULL,
	twos_att REAL NOT NULL,
	twos_made REAL NOT NULL,
	threes_att REAL NOT NULL,
	threes_made REAL NOT NULL,
	free_throws_att REAL NOT NULL,
	free_throws_made REAL NOT NULL,
	rebounds_off REAL NOT NULL,
	rebounds_def REAL NOT NULL,
	assists REAL NOT NULL,
	turnovers REAL NOT NULL,
	steals REAL NOT NULL,
	blocks REAL NOT NULL,
	personal_fouls REAL NOT NULL
);

.import data/NCAATournamentTeamAverageStatsScaled.csv ncaa_tournament_team_average_stats_scaled