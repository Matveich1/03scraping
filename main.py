import requests
import time
import json
from bs4 import BeautifulSoup
from fake_headers import Headers
from unicodedata import normalize
from progress.bar import ChargingBar

info = []

url = 'https://spb.hh.ru/search/vacancy?text=Django+Flask&salary=&ored_clusters=true&area=2&area=1&page=0'


def headers():
    return Headers(browser='chrome', os='win').generate()


def get_last_page():
    response = requests.get(url, headers=headers())
    soup = BeautifulSoup(response.text, 'lxml')
    last_page = int(soup.find('div', class_='pager').find_all(
        'a', class_='bloko-button')[-2].text)
    return last_page


def get_info():
    response = requests.get(url, headers=headers())
    soup = BeautifulSoup(response.text, 'lxml')
    for page in range(get_last_page()):
        bar = ChargingBar(
            f'Processing: page {page + 1} of {get_last_page()}', max=10)
        for i in range(10):
            response = requests.get(f'{url}&page={page}', headers=headers())
            soup = BeautifulSoup(response.text, 'lxml')
            vacancies_list = soup.find_all(
                'div', class_='vacancy-serp-item__layout')
            for vacancy in vacancies_list:
                vacancy_name = vacancy.find('a', class_='serp-item__title')
                company = vacancy.find('div', class_="bloko-text").text
                salary = vacancy.find('span', class_='bloko-header-section-2')
                if salary is None:
                    salary = 'Не указано'
                else:
                    salary = salary.text
                vacancy_link = vacancy_name['href']
                city = vacancy.find(
                    'div', {'data-qa': "vacancy-serp__vacancy-address"}).text
                info.append({
                    'company': company,
                    'vacancy_name': vacancy_name.text,
                    'link': vacancy_link,
                    'salary': normalize('NFKC', salary),
                    'city': city.split(',')[0]
                })
                time.sleep(0.1)
            bar.next()
        bar.finish()


if __name__ == '__main__':
    get_info()
    print(f'[INFO] Записано {len(info)} вакансий')
    with open('vacancies.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=4)
