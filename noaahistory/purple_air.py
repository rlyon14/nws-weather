
import http
import urllib.request
import numpy as np
import datetime
import re
import json
import markerplot
import matplotlib.pyplot as plt
from dateutil import tz
import configparser
from pathlib import Path
from markerplot import interactive_subplots

def query_sensor_data(name, days=1, sensor='primary'):
    dir_ = Path(__file__).parent

    config = configparser.ConfigParser()
    config.read(dir_ / 'air_keys.ini')
    
    channel_id = config[name]['{}_id'.format(sensor)]
    api_key = config[name]['{}_key'.format(sensor)]
    
    data = urllib.request.urlopen(r'https://api.thingspeak.com/channels/{}/feeds.json?api_key={}&days={}'.format(channel_id, api_key, days)).read().decode('utf-8')
    
    return json.loads(data), config[name]['station_label']

def parse_sensor_data(data):
    l_feeds = len(data['feeds'])
    xlabels = []
    xlabels_sec = []
    dt = []

    dates_sec = []
    pm2p5 = np.zeros(l_feeds)
    pm10 = np.zeros(l_feeds)
    pm1p0 = np.zeros(l_feeds)

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    for i, f in enumerate(data['feeds']):
        time_i = datetime.datetime.fromisoformat(f['created_at'][:-1])
        time_i = time_i.replace(tzinfo=from_zone)
        time_i = time_i.astimezone(to_zone)
        dt.append(time_i)

        pm2p5[i] = float(f['field2'])
        pm10[i] = float(f['field3'])
        pm1p0[i] = float(f['field1'])

    raw_hour_span = (dt[-1] - dt[0]).total_seconds()/3600
    label_hour_step = (raw_hour_span // 6) 

    if label_hour_step > 3:
        label_hour_step -= (label_hour_step % 3)

    if label_hour_step > 12:
        label_hour_step -= (label_hour_step % 12)

    if label_hour_step > 24:
        label_hour_step -= (label_hour_step % 24)

    label_delta = datetime.timedelta(hours=dt[0].hour % label_hour_step, 
                                     minutes=dt[0].minute, 
                                     seconds=dt[0].second,
                                     microseconds=dt[0].microsecond)

    start_time = (dt[0] - label_delta)
    time_span = (dt[-1] - start_time)
    hour_span = time_span.total_seconds()/3600

    for i, d in enumerate(dt):
        dates_sec.append((d-start_time).total_seconds())

    for h in range(int(hour_span/label_hour_step) +1):
        label = start_time + datetime.timedelta(hours=h*label_hour_step)
        xlabels_sec.append((label-start_time).total_seconds())
        xlabels.append(label.strftime('%m/%d %H:%M'))

    time_data = (start_time, xlabels, xlabels_sec)
    air_data = (dates_sec, pm2p5, pm10, pm1p0)
    return time_data, air_data

def get_plot_data(name, days=1, sensor='primary'):
    data, label = query_sensor_data(name, days, sensor)
    time_data, air_data = parse_sensor_data(data)
    return time_data, air_data, label
    
def create_plot(time_data, title=''):
    start_time, xlabels, xlabels_sec = time_data
    
    fig, ax1 = interactive_subplots(figsize=(15,9), constrained_layout=False)
    fig.marker_enable()
    
    def xdata_to_timestamp(sec):
        dt = start_time + datetime.timedelta(seconds=sec)
        return dt.strftime('%m/%d %H:%M')
    
    ax1.marker_set_params(xformat=xdata_to_timestamp, xreversed=False, show_xlabel=True)
    ax1.grid(linewidth=0.5, linestyle='-')

    ax1.set_title(title)
    
    ax1.set_xticks(xlabels_sec)
    ax1.set_xticklabels(xlabels)
    ax1.tick_params(labelsize='small')
    ax1.set_ylabel('PM2.5 ($\mu g / m^3$)')

    ax1.axhspan(0, 12, color='green', alpha=0.3)
    ax1.axhspan(12, 35, color='yellow', alpha=0.3)
    ax1.axhspan(35, 55, color='orange', alpha=0.35)
    ax1.axhspan(55, 150, facecolor='red', alpha=0.3)
    ax1.axhspan(150, 250, facecolor='purple', alpha=0.3)
    ax1.axhspan(250, 500, facecolor='maroon', alpha=0.3)
    
    return ax1
    

def plot_air_data(axes, air_data, label='', color=None, alpha=None, marker=False):
    
    dates_sec, pm2p5, pm10, pm1p0 = air_data
    
    l1 = axes.plot(dates_sec, pm2p5, label=label, color=color, alpha=alpha)
    #l1 = axes.plot(dates_sec, pm10, color='gray', alpha=0.5, label='PM10 ($\mu g / m^3$)')
    #axes.marker_ignore(*l1)
    
    if marker:
        axes.marker_add(xd=dates_sec[-1])
        axes.set_xlim([dates_sec[0] -5000, dates_sec[-1] + 5000])
    else:
        axes.marker_ignore(*l1)

def show_plots(*sites, savefig=False):
    time_data, air_data, label = get_plot_data(sites[0], days=1)
    axes = create_plot(time_data)
    plot_air_data(axes, air_data, label=label, marker=True)

    for s in sites[1:]:

        time_data, air_data, label = get_plot_data(s, days=1)
        plot_air_data(axes, air_data, label=label[:12], marker=False, alpha=0.2, color='gray')

    axes.set_ylim([-5, 100])

    plt.tight_layout()
    plt.legend()
    if savefig:
        axes.figure.savefig(r'air_quality_history.png')

# show_plots('uintah', 'morgan_city_b')
# plt.show()