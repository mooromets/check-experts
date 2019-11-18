# coding=utf-8

import br_scrape

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import os
import random
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import re
import time


url = "https://bookmaker-ratings.ru/forecast_homepage/" #start with experts list
out_dir = "data" #output directory
time_crawled = datetime.now().strftime("%d-%m-%Y %H:%M")

# create a new Firefox session
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(10)
driver.get(url)

#After opening the url above, close AD
try:
    adv_button = driver.find_element_by_id('float-banner-close')
    adv_button.click()
    print(str(datetime.now()), "LOG", "scraper", "AD closed")
except NoSuchElementException:
    print(str(datetime.now()), "LOG", "scraper", "no AD")

#expand all predictors
python_button = driver.find_element_by_class_name("predictors-reveal-btn")
python_button.click()

#page source
soup_level1=BeautifulSoup(driver.page_source, 'lxml')

uniqueUrls = br_scrape.get_urls_from_html(driver.page_source, "author")

print(str(datetime.now()), "LOG", "scraper", "experts' urls=", len(uniqueUrls))

ERR_CNT = 0

total = 0
for (author_cnt, author_url) in enumerate(uniqueUrls, 1):
#DEBUG for author_url in [random.choice(list(uniqueUrls))]:
#DEBUG for author_url in [u'https://bookmaker-ratings.ru/author/elvin/']:
#DEBUG for author_url in [u'https://bookmaker-ratings.ru/author/arturio/']:

#    driver.get(author_url) #author url has to be opened before navigating to staistics over months
    author_name = re.search("/[A-Za-z_0-9]+/$", author_url).group().replace('/',"")
    author_bets = []

    #iterate over dates
    now = datetime.now()
    months_inactive = 0
    for dat in br_scrape.month_year_down_iter(now.month, now.year, 3, 2015)  :
        if months_inactive == 0: time.sleep(random.randrange(5, 15)) #decrease the requests frequency
        #concat url
        driver.get(author_url + "#statistic?month=" + dat)
        print(str(datetime.now()), "LOG", "scraper", "open link", driver.current_url)
        #page source to Beautiful Soup
        soup_level2=BeautifulSoup(driver.page_source, 'lxml')
        ##onthly result
        was_active = False;
        #loop on all bets
        for bet in soup_level2.find_all('div', "one-bet"):
            newBet = br_scrape.read_bet(bet, time_crawled, author_name)
            if newBet is None:
                #skip tablet and head rows
                continue
            else:
                was_active = True
                author_bets.append(newBet)
                if not br_scrape.check_date_month(newBet['placed-date'], dat):
                    ERR_CNT = ERR_CNT + 1
                    print(str(datetime.now()), "ERR", "scraper", "WRONG MONTH", author_name, newBet["placed-date"], dat)

        #check acivity
        if not was_active:
            months_inactive = months_inactive + 1
            #report inactivity
            if (months_inactive == 6):
                print(str(datetime.now()), "LOG", "scraper", "author", author_name, "inactive 6 months", dat)
            #stop if more than a year of inactivity
            if (months_inactive > 13):
                print(str(datetime.now()), "LOG", "scraper", "author", author_name, "stopped", dat)
                break
        else :
            months_inactive = 0
            print(str(datetime.now()), "LOG", "scraper", "total author bets", len(author_bets), "author", author_name, dat)
    # create a dataframe of crawled data
    df_crawled = pd.DataFrame(author_bets).drop_duplicates(keep=False)
    total = total + len(df_crawled)
    print(str(datetime.now()), "LOG", "scraper", "author", author_name, "unique author bets", len(df_crawled), "total bets", total)
    if len(df_crawled) == 0:
        #nothing to do
        #TODO add info message
        continue
    path = os.path.join("..", out_dir, author_name + ".csv") #TODO fix pathes
    br_scrape.append_df_to_file(df_crawled, path)
    print(str(datetime.now()), "LOG", "scraper", "parsing progress, %", round(float(author_cnt) / len(uniqueUrls) * 100))

print(str(datetime.now()), "errors count ", ERR_CNT)
