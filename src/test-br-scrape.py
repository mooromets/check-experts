# coding=utf-8

import br_scrape

import unittest
from bs4 import BeautifulSoup
import pandas as pd
import os
from pandas.util.testing import assert_frame_equal

#XXX test already known issues only
#TODO add full tests

class TestMonthYearDownIter(unittest.TestCase):
    def test_simple(self):
        sample = [(2019,12), (2019,11), (2019,10), (2019,9), (2019,8), (2019,7)]
        for (idx, x) in enumerate(br_scrape.month_year_down_iter(12, 2019, 6, 2019), 0):
            self.assertEqual(x, sample[idx])


class TestGetUrlsFromHtml(unittest.TestCase):
    def test_simple(self):
        html = "<a href='foo/bar/'>text</a> \
                <a href='foo/baz/'>text2</a>\
                <a href='bar/quo/'>text3</a>\
                <a href='bar/quo/'>text4</a>"
        self.assertEqual(br_scrape.get_urls_from_html(html, "bar"),
            set(["foo/bar/","bar/quo/"]))


class TestReadBet(unittest.TestCase):
    def test_ordinar(self):
        ordinar = '<div class="is-hidden desktop-version one-bet data win ordinar even"> \
                    <div class="type">Ординар</div> \
                    <div class="date">11.05.2019</div>\
                        <div class="match">\
                            <a target="_blank" href="https://bookmaker-ratings.ru/tips/kristal-pe-las-bornmut-prognoz-i-stavka-artura-petros-yana/" class="match-name">«Кристал Пэлас» – «Борнмут»</a> \
                            <div class="express-date">12.05.2019</div>\
                        </div>\
                        <div class="stake">ТБ (2,5) и обе забьют</div>\
                        <div class="factor">\
                            <div class="factor-label factor-value" data-factor-dec="1,85" data-factor-fract="17/20" data-factor-american="-117"></div>\
                        </div>\
                        <div class="status">Выигрыш</div>\
                    </div>'
        soup_level1=BeautifulSoup(ordinar, 'lxml')
        bet_src = soup_level1.find('div', "one-bet")
        self.assertEqual(br_scrape.read_bet(bet_src,"2001-01-01", "me"),
            {   "author":"me",
                'crawled-date': '2001-01-01',
                'date': u'12.05.2019',
                'factor': 1.85,
                'match': u'«Кристал Пэлас» – «Борнмут»',
                'placed-date': u'11.05.2019',
                'stake': u'ТБ (2,5) и обе забьют',
                'status': 'W',
                'type': 'single'})

    def test_wrong_type(self):
        ordinar = '<div class="is-hidden desktop-version one-bet data win ordinar even"> \
                    <div class="type">NON-TYPE</div> \
                    <div class="date">11.05.2019</div>\
                        <div class="match">\
                            <a target="_blank" href="https://bookmaker-ratings.ru/tips/kristal-pe-las-bornmut-prognoz-i-stavka-artura-petros-yana/" class="match-name">«Кристал Пэлас» – «Борнмут»</a> \
                            <div class="express-date">12.05.2019</div>\
                        </div>\
                        <div class="stake">ТБ (2,5) и обе забьют</div>\
                        <div class="factor">\
                            <div class="factor-label factor-value" data-factor-dec="1,85" data-factor-fract="17/20" data-factor-american="-117"></div>\
                        </div>\
                        <div class="status">Выигрыш</div>\
                    </div>'
        soup_level1=BeautifulSoup(ordinar, 'lxml')
        bet_src = soup_level1.find('div', "one-bet")
        self.assertEqual(br_scrape.read_bet(bet_src,"2001-01-01", "me"),None)

    def test_empty_factor(self):
        ordinar = '<div class="is-hidden desktop-version one-bet data win ordinar even"> \
                    <div class="type">Ординар</div> \
                    <div class="date">11.05.2019</div>\
                        <div class="match">\
                            <a target="_blank" href="https://bookmaker-ratings.ru/tips/kristal-pe-las-bornmut-prognoz-i-stavka-artura-petros-yana/" class="match-name">«Кристал Пэлас» – «Борнмут»</a> \
                            <div class="express-date">12.05.2019</div>\
                        </div>\
                        <div class="stake">ТБ (2,5) и обе забьют</div>\
                        <div class="factor">\
                        </div>\
                        <div class="status">Выигрыш</div>\
                    </div>'
        soup_level1=BeautifulSoup(ordinar, 'lxml')
        bet_src = soup_level1.find('div', "one-bet")
        self.assertEqual(br_scrape.read_bet(bet_src,"2001-01-01", "me"), None)

    def test_unresolved(self):
        ordinar = '<div class="is-hidden desktop-version one-bet data win ordinar even"> \
                    <div class="type">Ординар</div> \
                    <div class="date">11.05.2019</div>\
                        <div class="match">\
                            <a target="_blank" href="https://bookmaker-ratings.ru/tips/kristal-pe-las-bornmut-prognoz-i-stavka-artura-petros-yana/" class="match-name">«Кристал Пэлас» – «Борнмут»</a> \
                            <div class="express-date">12.05.2019</div>\
                        </div>\
                        <div class="stake">ТБ (2,5) и обе забьют</div>\
                        <div class="factor">\
                            <div class="factor-label factor-value" data-factor-dec="1,85" data-factor-fract="17/20" data-factor-american="-117"></div>\
                        </div>\
                        <div class="status">Ожидание</div>\
                    </div>'
        soup_level1=BeautifulSoup(ordinar, 'lxml')
        bet_src = soup_level1.find('div', "one-bet")
        self.assertEqual(br_scrape.read_bet(bet_src,"2001-01-01", "me"), None)

    def test_tablet(self):
        tablet = '<div class="is-hidden tablet-version one-bet data loss ordinar">\
                    <div class="bet-row top-row">\
                        <div>\
                            <span class="type">\
                                Ординар\
                                <span class="date">(11.05.2019)</span>\
                            </span>\
                        </div>\
                        <div>\
                            <div class="status">Проигрыш</div>\
                        </div>\
                    </div>\
                    <div class="bet-row">\
                        <div>\
                            <div class="match">\
                                <div class="express-date">12.05.2019</div>\
                                <a target="_blank" href="https://bookmaker-ratings.ru/tips/fulhe-m-n-yukasl-prognoz-i-stavka-artura-petros-yana/" class="match-name">«Фулхэм» – «Ньюкасл»</a>\
                            </div>\
                            <div class="stake">ТБ (2,5) и обе забьют</div>\
                        </div>\
                        <div>\
                            <div class="factor">\
                                    <div class="factor-label factor-value" data-factor-dec="2,10" data-factor-fract="11/10" data-factor-american="+110"></div>\
                            </div>\
                        </div>\
                        </div>\
                        </div>'
        soup_level1=BeautifulSoup(tablet, 'lxml')
        bet_src = soup_level1.find('div', "one-bet")
        self.assertEqual(br_scrape.read_bet(bet_src,"2001-01-01", "me"), None)

    def test_accu(self):
        accu = '<div class="is-hidden desktop-version one-bet data loss express">\
                    <div class="type">Экспресс</div>\
                    <div class="date">11.05.2019</div>\
                        <div class="express-group">\
                            <div class="express-row">\
                            <div class="match">\
                                <a target="_blank" href="https://bookmaker-ratings.ru/tips/e-kspress-na-bundesligu-prognoz-i-stavki-artura-petros-yana/" class="match-name">«Айнтрахт» - «Майнц»</a>\
                                <div class="express-date">12.05.2019</div>\
                            </div>\
                            <div class="stake">П1</div>\
                            <div class="factor">\
                                <div class="factor-label factor-value" data-factor-dec="1,60" data-factor-fract="3/5" data-factor-american="-166"></div>\
                                </div>\
                        </div>\
                            <div class="express-row">\
                            <div class="match">\
                                <a target="_blank" href="https://bookmaker-ratings.ru/tips/e-kspress-na-bundesligu-prognoz-i-stavki-artura-petros-yana/" class="match-name">«Бавария» - «Айнтрахт»</a>\
                                <div class="express-date">18.05.2019</div>\
                            </div>\
                            <div class="stake">Х</div>\
                            <div class="factor">\
                                    <div class="factor-label factor-value" data-factor-dec="6,00" data-factor-fract="5/1" data-factor-american="+500"></div>\
                            </div>\
                        </div>\
                        <div class="express-row final-row">\
                            <div class="match"></div>\
                            <div class="stake">Итоговый коэфф.</div>\
                            <div class="factor">\
                                    <div class="factor-label factor-value" data-factor-dec="9,60" data-factor-fract="43/5" data-factor-american="+860"></div>\
                            </div>\
                        </div>\
                </div>\
                    <div class="status">Проигрыш</div>\
                </div>'
        soup_level1=BeautifulSoup(accu, 'lxml')
        bet_src = soup_level1.find('div', "one-bet")
        self.assertEqual(br_scrape.read_bet(bet_src,"2001-01-01", "me"),
            {   "author":"me",
                'crawled-date': '2001-01-01',
                'date': u'18.05.2019',
                'factor': 9.6,
                'match': u' 1.60 6.00',
                'placed-date': u'11.05.2019',
                'stake': "2",
                'status': 'L',
                'type': 'accu'})

