
import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import markerplot
from markerplot import interactive_subplots
import matplotlib


start_date = datetime.datetime.strptime('03/1/20', '%m/%d/%y')

dates_a   = []
date_days = []
date_label = []
date_label_i = []

days_projection = 7
        # self.ax1.set_xticks(xlabels_sec)
        # self.ax1.set_xticklabels(xlabels)

#us_data = np.array([13, 13, 13, 13, 13, 13, 15, 15, 51, 51, 57, 58, 60, 68 ,74, 
us_data = np.array([98, 118, 149, 217, 262, 402, 518, 583, 959, 1.3e3, 1.7e3, 2.2e3, 2.7e3, 3.5e3, 4.6e3, 6.4e3, 7.8e3, 13.7e3, 19.1e3, 25.5e3, 33.3e3, 43.8e3, 53.7e3, 65.8e3, 83.8e3, 101.7e3, 121.5e3])

for i, dp in enumerate(us_data):
    date =start_date + datetime.timedelta(days=i)
    dates_a.append(date)
    date_days.append(i)
    if i % 5 ==0 and i != 0:
        date_label.append(date.strftime('%m/%d'))
        date_label_i.append(i)

        


dates_p   = list(dates_a)
date_days_p = list(date_days)

for i in range(days_projection):
    date =start_date + datetime.timedelta(days=len(us_data)+i)
    dates_p.append(date)
    date_days_p.append(i+len(us_data))

    if i % 5 ==0  and i != 0:
        date_label.append(date.strftime('%m/%d'))
        date_label_i.append(len(us_data) + i)
        


def xformat(x, idx=None):
    date = start_date + datetime.timedelta(days=int(x))
    return date.strftime('%m/%d')

def yformat(x, y, mxd):
    return '{:0.3f}'.format(y)

fig, (ax1, ax2, ax3) = interactive_subplots(3, 1, figsize=(20,10), constrained_layout=True, show_xlabel=True, xformat=xformat)

date_days = np.array(date_days)
date_days_p = np.array(date_days_p)

r = 1.3

data = (us_data)/1
model = (r**(date_days_p + 18))/1

data_log = np.log10(data)
model_log = np.log10(model)

ax1.plot(date_days, data/1e6, label='actual')
ax1.plot(date_days_p, model/1e6, label='model')
ax1.marker_set_params(yformat=lambda x, y, mxd: '{:.3f} M'.format(y))
ax1.set_ylabel('US Cases (millions)')

ax1.set_xticks(date_label_i)
ax1.set_xticklabels(date_label)

diff = np.diff(us_data)
g_factor = diff[1:]/diff[:-1]

ax2.plot(date_days, data, label='actual')
ax2.plot(date_days_p, model, label='model')
ax2.set_yscale('log')
ax2.marker_set_params( inherit_ticker=False)

ax2.set_xticks(date_label_i)
ax2.set_xticklabels(date_label)

ax3.plot(date_days[:-2], g_factor, label='growth_factor')
ax3.set_ylabel('US Growth Rate')
ax3.set_xticks(date_label_i)
ax3.set_xticklabels(date_label)
ax3.set_xlim(ax2.get_xlim())


ax1.grid(True)
ax2.grid(True)
ax3.grid(True)
plt.show()