# coding=utf-8

import os
import pandas as pd

test_dir = "data4"
check_dir = ["data", "data2", "data3"]
for file in os.listdir("data4"):
    if file.endswith(".csv"):
        path1 = os.path.join(test_dir, file)
        print("DATA-1", path1)
        try:
            df1 = pd.read_csv(path1,
                                encoding="utf-8",
                                parse_dates=[1,4],
                                dayfirst=True)
            print("DATA-1", df1.shape)
        except pd.errors.EmptyDataError:
            print("DATA-1", path1, "no data")
        for dir2 in check_dir:
            path2 = os.path.join(dir2, file)
            print("DATA-2", path2)
            try:
                df2 = pd.read_csv(path2,
                                    encoding="utf-8",
                                    parse_dates=[1,4],
                                    dayfirst=True)
                print("DATA-2", df2.shape)
            except pd.errors.EmptyDataError:
                print("DATA-2", path2, "no data")
            diff = pd.concat([df1,df2]).drop_duplicates(keep=False)
            print("DIFF", diff.shape)
            if len(diff) > 0 :
                print (diff.head())
