from mwrogue.esports_client import EsportsClient
from mwrogue.auth_credentials import AuthCredentials
import math


class AutoTeamRosters(object):
    def __init__(self, overview_page):
        self.credentials = AuthCredentials(user_file="me")
        self.site = EsportsClient("lol", credentials=self.credentials)
        self.overview_page = self.site.cache.get_target(overview_page)
        self.match_data = {}
        self.alt_teamnames = {}
        self.rosters_data = {}

    def run(self):
        self.get_and_process_match_data()
        self.initialize_roster_data()
        players_data = self.get_player_data()
        self.process_game_data()
        print(self.rosters_data)

    def get_and_process_match_data(self):
        matchschedule_data = self.get_matchschedule_data()
        scoreboard_data = self.get_scoreboard_data(matchschedule_data)
        self.process_matchschedule_data(matchschedule_data)
        self.process_scoreboard_data(scoreboard_data)

    def get_matchschedule_data(self):
        matchschedule_data = self.site.cargo_client.query(
            tables="MatchSchedule=MS, MatchScheduleGame=MSG",
            fields=["MS.MatchId", "MSG.GameId", "MS.FF=MSFF", "MSG.FF=MSGFF", "MS.BestOf", "MS.Team1Final",
                    "MS.Team2Final", "MS.Team1", "MS.Team2"],
            join_on="MS.MatchId=MSG.MatchId",
            where=f"MS.OverviewPage = '{self.overview_page}'",
            order_by="MS.N_Page, MS.N_MatchInPage, MSG.N_GameInMatch"
        )
        return matchschedule_data

    @staticmethod
    def get_where_scoreboard_data(matchschedule_data):
        where = "SG.GameId IN ("
        for game in matchschedule_data:
            if not game["MSFF"] or not game["MSGFF"]:
                game_id = game["GameId"]
                where += f'"{game_id}", '
        where = where[:-2] + ")"
        return where

    def get_scoreboard_data(self, matchschedule_data):
        where = self.get_where_scoreboard_data(matchschedule_data)
        scoreboard_data = self.site.cargo_client.query(
            tables="ScoreboardGames=SG, ScoreboardPlayers=SP",
            fields=["SG.OverviewPage", "SG.Team1", "SG.Team2", "SP.IngameRole", "SP.Team", "SP.Link", "SG.GameId",
                    "SG.MatchId"],
            order_by="SG.N_Page, SG.N_MatchInPage, SG.N_GameInMatch",
            where=where,
            join_on="SG.GameId=SP.GameId"
        )
        return scoreboard_data

    def process_matchschedule_data(self, matchschedule_data):
        for match in matchschedule_data:
            if not self.match_data.get(match["MatchId"]):
                self.match_data[match["MatchId"]] = {"ff": False, "best_of": match["BestOf"], "team1": match["Team1"],
                                                     "team2": match["Team2"], "games": {}}
                if match["MSFF"]:
                    self.match_data[match["MatchId"]]["ff"] = True
                self.alt_teamnames[match["Team1"]] = match["Team1Final"]
                self.alt_teamnames[match["Team2"]] = match["Team2Final"]
            self.match_data[match["MatchId"]]["games"][match["GameId"]] = {"msg_data": match}

    def process_scoreboard_data(self, scoreboard_data):
        player_pages_cache = {}

        for scoreboard_game in scoreboard_data:
            if not self.match_data[scoreboard_game["MatchId"]]["games"][scoreboard_game["GameId"]].get("sg_data"):
                self.match_data[scoreboard_game["MatchId"]]["games"][scoreboard_game["GameId"]]["sg_data"] = {
                    "team1": scoreboard_game["Team1"],
                    "team2": scoreboard_game["Team2"],
                    "players": {}}
            if scoreboard_game["Link"] not in player_pages_cache:
                player_page = self.site.cache.get_target(scoreboard_game["Link"])
                player_pages_cache[scoreboard_game["Link"]] = player_page
            player_page = player_pages_cache[scoreboard_game["Link"]]
            self.match_data[scoreboard_game["MatchId"]]["games"][scoreboard_game["GameId"]]["sg_data"]["players"][player_page] = {"IngameRole": scoreboard_game["IngameRole"],
                                                                                                                                  "Team": scoreboard_game["Team"],
                                                                                                                                  "Link": player_page}

    def initialize_roster_data(self):
        for match in self.match_data.values():
            for game in match["games"].values():
                if game.get("sg_data"):
                    for player in game["sg_data"]["players"].values():
                        team = self.alt_teamnames[player["Team"]]
                        if team not in self.rosters_data.keys():
                            self.rosters_data[team] = {"players": {}, "teamsvs": []}
                        if player["Link"] not in self.rosters_data[team]["players"].keys(): # usar siempre not in en vez de if not
                            self.rosters_data[team]["players"][player["Link"]] = {"roles": {}}
                        self.rosters_data[team]["players"][player["Link"]]["roles"][player["IngameRole"]] = ""

    @staticmethod
    def get_where_player_data(rosters_data):
        players = []

        where = "PR.AllName IN ("
        for team in rosters_data.values():
            for player in team["players"].keys():
                if player not in players:
                    players.append(player)
                    where += f'"{player}", '
        where = where[:-2] + ")"
        return where

    def get_player_data(self):
        players_data = {}

        where = self.get_where_player_data(self.rosters_data)
        response = self.site.cargo_client.query(
            tables="Players=P, PlayerRedirects=PR",
            join_on="PR.OverviewPage=P.OverviewPage",
            where=where,
            fields=["P.NameFull=name", "P.Player", "P.NationalityPrimary", "P.Country", "P.Residency"]
        )

        for player_data in response:
            players_data[player_data["Player"]] = {"flag": player_data["NationalityPrimary"] or player_data["Country"],
                                                   "res": player_data["Residency"], "player": player_data["Player"],
                                                   "name": player_data["name"].replace("&amp;nbsp;", " ")}
        return players_data

    def process_game_data(self):
        for match in self.match_data.values():
            current_teams = [self.alt_teamnames[match["team1"]], self.alt_teamnames[match["team2"]]]
            if match["ff"]:
                for team in current_teams:
                    for player in self.rosters_data[team]["players"].values():
                        for role in player["roles"].keys():
                            player["roles"][role] += f"{'n' * math.ceil(int(match['best_of']) / 2)},"
                continue
            for game in match["games"].values():
                for team in current_teams:
                    for player in self.rosters_data[team]["players"].keys():
                        if player in game["sg_data"]["players"].keys():
                            for role in self.rosters_data[team]["players"][player]["roles"].keys():
                                if role == game["sg_data"]["players"][player]["IngameRole"]:
                                    self.rosters_data[team]["players"][player]["roles"][role] += "y"
                                else:
                                    self.rosters_data[team]["players"][player]["roles"][role] += "n"
                        else:
                            for role in self.rosters_data[team]["players"][player]["roles"].keys():
                                self.rosters_data[team]["players"][player]["roles"][role] += "n"
            for team in current_teams:
                for player in self.rosters_data[team]["players"].keys():
                    for role in self.rosters_data[team]["players"][player]["roles"].keys():
                        self.rosters_data[team]["players"][player]["roles"][role] += ","


if __name__ == '__main__':
    AutoTeamRosters("LMF 2022 Opening").run()
