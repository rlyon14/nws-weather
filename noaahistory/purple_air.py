
import http
import urllib.request
import numpy as np
import datetime
import re
import json
from markerplot import interactive_subplots
import matplotlib.pyplot as plt
from dateutil import tz

def get_station_id(label):
    f = urllib.request.urlopen(r'https://www.purpleair.com/json')
    url_stream = f.read().decode('utf-8')
    data = json.loads(url_stream)['results']
    results = {}
    label = label.lower().strip()
    for ii, d in enumerate(data):
        if label in d['Label'].lower().strip():
            results[d['Label']] = d['ID'], ii
    return results, data
    
def get_station_api_keys(station_id):

    f = urllib.request.urlopen(r'https://www.purpleair.com/json?show={}'.format(station_id))
    url_stream = f.read().decode('utf-8')
    data = json.loads(url_stream)['results']

    channel_id = data[0]['THINGSPEAK_PRIMARY_ID']
    api_key = data[0]['THINGSPEAK_PRIMARY_ID_READ_KEY']
    label = data[0]['Label']
    
    return channel_id, api_key, label

def get_sensor_data(channel, key, days=1):
    data = urllib.request.urlopen(r'https://api.thingspeak.com/channels/{}/feeds.json?api_key={}&days={}'.format(channel, key, days)).read().decode('utf-8')
    return json.loads(data)

## BEND: 34145
ch_id, api_key, site_label = get_station_api_keys(30993)
s = get_sensor_data(ch_id, api_key, days=1)

l_feeds = len(s['feeds'])
xlabels = []
xlabels_sec = []
dt = []

dates_sec = []
pm2p5 = np.zeros(l_feeds)
pm10 = np.zeros(l_feeds)
pm1p0 = np.zeros(l_feeds)

from_zone = tz.tzutc()
to_zone = tz.tzlocal()
for i, f in enumerate(s['feeds']):
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

    
## plotting
fig, ax1 = interactive_subplots(figsize=(15,10), constrained_layout=False)

def xdata_to_timestamp(sec):
    dt = start_time + datetime.timedelta(seconds=sec)
    return dt.strftime('%m/%d %H:%M')

ax1.grid(linewidth=0.5, linestyle='-')

ax1.set_title(site_label)
ax1.set_xticks(xlabels_sec)
ax1.set_xticklabels(xlabels)
ax1.tick_params(labelsize='small')

ax1.set_xlim([dates_sec[0]-5000, dates_sec[-1]+5000])
ax1.marker_set_params(xformat=xdata_to_timestamp, xreversed=False, show_xlabel=True)


ax1.plot(dates_sec, pm2p5, label='PM2.5 ($\mu g / m^3$)')
l1 = ax1.plot(dates_sec, pm10, color='gray', alpha=0.5, label='PM10 ($\mu g / m^3$)')

ax1.marker_ignore(*l1)

ax1.axhspan(0, 12, color='green', alpha=0.3)
ax1.axhspan(12, 35, color='yellow', alpha=0.3)
ax1.axhspan(35, 55, color='orange', alpha=0.35)
ax1.axhspan(55, 150, facecolor='red', alpha=0.3)
ax1.axhspan(150, 250, facecolor='purple', alpha=0.3)
ax1.axhspan(250, 500, facecolor='maroon', alpha=0.3)

ax1.set_ylim([-5, 100])
ax1.marker_add(xd=dates_sec[-1])

plt.tight_layout()
fig.savefig(r'C:\Users\rlyon\site\pages\air_quality_history.png')
# plt.show()
    
    
    