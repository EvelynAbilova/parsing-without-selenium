import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

day_names = {
    1: 'Пн',
    2: 'Вт',
    3: 'Ср',
    4: 'Чт',
    5: 'Пт',
    6: 'Сб',
    7: 'Вс',
}

cities = ['https://omsk.yapdomik.ru/about', 'https://achinsk.yapdomik.ru/about', 'https://tomsk.yapdomik.ru/about',
          'https://berdsk.yapdomik.ru/about', 'https://krsk.yapdomik.ru/about', 'https://nsk.yapdomik.ru/about']
shops_data = []

with sync_playwright() as p:
    browser = p.webkit.launch()

    page = browser.new_page()
    for city in cities:
        page_path = city

        page.goto(page_path, timeout=100000)
        page_content = page.content()

        soup = BeautifulSoup(page_content, 'lxml')
        shops = json.loads(soup.find_all('script')[5].contents[0].split(' = ')[1])['shops']
        phone = soup.find("a", {"class": 'link link--black link--underline'}).get_text()
        city_name = soup.find("a", {"class": 'city-select__current link link--underline'}).get_text()

        for shop in shops:
            default_dicts = [entry for entry in shop['workingHours'] if
                             entry.get('type') == 'default' and entry.get('date') is None]

            max_id_per_day = {}

            for dictionary in default_dicts:
                day = dictionary["day"]
                id_value = dictionary["id"]
                if day not in max_id_per_day or id_value > max_id_per_day[day]:
                    max_id_per_day[day] = id_value

            filtered_default_dicts = [
                dictionary for dictionary in default_dicts if dictionary["id"] == max_id_per_day[dictionary["day"]]
            ]

            for dictionary in filtered_default_dicts:
                day_value = dictionary['day']
                if day_value in day_names:
                    dictionary['day'] = day_names[day_value]
                if dictionary['from'] is not None:
                    dictionary['from'] = f'{dictionary["from"] // 60:02}:{dictionary["from"] % 60:02}'
                else:
                    dictionary['from'] = '00:00'
                if dictionary['to'] is not None:
                    dictionary['to'] = f'{dictionary["to"] // 60 % 24:02}:{dictionary["to"] % 60:02}'
                else:
                    dictionary['to'] = '00:00'

            open_time = set()
            close_time = set()
            working_hours = []
            for work_time in filtered_default_dicts:
                open_time.add(work_time['from'])
                close_time.add(work_time['to'])
            if len(open_time) == len(close_time) == 1:
                working_hours.append(f'Пн - Вс {list(open_time)[0]} - {list(close_time)[0]}')
            else:
                open_time = list(open_time)
                if len(open_time) == 2:
                    ejection = [w_time['from'] for w_time in filtered_default_dicts]
                    ejection = open_time[0] if ejection.count(open_time[0]) < ejection.count(open_time[1]) else \
                    open_time[1]
                    start_date = ''
                    end_date = ''
                    for index, w_time in enumerate(filtered_default_dicts):
                        if w_time['from'] == ejection:
                            working_hours.append(
                                f"{filtered_default_dicts[index + 1]['day']} - {filtered_default_dicts[index - 1]['day']} {filtered_default_dicts[index - 1]['from']} - {filtered_default_dicts[index - 1]['to']}")
                            working_hours.append(
                                f"{filtered_default_dicts[index]['day']} - {filtered_default_dicts[index]['day']} {filtered_default_dicts[index]['from']} - {filtered_default_dicts[index]['to']}")
                else:
                    for w_time in filtered_default_dicts:
                        working_hours.append(f"{w_time['day']} {w_time['from']} - {w_time['to']}")
            city_name_str = f"{city_name}, {shop['address']}"
            data = {
                "name": "Японский Домик",
                "address": city_name_str,
                "latlon": [shop['coord']['latitude'], shop['coord']['longitude']],
                "phones": [phone],
                "working_hours": [working_hours]
            }

            shops_data.append(data)

with open('yapdomik.json', 'w', encoding='utf-8') as json_file:
    json.dump(shops_data, json_file, ensure_ascii=False, indent=4)


