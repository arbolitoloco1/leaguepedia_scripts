from mwrogue.esports_client import EsportsClient
from mwrogue.auth_credentials import AuthCredentials


def main(year):
    credentials = AuthCredentials(user_file="bot")
    site = EsportsClient("lol", credentials=credentials)

    response = site.cargo_client.query(
        tables="Champions=C",
        fields="_pageName=Page"
    )

    for item in response:
        page_title = item["Page"] + f"/Statistics/{year}"
        page = site.client.pages[page_title]
        if not page.exists:
            site.save_title(title=page_title, text="{{ChampionYearStatsPage}}",
                            summary="Automatically creating statistics pages")


if __name__ == "__main__":
    current_year = "2023"
    main(current_year)
