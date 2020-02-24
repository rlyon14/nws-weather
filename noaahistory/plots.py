
import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import markerplot
from markerplot import interactive_subplots
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

    def xydata_to_wind(sec, ydata, mxd=None):
        idx = np.argmin(np.abs(dates_sec - sec))
        if wind[idx] > 0:
            return '{}{:.0f}\n{}'.format(wind_dir[idx], wind[idx], cond[idx].strip())
        else:
            return cond[idx].strip()

    ## create plots
    app, fig, (ax1, ax2) = interactive_subplots(2, 1, figsize=(18 ,9), constrained_layout=True, )
    par1 = ax1.twinx()
    ax1.grid(linewidth=0.5, linestyle='-')
    ax1.set_title('3 Day History for {} ({})'.format(title, site))

    ##precip plot
    max_precip = np.nanmax(precip) if np.any(np.isfinite(precip)) else 0
    m, s, b0 = par1.stem(dates_sec, precip, 'b', linefmt='-', markerfmt='b.', basefmt=' ', use_line_collection=True, label='precip (in)')

    par1.set_ylim([0, max_precip*4 + 0.1])
    #plt.sca(ax1)
    ax1.set_xticks(xlabels_sec)
    ax1.set_xticklabels(xlabels)
    ax1.tick_params(labelsize='small')

    ## temperature and dew point
    ax1.plot(dates_sec, temps, 'r', label = 'temp (F)')
    ax1.plot(dates_sec, dew, 'g', label = 'dewpnt (F)')
    
    ax1.legend(fontsize='small', loc='upper left')
    par1.legend(fontsize='small', loc='upper right')

    ## wind
    par2 = ax2.twinx()
    ax2.grid(linewidth=0.5, linestyle='-')
    
    #plt.sca(ax2)
    ax2.set_xticks(xlabels_sec)
    ax1.set_xticklabels(xlabels)
    ax2.tick_params(labelsize='small')
    
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

    app.show()


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

    def xydata_to_wind(sec, ydata, mxd=None):
        idx = np.argmin(np.abs(dates_sec - sec))
        if wind[idx] > 0:
            return '{} {:.0f}'.format(wind_dir[idx], wind[idx])
        else:
            return ''

    ## create plots
    app, fig, (ax1, ax2) = interactive_subplots(2, 1, figsize=(18 ,9), constrained_layout=True)
    ax1.grid(linewidth=0.5, linestyle='-')
    
    #plt.sca(ax1)
    ax1.set_title(title)

    ax1.set_xticks(xlabels_sec)
    ax1.set_xticklabels(xlabels)
    ax1.tick_params(labelsize='small')

    ## temperature and dew point
    ax1.plot(dates_sec, temps, 'r', label = 'temp (F)')
    ax1.plot(dates_sec, dew, 'g', label = 'dewpnt (F)')
    
    ax1.legend(fontsize='small', loc='upper left')

    ## wind
    par2 = ax2.twinx()
    ax2.grid(linewidth=0.5, linestyle='-')
    
    #plt.sca(ax2)
    ax2.set_xticks(xlabels_sec)
    ax2.set_xticklabels(xlabels)
    ax2.tick_params(labelsize='small')
    
    #m1, s1, b1 = ax2.stem(dates_sec, wind, 'b', label = 'max wind (mph)', markerfmt='.', basefmt=' ', use_line_collection=True)
    ax2.plot(dates_sec, wind, 'b', label = 'max wind (mph)')

    line = par2.plot(dates_sec, pres, 'gray', label = 'pres (mbar)')

    fig.marker_enable(xformat=xdata_to_timestamp, show_dot=True, show_xlabel=True, top_axes=(ax1, ax2))
    #ax2.marker_ignore(b1, line[0])
    ax2.marker_ignore(line[0])

    ax2.marker_set_params(yformat=xydata_to_wind)

    ax2.marker_link(ax1)
    ax1.marker_add(xd=dates_sec[-1])
    ax2.marker_add(xd=dates_sec[-1])

    ax2.legend(fontsize='small', loc='upper left')
    #par2.legend(fontsize='small', loc='upper right')
    app.show()


def plot_compare(*sites, days=3):
    matplotlib.use('Qt5Agg')
    titles = [None]*len(sites)
    time_dataz = [None]*len(sites)
    weather_dataz = [None]*len(sites) 

    for i, site in enumerate(sites):
        if site[0] == 'K' and len(site.strip()) == 4:
            titles[i], time_dataz[i], weather_dataz[i] = fetch_nws_station(site)
        else:
            titles[i], time_dataz[i], weather_dataz[i]  = fetch_aprs_station(site, days)

    app, fig, (ax1) = interactive_subplots(1, 1, figsize=(18 ,9), constrained_layout=True)
    ax1.grid(linewidth=0.5, linestyle='-')

    ## find earliest start time
    start_idx = 0
    start = time_dataz[0][1]
    epoch = datetime.datetime.utcfromtimestamp(0)
    max_points = 0
    for i, dt in enumerate(time_dataz):
        (dates_sec, start_time, xlabels, xlabels_sec) = dt
        start_time = start_time.replace(tzinfo=None)
        start = start.replace(tzinfo=None)
        if (start_time < start):
            start = start_time
            start_idx = i
        if len(dates_sec) > max_points:
            max_points = len(dates_sec)


    ax1.set_xticks(time_dataz[start_idx][3])
    ax1.set_xticklabels(time_dataz[start_idx][2])
    ax1.tick_params(labelsize='small')
    titles = list(titles)

    ## adjust other time data to new reference
    for i, dt in enumerate(time_dataz):
        titles[i] = titles[i].split(') in')[-1].strip()
        (dates_sec_t, start_time_t, xlabels, xlabels_sec) = time_dataz[i]
        (temps, dew, wind, wind_dir, cond, pres, precip) = weather_dataz[i]

        dates_sec = np.array(dates_sec_t)
        data = np.array(temps)

        if site[0] == 'K' and len(site.strip()) == 4:
            dates_sec = np.flip(dates_sec)
            data = np.flip(data)

        if i != start_idx: 
            start_time_t = start_time.replace(tzinfo=None)
            start = start.replace(tzinfo=None)
            delta = (start_time_t - start).total_seconds()
            dates_sec += delta

        ax1.plot(dates_sec, data, label = '{} ({}) $\degree$F'.format(titles[i], sites[i]))

    def xdata_to_timestamp(sec):
        dt = start + datetime.timedelta(seconds=sec)
        return dt.strftime('%m/%d %H:%M')

    ax1.legend(fontsize='small', loc='upper left')  
    fig.marker_enable(xformat=xdata_to_timestamp, show_dot=True, show_xlabel=True)
    app.show()
    #ax1.marker_add(xd=dates_sec[-1])


if __name__ == '__main__':
    #p = plot_nws('KLMO')
    #plot_aprs('EW0013')
    plot_compare('KLMO', 'KSLC', 'KPVU',days=3)
    #plt.show()