import pymongo
import json
import re

connection = pymongo.MongoClient('localhost', 27017)
db = connection['soccer']
table = db['player_all']
club_2015 = db['club2015']
club_2016 = db['club2016']
club_2017 = db['club2017']

seasons = ['15/16', '16/17', '17/18']

player_all = list(table.find())

for season in seasons:
    team_statistics = {}
    average = {}
    clubs = []
    if season == '15/16':
        clubs = list(club_2015.find())
    elif season == '16/17':
        clubs = list(club_2016.find())
    elif season == '17/18':
        clubs = list(club_2017.find())

    for club in clubs:
        player_list = club['club_information']['detail']
        for player in player_list:
            for i in player_all:
                if i['player_detail']['id'] == player['id']:
                    high = 0
                    goal = 0
                    assist = 0
                    conceded_goal = 0
                    yellow_card = 0
                    red_card = 0
                    market_value = 0
                    raw_market_value = player['market value'].replace(',', '.')
                    num = re.search(r'[\d.]+', raw_market_value)
                    unit = re.search(r'[A-Z][a-z]+', raw_market_value)
                    if (num is not None) and (unit is not None):
                        if unit.group() == 'Mill':
                            market_value = float(num.group()) * 1000000
                        elif unit.group() == 'Th':
                            market_value = float(num.group()) * 1000
                    if i['player_detail']['detail']['height'] != 'null':
                        high = float(i['player_detail']['detail']['height'].replace(',', '.').replace('m', ''))
                    if i['player_detail']['perform'] is not None:
                        for s in i['player_detail']['perform']:
                            if (s['season'] == season) and (s['detail'][0] != {}):
                                if s['detail'][0]['league'] == 'Premier League':
                                    goal = int(s['detail'][0]['goal'].replace('-', '0'))
                                    if 'assist' in s['detail'][0]:
                                        assist = int(s['detail'][0]['assist'].replace('-', '0'))
                                    elif 'conceded goal' in s['detail'][0]:
                                        conceded_goal = int(s['detail'][0]['conceded goal'].replace('-', '0'))
                                    yellow_card = int(s['detail'][0]['yellow_card'].replace('-', '0'))
                                    red_card = int(s['detail'][0]['red_card'].replace('-', '0'))
                    if club['club_information']['name'] in team_statistics:
                        for k, v in team_statistics[club['club_information']['name']]['tallest'].items():
                            if high > v['height']:
                                team_statistics[club['club_information']['name']]['tallest'] =\
                                    {i['player_detail']['id']: {'name': i['player_detail']['name'], 'height': high}}
                                break
                            elif high == v['height']:
                                team_statistics[club['club_information']['name']]['tallest'][i['player_detail']['id']]\
                                    = {'name': i['player_detail']['name'], 'height': high}
                                break
                        for k, v in team_statistics[club['club_information']['name']]['shortest'].items():
                            if high < v['height'] and high != 0:
                                team_statistics[club['club_information']['name']]['shortest'] =\
                                    {i['player_detail']['id']: {'name': i['player_detail']['name'], 'height': high}}
                                break
                            elif high == v['height'] and high != 0:
                                team_statistics[club['club_information']['name']]['shortest'][i['player_detail']['id']]\
                                    = {'name': i['player_detail']['name'], 'height': high}
                                break
                        for k, v in team_statistics[club['club_information']['name']]['top_scorer'].items():
                            if goal > v['goal']:
                                team_statistics[club['club_information']['name']]['top_scorer'] =\
                                    {i['player_detail']['id']: {'name': i['player_detail']['name'], 'goal': goal}}
                                break
                            elif goal == v['goal']:
                                team_statistics[club['club_information']['name']]['top_scorer'][i['player_detail']['id']] = \
                                    {'name': i['player_detail']['name'], 'goal': goal}
                                break
                        for k, v in team_statistics[club['club_information']['name']]['top_assister'].items():
                            if assist > v['assist']:
                                team_statistics[club['club_information']['name']]['top_assister'] =\
                                    {i['player_detail']['id']: {'name': i['player_detail']['name'], 'assist': assist}}
                                break
                            elif assist == v['assist']:
                                team_statistics[club['club_information']['name']]['top_assister'][i['player_detail']['id']] = \
                                    {'name': i['player_detail']['name'], 'assist': assist}
                                break
                        for k, v in team_statistics[club['club_information']['name']]['most_yellow'].items():
                            if yellow_card > v['num']:
                                team_statistics[club['club_information']['name']]['most_yellow'] =\
                                    {i['player_detail']['id']: {'name': i['player_detail']['name'], 'num': yellow_card}}
                                break
                            elif yellow_card == v['num'] and yellow_card != 0:
                                team_statistics[club['club_information']['name']]['most_yellow'][i['player_detail']['id']] = \
                                    {'name': i['player_detail']['name'], 'num': yellow_card}
                                break
                        for k, v in team_statistics[club['club_information']['name']]['most_red'].items():
                            if red_card > v['num']:
                                team_statistics[club['club_information']['name']]['most_red'] =\
                                    {i['player_detail']['id']: {'name': i['player_detail']['name'], 'num': red_card}}
                                break
                            elif red_card == v['num'] and red_card != 0:
                                team_statistics[club['club_information']['name']]['most_red'][i['player_detail']['id']] = \
                                    {'name': i['player_detail']['name'], 'num': red_card}
                                break
                        team_statistics[club['club_information']['name']]['total_goal'] += goal
                        team_statistics[club['club_information']['name']]['total_assist'] += assist
                        team_statistics[club['club_information']['name']]['conceded_goal'] += conceded_goal
                        team_statistics[club['club_information']['name']]['total_market_value'] += market_value
                        average[club['club_information']['name']]['total_height'] += high
                        average[club['club_information']['name']]['count'] += 1
                    else:
                        team_statistics[club['club_information']['name']] = {}
                        team_statistics[club['club_information']['name']]['tallest'] = \
                            {i['player_detail']['id']: {'name': i['player_detail']['name'], 'height': high}}
                        if high != 0:
                            team_statistics[club['club_information']['name']]['shortest'] = \
                                {i['player_detail']['id']: {'name': i['player_detail']['name'], 'height': high}}
                        else:
                            team_statistics[club['club_information']['name']]['shortest'] = \
                                {i['player_detail']['id']: {'name': i['player_detail']['name'], 'height': 3}}
                        team_statistics[club['club_information']['name']]['top_scorer'] = \
                            {i['player_detail']['id']: {'name': i['player_detail']['name'], 'goal': goal}}
                        team_statistics[club['club_information']['name']]['top_assister'] = \
                            {i['player_detail']['id']: {'name': i['player_detail']['name'], 'assist': assist}}
                        if yellow_card != 0:
                            team_statistics[club['club_information']['name']]['most_yellow'] = \
                                {i['player_detail']['id']: {'name': i['player_detail']['name'], 'num': yellow_card}}
                        else:
                            team_statistics[club['club_information']['name']]['most_yellow'] = \
                                {'null': {'name': 'null', 'num': 0}}
                        if red_card != 0:
                            team_statistics[club['club_information']['name']]['most_red'] = \
                                {i['player_detail']['id']: {'name': i['player_detail']['name'], 'num': red_card}}
                        else:
                            team_statistics[club['club_information']['name']]['most_red'] = \
                                {'null': {'name': 'null', 'num': 0}}
                        team_statistics[club['club_information']['name']]['total_goal'] = goal
                        team_statistics[club['club_information']['name']]['total_assist'] = assist
                        team_statistics[club['club_information']['name']]['conceded_goal'] = conceded_goal
                        team_statistics[club['club_information']['name']]['total_market_value'] = market_value
                        average[club['club_information']['name']] = {}
                        average[club['club_information']['name']]['total_height'] = high
                        average[club['club_information']['name']]['count'] = 1

    for team in team_statistics:
        team_statistics[team]['average_height'] = round(average[team]['total_height'] / average[team]['count'], 2)

    with open('output/team_stat/team_stat%s.json' % season.replace('/', '-'), 'w') as output:
        output.write('[')

        output.write(json.dumps(team_statistics))

        output.write(']')
    output.close()


