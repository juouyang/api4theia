import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DB = 'Json'
    SECRET_KEY = os.environ.get("SECRET_KEY") or '85114481'
    DOCKER_IMAGE = "theia-python:aicots"
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

    PACK_CMD = "curl -s https://raw.githubusercontent.com/juouyang-aicots/py2docker/main/build.sh | bash"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    API_PORT = 5000
    CONTAINER_PORT = 30000
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 0 # ERROR=40, https://docs.python.org/3/howto/logging.html#logging-levels
    FQDN = "pve.dev.net"
    CRT_FILE = 'app/ssl/pve.dev.net.crt'
    KEY_FILE = 'app/ssl/pve.dev.net.key'
    TEMPLATE_PROJECT = "/root/builds/Doquant/Strategy"
    STORAGE_POOL = "/media/nfs/theia"
    MAX_CONTAINER_NUM = 100
    MAX_STRATEGY_NUM = 100


class TestingConfig(DevelopmentConfig):
    TESTING = True
    DB = 'Ram'
    API_PORT = 65000
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    API_PORT = 443
    CONTAINER_PORT = 30000
    WTF_CSRF_ENABLED = True
    LOG_LEVEL = 40 # ERROR=40, https://docs.python.org/3/howto/logging.html#logging-levels
    FQDN = "dost1.doquant.com"
    CRT_FILE = '/etc/letsencrypt/live/dost1.doquant.com/fullchain.pem'
    KEY_FILE = '/etc/letsencrypt/live/dost1.doquant.com/privkey.pem'
    TEMPLATE_PROJECT = "/home/aicots/builds/Doquant/Strategy"
    STORAGE_POOL = "/media/aicots/ssd/theia"
    MAX_CONTAINER_NUM = 3
    MAX_STRATEGY_NUM = 100


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
