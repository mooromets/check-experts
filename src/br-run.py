# coding=utf-8

import br_scrape
import br_page_parser
import db_utils

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
import logging
import getopt, sys

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s;;%(levelname)s;;%(message)s")

# read commandline arguments, first
fullCmdArguments = sys.argv
# - further arguments
argumentList = fullCmdArguments[1:]

time_crawled = datetime.now().strftime("%d-%m-%Y %H:%M")

# create a new Firefox session
options = Options()
options.headless = True
parserBR = br_page_parser.BrPageParser(webdriver.Firefox(options=options))

now = datetime.now()

for expert in argumentList:
    if not db_utils.if_expert_exists(expert):
        continue
    months_inactive = 0
    for dat in br_scrape.month_year_down_iter(now.month, now.year, 12, 2019): #4 2015
        bets =  parserBR.getExpertBets(expert, dat[0], dat[1], time_crawled)
        db_utils.insert_untracked_bets(bets)
        if len(bets) == 0:
            months_inactive = months_inactive + 1
            #stop if more than a year of inactivity
            if (months_inactive > 13):
                logging.info('Stop by inactivity.Expert=%s;Y-m=%4d-%02d;bets=%d;months-inactivity=%d',
                    expert, dat[0], dat[1], len(bets), months_inactive)
                break
        else:
            months_inactive = 0
        logging.info('Expert=%s;Y-m=%4d-%02d;bets=%d;months-inactivity=%d',
            expert, dat[0], dat[1], len(bets), months_inactive)
