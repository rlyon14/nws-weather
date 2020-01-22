from noaahistory import plotTemp, plotAPRS, plotAirQuality
import matplotlib.pyplot as plt

import click

@click.command()
@click.option('--air', is_flag=True, help='Show pm2.5 and pm10 levels (Longmont only)')
@click.argument('site', default='KLMO')
@click.argument('days', default=3)
def cli(site, days, air):
    if (air):
        p1 = plotAirQuality()

    if site[0] == 'K':
        p = plotTemp(site)
    else:
        if site[1] == 'W':
           site = site.replace('W', '') 
        p = plotAPRS(site, days)
    plt.show()


if __name__ == '__main__':
    p = plotTemp('KSLC')
    plt.show()