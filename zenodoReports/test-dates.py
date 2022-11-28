#! /usr/bin/env python3

import sys
import codecs
import datetime
from dateutil import rrule
import pandas as pd
import numpy as np
from matplotlib import pylab
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from matplotlib.dates import DateFormatter

pd.plotting.plot_params = {'x_compat': True}

data = {
    'date': [pd.Timestamp(2014, 9, 28), pd.Timestamp(2014, 10, 5), pd.Timestamp(2014, 10, 12)],
    'val': [0.37,0.44,0.44]
}
df = pd.DataFrame(data=data)
ax = df.plot(x='date', y='val', kind='line')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

fig = ax.get_figure()
fig.savefig('test.png')