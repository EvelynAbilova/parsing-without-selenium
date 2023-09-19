# Не сделано

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

data = []

with sync_playwright() as p:
    browser = p.webkit.launch()

    page = browser.new_page()

    page.goto('https://www.santaelena.com.co/tiendas-pasteleria/', timeout=100000)
    page_content = page.content()

    soup = BeautifulSoup(page_content, 'lxml')
    list_shops = soup.find_all('section',
                               class_='elementor-section elementor-top-section elementor-element elementor-element-8a22020 elementor-section-full_width elementor-section-height-default elementor-section-height-default')
    shop_urls = [shop.attrs['href'] for shop in
                 list_shops[0].find_all(class_='elementor-button elementor-button-link elementor-size-sm')]


    browser.close()
    for url in shop_urls:
        browser = p.webkit.launch()
        page = browser.new_page()
        page.goto(url, timeout=100000)
        page_content = page.content()
        soup = BeautifulSoup(page_content, 'lxml')
        shops = soup.select('div.elementor-column.elementor-col-33.elementor-top-column.elementor-element')
        shops = [element for element in shops if len(element.find_all('p')) > 0]
        city = soup.find('h1', class_='elementor-heading-title elementor-size-default').get_text()
        city_name = city.split()[-1]
        for shop in shops:
            shop_name = shop.find('h3').text
            address, phone, _, *work_time = shop.find_all('p')
            address, phone, work_time = address.text, phone.text, [t.text for t in work_time]








