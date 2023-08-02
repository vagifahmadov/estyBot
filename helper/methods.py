from flask import Flask, render_template, request, jsonify, json, session
import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from waitress import serve
import json


def selenium_method(id_element):
    s = Service('./chromedriver/chromedriver')
    url_ws = "https://www.etsy.com/"
    options = Options()
    options.add_experimental_option('detach', True)
    driver = webdriver.Chrome(service=s, options=options)
    a = ActionChains(driver)
    # params
    driver.get(url_ws)
    driver.maximize_window()

    category = driver.find_element(By.XPATH, "//span[@id='catnav-primary-link-10923']")
    category.click()
    while True:
        time.sleep(3)
        pagination = driver.find_elements(By.XPATH, '//span[@class="screen-reader-only"]')
        last_pagination = pagination[-2].text
        prev_last_pagination = pagination[-3].text
        print(f'page len:\t{len(pagination)} | last: {last_pagination}')
        items = driver.find_elements(By.XPATH, "//div[@class='wt-height-full']")
        items = list(filter(lambda fit: json.loads(str(fit.get_attribute('data-appears-batch-options')))['total_items'] > 16, items))
        item_title_list = list(map(lambda fit: {
            'title': str(fit.find_element(By.TAG_NAME, "a").get_attribute('title')),
            # 'element': fit,
            'data-listing-id': str(fit.find_element(By.TAG_NAME, "a").get_attribute('data-listing-id'))
        }, items))
        print(f'\nList:\n--------------------\n{item_title_list}\n--------------------\n')
        print(f'items quota: {len(items)} | current url: {driver.current_url}')
        item_title_list = list(filter(lambda f: f['data-listing-id'] == id_element, item_title_list))
        result_count = len(item_title_list)
        print(f'{result_count} result fount')
        if result_count > 0 or prev_last_pagination == 'Current page':
            break
        elif result_count == 0 and prev_last_pagination != 'Current page':
            pagination[-1].click()

    driver.close()
    return item_title_list
