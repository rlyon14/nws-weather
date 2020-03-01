
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

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLineEdit, QInputDialog, QWidget, QPushButton, QGridLayout, QLabel, QWidget
from pathlib import Path
import sys

dir_ = Path(__file__).parent

class InputDialog(QtWidgets.QMainWindow):
    def __init__(self, parent, select_callback):       
        super(InputDialog, self).__init__(parent)

        self._main = QtWidgets.QWidget()
        self.select_callback = select_callback
        
        #self.setStyle(QStyleFactory.create('Fusion'))

        self.setCentralWidget(self._main)
        layout = QGridLayout(self._main)
        #self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        label1 = QLabel("Station ID:")
        label2 = QLabel("Days:")

        self.station_id = QLineEdit()
        self.days = QLineEdit()

        okbutton = QPushButton("Ok")
        okbutton.clicked.connect(self.select_station)
        okbutton.setDefault(True)
        cancelbutton = QPushButton("Cancel")
        cancelbutton.clicked.connect(self.select_cancel)

        layout.addWidget(label1,          0, 0)
        layout.addWidget(self.station_id,  0, 1, 1,2)

        layout.addWidget(label2,          1, 0)
        layout.addWidget(self.days, 1, 1,1,2)

        layout.addWidget(okbutton,          2, 1)
        layout.addWidget(cancelbutton,   2, 2)

        layout.setSpacing(5)

        #self.setLayout(layout)
        
        self.setWindowTitle('Station Entry')

    def select_station(self):
        id = self.station_id.text()
        days = self.days.text()
        self.select_callback(id, days)
        self.close()

    def select_cancel(self):
        self.close()

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            self.select_station()
        super().keyPressEvent(event)

class Second(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Second, self).__init__(parent)

