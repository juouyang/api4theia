import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DB = 'Json'
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'CHANGE_THIS_DEFAULT_SECRET'
    DOCKER_IMAGE = "theia-python:dev"
    ONETIME_PW_ENABLED = True
    ONETIME_PW_LEN = 18
    GIT_IGNORE = (
        "/.pytest_cache/\n"
        "__pycache__/\n"
        "*.py[cod]\n"
        "/venv/\n"
        "/.vscode/\n"
        "**/log*\n"
        "**/.theia\n"
        "**/.sandbox\n"
        "**/.Trash*\n"
    )
    GIT_INIT = "git init 2>&1 >/dev/null;git config user.email 'root@local';git add ./* 2>&1 >/dev/null;git add .gitignore 2>&1 >/dev/null;git commit -m 'first commit' 2>&1 >/dev/null"
    DEBUG_SETTING = '''
{"version":"0.2.0","configurations":[{"name":"PROJECT_NAME","type":"python","request":"launch","program":"${workspaceFolder}/%s/__main__.py","console":"integratedTerminal"}]}
    '''
    HELLO_MATPLOTLIB = (
        "import matplotlib\n"
        "import matplotlib.pyplot as plt\n"
        "import numpy as np\n"
        "t = np.arange(0.0, 2.0, 0.01)\n"
        "s = 1 + np.sin(2 * np.pi * t)\n"
        "fig, ax = plt.subplots()\n"
        "ax.plot(t, s)\n"
        "ax.set(xlabel='time (s)', ylabel='voltage (mV)', title='About as simple as it gets, folks')\n"
        "ax.grid()\n"
        "fig.savefig(\"plot.png\")\n"
    )
    HELLO_PLOTLY = (
        "import plotly.graph_objects as go\n"
        "import pandas as pd\n"
        "from datetime import datetime\n"
        "df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')\n"
        "fig = go.Figure(data=[go.Candlestick(x=df['Date'],\n"
        "               open=df['AAPL.Open'],\n"
        "                high=df['AAPL.High'],\n"
        "                low=df['AAPL.Low'],\n"
        "                close=df['AAPL.Close'],\n"
        "                increasing_line_color= 'red',\n"
        "                decreasing_line_color= 'green')])\n"
        "fig.update_layout(hovermode='x')\n"
        "fig.show()\n"
    )
    HELLO_TENSORFLOW = (
        "import tensorflow as tf\n"
        "mnist = tf.keras.datasets.mnist\n"
        "(x_train, y_train), (x_test, y_test) = mnist.load_data()\n"
        "x_train, x_test = x_train / 255.0, x_test / 255.0\n"
        "model = tf.keras.models.Sequential([\n"
        "    tf.keras.layers.Flatten(input_shape=(28, 28)),\n"
        "    tf.keras.layers.Dense(128, activation='relu'),\n"
        "    tf.keras.layers.Dropout(0.2),\n"
        "    tf.keras.layers.Dense(10)\n"
        "])\n"
        "predictions = model(x_train[:1]).numpy()\n"
        "predictions\n"
        "tf.nn.softmax(predictions).numpy()\n"
        "loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)\n"
        "loss_fn(y_train[:1], predictions).numpy()\n"
        "model.compile(optimizer='adam',\n"
        "    loss=loss_fn,\n"
        "    metrics=['accuracy'])\n"
        "model.fit(x_train, y_train, epochs=5)\n"
        "model.evaluate(x_test,  y_test, verbose=2)\n"
        "probability_model = tf.keras.Sequential([\n"
        "    model,\n"
        "    tf.keras.layers.Softmax()\n"
        "])\n"
        "probability_model(x_test[:5])\n"
    )
    HELLO_TALIB = (
        "import numpy as np\n"
        "import pandas as pd\n"
        "import talib\n"
        "all_ta_label = talib.get_functions()\n"
        "all_ta_groups = talib.get_function_groups()\n"
        "table = pd.DataFrame({\n"
        "    'TA-Lib Groups': list(all_ta_groups.keys()),\n"
        "    'Index Count': list(map(lambda x: len(x), all_ta_groups.values()))\n"
        "})\n"
        "print(table)\n"
    )
    HELLO_SCIPY = (
        "from scipy.interpolate import interp1d\n"
        "import pylab\n"
        "import numpy as np\n"
        "x = np.linspace(0, 5, 10)\n"
        "y = np.exp(x) / np.cos(np.pi * x)\n"
        "f_nearest = interp1d(x, y, kind='nearest')\n"
        "f_linear  = interp1d(x, y)\n"
        "f_cubic   = interp1d(x, y, kind='cubic')\n"
        "x2 = np.linspace(0, 5, 100)\n"
        "pylab.plot(x, y, 'o', label='data points')\n"
        "pylab.plot(x2, f_nearest(x2), label='nearest')\n"
        "pylab.plot(x2, f_linear(x2), label='linear')\n"
        "pylab.plot(x2, f_cubic(x2), label='cubic')\n"
        "pylab.legend()\n"
        "pylab.show()\n"
    )
    HELLO_STATSMODEL = (
        "import numpy as np\n"
        "import statsmodels.api as sm\n"
        "import statsmodels.formula.api as smf\n"
        "dat = sm.datasets.get_rdataset('Guerry', 'HistData').data\n"
        "results = smf.ols('Lottery ~ Literacy + np.log(Pop1831)', data=dat).fit()\n"
        "print(results.summary())\n"
    )
    HELLO_QUANDL = (
        "import quandl\n"
        "quandl.ApiConfig.api_key = 'xti1h_ei-7KweXvgU5VH' # Get your access key from https://www.quandl.com\n"
        "data = quandl.get('NSE/OIL')\n"
        "print(data.head())\n"
        "data = quandl.get_table('ZACKS/FC', ticker='AAPL')\n"
        "print(data.head())\n"
    )
    HELLO_PYTORCH = (
        "import torch\n"
        "import matplotlib.pyplot as plt\n"
        "myTensor = torch.FloatTensor(7, 7)\n"
        "myTensor[:, :] = 0   # Assign zeros everywhere in the matrix.\n"
        "myTensor[3, 3] = 1   # Assign one in position 3, 3\n"
        "myTensor[:2, :] = 1   # Assign ones on the top 2 rows.\n"
        "myTensor[-2:, :] = 1    # Assign ones on the bottom 2 rows.\n"
        "plt.figure()\n"
        "plt.imshow(myTensor.numpy())\n"
        "plt.colorbar()\n"
        "plt.show()\n"
    )
    HELLO_CAFFE2 = (
        "from caffe2.python import workspace\n"
        "import numpy as np\n"
        "print ('Creating random data')\n"
        "data = np.random.rand(3, 2)\n"
        "print(data)\n"
        "print('Adding data to workspace ...')\n"
        "workspace.FeedBlob('mydata', data)\n"
        "print('Retrieving data from workspace')\n"
        "mydata = workspace.FetchBlob('mydata')\n"
        "print(mydata)\n"
    )
    PACK_CMD = "echo Packing... && sleep 30 && echo Packed finished."

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    API_PORT = 5000
    CONTAINER_PORT = 30000 # 30000 ~ 30107 (12 * 9)
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 0 # ERROR=40, https://docs.python.org/3/howto/logging.html#logging-levels
    FQDN = "pve.dev.net"
    CRT_FILE = 'app/ssl/pve.dev.net.crt'
    KEY_FILE = 'app/ssl/pve.dev.net.key'
    TEMPLATE_PROJECT = basedir + "/migrations/templates/dev"
    STORAGE_POOL = "/tmp/theia-dev"
    MAX_CONTAINER_NUM = 9
    MAX_STRATEGY_NUM = 9
    ONETIME_PW_ENABLED = False


class TestingConfig(DevelopmentConfig):
    TESTING = True
    DB = 'Ram'
    API_PORT = 65000
    CONTAINER_PORT = 40000
    FQDN = 'localhost'
    WTF_CSRF_ENABLED = False
    ONETIME_PW_ENABLED = False


class ProductionConfig(Config):
    API_PORT = 443
    CONTAINER_PORT = 30000 # 30000 ~ 30035 (12 * 3)
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 40 # ERROR=40, https://docs.python.org/3/howto/logging.html#logging-levels
    FQDN = "THIS_IS_YOUR_PRODUCTION_FQDN"
    CRT_FILE = 'THIS_IS_THE_SSL_CRT_OF_YOUR_FQDN'
    KEY_FILE = 'THIS_IS_THE_SSL_KEY_OF_YOUR_FQDN'
    TEMPLATE_PROJECT = basedir + "/migrations/templates/prod"
    STORAGE_POOL = "/tmp/theia-prod"
    MAX_CONTAINER_NUM = 3
    MAX_STRATEGY_NUM = 100
    ONETIME_PW_ENABLED = False


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,

    'default': DevelopmentConfig
}
