import json
import re
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

league = ['GER', 'ENG', 'ESP', 'ITA', 'FRA']
year = ['2015', '2016', '2017']

domain = 'https://www.transfermarkt.com'


def parse_page(current_page):
    page_tree = requests.get(current_page, headers=headers)
    page_soup = BeautifulSoup(page_tree.content, 'html.parser')

    return page_soup


def get_detail(page, total):
    page_soup = parse_page(page)
    raw_date = page_soup.find_all('p', {'class': 'sb-datum hide-for-small'})
    starters = page_soup.find_all('span', {'class': 'aufstellung-rueckennummer-name'}, id=True)
    substitutes = page_soup.find_all('a', {'class': 'spielprofil_tooltip'}, id=True)
    tables = page_soup.find_all('table', {'class': 'ersatzbank'})
    managers = page_soup.find_all('a', id=True, href=True)
    goals_raw = page_soup.find_all('div', {'sb-aktion-aktion'})

    t = re.compile('<[^>]+>')
    date = t.sub('', str(raw_date)).split('|')

    home_starters = []
    home_substitutes = []
    away_starters = []
    away_substitutes = []
    home_manager_name = ''
    away_manager_name = ''
    home_manager = {}
    away_manager = {}

    if len(tables) == 2:
        for i in range(0, len(starters)):
            if i < len(starters) / 2:
                home_starters.append(starters[i]['id'])
            else:
                away_starters.append(starters[i]['id'])

        home_table = t.sub('', str(tables[0])).split()
        away_table = t.sub('', str(tables[1])).split()

        home_sub_num = 0
        for a in home_table:
            if a.isdigit():
                home_sub_num += 1

        processed_sub = []
        for i in substitutes:
            if i.text.strip() != '':
                processed_sub.append(i['id'])

        for i in range(0, len(processed_sub)):
            if i < int(home_sub_num):
                home_substitutes.append(processed_sub[i])
            else:
                away_substitutes.append(processed_sub[i])

        for m in range(0, len(home_table)):
            if home_table[m] == 'Manager:':
                for hm in range(m + 1, len(home_table)):
                    home_manager_name += home_table[hm] + ' '
                home_manager['Name'] = home_manager_name.strip()

        for m in range(0, len(away_table)):
            if away_table[m] == 'Manager:':
                for am in range(m + 1, len(away_table)):
                    away_manager_name += away_table[am] + ' '
                away_manager['Name'] = away_manager_name.strip()

        for m in managers:
            if m.text == home_manager_name.strip():
                home_manager['URL'] = domain + m['href']
                manager_id = re.search(r'\d+', m['href'])
                if manager_id is not None:
                    home_manager['ID'] = manager_id.group()
                else:
                    home_manager['ID'] = ''
                    print('home manager:', home_manager['URL'])
            elif m.text == away_manager_name.strip():
                away_manager['URL'] = domain + m['href']
                manager_id = re.search(r'\d+', m['href'])
                if manager_id is not None:
                    away_manager['ID'] = manager_id.group()
                else:
                    away_manager['ID'] = ''
                    print('away manager:', away_manager['URL'])

    goals = []
    if len(goals_raw) < total:
        print('goal:', page)
    else:
        for i in range(0, total):
            goals_processed = goals_raw[i].text.split()
            goal = ''
            for g in goals_processed:
                goal += g + ' '
            goals.append(goal)

    return [date[1].strip(), home_starters, away_starters, home_substitutes, away_substitutes, home_manager,
            away_manager, goals]


for yearNo in range(0, len(year)):

    page_list = ['https://www.transfermarkt.com/bundesliga/gesamtspielplan/wettbewerb/L1?saison_'
                 'id=%s&spieltagVon=1&spieltagBis=34' % year[yearNo],
                 'https://www.transfermarkt.com/premier-league/gesamtspielplan/wettbewerb/GB1?saison_'
                 'id=%s&spieltagVon=1&spieltagBis=38' % year[yearNo],
                 'https://www.transfermarkt.com/laliga/gesamtspielplan/wettbewerb/ES1?saison_'
                 'id=%s&spieltagVon=1&spieltagBis=38' % year[yearNo],
                 'https://www.transfermarkt.com/serie-a/gesamtspielplan/wettbewerb/IT1?saison_'
                 'id=%s&spieltagVon=1&spieltagBis=38' % year[yearNo],
                 'https://www.transfermarkt.com/ligue-1/gesamtspielplan/wettbewerb/FR1?saison_'
                 'id=%s&spieltagVon=1&spieltagBis=38' % year[yearNo]]

    for leagueNo in range(0, len(league)):

        soup = parse_page(page_list[leagueNo])
        teams = soup.find_all('a', {'class': 'vereinprofil_tooltip'}, id=True)
        results = soup.find_all('a', {'class': 'ergebnis-link'}, href=True, id=True)

        match_url_list = []
        date_list = []
        home_list = []
        away_list = []
        home_starter_list = []
        away_starter_list = []
        home_substitute_list = []
        away_substitute_list = []
        home_manager_list = []
        away_manager_list = []
        goal_list = []

        team_name = []
        team_id = []
        for i in teams:
            if i.text.strip() != '':
                team_name.append(i.text)
                team_id.append(i['id'])

        for i in range(0, len(team_id)):
            if i % 2 == 0:
                home_list.append({'Team Name': team_name[i], 'Team ID': team_id[i]})
            elif i % 2 == 1:
                away_list.append({'Team Name': team_name[i], 'Team ID': team_id[i]})

        for i in range(0, len(results)):
            match_url_list.append(domain + results[i]['href'])
            each_goal = results[i].text.split(':')
            total_goal = int(each_goal[0]) + int(each_goal[1])
            details = get_detail(match_url_list[i], total_goal)
            date_list.append(details[0])
            home_starter_list.append(details[1])
            away_starter_list.append(details[2])
            home_substitute_list.append(details[3])
            away_substitute_list.append(details[4])
            home_manager_list.append(details[5])
            away_manager_list.append(details[6])
            goal_list.append(details[7])

        with open('data/%s%s-detail.json' % (year[yearNo], league[leagueNo]), 'w') as data:

            data.write('[')

            for i in range(0, len(results)):
                row = {'Match URL': match_url_list[i], 'Date': date_list[i], 'Home': home_list[i], 'Away': away_list[i],
                       'Result': results[i].text, 'Home Starters': home_starter_list[i],
                       'Home Substitutes': home_substitute_list[i], 'Home Manager': home_manager_list[i],
                       'Away Starters': away_starter_list[i], 'Away Substitutes': away_substitute_list[i],
                       'Away Manager': away_manager_list[i], 'Goals': goal_list[i]}
                data.write(json.dumps(row))

                if i < len(results) - 1:
                    data.write(',\n')

            data.write(']')

        data.close()
        print(year[yearNo] + league[leagueNo] + " completed")
