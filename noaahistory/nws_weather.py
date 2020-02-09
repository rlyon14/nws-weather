

from . htmlreader import HTMLreader

import http
import urllib.request
import numpy as np
import datetime
import re

def str2float(ary, omit='NA'):
    ary = np.array(ary)
    ary = np.where(ary == omit, '-999', ary)#.astype(float)
    ary = np.where(ary == '', '-999', ary).astype(float)
    ary[ary <= -999] = np.inf#np.nan
    return ary


def fetch_nws_station(site):

    site = site.upper().strip()
    f = urllib.request.urlopen('https://w1.weather.gov/data/obhistory/{}.html'.format(site))
    html = HTMLreader(f)
    table = html.findElement('table', 'cellspacing','3')[0]
    try:
        title = html.findElement('title')
        title = title[0].getAllContent()[0].split(':')
        title = title[2].strip()
        print(title)
    
    except:
        title = ''

    temps = str2float(table[3:,6]).flatten()
    dew = str2float(table[3:,7]).flatten()

    wind_str = np.array(table[3:,2]).flatten()
    cond = np.array(table[3:,4]).flatten()

    dates = np.array(table[3:,0], dtype=np.object).flatten()
    times = np.array(table[3:,1], dtype=np.object).flatten()

    pres = str2float(table[3:,13]).flatten()
    precip = str2float(table[3:,15]).flatten()
    precip = np.where(precip <= 0, np.inf, precip)
    precip = np.where(precip == np.inf, np.nan, precip)

    ts = []
    xlabels = []
    xlabels_sec = []

    now = datetime.datetime.now()
    date_3 = now - datetime.timedelta(days=3)
    
    label_hour_step = 6
    label_delta = datetime.timedelta(hours=date_3.hour % label_hour_step, 
                                     minutes=date_3.minute, 
                                     seconds=date_3.second,
                                     microseconds=date_3.microsecond)

    start_time = (date_3 - label_delta)

    for h in range(int(72/label_hour_step) +1):
        label = start_time + datetime.timedelta(hours=h*label_hour_step)
        xlabels_sec.append((label-start_time).total_seconds())
        xlabels.append(label.strftime('%m/%d %H:%M'))
    
    xlabels = list(np.flip(xlabels, axis=0))
    xlabels_sec = list(np.flip(xlabels_sec, axis=0))

    days = [start_time + datetime.timedelta(days=i) for i in range(4)]
    days_idx = [dt.day for dt in days]
    dates_sec = []

    for i, d in enumerate(dates):
        idx = days_idx.index(int(d))
        day_i = days[idx]
        time_i = datetime.datetime.strptime(times[i], '%H:%M')
        dt_i = day_i.replace(hour=time_i.hour, minute=time_i.minute)
        dates_sec.append((dt_i-start_time).total_seconds())
    
    wind = np.zeros(shape=wind_str.shape)
    wind_dir = [None]*len(wind_str)
    for i, w in enumerate(wind[:-1]):
        val = re.findall(r'\d+', wind_str[i])
        wind[i] = float(val[-1]) if len(val) > 0 else 0
        
        wind_ary = wind_str[i].split()
        wind_dir[i] =  wind_ary[0].upper().strip() +' ' if wind[i] != 0 else ''

    time_data = (dates_sec, start_time, xlabels, xlabels_sec)
    weather_data = (temps, dew, wind, wind_dir, cond, pres, precip)
    return title, time_data, weather_data


