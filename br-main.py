# coding=utf-8

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import os
import random
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

try:
    #After opening the url above, close AD
    adv_button = driver.find_element_by_id('float-banner-close')
    adv_button.click()
except NoSuchElementException:
    xxx = 0

#expand all predictors
python_button = driver.find_element_by_class_name("predictors-reveal-btn")
python_button.click()

#page source
soup_level1=BeautifulSoup(driver.page_source, 'lxml')

####select one player (debug mode)
###link = random.choice(soup_level1.find_all('a', href=re.compile("author")))

allUrls = list()
for link in soup_level1.find_all('a', href=re.compile("author")):
    author_url = link.get("href")
    allUrls.append(author_url)
uniqueUrls = set(allUrls)

for author_url in uniqueUrls:
    author_name = re.search("author/.*/$", author_url).group()
    #print (author_url)

    ##navigate to player's page
    #driver.get(author_url)

    ##open statistic section
    #stats = driver.find_element_by_xpath("//a[@data-section='statistic']")
    #stats.click()

    #TODO generate dates
    dates = ["2018-10", "2018-11", "2018-12", "2019-01", "2019-02", "2019-03",
    "2019-04", "2019-05", "2019-06", "2019-07", "2019-08", "2019-09", "2019-10"]

    #result
    outcome = list()
    outcome_perc = list()
    outcome_val = list()

    for dat in dates:
        #concat url
        driver.get(author_url + "#statistic?month=" + dat)

        #page source to Beautiful Soup
        soup_level2=BeautifulSoup(driver.page_source, 'lxml')

        ##monthly result
        dat_outcome = list()

        #loop on all bets
        for bet in soup_level2.find_all('div', "one-bet"):
            #skip tablet and head rows
            if len(set(bet['class']) & set(["head", "tablet-version"])) == 0:
                #get factor
                factor_tag = bet.find('div', "factor")
                factor_value_tag = factor_tag.find('div', "factor-value")
                if (factor_value_tag is None) :
                    print(author_name, dat, factor_tag)
                    factor = 1
                else :
                    factor = float(factor_value_tag["data-factor-dec"].replace(",", "."))
                #get outcome
                bet_stat = bet.find('div', "status")
                outcomeDict = {
                    u'Проигрыш' : 0.0,
                    u'Возврат' : 1.0,
                    u'Выигрыш' : factor
                }
                outcomeVal = outcomeDict.get(bet_stat.string, 0.0)
                if bet_stat.string != u'Ожидание':
                    dat_outcome.append(outcomeVal)
    #
    #            print(bet_stat.string)
    #            utxt = u'Проигрыш'#.encode('utf-8')
    #            if bet_stat.string == utxt:
    #                print("bingo!")
    #                #print(bet.find('div', "type"))
    #                #print(bet.find('div', "stake"))
    #                #print(bet.find('div', "status"))
    #        #break
        outcome.extend(dat_outcome)
        if len(dat_outcome) :
            outcome_perc.append(
                round(sum(dat_outcome) / len(dat_outcome) * 100, 1))
            outcome_val.append(
                round((sum(dat_outcome) - len(dat_outcome)) * 10, 3))
        else :
            outcome_perc.append(float('nan'))
            outcome_val.append(float('nan'))
        #print(len(dat_outcome))
        #if (len(dat_outcome) > 0):
        #    print(sum(dat_outcome) / len(dat_outcome))
    if (len(outcome) > 0):
        print(
            round(sum(outcome) / len(outcome) * 100, 1),
            round((sum(outcome) - len(outcome)) * 10, 1 ),
            len(outcome),
            author_name)
        print(outcome_perc)
        print(outcome_val)
