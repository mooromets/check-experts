import pandas as pd
import glob
import datetime

IN_DIR = "../data" #output directory

# read data from all files
def all_bets(path = IN_DIR):
    return pd.concat(
        [pd.read_csv(file, encoding="utf-8", parse_dates=[1,2,5], dayfirst=True) for file in glob.glob(path + "/*.csv")],
        ignore_index=True)


def calc_win_rate(raw_data,
                period_split=None,
                min_games_thres=0):
    if period_split is None:
        grouping = ['author', 'status']
    else:
        grouping = ['author', raw_data['placed-date'].dt.to_period(period_split), 'status']
    df = raw_data.groupby(by=grouping).agg({'factor':['sum', 'count']})
    # tune up dataframe
    df.columns = ["_".join(x) for x in df.columns.ravel()]
    df.reset_index(inplace=True)
    # make columns with detailed data on W-R-L
    if period_split is None:
        indexing = ['author']
    else:
        indexing = ['author', 'placed-date']
    df = df.pivot_table(index=indexing, columns='status', values=['factor_sum', 'factor_count'])
    df.columns = ["_".join(x) for x in df.columns.ravel()]
    df = df.fillna(value=0)
    # add summary columns
    df['count'] = [s if s >= min_games_thres else float('nan') for s in df['factor_count_L'] + df['factor_count_R'] + df['factor_count_W']]
    df['return'] = df['factor_sum_W'] + df['factor_count_R']
    df['win'] = df['factor_sum_W'] - df['factor_count_L'] - df['factor_count_W']
    df['success_rate'] = df['win'] / df['count'] * 100
    df.reset_index(inplace=True)
    return df.drop(columns=['factor_sum_L',
                          'factor_sum_R',
                          'factor_sum_W',
                          'factor_count_L',
                          'factor_count_R',
                          'factor_count_W'])


def summary_chart(raw_data,
                count_bins=None,
                min_rate_thres=None):
    df = calc_win_rate(raw_data)
    if count_bins is None:
        sorting = ['success_rate']
    else:
        df['category'] = pd.cut(df['count'], count_bins)
        sorting = ['category', 'success_rate']
    if min_rate_thres is not None:
        df = df[df.success_rate >= min_rate_thres]
    return df.sort_values(by=sorting, ascending=False)
