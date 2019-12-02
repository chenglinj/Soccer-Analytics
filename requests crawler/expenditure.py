import json
import re
import requests
from bs4 import BeautifulSoup


# parse the target page
def parse_page(current_page):
    page_tree = requests.get(current_page, headers=headers)
    page_soup = BeautifulSoup(page_tree.content, 'html.parser')

    return page_soup


# check whether the league of the club is in our scraping range
def check_league(page_soup):
    odd = page_soup.find_all('tr', {'class': 'odd'})
    even = page_soup.find_all('tr', {'class': 'even'})
    table = []
    for i in range(0, len(even)):
        table.append(odd[i].text.strip())
        table.append(even[i].text.strip())
    table.append(odd[-1].text.strip())

    first_list = []
    for i in range(0, len(table)):
        if (re.search(r'Premier League 2 |U18 Premier League|LaLiga2|2\.Bundesliga|Junioren Bundesliga', table[i]) is None) and\
                (re.search(r'Bundesliga|Premier League|LaLiga|Serie A|Ligue 1', table[i]) is not None):
            first_list.append(i)

    return first_list


# get the target data from the parsed page
def get_page(page):
    soup = parse_page(page)
    raw_club = soup.find_all('a', {'class': 'vereinprofil_tooltip'}, href=True)
    expend = soup.find_all('td', {'class': 'rechts hauptlink redtext'})
    income = soup.find_all('td', {'class': 'rechts hauptlink greentext'})
    in_out = soup.find_all('td', {'class': 'zentriert'})
    balance = soup.find_all('td', {'class': 'rechts hauptlink'})

    club = []
    for i in raw_club:
        if i.text != '':
            club.append(i)

    in_list = []
    out_list = []
    for i in range(0, len(in_out)):
        if (i - 2) % 4 == 0:
            in_list.append(in_out[i].text)
        elif (i - 3) % 4 == 0:
            out_list.append(in_out[i].text)

    rows = []

    first_tier_list = check_league(soup)
    for i in first_tier_list:
        rows.append({club[i].text: {'id': club[i]['id'], 'expenditure': expend[i].text, 'arrival': in_list[i], 'income':
                    income[i].text, 'departure': out_list[i], 'balance': balance[i].text}})

    return rows


# get the x th page of the data
def get_page_x(page, x):
    soup = parse_page(page)
    button = soup.find_all('li', {'class': 'page'})
    page_x = ''
    for b in button:
        if b.text == str(x):
            page_x = domain + re.search(r'/transfers.+page/%s' % str(x), str(b)).group()
    return page_x


headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

domain = 'https://www.transfermarkt.com'

first_tier = ['Bundesliga', 'Premier League', 'LaLiga', 'Serie A', 'Ligue 1']

year = ['2015', '2016', '2017']

