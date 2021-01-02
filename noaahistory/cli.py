from noaahistory import WeatherPlot
import matplotlib.pyplot as plt
import configparser
from pathlib import Path
# import purple_air
from . purple_air import show_plots

import click

def write_station_name(name, site):
    dir_ = Path(__file__).parent
    filepath = dir_ / 'config.ini'
    config = configparser.ConfigParser()
    if filepath.exists():
        config.read(dir_ / 'config.ini')
        config['station_names'][name] = site
        with open(dir_ / 'config.ini', 'w') as configfile:
            config.write(configfile)
    else:
        config['station_names'] = {name:site}
        with open(filepath, 'w') as configfile:
            config.write(configfile)

def set_station_default(site):
    dir_ = Path(__file__).parent
    filepath = dir_ / 'config.ini'
    config = configparser.ConfigParser()
    if filepath.exists():
        config.read(dir_ / 'config.ini')
        config['station_default'] = {}
        config['station_default']['site'] = str(site)
        with open(dir_ / 'config.ini', 'w') as configfile:
            config.write(configfile)
    else:
        config['station_default'] = {}
        config['station_default']['site'] = str(site)
        with open(filepath, 'w') as configfile:
            config.write(configfile)

def get_station_names():
    dir_ = Path(__file__).parent
    filepath = dir_ / 'config.ini'
    config = configparser.ConfigParser()
    names = {}
    if filepath.exists():
        config.read(dir_ / 'config.ini')
        names = dict(config['station_names'])
    return names

def get_station_default():
    dir_ = Path(__file__).parent
    filepath = dir_ / 'config.ini'
    config = configparser.ConfigParser()
    config.read(dir_ / 'config.ini')
    site = config['station_default']['site']
    site = site.replace("'", "")
    return site.strip('][').split(', ') 

@click.command()
@click.argument('site', nargs=-1)
@click.option('--days', default=3, help='number of days (only for APRS)')
@click.option('--air', is_flag=True)
@click.option('--name', help='assign current station call sign to name')
@click.option('--default', is_flag=True, help='set current plot to default')

def cli(site, days, air, name, default):

    station_names = get_station_names()
    site = list(site)
    for i, s in enumerate(site):
        if s in station_names.keys():
            site[i] = station_names[s]

    if (air):
        show_plots('uintah', 'morgan_city_b')
    
    if len(site) == 0:
        site = get_station_default()

    if len(site) > 1:
        w = WeatherPlot(site, days)
    else:
        site = site[0]
        w = WeatherPlot(site, days)

        if name != None:
            write_station_name(name, site)

    if default:
        set_station_default(site)

    plt.show()

if __name__ == '__main__':
    w = WeatherPlot('KLMO')
    #plot_handler('KCLM', 'nws')

    #plot_aprs('EW0013')
    #plot_compare('KLMO', 'KSLC', 'KPVU',days=3)
    plt.show()