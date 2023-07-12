import requests
import datetime as dt
import os
from mwrogue.esports_client import EsportsClient

versions = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
currentVer = versions.json()[0]

response = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{str(currentVer)}/data/en_US/champion.json")

champdata = response.json()["data"]
champs = {}

for key, value in champdata.items():
    champname = value["name"]
    champid = value["id"]
    champkey = value["key"]
    champs[champname.lower()] = [champkey, champname]
    champs[champid.lower()] = [champkey, champname]

PICKSBANS = """{{{{PicksAndBansS7|blueteam={t1} |redteam={t2}\n|team1score= |team2score= |winner=\n|blueban1={bb1} |red_ban1={rb1}\n|blueban2={bb2} |red_ban2={rb2}\n|blueban3={bb3} |red_ban3={rb3}\n
|bluepick1={bp1} |bluerole1={bpo1}\n                                           |red_pick1={rp1} |red_role1={rpo1}\n                                           |red_pick2={rp2} |red_role2={rpo2}\n|bluepick2={bp2} |bluerole2={bpo2}\n|bluepick3={bp3} |bluerole3={bpo3}\n                                           |red_pick3={rp3} |red_role3={rpo3}\n
|blueban4={bb4} |red_ban4={rb4}\n|blueban5={bb5} |red_ban5={rb5}\n                                           |red_pick4={rp4} |red_role4={rpo4}\n|bluepick4={bp4} |bluerole4={bpo4}\n|bluepick5={bp5} |bluerole5={bpo5}\n                                           |red_pick5={rp5} |red_role5={rpo5}\n"""

PBWITHGAME1 = "|game1=yes}}"
PBWITHOUTGAME1 = "}}"

date = input("Match date in yyyy-mm-dd format: ")
date = dt.datetime.strptime(date, "%Y-%m-%d").date()
datedelta = str(date+dt.timedelta(2))
t1 = input("Blue Team: ")
t2 = input("Red Team: ")
site = EsportsClient('lol')

response = site.cargo_client.query(
	limit = "max",
	tables = "ScoreboardGames=SG",
	fields = "SG.Team1Bans, SG.Team2Bans, SG.Team1Picks, SG.Team2Picks, SG.GameId",
	where = f'SG.DateTime_UTC >= "{date} 00:00:00" AND SG.DateTime_UTC <= "{datedelta} 00:00:00" AND SG.Team1 = "{t1}" AND SG.Team2 = "{t2}"',
    order_by = "SG.GameId"
)

if not response:
    print("Not matches found!")
    os.system("pause")
    exit()
elif len(response) > 1:
    print("Multiple matches found!")
    foundGameIds = {}
    for x, game in enumerate(response):
        x += 1
        gameId = game["GameId"]
        print("{0}- {1}".format(str(x), gameId))
        foundGameIds[str(x)] = gameId
    gi = input("Which Game Id are you looking for? ")
    gi = foundGameIds.get(str(gi))
    while not gi:
        print("The ID is not on the list! Select it by its index.")
        gi = input("Which Game Id are you looking for? ")
        gi = foundGameIds.get(str(gi))
    for item in response:
        if item["GameId"] == gi:
            response[0] = item
            print(response)

res = response[0]["Team1Bans"]
t1bans = res.split(",")
res2 = response[0]["Team2Bans"]
t2bans = res2.split(",")

pbs = {}
bankeys = {}
posblue = []
posred = []
blueteamchamps = []
redteamchamps = []

types = {
    "bp1": "1st Blue Pick",
    "bp2": "2nd Blue Pick",
    "bp3": "3rd Blue Pick",
    "bp4": "4th Blue Pick",
    "bp5": "5th Blue Pick",
    "rp1": "1st Red Pick",
    "rp2": "2nd Red Pick",
    "rp3": "3rd Red Pick",
    "rp4": "4th Red Pick",
    "rp5": "5th Red Pick"
}

teambans = {
    "bb1": t1bans[0],
    "bb2": t1bans[1],
    "bb3": t1bans[2],
    "bb4": t1bans[3],
    "bb5": t1bans[4],
    "rb1": t2bans[0],
    "rb2": t2bans[1],
    "rb3": t2bans[2],
    "rb4": t2bans[3],
    "rb5": t2bans[4]
}

pbs = {}

for key, value in teambans.items():
    if value.lower() == "none":
        pbs[key] = str(value)
        pbs[key + "k"] = 0
        continue
    bankey = champs.get(value.lower())
    if not bankey:
        print("BAN ERROR!")
        os.system("pause")
        exit()
    pbs[key] = str(value)
    pbs[key + "k"] = bankey[0]

