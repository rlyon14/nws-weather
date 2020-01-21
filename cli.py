from noaahistory import plotTemp, plotAPRL
import matplotlib.pyplot as plt

import click

@click.command()
@click.argument('loc')
def cli(loc):
    """ [boulder, leesburg, provo, longmont, bend]
    """
    if loc[0] == 'K':
        p = plotTemp(loc)
    else:
        if loc[1] == 'W':
           loc = loc.replace('W', '') 
           p = plotAPRL(loc)
    plt.show()


if __name__ == '__main__':
    p = plotTemp('KSLC')
    plt.show()