# coding=utf-8

from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd


# produce year-month backwards iterators
def month_year_down_iter(start_month, start_year, end_month, end_year):
    ym_start= 12*start_year + start_month - 1
    ym_end= 12*end_year + end_month - 1
    for ym in range( ym_start, ym_end, -1 ):
        y, m = divmod( ym, 12 )
        yield "%4d-%02d" % (y, m+1)


# from html get all unique links, which contain a keyword
def get_urls_from_html(html, keyword):
    soup_level1=BeautifulSoup(html, 'lxml')
    allUrls = list()
    for link in soup_level1.find_all('a', href=re.compile(keyword)):
        author_url = link.get("href")
        allUrls.append(author_url)
    return set(allUrls)


# read one bet from an html-object bet_src
# time_crawled, author_name - will be added to the bet as is
def read_bet(bet_src, time_crawled, author_name):
    #skip tablet and head rows
    if not(len(set(bet_src['class']) & set(["head", "tablet-version"])) == 0):
        return None
    else :
        ##create bet
        record_bet = {}
        # date crawled
        record_bet["crawled-date"] = time_crawled
        #get type
        typeDict = {u'Ординар' : "single"
            ,u'Экспресс' : "accu"
            }
        record_bet["type"] = typeDict.get(bet_src.find('div', "type").string, "N")
        #get date
        record_bet["placed-date"] = bet_src.find('div', "date").string
        #get status
        bet_stat = bet_src.find('div', "status")
        if bet_stat.string == u'Ожидание':
            return None #don't store upcoming events
        outcomeDict = {u'Проигрыш' : "L"
            ,u'Возврат' : "R"
            ,u'Выигрыш' : "W"
            #,u'Ожидание' : "U" #don't store upcoming events
            }
        record_bet["status"] = outcomeDict.get(bet_stat.string, "X")

        #process single and multi differently
        if record_bet["type"] == "single" :
            #get factor
            factor_tag = bet_src.find('div', "factor")
            factor_value_tag = factor_tag.find('div', "factor-value")
            if (factor_value_tag is None) :
                print(str(datetime.now()), "ERR", "scraper", "empty factor", author_name, record_bet["placed-date"], factor_tag)
                return None
            else :
                record_bet["factor"] = float(
                    factor_value_tag["data-factor-dec"].replace(",", "."))
            #get stake
            bet_match = bet_src.find('div', "match")
            bet_match_name = bet_match.find('a', "match-name")
            record_bet["match"] = bet_match_name.string
            bet_date = bet_match.find('div', "express-date")
            record_bet["date"] = bet_date.string
            record_bet["stake"] = bet_src.find('div', "stake").string
        elif record_bet["type"] == "accu":
            for exp in bet_src.find_all('div', "express-group"):
                final_tag = exp.find('div', "final-row")
                #get factor
                factor_tag = final_tag.find('div', "factor")
                factor_value_tag = factor_tag.find('div', "factor-value")
                if (factor_value_tag is None) :
                    print(str(datetime.now()), "ERR", "scraper", "empty factor", author_name, record_bet["placed-date"], factor_tag)
                    return None
                else :
                    record_bet["factor"] = float(
                        factor_value_tag["data-factor-dec"].replace(",", "."))
                #match will contain all factors for singles
                record_bet["match"] = u''
                record_bet["date"] = record_bet["placed-date"]
                for exp_row in exp.find_all('div', "express-row"):
                    if"final-row" in exp_row["class"]:
                        continue
                    else:
                        #get match
                        match_exp = exp_row.find('div', "match")
                        if match_exp.find('div', "express-date").string > record_bet["date"]: #TODO correct comparison
                            record_bet["date"] = match_exp.find('div', "express-date").string
                        #get factor
                        factor_tag = exp_row.find('div', "factor")
                        factor_value_tag = factor_tag.find('div', "factor-value")
                        if (factor_value_tag is None) :
                            print(str(datetime.now()), "ERR", "scraper", "empty factor", author_name, dat, factor_tag)
                            continue
                        else :
                            record_bet["match"] = record_bet["match"] + u' ' + factor_value_tag["data-factor-dec"].replace(",", ".")
                #stake will contain the number of singles in multi
                record_bet["stake"] = str(record_bet["match"].count('.'))
                #TODO remove code duplicates
        else :
            print(str(datetime.now()), "ERR", "scraper", "unknown bet type", author_name, record_bet["placed-date"], record_bet["type"])
            return None
        record_bet["author"] = author_name
        return record_bet


# append df_crawled dataframe to df_saved one:
# 1. all existing records in df_saved stay unchaged
# 2. only records not present in df_saved will be upmerged
# 3. records from df_crawled and df_saved are regarded as equal,
#   if all of their values except 'crawled-date' are equal
def merge_crawled_saved(df_crawled, df_saved):
    if df_saved is None:
        return df_crawled
    else :
        # JOIN on all columns, except  crawled-date, because it changes in every execution
        join_cols = ["author", "type", "placed-date", "status", "factor", "match", "date", "stake"]
        df_merge = df_saved.merge(df_crawled, on=join_cols, indicator='join', how="outer")

        # create index for newly crawled records
        index = (df_merge['join'] == "right_only")
        # newly crawled records get the current crawled-dates
        # all other records - keep their old crawled-date
        df_merge.loc[index, 'crawled-date_x'] = df_merge.loc[index, 'crawled-date_y']
        return df_merge \
            .rename(columns={"crawled-date_x": "crawled-date"}) \
            .drop(columns=['join', 'crawled-date_y'])
