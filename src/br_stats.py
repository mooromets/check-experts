import datetime
import pandas as pd

import utils_explore as ue

#Stats - a statistics class
#calculates and stores a present state of bets data for each author
# table columns: [author, crawled-date_max, placed-date_max, placed-date_min, freqN, freq]

class Stats:
    def __init__(self, filename="./stats.csv", dataPath = "../data"):
        self.fname = filename
        self.dpath = dataPath

    # method collects all bets and store present state as a .csv-file
    def store_stats(self):
        df = ue.all_bets(self.dpath)

        # general statistic
        stats_df = df.groupby(by = 'author').agg({
            'placed-date':['max','min'],
            'crawled-date':'max'
        })
        stats_df.columns = ["_".join(x) for x in stats_df.columns.ravel()]
        stats_df.reset_index(inplace=True)

        # to determine activity, we take only recent time
        DAYS = 50
        df_latest = df[(df['date'] >= datetime.datetime.now() - datetime.timedelta(DAYS))]
        df_latest = df_latest.groupby(by = 'author').agg({'type':'count'})
        df_latest.reset_index(inplace=True)
        df_latest['freqN'] = df_latest['type'].div(DAYS)
        df_latest = df_latest.drop(columns=['type'])
        df_latest

        #merge freq to main dataframe
        stats_df = stats_df.merge(df_latest, on=['author'], indicator=False, how="left")
        stats_df = stats_df.fillna(0)

        #for convenience, create labels for frequency categories
        stats_df['freq'] = pd.cut(stats_df['freqN'], [-.001, 0.1, 1, 100], labels=['LOW', 'MEDIUM', 'HIGH'])

        stats_df.to_csv(self.fname, index = None, header=True,  encoding='utf-8')

    # load stats from an already saved file
    def load_stats(self):
        return pd.read_csv(self.fname, encoding="utf-8")