class TestMergeCrawledSaved(unittest.TestCase):
    def test_no_saved(self):
        df = pd.DataFrame({"arr" : ['one', 'two', 'three']})
        res = br_scrape.merge_crawled_saved(df, None)
        self.assertEqual(len(res), len(df))
        self.assertEqual(res.shape, df.shape)

    def test_simple(self):
        df_crawled = pd.DataFrame({
            "author" :      ['me', 'me', 'me'],
            'crawled-date': [41,    42,   43],
            'date':         ['10', '20', '30'],
            'factor':       [1.0,  2.0,  3.0],
            'match':        ['10', '20', '30'],
            'placed-date':  ['05', '05', '05'],
            'stake':        ['10', '20', '30'],
            'status':       ['L',  'R',  'W'],
            'type':         ['single', 'single', 'single']
            })
        df_saved = pd.DataFrame({
            "author" :      ['me', 'me', 'me'],
            'crawled-date': [10,    20,   30],
            'date':         ['10', '11', '12'],
            'factor':       [1.0,  1.1,  1.2],
            'match':        ['10', '11', '12'],
            'placed-date':  ['05', '11', '12'],
            'stake':        ['10', '20', '30'],
            'status':       ['L',  'W',  'L'],
            'type':         ['single', 'single', 'single']
            })
        res = br_scrape.merge_crawled_saved(df_crawled, df_saved)
        self.assertEqual(len(res), 5)
        self.assertEqual(res.shape, (5, 9))
        self.assertEqual(list(res.columns), list(['author', 'crawled-date', 'date', 'factor', 'match', 'placed-date', 'stake', 'status', 'type']))
        self.assertEqual(res['crawled-date'].sum(), 10+20+30+42+43)

