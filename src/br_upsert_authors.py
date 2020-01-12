# coding=utf-8

import br_page_parser
import db_utils

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s;;%(levelname)s;;%(message)s")

# create a new Firefox session
options = Options()
options.headless = True
parserBR = br_page_parser.BrPageParser(webdriver.Firefox(options=options))

# start session with a website
parserBR.startSession()

# do the job
db_utils.upsert_experts(parserBR.getExpertsList())
