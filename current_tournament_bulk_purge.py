import re

from mwrogue.auth_credentials import AuthCredentials
from mwrogue.esports_client import EsportsClient

from datetime import datetime, timedelta


class BulkTournamentPurger:
    def __init__(self, site: EsportsClient):
        self.site = site
        self.start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        print(f"Querying tournaments that started after {self.start_date}")

    def run(self):
        self.purge_stats()
        self.purge_results()

    def get_where_condition(self):
        return f"T.DateStart IS NOT NULL AND T.DateStart >= '{self.start_date}'"

    def purge_results(self):
        players_result = self.site.cargo_client.query(
            tables="Tournaments=T, TournamentPlayers=TP, PlayerRedirects=PR",
            join_on="T.OverviewPage=TP.OverviewPage, TP.Link=PR.AllName",
            where=self.get_where_condition(),
            fields="PR._pageName=PlayerPage, T.OverviewPage",
            group_by="PR._pageName",
            order_by="PR._pageName"
        )
        teams_result = self.site.cargo_client.query(
            tables="Tournaments=T, TournamentRosters=Ros, TeamRedirects=Red",
            join_on="T.OverviewPage=Ros.OverviewPage, Ros.Team=Red._pageName",
            where=self.get_where_condition(),
            fields="Red._pageName=TeamPage",
            group_by="Red._pageName"
        )
        for player_row in players_result:
            print(player_row["OverviewPage"])
            player = player_row["PlayerPage"]
            if player is None:
                continue
            if not player.strip():
                continue
            self.site.purge_title(player)
            self.site.purge_title(player + '/Tournament Results')
            print(f"Purged {player} results")
        for team_row in teams_result:
            team = team_row["TeamPage"]
            if team is None:
                continue
            if not team.strip():
                continue
            self.site.purge_title(team)
            self.site.purge_title(team + '/Tournament Results')
            print(f"Purged {team} results")

    def purge_stats(self):
        players_result = self.site.cargo_client.query(
            tables="Tournaments=T, ScoreboardPlayers=SP, PlayerRedirects=PR",
            join_on="T.OverviewPage=SP.OverviewPage, SP.Link=PR.AllName",
            where=self.get_where_condition(),
            fields="PR._pageName=PlayerPage, SP.StatsPage",
            group_by="PR._pageName"
        )
        teams_result = self.site.cargo_client.query(
            tables="Tournaments=T, ScoreboardTeams=ST, TeamRedirects=TR",
            join_on="T.OverviewPage=ST.OverviewPage, ST.Team=TR.AllName",
            where=self.get_where_condition(),
            fields="TR._pageName=TeamPage, ST.StatsPage",
            group_by="TR._pageName"
        )

        for player_row in players_result:
            player = player_row["PlayerPage"]
            if player is None:
                continue
            if not player.strip():
                continue
            self.site.purge_title(player)
            self.site.purge_title(player + '/Statistics')
            year = re.search(r"(\d\d\d\d)$", player_row['StatsPage'])[0]
            self.site.purge_title(player + '/Statistics + ' + year)
            self.site.purge_title(player + '/Match History')
            print(f"Purged {player} stats")
        for team_row in teams_result:
            team = team_row["TeamPage"]
            if team is None:
                continue
            if not team.strip():
                continue
            self.site.purge_title(team)
            self.site.purge_title(team + '/Statistics')
            year = re.search(r"(\d\d\d\d)$", team_row['StatsPage'])[0]
            self.site.purge_title(team + '/Statistics/' + year)
            self.site.purge_title(team + '/Match History')
            pb_page = self.site.client.pages[team + "/Pick-Ban History"]
            if pb_page.exists:
                self.site.purge(pb_page)
            print(f"Purged {team} stats")


def run(site: EsportsClient):
    BulkTournamentPurger(site).run()


if __name__ == '__main__':
    credentials = AuthCredentials(user_file="me")
    lol_site = EsportsClient('lol', credentials=credentials)  # Set wiki
    run(lol_site)
