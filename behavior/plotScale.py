import matplotlib.ticker as ticker

def plotScale(ax, axis, factor):
    if axis == 'x':
        ticks = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x*factor))
        ax.xaxis.set_major_formatter(ticks)
    elif axis == 'y':
        ticks = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x*factor))
        ax.yaxis.set_major_formatter(ticks)
    else:
        raise NameError('Wrong axis! Please pick "x" or "y".')
    return ax
