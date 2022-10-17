import requests
from partools import get_sheet_values, CONFIG, quickstart_sheet, interval_decorator, get_token, withdraw_vacantion, \
    try_three, update_id_and_put, hheaders
from Vacancy import Vacancy
import random
import json
import logging
from datetime import datetime
from time import sleep


def make_vacancy(sity: bool, sheet_name):
    free_geo = []
    sheet_values = get_sheet_values(sheet_name)
    values = list(sheet_values[0].keys())
    for i, k in enumerate(sheet_values):
        if k[values[1]] == '':
            free_geo.append({
                k[values[0]]: i + 2
            })
    free_geo = random.sample(free_geo, 1)[0]
    free_geo_key = list(free_geo.keys())[0]
    print(f'Локация {free_geo_key}')
    vacancy = Vacancy(sity=sity, geo=free_geo_key)
    params, meta_data = vacancy.get_json()
    req = try_three(requests.post)
    while True:
        r = req(url='https://api.avito.ru/job/v2/vacancies', headers=hheaders(), json=params)
        if r.status_code != 202:
            print(r)
            print(r.text)
            sleep(60)
            get_token()
            continue
        elif r.status_code == 202:
            vacancy_id_uuid = json.loads(r.text)['id']
            data = [[free_geo_key, '', vacancy_id_uuid, datetime.now().strftime('%Y.%m.%d %H:%M'), str(meta_data)]]
            spreadsheet_id, service = quickstart_sheet()
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=sheet_name + '!A' + str(free_geo[free_geo_key]),
                valueInputOption='RAW',
                body={'values': data
                      }
            ).execute()
            break
    sleep(10)
    for i in range(3):
        if update_id_and_put(sheet_name):
            return
        else:
            sleep(200)
    return


def looping_job():
    get_token()
    for i in range(30):
        make_vacancy_x2()
        if datetime.today().strftime("%H:%M") > '22:00':
            print('Наступает ночь')
            break


@interval_decorator(interval=1700)
def make_vacancy_x2():
    print('Архивация вакансий Москва')
    withdraw_vacantion(CONFIG['sheet_name_vacancy'])
    print('Публикация вакансии Москва')
    make_vacancy(True, CONFIG['sheet_name_vacancy'])
    sleep(500)
    print('Архивация вакансий МО')
    withdraw_vacantion(CONFIG['sheet_name_vacancy_mo'])
    print('Публикация вакансии МО')
    make_vacancy(False, CONFIG['sheet_name_vacancy_mo'])


if __name__ == "__main__":
    logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG, filename=u'log.log')
    while True:
        if datetime.today().strftime("%H:%M") > '08:00':
            looping_job()
            sleep(25000)
        else:
            sleep(10)
