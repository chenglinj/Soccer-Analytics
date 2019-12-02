import pymongo
import json

connection = pymongo.MongoClient('localhost', 27017)
db = connection['soccer']
player_all = db['player_all']
goal_stat = db['goal_stat']
club_2015 = db['club2015']
club_2016 = db['club2016']
club_2017 = db['club2017']
goal_2015 = db['goal_2015']
goal_2016 = db['goal_2016']
goal_2017 = db['goal_2017']

seasons = ['15/16', '16/17', '17/18']

for season in seasons:
    team_goal = []
    clubs = []
    if season == '15/16':
        clubs = list(club_2015.find())
        goals = list(goal_2015.find())
    elif season == '16/17':
        clubs = list(club_2016.find())
        goals = list(goal_2016.find())
    else:
        clubs = list(club_2017.find())
        goals = list(goal_2017.find())

    for club in clubs:
        club_name = club['club_information']['name']
        player_list = club['club_information']['detail']
        club_goal = {'club': club_name, 'freq': {'Header': 0, 'Right_footed_shot': 0, 'Left_footed_shot': 0, 'Penalty': 0, 'Direct_free_kick': 0, 'Others': 0}}
        for player in player_list:
            player_id = player['id']
            for goal_player in goals:
                if goal_player['goal_information']['id'] == player_id:
                    if goal_player['goal_information']['detail'] is not None:
                        for goal in goal_player['goal_information']['detail']:
                            if (goal['season'] == season) and (goal['league_name'] == 'Premier League'):
                                goal_type = goal['type_of_goal'].replace('-', '_').replace(' ', '_')
                                if goal_type != '':
                                    if goal_type in club_goal['freq']:
                                        club_goal['freq'][goal_type] += 1
                                    else:
                                        club_goal['freq']['Others'] += 1

        team_goal.append(club_goal)

    with open('output/team_goal_type/team_goal_type%s.json' % season.replace('/', '-'), 'w') as output:
        output.write('[')

        output.write(json.dumps(team_goal))

        output.write(']')
    output.close()