print("Blue Ban 1: {bb1}\nBlue Ban 2: {bb2}\nBlue Ban 3: {bb3}\nBlue Ban 4: {bb4}\nBlue Ban 5: {bb5}\nRed Ban 1: {rb1}\nRed Ban 2: {rb2}\nRed Ban 3: {rb3}\nRed Ban 4: {rb4}\nRed Ban 5: {rb5}"
.format(bb1 = t1bans[0], bb2 = t1bans[1], bb3 = t1bans[2], bb4 = t1bans[3], bb5 = t1bans[4], rb1 = t2bans[0], rb2 = t2bans[1], rb3 = t2bans[2], rb4 = t2bans[3], rb5 = t2bans[4]))

if "None" in pbs.values():
    print("\nCHECK FOR BAN ORDER!")

for type in list(types.keys()):
    inputstring = types.get(type)
    champ = input("{}: ".format(inputstring))
    key = champs.get(champ.lower().strip())
    while champ.lower().strip() not in list(champs.keys()) or key[0] in list(pbs.values()) or not key:
        print("Champ not found or already selected!")
        champ = input("{}: ".format(inputstring))
        key = champs.get(champ.lower().strip())
    prettychamp = key[1]
    pbs[type] = prettychamp
    pbs[type + "k"] = key[0]

typesblue = ["bpo1", "bpo2", "bpo3", "bpo4", "bpo5"]
typesred = ["rpo1", "rpo2", "rpo3", "rpo4", "rpo5"]

print("\nAccepted roles: t, j, m, b, s")

print("\nBLUE TEAM POSITIONS")

for x, type in enumerate(typesblue):
    inputstring = pbs.get(list(types.keys())[x])
    while True:
        role = input("Position/Role for {}: ".format(inputstring))
        role = role.lower().strip()
        if role == "t" or role == "j" or role == "m" or role == "b" or role == "s":
            if role in posblue:
                print("The position has already been chosen for this team!")
                continue
            pbs[type] = role
            posblue.append(role)
            break
        else:
            print("The position is not valid!")
            continue

print("\nRED TEAM POSITIONS")

for x, type in enumerate(typesred):
    x += 5
    inputstring = pbs.get(list(types.keys())[x])
    while True:
        role = input("Position/Role for {}: ".format(inputstring))
        role = role.lower().strip()
        if role == "t" or role == "j" or role == "m" or role == "b" or role == "s":
            if role in posred:
                print("The position has already been chosen for this team!")
                continue
            pbs[type] = role
            posred.append(role)
            break
        else:
            print("The position is not valid!")

print(pbs)

finaldata = PICKSBANS.format(t1 = t1, t2 = t2, bb1 = pbs.get("bb1"), bb2 = pbs.get("bb2"), bb3 = pbs.get("bb3"), bb4 = pbs.get("bb4"), bb5 = pbs.get("bb5"), rb1 = pbs.get("rb1"), rb2 = pbs.get("rb2"), rb3 = pbs.get("rb3"), rb4 = pbs.get("rb4"), rb5 = pbs.get("rb5"), 
bp1 = pbs.get("bp1"), bp2 = pbs.get("bp2"), bp3 = pbs.get("bp3"), bp4 = pbs.get("bp4"), bp5 = pbs.get("bp5"), rp1 = pbs.get("rp1"), rp2 = pbs.get("rp2"), rp3 = pbs.get("rp3"), rp4 = pbs.get("rp4"), rp5 = pbs.get("rp5"), 
bpo1 = pbs.get("bpo1"), bpo2 = pbs.get("bpo2"), bpo3 = pbs.get("bpo3"), bpo4 = pbs.get("bpo4"), bpo5 = pbs.get("bpo5"), rpo1 = pbs.get("rpo1"), rpo2 = pbs.get("rpo2"), rpo3 = pbs.get("rpo3"), rpo4 = pbs.get("rpo4"), rpo5 = pbs.get("rpo5"))

game1 = input("\nIs this game 1? (Y/N): ")
while game1.upper() not in ("Y", "N"):
    print("Choose Y or N!")
    game1 = input("\nIs this game 1? (Y/N): ")
if game1.upper() == "Y":
    finaldata = finaldata + PBWITHGAME1
elif game1.upper() == "N":
    finaldata = finaldata + PBWITHOUTGAME1

print("\n" + finaldata)

os.system("pause")
