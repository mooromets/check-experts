# coding=utf-8

import br_scrape

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

import time
import random
import logging
import re

# BrPageParser - parses pages from bookmaker-ratings.ru
# here comes all the staff , relevant to specific website
# TODO create a base parser?

class BrPageParser:
    def __init__(self, webdriver):
        self.webdriver = webdriver
        self.webdriver.implicitly_wait(15)
        self.home_url = u'https://bookmaker-ratings.ru/'
        self.experts_list_url = u'https://bookmaker-ratings.ru/forecast_homepage/'
        #self.author_base_url = u'https://bookmaker-ratings.ru/author/'
        self.author_stats_pattern = u'https://bookmaker-ratings.ru/author/%s/#statistic?month=%4d-%02d'


    # get url
    def get(self, url):
        logging.info('URL get: %s', url)
        self.webdriver.get(url)

    # open home page
    def openHome(self):
        self.webdriver.get(self.home_url)

    # close pop-advertisment
    def closeAd(self):
        try:
            adv_button = self.webdriver.find_element_by_id('float-banner-close')
            adv_button.click()
            logging.info('AD closed')
        except NoSuchElementException:
            logging.warning('there was no AD')

    # start working with website
    def startSession(self):
        self.openHome()
        self.closeAd()

    # return a list of experts, listed on a dedicated web page
    def getExpertsList(self):
        self.get(self.experts_list_url)
        #expand all predictors
        button = self.webdriver.find_element_by_class_name("predictors-reveal-btn")
        button.click()
        uniqueUrls = br_scrape.get_urls_from_html(self.webdriver.page_source, "author")
        # get names from urls
        names = []
        for url in uniqueUrls:
            tmp = re.search("/[A-Za-z_0-9]+/$", url).group().replace('/',"")
            names.append(tmp.lower())
        return set(names)

    # get all expert's bets in the selected month
    def getExpertBets(self, name, year, month, time_crawled):
        self.get(self.author_stats_pattern % (name, year, month))
        datum = "%4d-%02d" % (year, month) # TODO refactor br_scrape.is_page_consistent()

        # try to obtain data from page
        max_tries = 10
        while max_tries > 0:
            #page source to Beautiful Soup
            page_source = BeautifulSoup(self.webdriver.page_source, 'lxml')
            if (br_scrape.is_page_consistent(page_source, name, datum)):
                break
            else:
                time.sleep(random.randrange(4, 8)) #wait for AJAX stuff
            max_tries = max_tries - 1
        if max_tries == 0:
            logging.error('Could not load page for: name=%s and date=%4d-%02d', name, year, month)
            return []

        bets = []
        for bet in page_source.find_all('div', "one-bet"):
            newBet = br_scrape.read_bet(bet, time_crawled, name)
            if newBet is None:
                #skip tablet and head rows
                continue
            else:
                bets.append(newBet)

        return bets
