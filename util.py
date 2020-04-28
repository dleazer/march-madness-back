import os
import re
import numpy as np
import sqlite3

from time import time
from random import random
from datetime import datetime
from tensorflow.keras.models import load_model

def dict_factory(cursor, row):
	d = {}

	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]

	return d

def sql_connect():
	conn             = sqlite3.connect("march-madness.db")
	conn.row_factory = dict_factory

	return conn, conn.cursor()

def parse_ncaa_tournament_seed(seed):
	return int(re.sub(r"[A-Za-z]", "", seed))

def date_to_day_num(date, season):
	conn, sql = sql_connect()
	
	dates_q = "SELECT date_start, date_end FROM seasons WHERE season = ?;"
	dates_filter = [season]
	dates = sql.execute(dates_q, dates_filter).fetchone()

	ts_start = datetime.strptime(dates["date_start"], "%m/%d/%Y").timestamp()
	ts_date = date.timestamp()
	
	day_num = (ts_date - ts_start) % (60 * 60 * 24)

	return day_num

def get_teams():
	conn, sql = sql_connect()

	teams_q = "SELECT * FROM teams;"

	return sql.execute(teams_q).fetchall()

def get_ncaa_tournament_seeds(season):
	conn, sql = sql_connect()

	seeds_q = "SELECT * FROM ncaa_tournament_seeds WHERE season = ?;"
	seeds_filter = [season]

	return sql.execute(seeds_q, seeds_filter).fetchall()

def get_ncaa_tournament_slots(season):
	conn, sql = sql_connect()

	slots_q = "SELECT * FROM ncaa_tournament_slots WHERE season = ?;"
	slots_filter = [season]

	return sql.execute(slots_q, slots_filter).fetchall()

def get_ncaa_tournament_games(season):
	conn, sql = sql_connect()

	games_q = "SELECT * FROM ncaa_tournament_games WHERE season = ?;"
	games_filter = [season]

	return sql.execute(games_q, games_filter).fetchall()

def predict_game(season, team_a_id, team_b_id, team_a_home, neutral_court, reg_season, conf_tournament, ncaa_tournament, day_num):
	conn, sql = sql_connect()

	# Get seasons
	seasons_q = "SELECT DISTINCT season FROM team_average_stats;"
	seasons = [result["season"] for result in sql.execute(seasons_q).fetchall()]

	# Get seeds
	seeds_q = "SELECT DISTINCT seed FROM ncaa_tournament_seeds;"
	seeds = [parse_ncaa_tournament_seed(result["seed"]) for result in sql.execute(seeds_q).fetchall()]
	seeds = list(dict.fromkeys(seeds))

	# Get team seeds
	team_a_seed = 0
	team_b_seed = 0

	if ncaa_tournament:
		team_seeds_q = "SELECT seed FROM ncaa_tournament_seeds WHERE season = ? AND team_id = ?;"
		team_a_seed_filter = [season, team_a_id]
		team_b_seed_filter = [season, team_b_id]

		team_a_seed = parse_ncaa_tournament_seed(sql.execute(team_seeds_q, team_a_seed_filter).fetchone()["seed"])
		team_b_seed = parse_ncaa_tournament_seed(sql.execute(team_seeds_q, team_b_seed_filter).fetchone()["seed"])

	# Get team stats
	stats_q = "SELECT * FROM regular_season_team_average_stats_scaled WHERE season = ? AND team_id = ?;"
	
	if conf_tournament:
		stats_q = "SELECT * FROM conference_tournament_team_average_stats_scaled WHERE season = ? AND team_id = ?;"
	
	if ncaa_tournament:
		stats_q = "SELECT * FROM ncaa_tournament_team_average_stats_scaled WHERE season = ? AND team_id = ?;"
	
	team_a_stats_filter = [season, team_a_id]
	team_b_stats_filter = [season, team_b_id]

	team_a_stats = list(sql.execute(stats_q, team_a_stats_filter).fetchone().values())
	team_b_stats = list(sql.execute(stats_q, team_b_stats_filter).fetchone().values())

	# Build prediction query
	X = [1 if s == season else 0 for s in seasons]
	X.extend([1 if s == team_a_seed else 0 for s in seeds])
	X.extend([1 if s == team_b_seed else 0 for s in seeds])
	X.extend([
		int(reg_season), 
		int(conf_tournament),
		int(ncaa_tournament),
		int(team_a_home),
		int(neutral_court),
		day_num / 154 # 154 days in a basketball season
	])
	X.extend(team_a_stats[2:])
	X.extend(team_b_stats[2:])
	X = np.array(X, dtype=np.float32).reshape((1, len(X)))

	# Make prediction and return response
	model = load_model(os.path.join("models", "march-madness-{}.h5".format(season)))
	
	return model.predict(X).ravel()[0]

