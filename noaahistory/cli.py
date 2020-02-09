from noaahistory import plot_aprs, plot_nws, plotAirQuality, plot_compare
import matplotlib.pyplot as plt
import configparser
from pathlib import Path

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
        p1 = plotAirQuality()
    
    if len(site) == 0:
        site = get_station_default()

    if len(site) > 1:
        plot_compare(*site, days=days)
    else:
        site = site[0]
        if site[0] == 'K' and len(site.strip()) == 4:
            plot_nws(site)
        else:
            plot_aprs(site, days)

        if name != None:
            write_station_name(name, site)

    if default:
        set_station_default(site)

    plt.show()