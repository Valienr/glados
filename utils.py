# -*- coding: utf-8 -*-
import os
import pandas as pd
import requests
import psycopg2
import datetime

def printer(subs, views):
    s1 = "{:,d}".format(subs) + " подписчиков! 🍾🎉🍾"
    s2 = "{:,d}".format(views) + " просмотов! 🎈🎈🎈"
    return f'{s1}\n{s2}'


# def get_rhyme():
#     conn = sqlite3.connect("mydatabase.db")  # или :memory: чтобы сохранить в RAM
#     cursor = conn.cursor()
#     cursor.execute('SELECT name, rhyme FROM "rhyme"')  # все таблицы
#     items = cursor.fetchall()
#     # print(items)
#     # print(len(items))
#     rand_max = len(items) - 1
#     return items[randint(0, rand_max)]


# def add_rhyme(name, rhyme):
#     conn = sqlite3.connect("mydatabase.db")  # или :memory: чтобы сохранить в RAM
#     cursor = conn.cursor()
#     cursor.execute(f"insert into rhyme (name, rhyme) values('{name}', '{rhyme}')")
#     conn.commit()


def show_day_statistic(database):
    conn = psycopg2.connect(database)
    df = pd.read_sql('select * from detektivo', conn)
    df = df.assign(datetime=df['datetime'] + datetime.timedelta(minutes=180))  # так мы хитро получаем московское время.
    today = df[df['datetime'].dt.date == pd.Timestamp.now().date()].sort_values(by='datetime')
    today = today.assign(datetime=today['datetime'].values.astype('datetime64[s]'))
    today = today.assign(time=today['datetime'].dt.time)

    today = today.assign(subscribers_shifted=today['subscribers'].shift(1),
                         views_shifted=today['views'].shift(1))

    today = today.assign(subscribers_hourly=today['subscribers'] - today['subscribers_shifted'],
                         views_hourly=today['views'] - today['views_shifted'])

    max_sub = today.loc[today['subscribers_hourly'] == today['subscribers_hourly'].max()]['time'].tolist()[0]
    max_view = today.loc[today['views_hourly'] == today['views_hourly'].max()]['time'].tolist()[0]

    stat_text = f"""
    Сегодня, в период с {today.iloc[0]['datetime'].hour} по {today.iloc[-1]['datetime'].hour}
    подписалось *{today.iloc[-1]['subscribers'] - today.iloc[0]['subscribers']}* человек.
    Больше всего просмотров было в {max_view.hour} часов, а подписок в {max_sub.hour} часов."""
    return stat_text


def get_yt_info(youtube_token, c_id='UCawxRTnNrCPlXHJRttupImA'):
    """

    :param c_id: youtube channel id
    :return: youtube channel subscribers and sum(views)
    """
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={c_id}&key={youtube_token}"
    data = requests.get(url)
    if data.status_code == 200:
        subs = int(data.json()['items'][0]['statistics']['subscriberCount'])
        views = int(data.json()['items'][0]['statistics']['viewCount'])
        return subs, views
    else:
        print(data.status_code)


def get_weather(weather_token, city_id=550280):  # Khimky
    res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                       params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': weather_token})
    data = res.json()
    res_text = f"температура: {data['main']['temp']}C, {data['weather'][0]['description']}"
    return res_text
