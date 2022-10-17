from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import chromedriver_autoinstaller
import json
from time import sleep


def check_exists_by_xpath(driver, path):
    try:
        driver.find_element(By.XPATH, path)
    except NoSuchElementException:
        return False
    return True


def get_cordinats(addresses: list) -> dict:
    """
    Получает кординаты всех адрессов в списке
    Возвразщет словарь c кординатами,
    Если исклбчение то {Адрес':['','']}
    :param addresses: ['Адрес','Адрес',...]
    :return: {'Адрес':[Широта -> float, Долгота -> float];...}
    """
    driver = webdriver.Chrome(executable_path=chromedriver_autoinstaller.install())
    add_w_cordinats = {}
    for addres in addresses:
        driver.get('https://yandex.ru/maps/')
        sleep(2)
        if check_exists_by_xpath(driver,
                                 '/html/body/div[1]/div[2]/div[2]/header/div/div/div/form/div[2]/div/span/span/input'):
            driver.find_element(By.XPATH,
                                '/html/body/div[1]/div[2]/div[2]/header/div/div/div/form/div[2]/div/span/span/input').send_keys(
                addres)
        else:
            driver.find_element(By.XPATH,
                                '/html/body/div[1]/div[2]/div[1]/header/div/div/div/form/div[2]/div/span/span/input').send_keys(
                addres)
        sleep(1)
        if check_exists_by_xpath(driver, '/html/body/div[1]/div[2]/div[2]/header/div/div/div/form/div[3]/button'):
            driver.find_element(By.XPATH,
                                '/html/body/div[1]/div[2]/div[2]/header/div/div/div/form/div[3]/button').click()
        else:
            driver.find_element(By.XPATH,
                                '/html/body/div[1]/div[2]/div[1]/header/div/div/div/form/div[3]/button').click()
        sleep(3)
        cordinats = []
        for req in driver.requests:
            if req.url[:43] == 'https://yandex.ru/maps/api/search?add_type=':
                try:
                    body = decode(req.response.body, req.response.headers.get('Content-Encoding', 'identity'))
                except BaseException as r:
                    sleep(5)
                    body = decode(req.response.body, req.response.headers.get('Content-Encoding', 'identity'))
                body = json.loads(str(body.decode('UTF-8')))
                try:
                    list_cor = body['data']['exactResult']['displayCoordinates']
                    cordinats.append([list_cor[1], list_cor[0]])
                except KeyError:
                    cordinats.append(['', ''])
        add_w_cordinats[addres] = cordinats[-1]
    driver.close()
    return add_w_cordinats


if __name__ == '__main__':
    addresses = ['Москва']
    add_w_cordinats = get_cordinats(addresses)
    print(add_w_cordinats)
