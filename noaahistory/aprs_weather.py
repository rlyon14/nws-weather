
from . htmlreader import HTMLreader
import http
import urllib.request
import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import markerplot
import matplotlib
import tkinter
import re
from dateutil import tz
from time import time

def str2float(ary, omit='NA'):
    ary = np.array(ary)
    ary = np.where(ary == omit, '-999', ary)#.astype(float)
    ary = np.where(ary == '', '-999', ary).astype(float)
    ary[ary <= -999] = np.inf#np.nan
    return ary


def plotAPRS(site, days=7):

    try:
        f = urllib.request.urlopen('https://weather.gladstonefamily.net/site/{}'.format(site))
        html = HTMLreader(f)

        info = html.findElement('h1')[0]
        info = info.getAllContent()[0]
        print(info)
        title = info
    except:
        title = site

    matplotlib.use('Qt5Agg')
    f = urllib.request.urlopen('https://weather.gladstonefamily.net/cgi-bin/wxobservations.pl?site={}&days={}&html=1'.format(site, days))

    stime = time()
    html = HTMLreader(f)
    print(time()-stime)

    #html.head.printNode(r'C:\Users\rlyon\packages\noaahistory\trunk\noaahistory\test.html')
    table = html.findElement('table')[0]

    temps = str2float(table[1:,2]).flatten()

    dew = str2float(table[1:,3]).flatten()

    wind_mph = str2float(table[1:,5]).flatten()
    wind_dir = str2float(table[1:,6]).flatten()

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
    print(label_hour_step)
    if label_hour_step > 3:
        label_hour_step -= (label_hour_step % 3)
    print(label_hour_step)
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

    # xlabels = list(np.flip(xlabels, axis=0))
    # xlabels_sec = list(np.flip(xlabels_sec, axis=0))

    def xdata_to_timestamp(sec):
        dt = start_time + datetime.timedelta(seconds=sec)
        return dt.strftime('%m/%d %H:%M')

    wind_str = [None]*len(wind_dir)
    wind_key = np.array([0, 45, 90, 135, 180, 225, 270, 315, 360])
    wind_val = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    for i, w in enumerate(wind_dir):
        if np.isfinite(w):
            idx = np.argmin(w - wind_key)
            wind_str[i] = wind_val[idx]
        else:
            wind_mph[i] = 0
            wind_str[i] = ''

    def xydata_to_wind(sec, ydata, idx=None):
        idx = np.argmin(np.abs(dates_sec - sec))
        if wind_mph[idx] > 0:
            return '{} {:.0f}'.format(wind_str[idx], wind_mph[idx])
        else:
            return ''

    def plot_temp():
        fig, (ax1, ax2) = plt.subplots(2, 1, constrained_layout=True, figsize=(18 ,9))

        ax1.grid(linewidth=0.5, linestyle='-')

        plt.sca(ax1)
        plt.xticks(xlabels_sec, xlabels, fontsize='small')

        ax1.plot(dates_sec, temps, 'r', label = 'temp (F)')
        ax1.plot(dates_sec, dew, 'g', label = 'dewpnt (F)')
        
        ax1.legend(fontsize='small', loc='upper left')
    
        plt.title(title)

        ## wind
        par2 = ax2.twinx()
        ax2.grid(linewidth=0.5, linestyle='-')
        
        plt.sca(ax2)
        plt.xticks(xlabels_sec, xlabels, fontsize='small')
        
        m1, s1, b1 = ax2.stem(dates_sec, wind_mph, 'b', label = 'max wind (mph)', markerfmt='.', basefmt=' ', use_line_collection=True)


        line = par2.plot(dates_sec, pres, 'gray', label = 'pres (mbar)')

        fig.marker_enable(xformat=xdata_to_timestamp, show_dot=True, show_xlabel=True, top_axes=(ax1, ax2))
        ax2.marker_ignore(b1, line[0])

        ax2.marker_set_params(yformat=xydata_to_wind)

        ax2.marker_link(ax1)
        ax1.marker_add(xd=dates_sec[-1])
        ax2.marker_add(xd=dates_sec[-1])

        ax2.legend(fontsize='small', loc='upper left')
        par2.legend(fontsize='small', loc='upper right')
    
    plot_temp()


if __name__ == '__main__':
    #p = plotTemp('E1488')
    p = plotAPRS('E4897', days=1)
    plt.show()

