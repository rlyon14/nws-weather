from . htmlreader import HTMLreader
from pathlib import Path
import http
import urllib.request
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
#from cursorplot import Plotter
from markerplot import interactive_subplots
import matplotlib
import tkinter
import re


def plotAirQuality():
    now = datetime.now()
    epoch = datetime.utcfromtimestamp(0)
    strt = float((now-epoch).total_seconds())

    date_3 = now - timedelta(days=3)

    pm2_5 = np.array([])
    pm10 = np.array([])
    oz = np.array([])
    dt = np.array([])

    for i in range(3):
        date = date_3 + timedelta(days=i+1)
        date1 = date_3 + timedelta(days=i+2)
        date_str = date.strftime('%m/%d/%Y')
        date_str1 = date1.strftime('%m/%d/%Y')
        print(date_str)
        date_encode = urllib.parse.quote(date_str, safe='')
        f = urllib.request.urlopen(r'https://www.colorado.gov/airquality/site.aspx?aqsid=080130003&seeddate='+date_encode)
        html = HTMLreader(f)

        data_summary = html.findElement('div', 'id','divSummaryData')[0]
        table = data_summary.findElement('table', 'class', 'output1')[0]
        f = urllib.request.urlopen(r'https://www.colorado.gov/airquality/site.aspx?aqsid=080130014&seeddate='+date_encode)
        html = HTMLreader(f)
        data_summary = html.findElement('div', 'id','divSummaryData')[0]
        table_oz = data_summary.findElement('table', 'class', 'output1')[0]

        pm2_5_t = np.array(table[1:, 2], dtype='<U4').flatten()#.astype(int)
        pm2_5_t[pm2_5_t == ''] = "-1"
        pm2_5 = np.concatenate((pm2_5, pm2_5_t.astype(int)), axis=0)
        date = np.array([date_str + ' ']*len(pm2_5_t))
        date[-1] = date_str1 + ' '

        pm10_t = np.array(table[1:, 1], dtype='<U4').flatten()#.astype(int)
        pm10_t[pm10_t == ''] = "-1"
        pm10 = np.concatenate((pm10, pm10_t.astype(int)), axis=0)

        oz_t = np.array(table_oz[1:, 1], dtype='<U4').flatten()#.astype(int)
        oz_t[oz_t == ''] = "-1"
        oz = np.concatenate((oz, oz_t.astype(int)), axis=0)

        times = np.array(table[1:, 0], dtype=str).flatten()

        dt = np.concatenate((dt, np.core.defchararray.add(date, times)), axis=0)

    pm2_5[pm2_5 < 0] =np.inf
    pm10[pm10 < 0] =np.inf
    oz[oz < 0] =np.inf

    plot_ts = []
    show_ts = []
    xlabels = []
    xlabel_loc = []
    hour = -1
    for i, d in enumerate(dt):
        dt = datetime.strptime(d, '%m/%d/%Y %I:%M %p')
        if (hour != dt.hour and (dt.hour == 0 or dt.hour == 12)):
            hour = dt.hour
            xlabel_loc.append((dt-epoch).total_seconds())
            xlabels.append(dt.strftime('%m/%d %H:%M'))
        
        plot_ts.append((dt-epoch).total_seconds())
        show_ts.append(dt.strftime('%m/%d %H:%M'))

    def xdata_to_timestamp(sec):
        idx = np.argmin(np.abs(plot_ts - sec))
        return show_ts[idx]

    fig, ax = interactive_subplots(1, 1, constrained_layout=True, figsize=(14,7))
    fig.marker_enable(xreversed=False, show_xlabel=True, xformat=xdata_to_timestamp)
    ax.grid(linewidth=0.5, linestyle='-')

    #p = MarkerPlot(1,1, xDisplay=show_ts, figsize=(14,7))
    #ax = p.axes[0]
    plt.sca(ax)
    plt.xticks(xlabel_loc, xlabels)

    ax.plot(plot_ts, pm2_5, color='darkBlue', label='PM2.5 ($\mu$g/m$^3$)')

    ax.plot(plot_ts, pm10, color='darkGreen', label='PM10 ($\mu$g/m$^3$)')
    #ax.plot(plot_ts, oz, color='darkOrange', label='O3 (ppb)')
    #ax.legend()

    #ax = p.axes[1]

    plt.legend(fontsize='small', loc='best')
    plt.title('3 Day history for {}'.format('Longmont air quality'))
    #plt.show()
    return ax

if __name__ == "__main__":
    p = plotAirQuality()
    plt.show()