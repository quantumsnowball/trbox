from pandas import DataFrame, read_csv


def import_yahoo_csv(path: str) -> DataFrame:
    df = read_csv(path,
                  index_col='Date',
                  parse_dates=True)
    if 'Close' in df.columns and 'Adj Close' in df.columns:
        df.drop('Close', axis=1, inplace=True)
        df.rename({'Adj Close': 'Close'}, axis=1, inplace=True)
    return df