'''for i in players:
    if i['player_detail']['perform'] is not None:
        for s in i['player_detail']['perform']:
            if (s['season'] == given_season) and (len(s['detail']) == 1) \
                    and (s['detail'][0]['league'] == 'Premier League'):
                if i['player_detail']['detail']['height'] != 'null':
                    high = float(i['player_detail']['detail']['height'].replace(',', '.').replace('m', ''))

                    if s['club_name'] in average:
                        average[s['club_name']]['total'] += high
                        average[s['club_name']]['count'] += 1
                    else:
                        average[s['club_name']] = {}
                        average[s['club_name']]['total'] = high
                        average[s['club_name']]['count'] = 1

                    if s['club_name'] in height:
                        for p, d in height[s['club_name']]['highest'].items():
                            if high > d['height']:
                                height[s['club_name']]['highest'] =\
                                    {i['player_detail']['name']: {'id': i['player_detail']['id'],
                                     'height': high, 'citizenship': i['player_detail']['detail']['citizenship']}}
                                break
                            elif high == d['height']:
                                height[s['club_name']]['highest'][i['player_detail']['name']] = \
                                    {'id': i['player_detail']['id'],
                                     'height': high, 'citizenship': i['player_detail']['detail']['citizenship']}
                                break
                        for p, d in height[s['club_name']]['lowest'].items():
                            if high < d['height']:
                                height[s['club_name']]['lowest'] = \
                                    {i['player_detail']['name']: {'id': i['player_detail']['id'],
                                     'height': high, 'citizenship': i['player_detail']['detail']['citizenship']}}
                                break
                            elif high == d['height']:
                                height[s['club_name']]['lowest'][i['player_detail']['name']] = \
                                    {'id': i['player_detail']['id'],
                                     'height': high, 'citizenship': i['player_detail']['detail']['citizenship']}
                                break

                        height[s['club_name']]['total_goal'] += int(s['detail'][0]['goal'].replace('-', '0'))
                        # height[s['club_name']]['total_assist'] += s['detail'][0]['assistent']
                    else:
                        height[s['club_name']] = {}
                        height[s['club_name']]['highest'] = \
                            {i['player_detail']['name']: {'id': i['player_detail']['id'],
                             'height': high, 'citizenship': i['player_detail']['detail']['citizenship']}}
                        height[s['club_name']]['lowest'] = \
                            {i['player_detail']['name']: {'id': i['player_detail']['id'],
                             'height': high, 'citizenship': i['player_detail']['detail']['citizenship']}}

                        height[s['club_name']]['total_goal'] = int(s['detail'][0]['goal'].replace('-', '0'))
                        # height[s['club_name']]['total_assist'] = s['detail'][0]['assistent']

for club in height:
    height[club]['average_height'] = round(average[club]['total'] / average[club]['count'], 2)
    if 'total' not in league:
        league['total'] = average[club]['total']
        league['count'] = average[club]['count']
    else:
        league['total'] += average[club]['total']
        league['count'] += average[club]['count']
    if 'highest' not in league:
        league['highest'] = height[club]['highest']
        league['lowest'] = height[club]['lowest']
    else:
        for h in height[club]['highest']:
            for hl in league['highest']:
                if height[club]['highest'][h]['height'] > league['highest'][hl]['height']:
                    league['highest'] = height[club]['highest']
                    break
                elif height[club]['highest'][h]['height'] == league['highest'][hl]['height']:
                    league['highest'][h] = height[club]['highest'][h]
                    break

league['average'] = round(league['total'] / league['count'], 2)

if given_club == 'whole_league':
    print(league)
else:
    print(height[given_club])'''