class TestAppendDfFile(unittest.TestCase):
    def test_empty_df(self):
        self.assertEqual(br_scrape.append_df_to_file(pd.DataFrame(), "path"), False)

    def test_append_simple(self):
        df = pd.DataFrame({
            "author" :      ['me', 'me'],
            'crawled-date': ["29-10-2019 22:07", "29-10-2019 22:07"],
            'date':         ['28.09.2019', '22.09.2019'],
            'factor':       [2.4,  2.08],
            'match':        [u'Атлетико Мадрид - Реал Мадрид', u'Челси - Ливерпуль'],
            'placed-date':  ['27.09.2019', '21.09.2019'],
            'stake':        [u'П1', u'П2'],
            'status':       ['L',  'W'],
            'type':         ['single', 'single']
            })
        df_crawled = pd.DataFrame({
            "author" :      ['me', 'me', 'me', 'me'],
            'crawled-date': ["30-10-2019 12:07", "30-10-2019 12:07", "30-10-2019 12:07", "30-10-2019 12:07"],
            'date':         ['28.09.2019', '22.09.2019', '01.10.2019', '01.10.2019'],
            'factor':       [2.4,  2.08, 2.45,  3.7],
            'match':        [u'Атлетико Мадрид - Реал Мадрид', u'Челси - Ливерпуль', u'Реал Мадрид - Брюгге', u'Локомотив - Атлетико Мадрид'],
            'placed-date':  ['27.09.2019', '21.09.2019', '30.09.2019', '30.09.2019'],
            'stake':        [u'П1', u'П2', u'П1 всухую', u'X'],
            'status':       ['L',  'W', 'L',  'L'],
            'type':         ['single', 'single', 'single', 'single']
            })
        df_sample_res = pd.DataFrame({
            "author" :      ['me', 'me', 'me', 'me'],
            'crawled-date': ["29-10-2019 22:07", "29-10-2019 22:07", "30-10-2019 12:07", "30-10-2019 12:07"],
            'date':         ['28.09.2019', '22.09.2019', '01.10.2019', '01.10.2019'],
            'factor':       [2.4,  2.08, 2.45,  3.7],
            'match':        [u'Атлетико Мадрид - Реал Мадрид', u'Челси - Ливерпуль', u'Реал Мадрид - Брюгге', u'Локомотив - Атлетико Мадрид'],
            'placed-date':  ['27.09.2019', '21.09.2019', '30.09.2019', '30.09.2019'],
            'stake':        [u'П1', u'П2', u'П1 всухую', u'X'],
            'status':       ['L',  'W', 'L',  'L'],
            'type':         ['single', 'single', 'single', 'single']
            })
        PATH = "tmp.csv"
        df.to_csv(PATH, index = None, header=True,  encoding='utf-8')
        br_scrape.append_df_to_file(df_crawled, PATH)
        df_new = pd.read_csv(PATH, encoding="utf-8")
        self.assertEqual(df_new.shape, (4, 9))
        self.assertEqual(list(df_new.columns), list(['author', 'crawled-date', 'date', 'factor', 'match', 'placed-date', 'stake', 'status', 'type']))
        assert_frame_equal(df_new, df_sample_res)
        os.remove(PATH)


class TestCheckDateMonth(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(br_scrape.check_date_month('10.10.2010','2010-10'), True)
        self.assertEqual(br_scrape.check_date_month('01.11.2010','2010-11'), True)
        self.assertEqual(br_scrape.check_date_month('31.12.2010','2010-12'), True)
        self.assertEqual(br_scrape.check_date_month('31.12.2010','2011-01'), False)
        self.assertEqual(br_scrape.check_date_month('31.05.2018','2018-06'), False)


if __name__ == '__main__':
    unittest.main()
