from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import os
#import pandas as pd
#from tabulate import tabulate

#start with experts list
url = "https://bookmaker-ratings.ru/forecast_homepage/"

# create a new Firefox session
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(10)
driver.get(url)

#After opening the url above, close AD
adv_button = driver.find_element_by_id('float-banner-close')
adv_button.click()

#expand all predictors
python_button = driver.find_element_by_class_name("predictors-reveal-btn")
python_button.click()

soup_level1=BeautifulSoup(driver.page_source, 'lxml')

for link in soup_level1.find_all('a', href=re.compile("author")):
    author_url = link.get("href")
    print (author_url)

    driver.get(author_url)
    #stats = "#statistic"

    stats = driver.find_element_by_xpath("//a[@data-section='statistic']")
    stats.click()

    #page source to Beautiful Soup
    soup_level2=BeautifulSoup(driver.page_source, 'lxml')

    for bet in soup_level2.find_all('div', "one-bet"):
        print( bet.find('div', "date"))
        print(bet.find('div', "type"))
        print(bet.find('div', "stake"))
        print(bet.find('div', "status"))

    break
