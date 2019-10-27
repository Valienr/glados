# -*- coding: utf-8 -*-
import pandas as pd
import requests
import psycopg2
import datetime
import matplotlib.pyplot as plt
from matplotlib import ticker


def printer(subs: int, views: int) -> str:
    """

    :param subs:
    :param views:
    :return:
    """

    s1 = "{:,d}".format(subs) + " подписчиков! 🍾🎉🍾"
    s2 = "{:,d}".format(views) + " просмотов! 🎈🎈🎈"
    return f'{s1}\n{s2}'


def get_yt_info(youtube_token: str, c_id: str = 'UCawxRTnNrCPlXHJRttupImA') -> (int, int):
    """

    :param youtube_token: youtube api token
    :param c_id: youtube channel id
    :return: youtube channel subscribers and sum(all videos views)
    """
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={c_id}&key={youtube_token}"
    data = requests.get(url)
    if data.status_code == 200:
        subs = int(data.json()['items'][0]['statistics']['subscriberCount'])
        views = int(data.json()['items'][0]['statistics']['viewCount'])
        return subs, views
    else:
        print(data.status_code)


def _get_db_data(database: str, quary_name: str = 'day', period=None, depth: int = 1, tz: int = 3) -> pd.DataFrame:
    """

    :param database: database connection string
    :param depth_days: how many days ago you need to get from DB
    :param tz: correct timezone from UTC to GMT +3 (Russia/Moscow)
    :return: result dataframe
    """
    conn = psycopg2.connect(database)
    with open(f'./sql_queries/{quary_name}.sql', encoding='utf-8', mode='r') as o:
        query = o.read()
    query = query.format(tz, depth, period)
    # print(query)
    df = pd.read_sql(query, conn)
    return df


def day_stat(database):
    df = _get_db_data(database, quary_name='day', depth=1)
    df.loc[df['views'] < 0, ['views']] = None
    df = df.fillna(method='backfill')
    res = pd.DataFrame(index=list(range(0, 24)))
    for i in df['day'].unique():
        temp_df = df.loc[df['day'] == i][['subscribers', 'views', 'hour']].set_index('hour').add_suffix(f'_{int(i)}')
        res = pd.merge(res, temp_df, how='outer', left_index=True, right_index=True)
    return res


def week_stat(database):
    df = _get_db_data(database, quary_name='ststistic_query', period='week')
    df.loc[df['views'] < 0, ['views']] = None
    df = df.fillna(method='backfill')
    df['dayofweek'] = df['dayofweek'].astype(int)
    res = pd.DataFrame(index=list(range(1, 8)))
    for i in df['week'].unique():
        temp_df = df.loc[df['week'] == i][[
            #             'subscribers',
            'views', 'day', 'dayofweek']].set_index('dayofweek').add_suffix(f'_{int(i)}')
        res = pd.merge(res, temp_df, how='outer', left_index=True, right_index=True)
    return res


def month_stat(database):
    df = _get_db_data(database, quary_name='ststistic_query', period='month')
    df.loc[df['views'] < 0, ['views']] = None
    df = df.fillna(method='backfill')
    res = pd.DataFrame(index=list(range(1, 32)))
    for i in df['month'].unique():
        temp_df = df.loc[df['month'] == i][[
            #             'subscribers',
            'views', 'day']].set_index('day').add_suffix(f'_{int(i)}')
        res = pd.merge(res, temp_df, how='outer', left_index=True, right_index=True)

    return res


def _make_picture(df: pd.DataFrame):
    name = 'day'
    df = df.filter(like='views')
    x = df.index.values
    if df.shape[0] == 7:
        name = 'week'
    elif df.shape[0] == 31:
        name = 'month'
    print(name)

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    width = 3
    for i in df.columns:
        ax.plot(x, df[i], label=i, linewidth=width)
        width += 5
    ax.set(xlim=[x.min(), x.max()])
    ax.set_xlabel('hour', fontsize=15, )
    ax.set_ylabel('views', fontsize=15, )
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    leg = plt.legend()

    plt.savefig(f'{name}.png')



