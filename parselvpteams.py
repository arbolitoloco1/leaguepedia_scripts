import requests
from bs4 import BeautifulSoup
from mwrogue.esports_client import EsportsClient
from mwrogue.auth_credentials import AuthCredentials
from datetime import datetime
import pytz
import time

credentials = AuthCredentials(user_file="bot")
site = EsportsClient("lol", credentials=credentials)

PST = pytz.timezone('PST8PDT')

date = datetime.now(PST)
year = str(date.year).zfill(4)
month = str(date.month).zfill(2)
day = str(date.day).zfill(2)

full_date = f"{year}-{month}-{day}"

lolesports_endpoint = "https://esports-api.lolesports.com/persisted/gw/getTeams?hl=es-MX&id={}"
lolesports_headers = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}

output = "{{TOCRight}}\n\n"

teams = {"lolesports": ["rainbow7", "infinity", "estral-esports", "team-aze", "xten-esports", "isurus", "all-knights",
                        "globant-emerald-team"],
         "ligamaster": ["boca-juniors-gaming", "leviatan_esports", "uala_pampas", "ebro", "stone-movistar",
                        "9z", "river-plate-gaming", "malvinas_gaming", "krü_esports", "maycam-evolve",
                        "undeadbk", "wapesports"],
         "ligadehonor": ["furious-gaming", "dark-horse", "meta_gaming", "movistar-optix", "santiago-wanderers-esports",
                         "maze_gaming", "newstar", "cruzados-esports", "rebirth-esports", "wolf_club_esports"],
         "golden": ["zeu5bogota", "kingofgoats", "bravesrising", "awakegaming", "NOCTA", "teammayanesports",
                    "elrgaming", "spiritual"],
         "volcano": ["descuydadoesports", "skullcrackerclan", "godsplan", "piratedreamesports", "acesgaming",
                     "waiasnikt", "geeksideesports", "hookedesports"],
         "stars": ["incubus", "instinctgaming", "spectacledbears", "diamonddoves", "cienciano",
                   "clubdeportivomunicipal", "deliveranceesports", "fantasygaming"],
         "ddh": ["6K", "ath-esports", "arc-gaming", "zlt-esports", "THE-KINGS", "2MR", "ATOMIC-MEXICO",
                 "pk-gaming"],
         "elements": ["SAPRISSA-ESPORTS", "GRAVITY-ELITE", "JANUS-ESPORTS", "FUEGO", "RED-ROOSTER", "BANDITS",
                      "VANDALS-ESPORTS", "GOAT-ESPORTS"],
         "superliga": ["FnaticTeamQueso", "bar", "heretics", "giants", "bisons", "KOI", "g2arctic", "movistarriders",
                       "madlions", "UCAM"]}


def parse_lvp(web, output):
    print(web)
    languages_dict = {"ligamaster": "/ar", "ligadehonor": "/cl", "golden": "/co", "volcano": "/ec", "stars": "/pe",
                      "ddh": "/mx", "elements": "", "superliga": ""}

    output += f"== {web} ==\n\n"
    language = languages_dict[web]
    for team in teams[web]:
        try:
            html = requests.get(f"https://{web}.lvp.global{language}/equipo/{team}/")
            html = html.text

            parsed_html = BeautifulSoup(html, "html.parser")
            page = parsed_html.find_all("div", "squad-container-outer")
            squad = page[0].find("div", "players-container-inner")
            players = squad.find_all("a", "player-card")
            output += f"=== {team} ===\n\n"
            output += f"https://{web}.lvp.global{language}/equipo/{team}/\n\n"
            for player in players:
                player_info = player.find("div", "upper-player-info-container")
                player_nick = player_info.find("span", "player-nickname").text
                player_position = player_info.find("span", "player-position").text
                output += f"{player_nick} - {player_position}\n\n"
            output += "\n"
            print(f"{team} - {web}")
        except Exception as e:
            output += f"ERROR: {e}\n\n"
            with open(file="errores.txt", mode="a+", encoding="utf8") as f:
                f.write(str(e))
            continue
    return output


def parse_lolesports(output):
    try:
        output += f"== LLA ==\n\n"
        try:
            for team in teams["lolesports"]:
                response = requests.get(lolesports_endpoint.format(team), headers=lolesports_headers)
                response = response.json()
                print(response)
                players = response["data"]["teams"][0]["players"]
                output += f"=== {team} ===\n\n"
                for player in players:
                    player_nick = player["summonerName"]
                    player_position = player["role"]
                    output += f"{player_nick} - {player_position}\n\n"
                output += "\n"
        except Exception as e:
            output += f"ERROR: {e}\n\n"
            with open(file="errores.txt", mode="a+", encoding="utf8") as f:
                f.write(str(e))
    except Exception as e:
        output += f"ERROR: {e}\n\n"
        with open(file="errores.txt", mode="a+", encoding="utf8") as f:
            f.write(str(e))
    return output


for web in teams.keys():
    if web != "lolesports":
        output = parse_lvp(web, output)
    else:
        output = parse_lolesports(output)

while True:
    try:
        time.sleep(120)
        site.save_title(title=f"User:Arbolitoloco/RostersLVP", text=str(output), summary=f"{datetime.now()}")
        site.save_title(title=f"User:Arbolitoloco/RostersLVP/{full_date}", text=str(output),
                        summary=f"{datetime.now()}")
        break
    except Exception as e:
        with open(file="errores.txt", mode="a+", encoding="utf8") as f:
            f.write(str(e))
        continue

