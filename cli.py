from noaahistory import plotTemp
import matplotlib.pyplot as plt

import click

@click.command()
@click.argument('loc')
def cli(loc):
    """ [boulder, leesburg, provo, longmont, bend]
    """

    p = plotTemp(loc)
    plt.show()


if __name__ == '__main__':
    p = plotTemp('KSLC')
    plt.show()