class WeatherPlot():
    def __init__(self, site, days=3):

        icon = dir_/ 'icons/location.png'
        self.fig, (self.ax1, self.ax2) = interactive_subplots(2, 1, figsize=(20,10), constrained_layout=True, icon=str(icon), title='Weather History')
        self.site = site
        self.days = days
        self.qapp = self.fig.qapp
        self.app = self.fig.app

        self.par1 = self.ax1.twinx()
        self.par2 = self.ax2.twinx()

        self.fig.marker_enable(show_xlabel=True, top_axes=(self.ax1, self.ax2))
        self.ax2.marker_link(self.ax1)

        self.app.add_toolbar_actions((dir_/ 'icons/location.png', 'Location', 'Set Station', self.set_station),
                                    (dir_/ 'icons/refresh.png', 'Update', 'Update', self.plot ))
        self.plot(site)

    def plot(self, site=None, days=None):
        print(days)
        site = self.site if site == None else site
        days = days.strip() if days != None else self.days
        if days == '':
            days = self.days
        try:
            days = str(days)
        except:
            days = self.days
        
        self.ax1.clear()
        self.ax2.clear()
        self.par1.clear()
        self.par2.clear()

        self.ax2.patch.set_visible(False)
        self.ax1.patch.set_visible(False)   
        print(days)

        #fig.canvas.draw()
        if site[0] == 'K' and len(site.strip()) == 4:
            self.plot_nws(site)
        else:
            self.plot_aprs(site, days=days)

        self.app.update_traces_group()

        self.ax1.legend(fontsize='small', loc='upper left')
        self.par1.legend(fontsize='small', loc='upper right')

        self.ax2.legend(fontsize='small', loc='upper left')
        self.par2.legend(fontsize='small', loc='upper right')
        self.fig.canvas.draw()
        self.site = site
        self.days = days


    def set_station(self):
        #site, ok = 
        dialog = InputDialog(self.app, self.plot)
        dialog.show()
        #self.qapp.exec_()

    def plot_nws(self, site):

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

        self.ax1.set_title('3 Day History for {} ({})'.format(title, site))
        self.ax1.grid(linewidth=0.5, linestyle='-')
        self.ax2.grid(linewidth=0.5, linestyle='-')

        ##precip plot
        max_precip = np.nanmax(precip) if np.any(np.isfinite(precip)) else 0
        m, s, b0 = self.par1.stem(dates_sec, precip, 'b', linefmt='-', markerfmt='b.', basefmt=' ', use_line_collection=True, label='precip (in)')
        #par1.plot(dates_sec, precip, 'b', label='precip (in)')

        self.par1.set_ylim([0, max_precip*4 + 0.1])
        #plt.sca(ax1)
        self.ax1.set_xticks(xlabels_sec)
        self.ax1.set_xticklabels(xlabels)
        self.ax1.tick_params(labelsize='x-small')
        self.par1.tick_params(labelsize='x-small')

        ## temperature and dew point
        self.ax1.plot(dates_sec, temps, 'r', label = 'temp (F)')
        self.ax1.plot(dates_sec, dew, 'g', label = 'dewpnt (F)')
        
        #plt.sca(ax2)
        self.ax2.set_xticks(xlabels_sec)
        self.ax2.set_xticklabels(xlabels)
        self.ax2.tick_params(labelsize='x-small')
        self.par2.tick_params(labelsize='x-small')

        self.ax1.set_xlim([dates_sec[-1]-5000, dates_sec[0]+5000])
        self.ax2.set_xlim([dates_sec[-1]-5000, dates_sec[0]+5000])
        
        #m1, s1, b1 = ax2.stem(dates_sec, wind, 'b', label = 'max wind (mph)', markerfmt='.', basefmt=' ', use_line_collection=True)
        self.ax2.plot(dates_sec, wind, 'b', label = 'max wind (mph)')
        line = self.par2.plot(dates_sec, pres, 'gray', label = 'pres (inHg)')

        ## set up markers
        self.ax1.marker_set_params(xreversed=True, xformat=xdata_to_timestamp)
        self.ax2.marker_set_params(xreversed=True, xformat=xdata_to_timestamp)

        self.ax1.marker_ignore(b0)
        self.ax2.marker_ignore(line[0])

        self.ax2.marker_set_params(yformat=xydata_to_wind)
        
        self.ax1.marker_add(xd=dates_sec[0])
        self.ax2.marker_add(xd=dates_sec[0])


    def plot_aprs(self, site, days=3):

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

        self.ax1.set_title(title)
        self.ax1.grid(linewidth=0.5, linestyle='-')
        self.ax2.grid(linewidth=0.5, linestyle='-')

        self.ax1.set_xticks(xlabels_sec)
        self.ax1.set_xticklabels(xlabels)
        self.ax1.tick_params(labelsize='x-small')
        self.par1.tick_params(labelsize='x-small')

        ## temperature and dew point
        self.ax1.plot(dates_sec, temps, 'r', label = 'temp (F)')
        self.ax1.plot(dates_sec, dew, 'g', label = 'dewpnt (F)')
        
        self.ax1.legend(fontsize='small', loc='upper left')
        
        #plt.sca(ax2)
        self.ax2.set_xticks(xlabels_sec)
        self.ax2.set_xticklabels(xlabels)
        self.ax2.tick_params(labelsize='x-small')
        self.par2.tick_params(labelsize='x-small')

        self.ax1.set_xlim([dates_sec[0]-5000, dates_sec[-1]+5000])
        self.ax2.set_xlim([dates_sec[0]-5000, dates_sec[-1]+5000])
        
        #m1, s1, b1 = ax2.stem(dates_sec, wind, 'b', label = 'max wind (mph)', markerfmt='.', basefmt=' ', use_line_collection=True)
        self.ax2.plot(dates_sec, wind, 'b', label = 'max wind (mph)')

        line = self.par2.plot(dates_sec, pres, 'gray', label = 'pres (mbar)')

        self.ax2.marker_ignore(line[0])
        #ax2.marker_ignore(line[0])

        self.ax1.marker_set_params(xformat=xdata_to_timestamp)
        self.ax2.marker_set_params(xformat=xdata_to_timestamp)

        self.ax2.marker_set_params(yformat=xydata_to_wind)

        self.ax1.marker_add(xd=dates_sec[-1])
        self.ax2.marker_add(xd=dates_sec[-1])


    def plot_compare(self, *sites, days=7):
        matplotlib.use('Qt5Agg')
        titles = [None]*len(sites)
        time_dataz = [None]*len(sites)
        weather_dataz = [None]*len(sites) 

        for i, site in enumerate(sites):
            if site[0] == 'K' and len(site.strip()) == 4:
                titles[i], time_dataz[i], weather_dataz[i] = fetch_nws_station(site)
            else:
                titles[i], time_dataz[i], weather_dataz[i]  = fetch_aprs_station(site, days)

        fig, (ax1) = interactive_subplots(1, 1, figsize=(18 ,9), constrained_layout=True)
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
        plt.show()
        #ax1.marker_add(xd=dates_sec[-1])


if __name__ == '__main__':
    plot_nws('KLMO')
    #plot_aprs('EW0013')
    #plot_compare('KLMO', 'KSLC', 'KPVU',days=3)
    plt.show()