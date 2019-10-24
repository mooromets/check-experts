# coding=utf-8

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import random
import datetime
import time

# iterate over year-month backwards
def month_year_down_iter( start_month, start_year, end_month, end_year ):
    ym_start= 12*start_year + start_month - 1
    ym_end= 12*end_year + end_month - 1
    for ym in range( ym_start, ym_end, -1 ):
        y, m = divmod( ym, 12 )
        yield "%4d-%02d" % (y, m+1)

#start with experts list
url = "https://bookmaker-ratings.ru/forecast_homepage/"

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
    print("LOG", "scraper", "AD closed")
except NoSuchElementException:
    print("LOG", "scraper", "no AD")

#expand all predictors
python_button = driver.find_element_by_class_name("predictors-reveal-btn")
python_button.click()

#page source
soup_level1=BeautifulSoup(driver.page_source, 'lxml')

allUrls = list()
for link in soup_level1.find_all('a', href=re.compile("author")):
    author_url = link.get("href")
    allUrls.append(author_url)
uniqueUrls = set(allUrls)
print("LOG", "scraper", "experts' urls=",len(allUrls), "unique urls:", len(uniqueUrls))

allbets = []
for author_url in uniqueUrls:
#for author_url in [random.choice(list(uniqueUrls))]: #DEBUG
    author_name = re.search("/[A-Za-z_0-9]+/$", author_url).group().replace('/',"")

    #iterate over dates
    now = datetime.datetime.now()
    months_inactive = 0
    for dat in month_year_down_iter(now.month, now.year, 3, 2015)  :
        #time.sleep(10) #DEBUG decrease the requests frequency
        #concat url
        driver.get(author_url + "#statistic?month=" + dat)
        print("LOG", "scraper", "open link", driver.current_url)
        #page source to Beautiful Soup
        soup_level2=BeautifulSoup(driver.page_source, 'lxml')
        ##onthly result
        was_active = False;
        #loop on all bets
        for bet in soup_level2.find_all('div', "one-bet"):
            #skip tablet and head rows
            if len(set(bet['class']) & set(["head", "tablet-version"])) == 0:
                was_active = True

                ##create bet
                record_bet = {}
                #get factor
                factor_tag = bet.find('div', "factor")
                factor_value_tag = factor_tag.find('div', "factor-value")
                if (factor_value_tag is None) :
                    print("LOG", "scraper", "empty facotr", author_name, dat, factor_tag)
                    continue
                else :
                    record_bet["factor"] = float(
                        factor_value_tag["data-factor-dec"].replace(",", "."))
                #get status
                bet_stat = bet.find('div', "status")
                outcomeDict = {u'Проигрыш' : "L",
                    u'Возврат' : "R",
                    u'Выигрыш' : "W",
                    u'Ожидание' : "U"}
                record_bet["status"] = outcomeDict.get(bet_stat.string, "X")
                #get type
                record_bet["type"] = bet.find('div', "type").string
                #get date
                record_bet["placed-date"] = bet.find('div', "date").string
                #get stake
                bet_match = bet.find('div', "match")
                bet_match_name = bet_match.find('a', "match-name")
                record_bet["match"] = bet_match_name.string
                bet_date = bet_match.find('div', "express-date")
                record_bet["date"] = bet_date.string
                record_bet["stake"] = bet.find('div', "stake").string
                record_bet["author"] = author_name
                allbets.append(record_bet)
        #check acivity
        if not was_active:
            months_inactive = months_inactive + 1
            #report inactivity
            if (months_inactive == 6):
                print("LOG", "scraper", "author", author_name, "inactive 6 months", dat)
            #stop if more than a year of inactivity
            if (months_inactive > 13):
                print ("LOG", "scraper", "author", author_name, "stopped", dat)
                break
        else :
            months_inactive = 0
            print("LOG", "scraper", "overall entries number", len(allbets), "author", author_name, dat)

df1 = pd.DataFrame(allbets)
df1.to_csv(r'bets_history.csv', index = None, header=True,  encoding='utf-8')
print ("LOG", "scraper", "file saved", 'bets_history.csv')
