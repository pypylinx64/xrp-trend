import pandas as pd


COL_OUT_DATE = 'date'
COL_OUT_PRICE = 'price'
COL_OUT_PREDICT = 'price_prediction'

MAP_COLS = {
    'date_format': COL_OUT_DATE,
    'prices': COL_OUT_PRICE,
}


def get_raw(url):

    df = None
    try:
        df = pd.read_json(url)

    except Exception as Exc:
        print(Exc)

    return df

# granul:
# 1 day = 5 min
# 2-90 days = 1 hour
# >90 days = 1 day
def get_data(
        key,
        days,
        interval='daily',
        ):
    
    url = ''

    if interval == 'granul':
        url = f"https://api.coingecko.com/api/v3/coins/ripple/market_chart?vs_currency=usd&days={days}&precision=full?accept=application/json&x-cg-demo-api-key={key}"
    if interval == 'daily':
        url = f"https://api.coingecko.com/api/v3/coins/ripple/market_chart?vs_currency=usd&days={days}&interval=daily&precision=full?accept=application/json&x-cg-demo-api-ke={key}"
    if interval == '':
        url = key

    df_raw = get_raw(url)

    df_concat = pd.DataFrame()
    cols = df_raw.columns
    for col in cols:
        df_split = pd.DataFrame(df_raw[col].to_list(), columns=['timestamp', col])
        df_concat = pd.concat([df_concat, df_split], axis=1)
    
    df_duplicate = df_concat.T.drop_duplicates().T
    df_duplicate['timestamp'] = df_duplicate['timestamp'].astype('Int64')

    return df_duplicate

def processing(
        raw_df,
        ):

    series_datetime = pd.to_datetime(raw_df['timestamp'], unit='ms')
    series_date = series_datetime.dt.strftime('%Y-%m-%d %H:%M:%S')
    raw_df['date_format'] = series_date

    rename_df = raw_df.rename(columns=MAP_COLS)
    slice_df = rename_df[list(MAP_COLS.values())]

    slice_df.index = slice_df[COL_OUT_DATE]
    slice_df = slice_df.drop(COL_OUT_DATE, axis=1)

    sort_df = slice_df.sort_index()
    data_na = sort_df.dropna()

    return data_na

def preparation(
        data,
        y_data,
        index_start,
        ):

    date_range_result = data.index[index_start:]
    predict_series = pd.Series(y_data, index=date_range_result, name=COL_OUT_PREDICT)
    data[COL_OUT_PREDICT] = predict_series
    data_slice = data[index_start:]

    return data_slice


if __name__ == '__main__':
    pass
