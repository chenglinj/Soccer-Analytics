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
    team_goal = {}
    team_partner = {}
    team_best_partner = {}
    clubs = []
    goals = []
    if season == '15/16':
        clubs = list(club_2015.find())
        goals = list(goal_2015.find())
    elif season == '16/17':
        clubs = list(club_2016.find())
        goals = list(goal_2016.find())
    elif season == '17/18':
        clubs = list(club_2017.find())
        goals = list(goal_2017.find())

    for club in clubs:
        club_name = club['club_information']['name']
        team_goal[club_name] = {}
        team_partner[club_name] = {}
        club_player_list = []
        player_list = club['club_information']['detail']
        for player in player_list:
            club_player_list.append(player['id'])
        for player in player_list:
            player_id = player['id']
            # player_name = ''
            # team_goal[club_name][player_id] = {}
            for goal_player in goals:
                if goal_player['goal_information']['id'] == player_id:
                    player_name = goal_player['goal_information']['name']
                    team_goal[club_name][player_name] = {}
                    if goal_player['goal_information']['detail'] is not None:
                        for goal in goal_player['goal_information']['detail']:
                            if goal['provider_id'] in club_player_list:
                                if goal['provider'] in team_goal[club_name][player_name]:
                                    team_goal[club_name][player_name][goal['provider']] += 1
                                else:
                                    team_goal[club_name][player_name][goal['provider']] = 1
        for player in team_goal[club_name]:
            team_partner[club_name][player] = {}
            if team_goal[club_name][player] != {}:
                for provider in team_goal[club_name][player]:
                    if player in team_goal[club_name][provider]:
                        if (provider in team_partner[club_name]) and (player in team_partner[club_name][provider]):
                            pass
                        else:
                            team_partner[club_name][player][provider] = team_goal[club_name][player][provider] + team_goal[club_name][provider][player]

    for club in team_partner:
        team_best_partner[club] = [{'player1': '', 'player2': '', 'total_goals': 0}]
        for player in team_partner[club]:
            if team_partner[club][player] != {}:
                for provider in team_partner[club][player]:
                    if team_partner[club][player][provider] > team_best_partner[club][0]['total_goals']:
                        team_best_partner[club] = [{'player1': player, 'player2': provider,
                                                    'total_goals': team_partner[club][player][provider]}]
                    elif team_partner[club][player][provider] == team_best_partner[club][0]['total_goals']:
                        team_best_partner[club].append({'player1': player, 'player2': provider,
                                                        'total_goals': team_partner[club][player][provider]})

    with open('output/team_goal_provider/team_goal_provider%s.json' % season.replace('/', '-'), 'w') as output:
        output.write('[')

        output.write(json.dumps(team_goal))

        output.write(']')
    output.close()

    with open('output/team_partner/team_partner%s.json' % season.replace('/', '-'), 'w') as output:
        output.write('[')

        output.write(json.dumps(team_partner))

        output.write(']')
    output.close()

    with open('output/team_best_partner/team_best_partner%s.json' % season.replace('/', '-'), 'w') as output:
        output.write('[')

        output.write(json.dumps(team_best_partner))

        output.write(']')
    output.close()
