import requests
import json
import csv
import statistics
import pickle


PRO_TEAM_MAP = {
    0: 'FA',
    1: 'ATL',
    2: 'BUF',
    3: 'CHI',
    4: 'CIN',
    5: 'CLE',
    6: 'DAL',
    7: 'DEN',
    8: 'DET',
    9: 'GB',
    10: 'TEN',
    11: 'IND',
    12: 'KC',
    13: 'OAK',
    14: 'LAR',
    15: 'MIA',
    16: 'MIN',
    17: 'NE',
    18: 'NO',
    19: 'NYG',
    20: 'NYJ',
    21: 'PHI',
    22: 'ARI',
    23: 'PIT',
    24: 'LAC',
    25: 'SF',
    26: 'SEA',
    27: 'TB',
    28: 'WSH',
    29: 'CAR',
    30: 'JAX',
    33: 'BAL',
    34: 'HOU'
}

POSITION_MAP = {
    1: 'QB',
    2: 'RB',
    3: 'WR',
    4: 'TE',
    5: 'K',
    16: 'D/ST'
}

# needs expansion (dropped many defensive/kicking/punting/coaching already)
PLAYER_STATS_MAP = {
    0: "passingAttempts",
    1: "completions",
    3: "passingYards",
    4: "passingTouchdowns",

    19: "passing2PtConversions",
    20: "passingInterceptions",

    23: "rushingAttempts",
    24: "rushingYards",
    25: "rushingTouchdowns",
    26: "rushing2PtConversions",

    41: "receptions",
    42: "receivingYards",
    43: "receivingTouchdowns",
    44: "receiving2PtConversions",
    53: "receivingReceptions"
}


def fetch_data(cache):
    url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2021/segments/0/leagues/170176?"
    view = "view=kona_player_info"
    cookies = {
        "swid": "{SWID HERE}",
        "espn_s2": "ESPN_S2 HERE"
    }
    header_data = {
        "players": {
            "limit": 1500,
            "sortDraftRanks": {
                "sortPriority": 100,
                "sortAsc": True,
                "value": "STANDARD"
            }
        }
    }
    header = {"x-fantasy-filter": json.dumps(header_data)}
    res = requests.get(url + view, cookies=cookies, headers=header)

    data = res.json()
    players = data["players"]

    if cache: cache_data(data)

    return players


def cache_data(data):
    with open("espn_data.pickle", "wb") as file:
        pickle.dump(data, file)


def load_cache():
    with open("espn_data.pickle", "rb") as file:
        data = pickle.load(file)
    return data


def write_csv(players):
    file = open("output.csv", "w", newline="", encoding="utf-8")
    writer = csv.writer(file)

    header_row = ["NAME", "TEAM", "POS",
                  "RANK - PPR", "AVG - PPR", "HIGH - PPR", "LOW - PPR",
                  "RANK - STD", "AVG - STD", "HIGH - STD", "LOW - STD",
                  "STATUS", "OUTLOOK"]
    writer.writerow(header_row)

    for item in players:
        player = item["player"]

        if player["defaultPositionId"] == 5 or player["defaultPositionId"] == 16: continue  # skip K and D/ST

        data_row = []

        data_row.append(player["fullName"])

        data_row.append(PRO_TEAM_MAP[player["proTeamId"]])

        data_row.append(POSITION_MAP[player["defaultPositionId"]])

        ranks = {"STANDARD": {"data": [], "avg": ""}, "PPR": {"data": [], "avg": ""}}
        rankings = player.get("rankings") if player.get("rankings") is not None else {"0": []}
        for rank_item in rankings["0"]:
            if rank_item["rank"] == 0:
                ranks[rank_item["rankType"]]["avg"] = rank_item["averageRank"]
            else:
                ranks[rank_item["rankType"]]["data"].append(rank_item["rank"])

        data_row.append(player["draftRanksByRankType"]["PPR"]["rank"])
        data_row.append(ranks["PPR"]["avg"])
        data_row.append(min(ranks["PPR"]["data"]) if len(ranks["PPR"]["data"]) > 0 else "")
        data_row.append(max(ranks["PPR"]["data"]) if len(ranks["PPR"]["data"]) > 0 else "")

        data_row.append(player["draftRanksByRankType"]["STANDARD"]["rank"])
        data_row.append(ranks["STANDARD"]["avg"])
        data_row.append(min(ranks["STANDARD"]["data"]) if len(ranks["STANDARD"]["data"]) > 0 else "")
        data_row.append(max(ranks["STANDARD"]["data"]) if len(ranks["STANDARD"]["data"]) > 0 else "")

        status = player.get("injuryStatus") if player.get("injuryStatus") is not None else ""
        data_row.append(status)

        data_row.append(player["seasonOutlook"] if len(player["seasonOutlook"]) > 0 else "")

        writer.writerow(data_row)

    file.close()


def test_stat_print(players):
    player1 = players[0]["player"]
    print(list(player1.keys()))
    print(list(player1["stats"][0].keys()))
    print("---------------------------------------")
    print("season:", player1["stats"][0]["seasonId"])
    for key in player1["stats"][0]["stats"].keys():
        if int(key) not in PLAYER_STATS_MAP.keys():
            continue
        name = PLAYER_STATS_MAP[int(key)]  # if int(key) in PLAYER_STATS_MAP.keys() else key
        value = player1["stats"][0]["stats"][key]
        print(name, ":", value)


if __name__ == "__main__":
    cached_data = load_cache()
    test_stat_print(cached_data["players"])
