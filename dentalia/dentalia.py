import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.webkit.launch()

    page = browser.new_page()

    page_path = "https://dentalia.com/clinica/"

    page.goto(page_path, timeout=100000)
    page_content = page.content()

    soup = BeautifulSoup(page_content, 'lxml')
    data = {}
    container = soup.find_all('div', class_='jet-listing-grid jet-listing')
    clinics = container[0].find_all('div', class_='jet-listing-grid__item')
    for clinic in clinics:
        clinic_id = int(clinic.attrs['data-post-id'])
        data[clinic_id] = {}
        address, phones, working_hours = clinic.find_all('div', class_='jet-listing-dynamic-field__content')
        data[clinic_id]['name'] = clinic.find('h3').contents[0]
        data[clinic_id]['address'] = address.contents[0]
        data[clinic_id]['phones'] = phones.contents[0].split(': ')[1].split(' \n')
        data[clinic_id]['working_hours'] = [working_hours.contents[0].split('Horario: ')[1].replace('\n', ' ')]
    points = json.loads(soup.find('div', class_='jet-map-listing google-provider').attrs['data-markers'])
    for point in points:
        if point['id'] in data:
            data[point['id']]['latlon'] = [point['latLang']['lat'], point['latLang']['lng']]
    with open('dentalia.json', 'w') as f:
        normalized_data = [clinic for clinic in data.values()]
        f.write(json.dumps(normalized_data))
    browser.close()


