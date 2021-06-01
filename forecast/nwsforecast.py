from noaahistory import HTMLreader, HTMLnode
import http
import urllib.request
import numpy as np
import datetime
import re
import matplotlib.pyplot as plt
from pathlib import Path

dir_ = Path(__file__).parent

site = r'https://forecast.weather.gov/MapClick.php?lat=41.15&lon=-111.95'
f = urllib.request.urlopen(site)
html = HTMLreader(f)

template_f = open(dir_ / r'template.html')
html_template = HTMLreader(template_f)

forecast_7day = html.findElement('div', 'id','seven-day-forecast')[0]

template_loc = html_template.findElement('div', 'class','contentArea')[0]

embedded_imgs = forecast_7day.findElement('img')

for img_node in embedded_imgs:
    path = img_node.attr['src'].strip()

    path = r'https://forecast.weather.gov/' + path
    img_node.attr['src'] = path

## substitute new data in template
forecast_7day.nextSib = None
forecast_7day.prevSib = None
forecast_7day.parent = template_loc

template_loc.firstChild = forecast_7day
template_loc.lastChild = forecast_7day

html_template.printToFile(dir_ / 'test.html')