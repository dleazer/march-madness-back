from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse, inputs
import util

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument("season")
parser.add_argument("team_a")
parser.add_argument("team_b")
parser.add_argument("team_a_home")
parser.add_argument("neutral_court")
parser.add_argument("regular_season")
parser.add_argument("conference_tournament")
parser.add_argument("ncaa_tournament")
parser.add_argument("date")

class Season(Resource):
	def get(self, season):
		return util.get_season(season)

class Seasons(Resource):
	def get(self):
		return util.get_seasons()

class Teams(Resource):
	def get(self):
		response = {
			"teams": util.get_teams()
		}

		return response

class NcaaTournamentSeeds(Resource):
	def get(self, season):
		response = {
			"ncaa_tournament_seeds": util.get_ncaa_tournament_seeds(season)
		}

		return response

class NcaaTournamentSlots(Resource):
	def get(self, season):
		response = {
			"ncaa_tournament_slots": util.get_ncaa_tournament_slots(season)
		}

		return response

class NcaaTournamentGames(Resource):
	def get(self, season):
		response = {
			"ncaa_tournament_games": util.get_ncaa_tournament_games(season)
		}

		return response

class PredictGame(Resource):
	def post(self):
		args = parser.parse_args()

		season          = args["season"]
		team_a          = args["team_a"]
		team_b          = args["team_b"]
		team_a_home     = inputs.boolean(args["team_a_home"]) if args["team_a_home"] is not None else False
		neutral_court   = inputs.boolean(args["neutral_court"]) if args["neutral_court"] is not None else False
		reg_season      = inputs.boolean(args["regular_season"]) if args["regular_season"] is not None else False
		conf_tournament = inputs.boolean(args["conference_tournament"]) if args["conference_tournament"] is not None else False
		ncaa_tournament = inputs.boolean(args["ncaa_tournament"]) if args["ncaa_tournament"] is not None else False
		date            = args["date"] if args["date"] is not None else "{}-02-01".format(season)

		switched = False

		if int(team_a) > int(team_b):
			temp = team_a
			team_a = team_b
			team_b = temp
			switched = True

		if team_a_home:
			neutral_court = False

		if neutral_court:
			team_a_home = False

		if reg_season:
			conf_tournament = False
			ncaa_tournament = False
		
		if conf_tournament:
			reg_season      = False
			ncaa_tournament = False

		if ncaa_tournament:
			reg_season      = False
			conf_tournament = False

		day_num = util.date_to_day_num(inputs.date(date), season)

		prediction = util.predict_game(season, team_a, team_b, team_a_home, neutral_court, reg_season, conf_tournament, ncaa_tournament, day_num)

		if switched:
			prediction = 1 - prediction

		response = {
			"team_a_win_prob": float(prediction)
		}

		return response

class PredictTournament(Resource):
	def get(self, season):
		response = {
			"predictions": util.predict_tournament(season)
		}

		return response

	def post(self):
		args = parser.parse_args()
		season = args["season"]

		response = {
			"predictions": util.predict_tournament(season)
		}

		return response

# Endpoints
api.add_resource(Season, "/api/season/<season>")
api.add_resource(Seasons, "/api/seasons")
api.add_resource(Teams, "/api/teams")
api.add_resource(NcaaTournamentSeeds, "/api/ncaa-tournament-seeds/<season>")
api.add_resource(NcaaTournamentSlots, "/api/ncaa-tournament-slots/<season>")
api.add_resource(NcaaTournamentGames, "/api/ncaa-tournament-games/<season>")
api.add_resource(PredictGame, "/api/predict-game")
api.add_resource(PredictTournament, "/api/predict-tournament/<season>")

if __name__ == "__main__":
	app.run(debug=False)