import http
import urllib.request
import datetime
import re
import json
import markerplot
import matplotlib.pyplot as plt
from dateutil import tz
import configparser
from pathlib import Path

# This doesn't work anymore since they updated their API, as far I can tell, they no longer provide a full index of sensors
# You can click on JSON data at the bottom of the sensor popup on the map to get the station ID
# def get_station_id(label):
#     f = urllib.request.urlopen(r'https://www.purpleair.com/json')
#     url_stream = f.read().decode('utf-8')
#     data = json.loads(url_stream)['results']
#     results = {}
#     label = label.lower().strip()
#     for ii, d in enumerate(data):
#         if label in d['Label'].lower().strip():
#             results[d['ID']] = d['Label']
#     return results
    
def write_station_api_keys(station_id, name):
    dir_ = Path(__file__).parent

    config = configparser.ConfigParser()
    config.read(dir_ / 'air_keys.ini')
    
    f = urllib.request.urlopen(r'https://www.purpleair.com/json?show={}'.format(station_id))
    url_stream = f.read().decode('utf-8')
    data = json.loads(url_stream)['results']
    
    keys = {'STATION_ID': data[0]['ID'],
            'STATION_LABEL': data[0]['Label'],
            'PRIMARY_ID': data[0]['THINGSPEAK_PRIMARY_ID'],
            'PRIMARY_KEY': data[0]['THINGSPEAK_PRIMARY_ID_READ_KEY'],
            'SECONDARY_ID': data[0]['THINGSPEAK_SECONDARY_ID'],
            'SECONDARY_KEY': data[0]['THINGSPEAK_SECONDARY_ID_READ_KEY'],
           }
    
    config[name] = keys
    with open(dir_ / 'air_keys.ini', 'w') as configfile:
        config.write(configfile)
    
    return data

# r = write_station_api_keys(45627, "uintah")
# print(r)
