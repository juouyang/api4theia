API_PORT = 5000
TESTING = False
DEBUG = False
LOG_LEVEL = 0 # ERROR=40, https://docs.python.org/3/howto/logging.html#logging-levels

# change the following settings before run
DOCKER_HOST = "pve.dev.net"
CRT_FILE = 'ssl/dev.net.crt'
KEY_FILE = 'ssl/dev.net.key'
STRATEGY_TEMPLATE = "/root/builds/Doquant/Strategy"
THEIA_ROOT = "/media/nfs/theia"
#

THEIA_PORT = 30000
DOCKER_IMAGE = "theia-python:aicots"
PACK_CMD = "curl -s https://raw.githubusercontent.com/juouyang-aicots/py2docker/main/build.sh | bash"
RUNNING_THEIA_PER_USER = 100
MAX_STRATEGY_NUM = 100
GIT_IGNORE = '''
/.pytest_cache/
__pycache__/
*.py[cod]
/venv/
/.vscode/
**/log*
**/.theia
**/.sandbox
**/.Trash*
'''
GIT_INIT = "git init;git config user.email 'root@local';git add ./*;git add .gitignore;git commit -m 'first commit'"
MATPLOTLIB_SAMPLE = '''
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
t = np.arange(0.0, 2.0, 0.01)
s = 1 + np.sin(2 * np.pi * t)
fig, ax = plt.subplots()
ax.plot(t, s)
ax.set(xlabel='time (s)', ylabel='voltage (mV)', title='About as simple as it gets, folks')
ax.grid()
fig.savefig("plot.png")
'''
PLOTLY_SAMPLE = '''
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['AAPL.Open'],
                high=df['AAPL.High'],
                low=df['AAPL.Low'],
                close=df['AAPL.Close'],
                increasing_line_color= 'red',
                decreasing_line_color= 'green')])
fig.update_layout(hovermode='x')
fig.show()
'''