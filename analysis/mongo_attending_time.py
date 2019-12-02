import pymongo
import re
import json

connection = pymongo.MongoClient('localhost', 27017)
db = connection['soccer']
table = db['player_all']
club_2015 = db['club2015']
club_2016 = db['club2016']
club_2017 = db['club2017']

seasons = ['15/16', '16/17', '17/18']

player_all = list(table.find())

for season in seasons:
    team_attending = {}
    clubs = []
    if season == '15/16':
        clubs = list(club_2015.find())
    elif season == '16/17':
        clubs = list(club_2016.find())
    elif season == '17/18':
        clubs = list(club_2017.find())

    for club in clubs:
        team_attending[club['club_information']['name']] = {}
        player_list = club['club_information']['detail']
        for player in player_list:
            player_id = player['id']
            name = 'null'
            position = player['position']
            market_value = 0
            minutes_played = 0
            goal = 0
            assist = 0
            conceded_goal = 0
            clean_sheet = 0
            raw_market_value = player['market value'].replace(',', '.')
            # print(raw_market_value)
            num = re.search(r'\d+', raw_market_value)
            unit = re.search(r'[A-Z][a-z]+', raw_market_value)
            if (num is not None) and (unit is not None):
                if unit.group() == 'Mill':
                    market_value = float(num.group()) * 1000000
                elif unit.group() == 'Th':
                    market_value = float(num.group()) * 1000
            for i in player_all:
                if i['player_detail']['id'] == player['id']:
                    name = i['player_detail']['name']
                    if i['player_detail']['perform'] is not None:
                        for s in i['player_detail']['perform']:
                            if s['season'] == season:

                                if len(s['detail']) == 1 and (s['detail'][0] != {}):
                                    minutes_played = s['detail'][0]['minutes played'].replace('.', '').replace("'", '')
                                    if minutes_played == '-':
                                        minutes_played = 0
                                    if (position == 'Goalkeeper') and ('conceded goal' in s['detail'][0]):
                                        conceded_goal = s['detail'][0]['conceded goal'].replace('-', '0')
                                        clean_sheet = s['detail'][0]['clean sheets'].replace('-', '0')
                                    else:
                                        goal = s['detail'][0]['goal'].replace('-', '0')
                                        assist = s['detail'][0]['goal'].replace('-', '0')
            if position == 'Goalkeeper':
                team_attending[club['club_information']['name']][name] = {'position': position, 'market_value': market_value, 'minutes_played': minutes_played, 'conceded_goal': conceded_goal, 'clean_sheet': clean_sheet}
            else:
                team_attending[club['club_information']['name']][name] = {'position': position, 'market_value': market_value, 'minutes_played': minutes_played, 'goal': goal, 'assist': assist}
            if (market_value == 0) and (minutes_played == 0):
                print('no data', season, player_id, name)

    with open('output/team_attending/team_attending%s.json' % season.replace('/', '-'), 'w') as output:
        output.write('[')

        output.write(json.dumps(team_attending))

        output.write(']')
    output.close()


    '''for i in players:
        if i['player_detail']['id'] == given_player_id:
            if i['player_detail']['perform'] is not None:
                for s in i['player_detail']['perform']:
                    if (s['season'] == given_season) and (len(s['detail']) == 1):
                        raw_market_value = s['market_value'].replace(',', '')
                        num = re.search(r'\d+', raw_market_value).group()
                        unit = re.search(r'[A-Z][a-z]+', raw_market_value).group()
                        if unit is not None:
                            if unit == 'Mill':
                                market_value = int(num) * 1000000
                            elif unit == 'Th':
                                market_value = int(num) * 1000
                        minutes_played = s['detail'][0]['minutes played'].replace('.', '').replace("'", '')

    print(market_value, minutes_played)'''