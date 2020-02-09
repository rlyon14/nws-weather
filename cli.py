from noaahistory import plot_aprs, plot_nws, plotAirQuality
import matplotlib.pyplot as plt

import click

@click.command()
@click.option('--air', is_flag=True, help='Show pm2.5 and pm10 levels (Longmont only)')
@click.argument('site', default='KLMO')
@click.argument('days', default=3)
def cli(site, days, air):
    if (air):
        p1 = plotAirQuality()

    if site[0] == 'K' and len(site.strip()) == 4:
        plot_nws(site)
    else:
        plot_aprs(site, days)
    plt.show()

if __name__ == '__main__':
    p = plot_nws('KLMO')
    plt.show()