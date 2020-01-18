
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

def str2float(ary, omit='NA'):
    ary = np.array(ary)
    ary = np.where(ary == omit, '-999', ary)#.astype(float)
    ary = np.where(ary == '', '-999', ary).astype(float)
    ary[ary <= -999] = np.inf#np.nan
    return ary


def plotTemp(plotloc='longmont'):
    loc = dict(
        boulder = 'KBDU',
        leesburg = 'KJYO',
        provo = 'KPVU',
        longmont = 'KLMO',
        bend = 'KBDN',
    )

    matplotlib.use('Qt5Agg')
    site = loc[plotloc] if plotloc in loc else plotloc
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
    precip_nan = np.where(precip == np.inf, np.nan, precip)
    max_precip = np.nanmax(precip_nan) if np.any(np.isfinite(precip_nan)) else 0

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
        #dates.append(dt_i)
        dates_sec.append((dt_i-start_time).total_seconds())

    def xdata_to_timestamp(sec):
        dt = start_time + datetime.timedelta(seconds=sec)
        return dt.strftime('%m/%d %H:%M')
    
    wind = np.zeros(shape=wind_str.shape)
    wind_dir = [None]*len(wind_str)
    for i, w in enumerate(wind[:-1]):
        val = re.findall(r'\d+', wind_str[i])
        wind[i] = float(val[-1]) if len(val) > 0 else 0
        
        wind_ary = wind_str[i].split()
        wind_dir[i] =  wind_ary[0].upper().strip() +' ' if wind[i] != 0 else ''

    def xydata_to_wind(sec, ydata, idx=None):
        idx = np.argmin(np.abs(dates_sec - sec))
        if wind[idx] > 0:
            return '{}{:.0f}\n{}'.format(wind_dir[idx], wind[idx], cond[idx].strip())
        else:
            return cond[idx].strip()

    def plot_temp():
        fig, (ax1, ax2) = plt.subplots(2, 1, constrained_layout=True, figsize=(18 ,9))

        par1 = ax1.twinx()

        ax1.grid(linewidth=0.5, linestyle='-')

        m, s, b0 = par1.stem(dates_sec, precip, 'b', linefmt='-', markerfmt='b.', basefmt=' ', use_line_collection=True, label='precip (in)')

        par1.set_ylim([0, max_precip*4 + 0.1])
        plt.sca(ax1)
        plt.xticks(xlabels_sec, xlabels, fontsize='small')

        ax1.plot(dates_sec, temps, 'r', label = 'temp (F)')
        ax1.plot(dates_sec, dew, 'g', label = 'dewpnt (F)')
        
        ax1.legend(fontsize='small', loc='upper left')
        par1.legend(fontsize='small', loc='upper right')
    
        plt.title('3 Day History for {} ({})'.format(title, site))

        ## wind
        par2 = ax2.twinx()
        ax2.grid(linewidth=0.5, linestyle='-')
        
        plt.sca(ax2)
        plt.xticks(xlabels_sec, xlabels, fontsize='small')
        
        m1, s1, b1 = ax2.stem(dates_sec, wind, 'b', label = 'max wind (mph)', markerfmt='.', basefmt=' ', use_line_collection=True)


        line = par2.plot(dates_sec, pres, 'gray', label = 'pres (inHg)')

        fig.marker_enable(xreversed=True, xformat=xdata_to_timestamp, show_dot=True, show_xlabel=True, top_axes=(ax1, ax2))
        ax1.marker_ignore(b0)
        ax2.marker_ignore(b1, line[0])

        ax2.marker_set_params(yformat=xydata_to_wind)

        ax2.marker_link(ax1)
        ax1.marker_add(xd=dates_sec[0])
        ax2.marker_add(xd=dates_sec[0])

        ax2.legend(fontsize='small', loc='upper left')
        par2.legend(fontsize='small', loc='upper right')
    
    plot_temp()
