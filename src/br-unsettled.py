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
import io #DEBUG


url = "https://bookmaker-ratings.ru/"
time_crawled = datetime.now().strftime("%d-%m-%Y %H:%M")

# create a new Firefox session
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(20)
driver.get(url)

#After opening the url above, close AD
try:
    adv_button = driver.find_element_by_id('float-banner-close')
    adv_button.click()
    print(str(datetime.now()), "LOG", "scraper", "AD closed")
except NoSuchElementException:
    print(str(datetime.now()), "LOG", "scraper", "no AD")

urls = [
    u'https://bookmaker-ratings.ru/author/teplofevralya/',
    u'https://bookmaker-ratings.ru/author/zhukov/',
    u'https://bookmaker-ratings.ru/author/netsenko/',
    u'https://bookmaker-ratings.ru/author/falcao1984/',
    u'https://bookmaker-ratings.ru/author/chaplygin/',
    u'https://bookmaker-ratings.ru/author/netsenko/',
    u'https://bookmaker-ratings.ru/author/ostapbender/',
    u'https://bookmaker-ratings.ru/author/nvaluev/',
    u'https://bookmaker-ratings.ru/author/karpovvyacheslav/']
random.shuffle(urls)

bets = []

for author_url in urls:
    author_name = re.search("/[A-Za-z_0-9]+/$", author_url).group().replace('/',"")
    month = "%4d-%02d" % (datetime.now().year, datetime.now().month)
    time.sleep(random.randrange(10, 15)) #decrease the requests frequency
    driver.get(author_url + "#statistic?month=" + month)
    max_tries = 60
    while max_tries > 0:
        #page source to Beautiful Soup
        soup_level2=BeautifulSoup(driver.page_source, 'lxml')
        if (br_scrape.is_page_consistent(soup_level2, author_name, month)):
            break
        else:
            time.sleep(random.randrange(2, 5)) #wait for AJAX stuff
        max_tries = max_tries - 1
    if max_tries == 0:
        continue

    #loop on all bets
    for bet in soup_level2.find_all('div', "one-bet"):
        newBet = br_scrape.read_bet_U(bet, time_crawled, author_name)
        if newBet is None:
            #skip tablet and head rows
            continue
        else:
            bets.append(newBet)
    #DEBUG
    with io.open(month + author_name +'.xml', 'w', encoding="utf-8") as f_out:
        f_out.write(soup_level2.prettify())
        f_out.close()

df = pd.DataFrame(bets)
df = df.sort_values(by=['placed-date','author','date'],
                    ascending=[False, True, False])
print(df[['placed-date', 'author','date','match', 'stake', 'factor']])

#watch -d -n X CMD
#while true; reset && CMD; sleep `shuf -i 100-2500 -n 1`; done
