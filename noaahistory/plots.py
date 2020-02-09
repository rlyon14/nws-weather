
import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import markerplot
import matplotlib
import tkinter
import re

from . nws_weather import fetch_nws_station
from . aprs_weather import fetch_aprs_station

def plot_nws(plotloc='longmont'):
    loc = dict(
        boulder = 'KBDU',
        leesburg = 'KJYO',
        provo = 'KPVU',
        longmont = 'KLMO',
        bend = 'KBDN',
    )

    matplotlib.use('Qt5Agg')
    site = loc[plotloc] if plotloc in loc else plotloc

    ## fetch and unpack data
    title, time_data, weather_data = fetch_nws_station(site)
    (dates_sec, start_time, xlabels, xlabels_sec) = time_data
    (temps, dew, wind, wind_dir, cond, pres, precip) = weather_data

    ## formatting functions for markers
    def xdata_to_timestamp(sec):
        dt = start_time + datetime.timedelta(seconds=sec)
        return dt.strftime('%m/%d %H:%M')

    def xydata_to_wind(sec, ydata, idx=None):
        idx = np.argmin(np.abs(dates_sec - sec))
        if wind[idx] > 0:
            return '{}{:.0f}\n{}'.format(wind_dir[idx], wind[idx], cond[idx].strip())
        else:
            return cond[idx].strip()

    ## create plots
    fig, (ax1, ax2) = plt.subplots(2, 1, constrained_layout=True, figsize=(18 ,9))
    par1 = ax1.twinx()
    ax1.grid(linewidth=0.5, linestyle='-')
    plt.title('3 Day History for {} ({})'.format(title, site))

    ##precip plot
    max_precip = np.nanmax(precip) if np.any(np.isfinite(precip)) else 0
    m, s, b0 = par1.stem(dates_sec, precip, 'b', linefmt='-', markerfmt='b.', basefmt=' ', use_line_collection=True, label='precip (in)')

    par1.set_ylim([0, max_precip*4 + 0.1])
    plt.sca(ax1)
    plt.xticks(xlabels_sec, xlabels, fontsize='small')

    ## temperature and dew point
    ax1.plot(dates_sec, temps, 'r', label = 'temp (F)')
    ax1.plot(dates_sec, dew, 'g', label = 'dewpnt (F)')
    
    ax1.legend(fontsize='small', loc='upper left')
    par1.legend(fontsize='small', loc='upper right')

    ## wind
    par2 = ax2.twinx()
    ax2.grid(linewidth=0.5, linestyle='-')
    
    plt.sca(ax2)
    plt.xticks(xlabels_sec, xlabels, fontsize='small')
    
    m1, s1, b1 = ax2.stem(dates_sec, wind, 'b', label = 'max wind (mph)', markerfmt='.', basefmt=' ', use_line_collection=True)
    line = par2.plot(dates_sec, pres, 'gray', label = 'pres (inHg)')

    ## set up markers
    fig.marker_enable(xreversed=True, xformat=xdata_to_timestamp, show_dot=True, show_xlabel=True, top_axes=(ax1, ax2))
    ax1.marker_ignore(b0)
    ax2.marker_ignore(b1, line[0])

    ax2.marker_set_params(yformat=xydata_to_wind)

    ax2.marker_link(ax1)
    ax1.marker_add(xd=dates_sec[0])
    ax2.marker_add(xd=dates_sec[0])

    ax2.legend(fontsize='small', loc='upper left')
    par2.legend(fontsize='small', loc='upper right')

    plt.show()


def plot_aprs(site, days=7):
    
    matplotlib.use('Qt5Agg')

    ## fetch and unpack data
    title, time_data, weather_data = fetch_aprs_station(site, days)
    (dates_sec, start_time, xlabels, xlabels_sec) = time_data
    (temps, dew, wind, wind_dir, cond, pres, precip) = weather_data

    ## formatting functions for markers
    def xdata_to_timestamp(sec):
        dt = start_time + datetime.timedelta(seconds=sec)
        return dt.strftime('%m/%d %H:%M')

    def xydata_to_wind(sec, ydata, idx=None):
        idx = np.argmin(np.abs(dates_sec - sec))
        if wind[idx] > 0:
            return '{} {:.0f}'.format(wind_dir[idx], wind[idx])
        else:
            return ''

    ## create plots
    fig, (ax1, ax2) = plt.subplots(2, 1, constrained_layout=True, figsize=(18 ,9))
    ax1.grid(linewidth=0.5, linestyle='-')
    
    plt.sca(ax1)
    plt.title(title)
    plt.xticks(xlabels_sec, xlabels, fontsize='small')

    ## temperature and dew point
    ax1.plot(dates_sec, temps, 'r', label = 'temp (F)')
    ax1.plot(dates_sec, dew, 'g', label = 'dewpnt (F)')
    
    ax1.legend(fontsize='small', loc='upper left')

    ## wind
    par2 = ax2.twinx()
    ax2.grid(linewidth=0.5, linestyle='-')
    
    plt.sca(ax2)
    plt.xticks(xlabels_sec, xlabels, fontsize='small')
    
    m1, s1, b1 = ax2.stem(dates_sec, wind, 'b', label = 'max wind (mph)', markerfmt='.', basefmt=' ', use_line_collection=True)

    line = par2.plot(dates_sec, pres, 'gray', label = 'pres (mbar)')

    fig.marker_enable(xformat=xdata_to_timestamp, show_dot=True, show_xlabel=True, top_axes=(ax1, ax2))
    ax2.marker_ignore(b1, line[0])

    ax2.marker_set_params(yformat=xydata_to_wind)

    ax2.marker_link(ax1)
    ax1.marker_add(xd=dates_sec[-1])
    ax2.marker_add(xd=dates_sec[-1])

    ax2.legend(fontsize='small', loc='upper left')
    par2.legend(fontsize='small', loc='upper right')


if __name__ == '__main__':
    #p = plot_nws('KLMO')
    p = plot_aprs('EW1488', days=3)
    plt.show()