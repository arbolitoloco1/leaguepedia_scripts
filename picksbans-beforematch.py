import requests
import datetime as dt
from datetime import date, timedelta
import os

versions = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
currentVer = versions.json()[0]

response = requests.get("http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion.json".format(str(currentVer)))

champkeys = response.json()["data"]
champids = list(champkeys.keys())
champnames = []
champidslower = []

for x in range(len(champids)):
    champid = champids[x]
    champname = response.json()["data"][champid]["name"]
    champnames.append(champname.lower())
    champidslower.append(champid.lower())

PICKSBANS = "{{PicksAndBansS7|blueteam={t1} |redteam={t2}\n|team1score= |team2score= |winner=\n|blueban1={bb1} |red_ban1={rb1}\n|blueban2={bb2} |red_ban2={rb2}\n|blueban3={bb3} |red_ban3={rb3}\n|bluepick1={bp1} |bluerole1={bpo1}\n                                           |red_pick1={rp1} |red_role1={rpo1}\n                                           |red_pick2={rp2} |red_role2={rpo2}\n|bluepick2={bp2} |bluerole2={bpo2}\n|bluepick3={bp3} |bluerole3={bpo3}\n                                           |red_pick3={rp3} |red_role3={rpo3}\n|blueban4={bb4} |red_ban4={rb4}\n|blueban5={bb5} |red_ban5={rb5}\n                                           |red_pick4={rp4} |red_role4={rpo4}\n|bluepick4={bp4} |bluerole4={bpo4}\n|bluepick5={bp5} |bluerole5={bpo5}\n                                           |red_pick5={rp5} |red_role5={rpo5}\n|game1=yes}}"

types = {
    "bb1": "1st Blue Ban",
    "rb1": "1st Red Ban",
    "bb2": "2nd Blue Ban",
    "rb2": "2nd Red Ban",
    "bb3": "3rd Blue Ban",
    "rb3": "3rd Red Ban",
    "bp1": "1st Blue Pick",
    "rp1": "1st Red Pick",
    "rp2": "2nd Red Pick",
    "bp2": "2nd Blue Pick",
    "bp3": "3rd Blue Pick",
    "rp3": "3rd Red Pick",
    "rb4": "4th Red Ban",
    "bb4": "4th Blue Ban",
    "rb5": "5th Red Ban",
    "bb5": "5th Blue Ban",
    "rp4": "4th Red Pick",
    "bp4": "4th Blue Pick",
    "bp5": "5th Blue Pick",
    "rp5": "5th Red Pick"
}

list = list(types.keys())
pbs = {}
pbslower = []
posblue = []
posred = []
blueteamchamps = []
redteamchamps = []

t1 = input("Blue Team: ")
t2 = input("Red Team: ")

for x in (range(len(list))):
    type = list[x]
    inputstring = types.get(type)
    while True:
        champ = input("{}: ".format(inputstring))
        if champ.lower() == "none":
            if champ == "None" and ("bb" in type or "rb" in type):
                pbs[type] = champ
                break
            else:
                print("Use None!")
                continue
        elif champ.lower() in champnames or champ in champidslower:
            if champ.lower() in pbslower:
                print("The champ has already been chosen.")
                continue
            else:
                pbs[type] = champ
                pbslower.append(champ.lower())
                if "bp" in type:
                    blueteamchamps.append(champ)
                elif "rp" in type:
                    redteamchamps.append(champ)
                break
        else:
            print("Not found!")
            continue

typesblue = ["bpo1", "bpo2", "bpo3", "bpo4", "bpo5"]
typesred = ["rpo1", "rpo2", "rpo3", "rpo4", "rpo5"]

print("\nBLUE TEAM POSITIONS")

for x in range(len(typesblue)):
    type = typesblue[x]
    inputstring = blueteamchamps[x]
    while True:
        champ = input("Position/Role for {}: ".format(inputstring))
        if champ == "t" or champ == "j" or champ == "m" or champ == "b" or champ == "s":
            if champ in posblue:
                print("The position has already been chosen for this team!")
                continue
            else:
                pbs[type] = champ
                posblue.append(champ)
                break
        else:
            print("The position is not valid!")
            continue

print("\nRED TEAM POSITIONS")

for x in range(len(typesred)):
    type = typesred[x]
    inputstring = redteamchamps[x]
    while True:
        champ = input("Position/Role for {}: ".format(inputstring))
        if champ == "t" or champ == "j" or champ == "m" or champ == "b" or champ == "s":
            if champ in posred:
                print("The position has already been chosen for this team!")
                continue
            else:
                pbs[type] = champ
                posred.append(champ)
                break
        else:
            print("The position is not valid!")
            continue

finaldata = PICKSBANS.format(t1 = t1, t2 = t2, bb1 = pbs.get("bb1"), bb2 = pbs.get("bb2"), bb3 = pbs.get("bb3"), bb4 = pbs.get("bb4"), bb5 = pbs.get("bb5"), rb1 = pbs.get("rb1"), rb2 = pbs.get("rb2"), rb3 = pbs.get("rb3"), rb4 = pbs.get("rb4"), rb5 = pbs.get("rb5"), 
bp1 = pbs.get("bp1"), bp2 = pbs.get("bp2"), bp3 = pbs.get("bp3"), bp4 = pbs.get("bp4"), bp5 = pbs.get("bp5"), rp1 = pbs.get("rp1"), rp2 = pbs.get("rp2"), rp3 = pbs.get("rp3"), rp4 = pbs.get("rp4"), rp5 = pbs.get("rp5"), 
bpo1 = pbs.get("bpo1"), bpo2 = pbs.get("bpo2"), bpo3 = pbs.get("bpo3"), bpo4 = pbs.get("bpo4"), bpo5 = pbs.get("bpo5"), rpo1 = pbs.get("rpo1"), rpo2 = pbs.get("rpo2"), rpo3 = pbs.get("rpo3"), rpo4 = pbs.get("rpo4"), rpo5 = pbs.get("rpo5"))

print("\n" + finaldata)

os.system("pause")
