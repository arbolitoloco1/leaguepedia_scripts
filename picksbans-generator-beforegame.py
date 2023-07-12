import requests
import os

versions = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
currentVer = versions.json()[0]

response = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{currentVer}/data/en_US/champion.json")

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
    "rp5": "5th Red Pick",
    "bb1": "1st Blue Ban",
    "bb2": "2nd Blue Ban",
    "bb3": "3rd Blue Ban",
    "bb4": "4th Blue Ban",
    "bb5": "5th Blue Ban",
    "rb1": "1st Red Ban",
    "rb2": "2nd Red Ban",
    "rb3": "3rd Red Ban",
    "rb4": "4th Red Ban",
    "rb5": "5th Red Ban"
}

order = input("PB Order Type (1 or 2): ")
while str(order) not in ("1", "2"):
    print("Choose 1 or 2!")
    order = input("PB Order Type (1 or 2): ")
if str(order) == "1":
    orderl = ["bb1", "rb1", "bb2", "rb2", "bb3", "rb3", "bp1", "rp1", "rp2", "bp2", "bp3", "rp3", "rb4", "bb4", "rb5", "bb5", "rp4", "bp4", "bp5", "rp5"]
elif str(order) == "2":
    orderl = ["bb1", "bb2", "bb3", "bb4", "bb5", "rb1", "rb2", "rb3", "rb4", "rb5", "bp1", "bp2", "bp3", "bp4", "bp5", "rp1", "rp2", "rp3", "rp4", "rp5"]

pbs = {}
posblue = []
posred = []
blueteamchamps = []
redteamchamps = []

t1 = input("Blue Team: ")
t2 = input("Red Team: ")

for type in orderl:
    inputstring = types.get(type)
    champ = input("{}: ".format(inputstring))
    if champ.lower().strip() == "none" and ("bb" in type or "rb" in type):
        pbs[type] = "None"
        pbs[type + "k"] = 0
        continue
    key = champs.get(champ.lower().strip())
    while champ.lower().strip() not in list(champs.keys()) or key[0] in list(pbs.values()) or not key:
        print("Champ not found or already selected!")
        champ = input("{}: ".format(inputstring))
        if champ.lower().strip() == "none" and ("bb" in type or "rb" in type):
            pbs[type] = "None"
            pbs[type + "k"] = 0
            continue
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
            else:
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
            else:
                pbs[type] = role
                posred.append(role)
                break
        else:
            print("The position is not valid!")
            continue

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
