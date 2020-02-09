
from . htmlreader import HTMLreader

import http
import urllib.request
import numpy as np
import datetime
import re
from dateutil import tz
from time import time

def str2float(ary, omit='NA'):
    ary = np.array(ary)
    ary = np.where(ary == omit, '-999', ary)#.astype(float)
    ary = np.where(ary == '', '-999', ary).astype(float)
    ary[ary <= -999] = np.inf#np.nan
    return ary


def fetch_aprs_station(site, days):

    site = site.upper().strip()
    try:
        f = urllib.request.urlopen('https://weather.gladstonefamily.net/site/{}'.format(site))
        html = HTMLreader(f)

        info = html.findElement('h1')[0]
        info = info.getAllContent()[0]
        print(info)
        title = info
    except:
        title = site

    if site[1] == 'W':
        site = site.replace('W', '')
    
    url = 'https://weather.gladstonefamily.net/cgi-bin/wxobservations.pl?site={}&days={}&html=1'.format(site, days)
    print(url)
    f = urllib.request.urlopen(url)

    stime = time()
    html = HTMLreader(f)

    table = html.findElement('table')[0]

    temps = str2float(table[1:,2]).flatten()

    dew = str2float(table[1:,3]).flatten()

    wind = str2float(table[1:,5]).flatten()
    wind_dir_raw = str2float(table[1:,6]).flatten()

    dates = np.array(table[1:,0], dtype=np.object).flatten()

    pres = str2float(table[1:,1]).flatten()

    dt = []
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    for i, d in enumerate(dates):
        time_i = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
        time_i = time_i.replace(tzinfo=from_zone)
        time_i = time_i.astimezone(to_zone)
        dt.append(time_i)
        #print(time_i.strftime('%Y-%m-%d %H:%M:%S'))

    raw_hour_span = (dt[-1] - dt[0]).total_seconds()/3600
    label_hour_step = (raw_hour_span // 8) 

    if label_hour_step > 3:
        label_hour_step -= (label_hour_step % 3)

    label_delta = datetime.timedelta(hours=dt[0].hour % label_hour_step, 
                                     minutes=dt[0].minute, 
                                     seconds=dt[0].second,
                                     microseconds=dt[0].microsecond)

    start_time = (dt[0] - label_delta)
    time_span = (dt[-1] - start_time)
    hour_span = time_span.total_seconds()/3600

    xlabels = []
    xlabels_sec = []

    dates_sec = []
    for i, d in enumerate(dt):
        dates_sec.append((d-start_time).total_seconds())

    for h in range(int(hour_span/label_hour_step) +1):
        label = start_time + datetime.timedelta(hours=h*label_hour_step)
        xlabels_sec.append((label-start_time).total_seconds())
        xlabels.append(label.strftime('%m/%d %H:%M'))


    wind_dir = [None]*len(wind_dir_raw)
    wind_key = np.array([0, 45, 90, 135, 180, 225, 270, 315, 360])
    wind_val = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    for i, w in enumerate(wind_dir_raw):
        if np.isfinite(w):
            idx = np.argmin(w - wind_key)
            wind_dir[i] = wind_val[idx]
        else:
            wind[i] = 0
            wind_dir[i] = ''

    precip = None
    cond = None

    time_data = (dates_sec, start_time, xlabels, xlabels_sec)
    weather_data = (temps, dew, wind, wind_dir, cond, pres, precip)
    return title, time_data, weather_data