for yearNo in year:
    pages = ['https://www.transfermarkt.com/transfers/einnahmenausgaben/statistik/a/ids/a/sa//saison_id/%s'
             '/saison_id_bis/%s/land_id/40/nat/0/pos//w_s//intern/0/plus/1' % (yearNo, yearNo),
             'https://www.transfermarkt.com/transfers/einnahmenausgaben/statistik/a/ids/a/sa//saison_id/%s'
             '/saison_id_bis/%s/land_id/189/nat/0/pos//w_s//intern/0/plus/1' % (yearNo, yearNo),
             'https://www.transfermarkt.com/transfers/einnahmenausgaben/statistik/a/ids/a/sa//saison_id/%s'
             '/saison_id_bis/%s/land_id/157/nat/0/pos//w_s//intern/0/plus/1' % (yearNo, yearNo),
             'https://www.transfermarkt.com/transfers/einnahmenausgaben/statistik/a/ids/a/sa//saison_id/%s'
             '/saison_id_bis/%s/land_id/75/nat/0/pos//w_s//intern/0/plus/1' % (yearNo, yearNo),
             'https://www.transfermarkt.com/transfers/einnahmenausgaben/statistik/a/ids/a/sa//saison_id/%s'
             '/saison_id_bis/%s/land_id/50/nat/0/pos//w_s//intern/0/plus/1' % (yearNo, yearNo)]

    for leagueNo in range(0, len(first_tier)):

        page1 = get_page(pages[leagueNo])
        page2 = get_page(get_page_x(pages[leagueNo], 2))
        page1.extend(page2)

        with open('output/expenditure/%s%s-detail.json' % (yearNo, first_tier[leagueNo]), 'w') as output:
            output.write('[')

            for i in range(0, len(page1)):
                output.write(json.dumps(page1[i]))
                if i < len(page1)-1:
                    output.write(',\n')

            if first_tier[leagueNo] == 'Premier League':
                if yearNo == '2015':
                    output.write(',\n')
                    output.write(json.dumps({'Swansea City': {'id': '2288', 'expenditure': '21,81 Mill. €', 'arrival': '20', 'income':
                                            '16,81 Mill. €', 'departure': '24', 'balance': '-5,00 Mill. €'}}))
                elif yearNo == '2016':
                    output.write(',\n')
                    output.write(json.dumps({'Swansea City': {'id': '2288', 'expenditure': '58,20 Mill. €', 'arrival': '18', 'income':
                                            '48,60 Mill. €', 'departure': '18', 'balance': '-9,60 Mill. €'}}))
                elif yearNo == '2017':
                    output.write(',\n')
                    output.write(json.dumps({'Swansea City': {'id': '2288', 'expenditure': '73,39 Mill. €', 'arrival': '18', 'income':
                                            '81,10 Mill. €', 'departure': '24', 'balance': '7,71 Mill. €'}}))

            elif first_tier[leagueNo] == 'LaLiga':
                if yearNo == '2015':
                    output.write(',\n')
                    output.write(json.dumps({'Sporting Gijón': {'id': '2448', 'expenditure': '0', 'arrival': '8', 'income':
                                            '0', 'departure': '7', 'balance': '0'}}))
                elif yearNo == '2016':
                    output.write(',\n')
                    output.write(json.dumps({'Athletic Bilbao': {'id': '621', 'expenditure': '0', 'arrival': '9', 'income':
                                            '0', 'departure': '14', 'balance': '0'}}))

            elif first_tier[leagueNo] == 'Ligue 1':
                if yearNo == '2015':
                    output.write(',\n')
                    output.write(json.dumps({'AS Monaco': {'id': '162', 'expenditure': '101,06 Mill. €', 'arrival': '21', 'income':
                                            '185,15 Mill. €', 'departure': '26', 'balance': '84,09 Mill. €'}}))
                    output.write(',\n')
                    output.write(json.dumps({'SCO Angers': {'id': '1420', 'expenditure': '0', 'arrival': '19', 'income':
                                            '5,90 Mill. €', 'departure': '20', 'balance': '5,90 Mill. €'}}))
                    output.write(',\n')
                    output.write(json.dumps({'SC Bastia': {'id': '595', 'expenditure': '0', 'arrival': '12', 'income':
                                             '1,70 Mill. €', 'departure': '12', 'balance': '1,70 Mill. €'}}))
                elif yearNo == '2016':
                    output.write(',\n')
                    output.write(json.dumps({'AS Monaco': {'id': '162', 'expenditure': '50,50 Mill. €', 'arrival': '12', 'income':
                                            '18,45 Mill. €', 'departure': '25', 'balance': '-32,05 Mill. €'}}))
                    output.write(',\n')
                    output.write(json.dumps({'EA Guingamp': {'id': '855', 'expenditure': '0', 'arrival': '12', 'income':
                                            '2,50 Mill. €', 'departure': '15', 'balance': '2,50 Mill. €'}}))
                elif yearNo == '2017':
                    output.write(',\n')
                    output.write(json.dumps({'AS Monaco': {'id': '162', 'expenditure': '123,60 Mill. €', 'arrival': '16', 'income':
                                            '244,50 Mill. €', 'departure': '23', 'balance': '120,90 Mill. €'}}))
                    output.write(',\n')
                    output.write(json.dumps({'ES Troyes AC': {'id': '1095', 'expenditure': '0', 'arrival': '9', 'income':
                                            '0', 'departure': '11', 'balance': '0'}}))

            output.write(']')
        output.close()

        print(len(page1), len(page2), yearNo, first_tier[leagueNo], pages[leagueNo])
