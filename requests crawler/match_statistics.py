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


def page_jump(page):
    page_soup = parse_page(page)
    buttons = page_soup.find_all('a', {'class': 'megamenu', 'name': 'SubNavi'})

    statistics_page = ''

    for i in range(0, len(buttons)):
        if buttons[i].text == 'Statistics':
            statistics_page = domain + buttons[i]['href']

    return statistics_page


def get_statistics(page):
    page_soup = parse_page(page)
    raw_date = page_soup.find_all('p', {'class': 'sb-datum hide-for-small'})
    stat = page_soup.find_all('div', {'class': 'sb-statistik-zahl'})

    t = re.compile('<[^>]+>')
    date = t.sub('', str(raw_date)).split('|')

    stat_text = []

    if len(stat) == 16:
        for s in stat:
            stat_text.append(s.text)
    else:
        for i in range(0, 16):
            stat_text.append(' ')

    return [date[1].strip(), stat_text]


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
        statistics_url_list = []
        date_list = []
        home_list = []
        away_list = []

        home_total_shots = []
        away_total_shots = []
        home_shots_on_target = []
        away_shots_on_target = []
        home_shots_off_target = []
        away_shots_off_target = []
        home_shots_saved = []
        away_shots_saved = []
        home_corners = []
        away_corners = []
        home_free_kicks = []
        away_free_kicks = []
        home_fouls = []
        away_fouls = []
        home_offsides = []
        away_offsides = []

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
            statistics_url = page_jump(match_url_list[i])
            statistics_url_list.append(statistics_url)
            output = get_statistics(statistics_url)

            date_list.append(output[0])
            statistics = output[1]

            home_total_shots.append(statistics[0])
            away_total_shots.append(statistics[1])
            home_shots_on_target.append(statistics[2])
            away_shots_on_target.append(statistics[3])
            home_shots_off_target.append(statistics[4])
            away_shots_off_target.append(statistics[5])
            home_shots_saved.append(statistics[6])
            away_shots_saved.append(statistics[7])
            home_corners.append(statistics[8])
            away_corners.append(statistics[9])
            home_free_kicks.append(statistics[10])
            away_free_kicks.append(statistics[11])
            home_fouls.append(statistics[12])
            away_fouls.append(statistics[13])
            home_offsides.append(statistics[14])
            away_offsides.append(statistics[15])

        with open('data/%s%s-statistics.json' % (year[yearNo], league[leagueNo]), 'w') as data:

            data.write('[')

            for i in range(0, len(results)):
                row = {'Statistics URL': statistics_url_list[i], 'Date': date_list[i], 'Home': home_list[i],
                       'Away': away_list[i], 'Home Total Shots': home_total_shots[i],
                       'Away Total Shots': away_total_shots[i], 'Home Shots On Target': home_shots_on_target[i],
                       'Away Shots On Target': away_shots_on_target[i],
                       'Home Shots Off Target': home_shots_off_target[i],
                       'Away Shots Off Target': away_shots_off_target[i], 'Home Shots Saved': home_shots_saved[i],
                       'Away Shots Saved': away_shots_saved[i], 'Home Corners': home_corners[i],
                       'Away Corners': away_corners[i], 'Home Free Kicks': home_free_kicks[i],
                       'Away Free Kicks': away_free_kicks[i], 'Home Fouls': home_fouls[i], 'Away Fouls': away_fouls[i],
                       'Home Offsides': home_offsides[i], 'Away Offsides': away_offsides[i]}
                data.write(json.dumps(row))

                if i < len(results) - 1:
                    data.write(',\n')

            data.write(']')

        data.close()
        print(year[yearNo] + league[leagueNo] + " completed")
