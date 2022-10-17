from oauth2client.service_account import ServiceAccountCredentials
import apiclient
import httplib2
import random
import requests
import json
import yaml
from datetime import datetime, timedelta
from time import sleep
import functools
from .config import CONFIG


def put_vacantion(vacancy_id):
    if bool(CONFIG['allow_messages']):
        return True
    else:
        data = {"billing_type": "package",
                "allow_messages": False}
        req = try_three(requests.put)
        while True:
            r = req(url=f'https://api.avito.ru/job/v1/vacancies/{vacancy_id}', headers=hheaders(), json=data)
            if r.status_code != 204:
                print(r)
                print(r.text)
                sleep(60)
                get_token()
                continue
            if r.status_code == 204:
                return True


def try_three(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseException as r:
            try:
                print(f"Ошибка request{r}")
                sleep(10)
                return func(*args, **kwargs)
            except BaseException as m:
                try:
                    print(f"Ошибка 2 request{m}")
                    sleep(30)
                    return func(*args, **kwargs)
                except BaseException as e:
                    print(f"Ошибка 3 request{e}")
                    return False

    return inner


def quickstart_sheet(spreadsheet_id=CONFIG['spreadsheet_id'], credentials_file=CONFIG['credentials_file'],
                     type_conection='sheets',
                     version_conection='v4'):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_file,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build(type_conection, version_conection, http=httpAuth)
    return spreadsheet_id, service


def grv(value: list) -> str:
    return value[random.randint(0, len(value) - 1)]


def grv2(value: list) -> str:
    r = random.randint(0, len(value))
    return "".join(['<p>' + i + '</p>' + '\n' for i in random.sample(value, r)])


def get_emoji():
    title = ['🔥', '⚡️', '🚚', '🚛']
    bests = ['✅', '✔️', '☑️']
    adress = ['🏢', '🛣', '🤝']

    if random.randint(0, 100) > 60:
        title_em = title[random.randint(0, len(title) - 1)]
        bests_em = bests[random.randint(0, len(bests) - 1)]
        adress_em = adress[random.randint(0, len(adress) - 1)]
        return title_em, bests_em, adress_em, True
    return "", "", "", False


def get_html_strong():
    if random.randint(0, 100) < 60:
        return "<strong>", "</strong>", True
    return "", "", False


def interval_decorator(interval: int):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            print(f'Start {start_time}')
            func(*args, **kwargs)
            end_time = datetime.now()
            print(f'End {end_time}')
            delta = end_time - start_time
            t_t_sleep = interval - int(delta.seconds)
            if t_t_sleep > 0:
                print(f"Сон {t_t_sleep} секунд")
                sleep(t_t_sleep)
            else:
                print(f"Скрипт опоздал на {t_t_sleep} секунд")
            return

        return wrapper

    return decorator


def get_id_vacancy(page: int = 1, id_vacancy: list = None):
    if id_vacancy is None:
        id_vacancy = []
    params = {
        "per_page": 100,
        "page": page,
        "category": 111}
    req = try_three(requests.get)
    while True:
        r = req(url='https://api.avito.ru/core/v1/items', headers=hheaders(), params=params)
        if r.status_code != 200:
            print(r)
            print(r.text)
            sleep(60)
            get_token()
            continue
        elif r.status_code == 200:
            break
    data = json.loads(r.text)
    if data['resources']:
        for i in data['resources']:
            id_vacancy.append(i['id'])
        get_id_vacancy(page + 1, id_vacancy)
    else:
        return id_vacancy
    return id_vacancy


def hheaders():
    with open('./token.yml', 'r', encoding='utf8') as f:
        token = yaml.safe_load(f)['token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    return headers


def get_token():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    params = {'grant_type': 'client_credentials',
              'client_id': CONFIG['client_id'],
              'client_secret': CONFIG['client_secret']}
    reg = try_three(requests.post)
    r = reg(url='https://api.avito.ru/token/', headers=headers, params=params)
    data = json.loads(r.text)
    to_yamal = {'token': data['access_token']}
    with open('token.yml', 'w') as f:
        yaml.dump(to_yamal, f)


def withdraw_vacantion(sheet_name):
    try:
        sheet_values = get_sheet_values(sheet_name)
    except BaseException as r:
        print(r)
        sleep(10)
        sheet_values = get_sheet_values(sheet_name)
    spreadsheet_id, service = quickstart_sheet()
    data = []
    keys = list(sheet_values[0].keys())
    for i, k in enumerate(sheet_values):
        if k[keys[2]] != '':
            try:
                sheet_time = datetime.strptime(k[keys[2]], '%Y.%m.%d %H:%M')
            except BaseException as r:
                sheet_time = datetime.strptime(k[keys[3]], '%Y.%m.%d %H:%M')
            delta = datetime.today() - sheet_time
            delta = int(delta.total_seconds())
            if delta > 345600:
                try:
                    metadata = [i for i in eval(k[keys[4]]).values()]
                except SyntaxError:
                    metadata = []
                if not metadata:
                    sheet_value = ''
                else:
                    sheet_value = [k[keys[0]], k[keys[1]], k[keys[2]], k[keys[3]],
                                   datetime.now().strftime('%Y.%m.%d %H:%M')
                                   ] + metadata
                data.append({
                    'ID': k[keys[1]],
                    'range': sheet_name + '!A' + str(i + 2),
                    'values': [[k[keys[0]], '', '', '', '']],
                    'bad_range': sheet_name + '!D' + str(i + 2),
                    'sheet_value': sheet_value
                }
                )
    try:
        id_v = list(data[0].keys())[0]
    except IndexError:
        return
    stats = get_stats([int(i[id_v]) for i in data])
    for k, v in stats.items():
        for i in data:
            if i[id_v] == str(k):
                if i['sheet_value'] != '':
                    i['sheet_value'] += list(v.values())
    for m in data:
        reg = try_three(requests.put)
        while True:
            r = reg(f"https://api.avito.ru/job/v1/vacancies/archived/{m[id_v]}", headers=hheaders())
            if r.status_code == 204:
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=m['range'],
                    valueInputOption='RAW',
                    body={'values': m['values']
                          }
                ).execute()
                if m['sheet_value'] != '':
                    service.spreadsheets().values().append(
                        spreadsheetId=spreadsheet_id,
                        range=CONFIG['prefix_arh'] + ' ' + sheet_name + '!A1',
                        valueInputOption='RAW',
                        body={'values': [m ['sheet_value']]
                              }
                    ).execute()
                break
            elif r.status_code != 204:
                print(r)
                print(r.text)
                sleep(60)
                get_token()
                continue


def get_sheet_values2(sheet):
    spreadsheet_id, service = quickstart_sheet()
    sheet_values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=sheet + '!A1:Z9999999'
    ).execute()
    keys = sheet_values['values'][0]
    values_dict = {i: [] for i in sheet_values['values'][0]}
    dic_values = []
    for k in sheet_values['values']:
        d = {}
        m = 0
        for i in keys:
            try:
                d.update({i: k[m]})
                m += 1
            except BaseException:
                d.update({i: ''})
                m += 1
        dic_values.append(d)
    dic_values.pop(0)
    for i in values_dict:
        for j in dic_values:
            if j[i] != '':
                values_dict[i].append(j[i])
    return values_dict