def predict_tournament(season):
	conn, sql = sql_connect()

	# First see if this tournament prediction already exists in the database
	predictions_q = "SELECT team_a, team_b, team_a_win_prob FROM ncaa_tournament_predictions WHERE season = ?;"
	predictions_filter = [season]
	predictions = sql.execute(predictions_q, predictions_filter).fetchall()

	# If this predicition already exists, return it
	if len(predictions) > 0:
		return predictions

	# Get seeds
	seeds_q = "SELECT seed, team_id FROM ncaa_tournament_seeds WHERE season = ?;"
	seeds_filter = [season]
	seeds = sql.execute(seeds_q, seeds_filter).fetchall()
	seed_labels = []
	seed_teams = []
	
	for seed in seeds:
		seed_labels.append(seed["seed"])
		seed_teams.append(seed["team_id"])

	# Get tournament slots
	slots_q = "SELECT slot, strong_seed, weak_seed FROM ncaa_tournament_slots WHERE season = ?;"
	slots_filter = [season]
	slots = sql.execute(slots_q, slots_filter).fetchall()

	# Get possible teams for each slot
	possible_teams_in_slot = dict()

	# Populate teams of the first round
	for s in slots:
		slot, strong_seed, weak_seed = s.values()

		# If this is the first time seeing this slot, add it to the dictionary
		if slot not in possible_teams_in_slot.keys():
			possible_teams_in_slot[slot] = []

		# If strong_seed or weak_seed are specific teams, add them to the list of possible teams for this slot
		if strong_seed in seed_labels:
			possible_teams_in_slot[slot].append(seed_teams[seed_labels.index(strong_seed)])

		if weak_seed in seed_labels:
			possible_teams_in_slot[slot].append(seed_teams[seed_labels.index(weak_seed)])

	# Populate the other rounds
	for s in slots:
		slot, strong_seed, weak_seed = s.values()

		if strong_seed in possible_teams_in_slot.keys():
			possible_teams_in_slot[slot].extend([team_id for team_id in possible_teams_in_slot[strong_seed] if team_id not in possible_teams_in_slot[slot]])
		
		if weak_seed in possible_teams_in_slot.keys():
			possible_teams_in_slot[slot].extend([team_id for team_id in possible_teams_in_slot[weak_seed] if team_id not in possible_teams_in_slot[slot]])

		possible_teams_in_slot[slot] = sorted(possible_teams_in_slot[slot])
		
	# Make predictions
	predictions = []
	made_predictions = []

	for i, team_id in enumerate(seed_teams):
		print("Predicting for team {} ({})".format(team_id, i))
		seed = seed_labels[i]

		# Get tournament rounds that this team may partipate in
		round_slots_q = "SELECT slot, early_day_num, late_day_num FROM ncaa_tournament_seed_round_slots WHERE seed = ? ORDER BY round;"
		round_slots_filter = [seed]
		round_slots = sql.execute(round_slots_q, round_slots_filter).fetchall()

		# Get this team's possible opponents in each round
		for round_slot in round_slots:
			slot, early_day_num, late_day_num = round_slot.values()

			slot_i = [s["slot"] for s in slots].index(slot)
			strong_seed = slots[slot_i]["strong_seed"]
			weak_seed = slots[slot_i]["weak_seed"]

			teams_a = []
			teams_b = []

			if strong_seed in seed_labels:
				teams_a = [seed_teams[seed_labels.index(strong_seed)]]
			else:
				teams_a = possible_teams_in_slot[strong_seed]
			
			if weak_seed in seed_labels:
				teams_b = [seed_teams[seed_labels.index(weak_seed)]]
			else:
				teams_b = possible_teams_in_slot[weak_seed]

			if team_id in teams_a:
				possible_opponents = teams_b
			else:
				possible_opponents = teams_a

			possible_opponents = sorted(possible_opponents)

			# Make a prediction for each possible opponent
			for opponent_id in possible_opponents:
				team_a = team_id
				team_b = opponent_id

				if int(team_b) < int(team_a):
					temp = team_a
					team_a = team_b
					team_b = temp

				if (team_a, team_b) in made_predictions:
					continue

				# Randomly choose early_day_num or late_day_num (they are different by at most one day)
				day_num = early_day_num

				if random() >= 0.5:
					day_num = late_day_num
				
				predictions.append({
					"team_a": team_a,
					"team_b": team_b,
					"team_a_win_prob": predict_game(season, team_a, team_b,
													team_a_home=False,
													neutral_court=True,
													reg_season=False,
													conf_tournament=False,
													ncaa_tournament=True,
													day_num=day_num)
				})

				made_predictions.append((team_a, team_b))

	# Write these predictions to the database before returning so they don't need to be
	# calculated again in the future
	for prediction in predictions:
		insert_q = "INSERT INTO ncaa_tournament_predictions (season, team_a, team_b, team_a_win_prob) VALUES (?, ?, ?, ?);"
		insert_filter = [season, prediction["team_a"], prediction["team_b"], float(prediction["team_a_win_prob"])]
		sql.execute(insert_q, insert_filter)
		conn.commit()

	return predictions