def get_sheet_values(sheet):
    spreadsheet_id, service = quickstart_sheet()
    sheet_values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=sheet + '!A1:Z9999999'
    ).execute()
    keys = sheet_values['values'][0]
    dic_values = []
    for k in sheet_values['values']:
        d = {}
        m = 0
        for i in keys:
            try:
                d.update({i: k[m]})
                m += 1
            except BaseException:
                d.update({i: ''})
                m += 1
        dic_values.append(d)
    dic_values.pop(0)
    return dic_values


def get_stats(itemIds):
    stats = {}
    for i in itemIds:
        stats[i] = {
            "views": 0,
            "contacts": 0,
            "favorites": 0,
            "response": 0
        }
    dateFrom = (datetime.today() - timedelta(days=6)).strftime("%Y-%m-%d")
    dateTo = datetime.today().strftime("%Y-%m-%d")
    data = {
        "dateFrom": dateFrom,
        "dateTo": dateTo,
        "fields": [
            "uniqViews", "uniqContacts", "uniqFavorites"
        ],
        "itemIds": itemIds,
        "periodGrouping": "day"
    }
    req = try_three(requests.post)
    while True:
        r = req(url='https://api.avito.ru/stats/v1/accounts/92959008/items', headers=hheaders(), json=data)
        if r.status_code != 200:
            print(r)
            print(r.text)
            sleep(60)
            get_token()
            continue
        items = json.loads(r.text)['result']['items']
        for m in items:
            for i in m['stats']:
                stats[m["itemId"]]["views"] += i['uniqViews']
                stats[m["itemId"]]["contacts"] += i['uniqContacts']
                stats[m["itemId"]]["favorites"] += i['uniqFavorites']
        req = try_three(requests.get)
        while True:
            r = req(url=f'https://api.avito.ru/job/v1/applications/get_ids?updatedAtFrom={dateFrom}',
                    headers=hheaders())
            if r.status_code != 200:
                print(r)
                print(r.text)
                sleep(60)
                get_token()
                continue
            r = json.loads(r.text)
            indeficators_ids = []
            for i in r['applies']:
                indeficators_ids.append(i['id'])
            req = try_three(requests.post)
            data = {
                "ids": indeficators_ids
            }
            sleep(1)
            while True:
                r = req(url='https://api.avito.ru/job/v1/applications/get_by_ids', headers=hheaders(), json=data)
                if r.status_code != 200:
                    print(r)
                    print(r.text)
                    sleep(60)
                    get_token()
                    continue
                r = json.loads(r.text)
                for i in r["applies"]:
                    if i["vacancy_id"] in itemIds:
                        stats[i["vacancy_id"]]['response'] += 1
                break
            break
        break
    return stats


def update_id_and_put(sheet_name):
    sheet_values = get_sheet_values(sheet_name)
    updt_values = {
    }
    for i, k in enumerate(sheet_values):
        if k['ID'] == '' and k['ID_UUID'] != '':
            updt_values[k['ID_UUID']] = str(i + 2)
    if updt_values != {}:
        data = {
            "ids": list(updt_values.keys())
        }
        req = try_three(requests.post)
        while True:
            r = req(url='https://api.avito.ru/job/v2/vacancies/statuses', headers=hheaders(), json=data)
            if r.status_code != 200:
                print(r)
                print(r.text)
                sleep(60)
                get_token()
                continue
            elif r.status_code == 200:
                vacancy_ids = eval(r.text)
                for i in vacancy_ids:
                    try:
                        sleep(10)
                        vacancy_id = i['vacancy']['id']
                        if put_vacantion(vacancy_id):
                            spreadsheet_id, service = quickstart_sheet()
                            service.spreadsheets().values().update(
                                spreadsheetId=spreadsheet_id,
                                range=sheet_name + '!B' + updt_values[i['id']],
                                valueInputOption='RAW',
                                body={'values': [[vacancy_id]]
                                      }
                            ).execute()
                    except KeyError:
                        continue
                return False
    else:
        return True
